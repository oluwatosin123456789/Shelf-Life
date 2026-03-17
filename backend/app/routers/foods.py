"""
Shelf Life Estimator — Foods Router
=====================================
CRUD endpoints for the food items reference database.
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_db
from app.models.schema import FoodItem
from app.schemas.schemas import (
    FoodItemCreate,
    FoodItemList,
    FoodItemResponse,
    MessageResponse,
)

router = APIRouter(prefix="/api/foods", tags=["Foods"])


@router.get(
    "/",
    response_model=FoodItemList,
    summary="List all food items",
    description="Get a paginated list of all food items in the database. "
    "Supports filtering by category and searching by name.",
)
async def get_foods(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    category: str | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search by name"),
    db: AsyncSession = Depends(get_db),
):
    """Get all food items with optional filtering and pagination."""
    query = select(FoodItem)

    # Apply filters
    if category:
        query = query.where(FoodItem.category == category.lower())
    if search:
        query = query.where(FoodItem.name.ilike(f"%{search}%"))

    # Count total matching items
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    query = query.order_by(FoodItem.name)

    result = await db.execute(query)
    items = result.scalars().all()

    return FoodItemList(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/categories",
    response_model=list[str],
    summary="List all food categories",
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get a list of all unique food categories."""
    result = await db.execute(
        select(FoodItem.category).distinct().order_by(FoodItem.category)
    )
    return result.scalars().all()


@router.get(
    "/{food_id}",
    response_model=FoodItemResponse,
    summary="Get food item details",
)
async def get_food(food_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific food item including storage tips."""
    result = await db.execute(select(FoodItem).where(FoodItem.id == food_id))
    food = result.scalar_one_or_none()

    if not food:
        raise HTTPException(status_code=404, detail=f"Food item with id {food_id} not found")

    return food


@router.post(
    "/",
    response_model=FoodItemResponse,
    status_code=201,
    summary="Add a new food item",
)
async def create_food(food: FoodItemCreate, db: AsyncSession = Depends(get_db)):
    """Add a new food item to the reference database."""
    # Check for duplicate name
    existing = await db.execute(
        select(FoodItem).where(FoodItem.name.ilike(food.name))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Food item '{food.name}' already exists"
        )

    db_food = FoodItem(**food.model_dump())
    db.add(db_food)
    await db.flush()
    await db.refresh(db_food)

    return db_food


@router.delete(
    "/{food_id}",
    response_model=MessageResponse,
    summary="Delete a food item",
)
async def delete_food(food_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a food item from the reference database."""
    result = await db.execute(select(FoodItem).where(FoodItem.id == food_id))
    food = result.scalar_one_or_none()

    if not food:
        raise HTTPException(status_code=404, detail=f"Food item with id {food_id} not found")

    await db.delete(food)
    return MessageResponse(message=f"Food item '{food.name}' deleted successfully")
