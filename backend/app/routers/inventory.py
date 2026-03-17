"""
Shelf Life Estimator — Inventory Router
=========================================
Manage the user's personal food inventory.
Track scanned items, update storage methods, mark consumed.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.schema import FoodItem, UserInventory, Notification
from app.schemas.schemas import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventoryListResponse,
    MessageResponse,
)
from app.ai.estimator import estimate_shelf_life, get_days_for_method

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

# Hardcoded user_id for Phase 1 (single-user mode)
# Will be replaced with actual auth in Phase 4
DEFAULT_USER_ID = 1


@router.get(
    "/",
    response_model=InventoryListResponse,
    summary="Get user's inventory",
    description="Get all food items in the user's inventory with freshness status.",
)
async def get_inventory(
    include_consumed: bool = Query(False, description="Include consumed items"),
    include_expired: bool = Query(True, description="Include expired items"),
    sort_by: str = Query("expiry", description="Sort by: expiry, name, freshness, added"),
    db: AsyncSession = Depends(get_db),
):
    """Get the user's full food inventory with summary stats."""
    query = (
        select(UserInventory)
        .options(selectinload(UserInventory.food_item))
        .where(UserInventory.user_id == DEFAULT_USER_ID)
    )

    if not include_consumed:
        query = query.where(UserInventory.is_consumed == False)
    if not include_expired:
        query = query.where(UserInventory.is_expired == False)

    # Apply sorting
    if sort_by == "expiry":
        query = query.order_by(UserInventory.estimated_expiry.asc())
    elif sort_by == "name":
        query = query.order_by(UserInventory.food_item_id)
    elif sort_by == "freshness":
        query = query.order_by(UserInventory.freshness_score.desc())
    elif sort_by == "added":
        query = query.order_by(UserInventory.scanned_at.desc())

    result = await db.execute(query)
    items = result.scalars().all()

    # Calculate summary stats
    now = datetime.now(timezone.utc)
    two_days_later = now + timedelta(days=2)

    total = len(items)
    expiring_soon = sum(
        1 for item in items
        if not item.is_expired
        and not item.is_consumed
        and item.estimated_expiry <= two_days_later
    )
    expired = sum(1 for item in items if item.is_expired)

    return InventoryListResponse(
        items=items,
        total=total,
        expiring_soon=expiring_soon,
        expired=expired,
    )


@router.post(
    "/",
    response_model=InventoryItemResponse,
    status_code=201,
    summary="Add item to inventory",
)
async def add_to_inventory(
    item: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a scanned/selected food item to the user's inventory."""
    # Verify the food item exists
    result = await db.execute(
        select(FoodItem).where(FoodItem.id == item.food_item_id)
    )
    food = result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=404,
            detail=f"Food item with id {item.food_item_id} not found"
        )

    # Calculate shelf life for selected storage method
    shelf_life = estimate_shelf_life(
        shelf_life_room_temp=food.shelf_life_room_temp_days,
        shelf_life_fridge=food.shelf_life_fridge_days,
        shelf_life_freezer=food.shelf_life_freezer_days,
        freshness_score=item.freshness_score,
    )
    days_remaining = get_days_for_method(shelf_life, item.storage_method.value)

    now = datetime.now(timezone.utc)
    estimated_expiry = now + timedelta(days=days_remaining)

    # Create inventory item
    inventory_item = UserInventory(
        user_id=DEFAULT_USER_ID,
        food_item_id=item.food_item_id,
        freshness_score=item.freshness_score,
        storage_method=item.storage_method.value,
        estimated_days_remaining=days_remaining,
        scanned_at=now,
        estimated_expiry=estimated_expiry,
        is_expired=False,
        is_consumed=False,
        image_path=item.image_path,
        quantity=item.quantity,
        notes=item.notes,
    )

    db.add(inventory_item)
    await db.flush()

    # Create an expiry notification (1 day before expiry)
    if days_remaining > 1:
        notify_at = estimated_expiry - timedelta(days=1)
        notification = Notification(
            inventory_id=inventory_item.id,
            message=f"⚠️ Your {food.name} expires tomorrow! Consider using it today.",
            notify_at=notify_at,
            sent=False,
        )
        db.add(notification)
        await db.flush()

    # Load the food_item relationship for the response
    await db.refresh(inventory_item)
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.food_item))
        .where(UserInventory.id == inventory_item.id)
    )
    inventory_item = result.scalar_one()

    return inventory_item


@router.get(
    "/{item_id}",
    response_model=InventoryItemResponse,
    summary="Get inventory item details",
)
async def get_inventory_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific inventory item."""
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.food_item))
        .where(
            UserInventory.id == item_id,
            UserInventory.user_id == DEFAULT_USER_ID,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    return item


@router.patch(
    "/{item_id}",
    response_model=InventoryItemResponse,
    summary="Update inventory item",
)
async def update_inventory_item(
    item_id: int,
    update: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an inventory item (storage method, mark consumed, etc.)."""
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.food_item))
        .where(
            UserInventory.id == item_id,
            UserInventory.user_id == DEFAULT_USER_ID,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Apply updates
    if update.is_consumed is not None:
        item.is_consumed = update.is_consumed

    if update.quantity is not None:
        item.quantity = update.quantity

    if update.notes is not None:
        item.notes = update.notes

    # If storage method changed, recalculate shelf life
    if update.storage_method is not None:
        item.storage_method = update.storage_method.value

        shelf_life = estimate_shelf_life(
            shelf_life_room_temp=item.food_item.shelf_life_room_temp_days,
            shelf_life_fridge=item.food_item.shelf_life_fridge_days,
            shelf_life_freezer=item.food_item.shelf_life_freezer_days,
            freshness_score=item.freshness_score,
        )
        days_remaining = get_days_for_method(shelf_life, update.storage_method.value)

        item.estimated_days_remaining = days_remaining
        item.estimated_expiry = item.scanned_at + timedelta(days=days_remaining)

    await db.flush()
    await db.refresh(item)

    return item


@router.delete(
    "/{item_id}",
    response_model=MessageResponse,
    summary="Remove from inventory",
)
async def delete_inventory_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a food item from the user's inventory."""
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.food_item))
        .where(
            UserInventory.id == item_id,
            UserInventory.user_id == DEFAULT_USER_ID,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    food_name = item.food_item.name
    await db.delete(item)

    return MessageResponse(message=f"'{food_name}' removed from inventory")
