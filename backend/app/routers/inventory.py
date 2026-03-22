"""
Shelf Life Estimator — Inventory Router
=========================================
Manage the user's personal fruit inventory.
Track scanned items, update storage methods, mark consumed.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.schema import Fruit, UserInventory, Notification
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
    description="Get all fruits in the user's inventory with freshness status.",
)
async def get_inventory(
    include_consumed: bool = Query(False, description="Include consumed items"),
    include_expired: bool = Query(True, description="Include expired items"),
    sort_by: str = Query("expiry", description="Sort by: expiry, name, freshness, added"),
    db: AsyncSession = Depends(get_db),
):
    """Get the user's full fruit inventory with summary stats."""
    query = (
        select(UserInventory)
        .options(selectinload(UserInventory.fruit))
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
        query = query.order_by(UserInventory.fruit_id)
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
    summary="Add fruit to inventory",
)
async def add_to_inventory(
    item: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a scanned/selected fruit to the user's inventory."""
    # Verify the fruit exists
    result = await db.execute(
        select(Fruit).where(Fruit.id == item.fruit_id)
    )
    fruit = result.scalar_one_or_none()

    if not fruit:
        raise HTTPException(
            status_code=404,
            detail=f"Fruit with id {item.fruit_id} not found"
        )

    # Calculate shelf life using the upgraded multi-factor formula
    shelf_life = estimate_shelf_life(
        shelf_life_room_temp=fruit.shelf_life_room_temp_days,
        shelf_life_fridge=fruit.shelf_life_fridge_days,
        shelf_life_freezer=fruit.shelf_life_freezer_days,
        freshness_score=item.freshness_score,
        optimal_temp_min=fruit.optimal_temp_min,
        optimal_temp_max=fruit.optimal_temp_max,
    )
    days_remaining = get_days_for_method(shelf_life, item.storage_method.value)

    now = datetime.now(timezone.utc)
    estimated_expiry = now + timedelta(days=days_remaining)

    # Create inventory item
    inventory_item = UserInventory(
        user_id=DEFAULT_USER_ID,
        fruit_id=item.fruit_id,
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
            message=f"⚠️ Your {fruit.name} expires tomorrow! Consider using it today.",
            notify_at=notify_at,
            sent=False,
        )
        db.add(notification)
        await db.flush()

    # Load the fruit relationship for the response
    await db.refresh(inventory_item)
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.fruit))
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
        .options(selectinload(UserInventory.fruit))
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
        .options(selectinload(UserInventory.fruit))
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
            shelf_life_room_temp=item.fruit.shelf_life_room_temp_days,
            shelf_life_fridge=item.fruit.shelf_life_fridge_days,
            shelf_life_freezer=item.fruit.shelf_life_freezer_days,
            freshness_score=item.freshness_score,
            optimal_temp_min=item.fruit.optimal_temp_min,
            optimal_temp_max=item.fruit.optimal_temp_max,
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
    """Remove a fruit from the user's inventory."""
    result = await db.execute(
        select(UserInventory)
        .options(selectinload(UserInventory.fruit))
        .where(
            UserInventory.id == item_id,
            UserInventory.user_id == DEFAULT_USER_ID,
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    fruit_name = item.fruit.name
    await db.delete(item)

    return MessageResponse(message=f"'{fruit_name}' removed from inventory")
