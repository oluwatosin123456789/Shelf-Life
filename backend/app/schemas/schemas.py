"""
Shelf Life Estimator — Pydantic Schemas
========================================
Request/response validation schemas for all API endpoints.
Pydantic handles serialization, validation, and API documentation.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ============================================
# Enums
# ============================================

class StorageMethod(str, Enum):
    """Valid storage methods for food items."""
    ROOM_TEMP = "room_temp"
    FRIDGE = "fridge"
    FREEZER = "freezer"


class FoodCategory(str, Enum):
    """Subcategories for fruit classification."""
    COMMON = "common"
    CITRUS = "citrus"
    BERRIES = "berries"
    TROPICAL = "tropical"
    STONE = "stone"
    MELONS = "melons"
    OTHER = "other"


# ============================================
# Food Item Schemas
# ============================================

class FoodItemBase(BaseModel):
    """Base schema for food item data."""
    name: str = Field(..., min_length=1, max_length=100, examples=["Banana"])
    category: str = Field(..., min_length=1, max_length=50, examples=["fruits"])
    shelf_life_room_temp_days: float = Field(..., ge=0, examples=[5.0])
    shelf_life_fridge_days: float = Field(..., ge=0, examples=[14.0])
    shelf_life_freezer_days: float = Field(..., ge=0, examples=[180.0])
    storage_tips: str | None = Field(
        None,
        examples=["Store at room temperature until ripe, then refrigerate."]
    )
    image_url: str | None = None


class FoodItemCreate(FoodItemBase):
    """Schema for creating a new food item."""
    pass


class FoodItemResponse(FoodItemBase):
    """Schema for food item in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int


class FoodItemList(BaseModel):
    """Paginated list of food items."""
    items: list[FoodItemResponse]
    total: int
    page: int
    per_page: int


# ============================================
# Scan Schemas
# ============================================

class ScanResultResponse(BaseModel):
    """
    Response from the /api/scan endpoint.
    Contains everything the frontend needs to display results.
    """
    food_item: FoodItemResponse
    classification_confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="How confident the AI is about the food identification (0-1)"
    )
    freshness_score: float = Field(
        ..., ge=0.0, le=1.0,
        description="Visual freshness assessment (0 = spoiled, 1 = perfectly fresh)"
    )
    freshness_label: str = Field(
        ...,
        description="Human-readable freshness label",
        examples=["Fresh", "Slightly Aged", "Aging", "Spoiled"]
    )
    estimated_shelf_life: dict[str, float] = Field(
        ...,
        description="Estimated days remaining per storage method",
        examples=[{"room_temp": 3.5, "fridge": 10.0, "freezer": 120.0}]
    )
    storage_tips: str | None = None
    image_path: str | None = None


# ============================================
# Inventory Schemas
# ============================================

class InventoryItemCreate(BaseModel):
    """Schema for adding an item to the user's inventory."""
    food_item_id: int = Field(..., gt=0)
    freshness_score: float = Field(1.0, ge=0.0, le=1.0)
    storage_method: StorageMethod = StorageMethod.ROOM_TEMP
    quantity: int = Field(1, ge=1)
    notes: str | None = None
    image_path: str | None = None


class InventoryItemUpdate(BaseModel):
    """Schema for updating an inventory item."""
    storage_method: StorageMethod | None = None
    is_consumed: bool | None = None
    quantity: int | None = Field(None, ge=1)
    notes: str | None = None


class InventoryItemResponse(BaseModel):
    """Schema for inventory item in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    food_item_id: int
    freshness_score: float
    storage_method: str
    estimated_days_remaining: float
    scanned_at: datetime
    estimated_expiry: datetime
    is_expired: bool
    is_consumed: bool
    image_path: str | None
    quantity: int
    notes: str | None

    # Nested food item details
    food_item: FoodItemResponse


class InventoryListResponse(BaseModel):
    """List of inventory items with summary stats."""
    items: list[InventoryItemResponse]
    total: int
    expiring_soon: int  # items expiring within 2 days
    expired: int


# ============================================
# Notification Schemas
# ============================================

class NotificationResponse(BaseModel):
    """Schema for notification in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_id: int
    message: str
    notify_at: datetime
    sent: bool


# ============================================
# General Schemas
# ============================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    debug: bool


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True
