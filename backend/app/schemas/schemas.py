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
    """Valid storage methods for fruits."""
    ROOM_TEMP = "room_temp"
    FRIDGE = "fridge"
    FREEZER = "freezer"


class FruitSubcategory(str, Enum):
    """Subcategories for fruit classification."""
    COMMON = "common"
    CITRUS = "citrus"
    BERRIES = "berries"
    TROPICAL = "tropical"
    STONE = "stone"
    MELONS = "melons"
    OTHER = "other"


# ============================================
# Fruit Schemas
# ============================================

class FruitBase(BaseModel):
    """Base schema for fruit data."""
    name: str = Field(..., min_length=1, max_length=100, examples=["Banana"])
    subcategory: str = Field(..., min_length=1, max_length=50, examples=["common"])
    shelf_life_room_temp_days: float = Field(..., ge=0, examples=[5.0])
    shelf_life_fridge_days: float = Field(..., ge=0, examples=[14.0])
    shelf_life_freezer_days: float = Field(..., ge=0, examples=[180.0])
    is_ethylene_producer: bool = Field(False, examples=[True])
    is_ethylene_sensitive: bool = Field(False, examples=[True])
    optimal_temp_min: float | None = Field(None, examples=[13.0])
    optimal_temp_max: float | None = Field(None, examples=[15.0])
    ripeness_indicator: str | None = Field(
        None,
        examples=["Yellow skin with small brown spots = perfectly ripe"]
    )
    storage_tips: str | None = Field(
        None,
        examples=["Store at room temperature until ripe, then refrigerate."]
    )
    image_url: str | None = None


class FruitCreate(FruitBase):
    """Schema for adding a new fruit to the reference database."""
    pass


class FruitResponse(FruitBase):
    """Schema for fruit in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int


class FruitList(BaseModel):
    """Paginated list of fruits."""
    items: list[FruitResponse]
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
    fruit: FruitResponse
    classification_confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="How confident the AI is about the fruit identification (0-1)"
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
    recommended_storage: str | None = Field(
        None,
        description="Best storage recommendation from the estimator",
        examples=["Move to fridge — you'll gain 6.5 extra days"]
    )
    storage_tips: str | None = None
    image_path: str | None = None


# ============================================
# Inventory Schemas
# ============================================

class InventoryItemCreate(BaseModel):
    """Schema for adding a fruit to the user's inventory."""
    fruit_id: int = Field(..., gt=0)
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
    fruit_id: int
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

    # Nested fruit details
    fruit: FruitResponse


class InventoryListResponse(BaseModel):
    """List of inventory items with summary stats."""
    items: list[InventoryItemResponse]
    total: int
    expiring_soon: int  # items expiring within 2 days
    expired: int


# ============================================
# Compatibility Schemas (Phase D)
# ============================================

class CompatibilityPair(BaseModel):
    """An incompatible fruit pair with explanation."""
    producer: str
    sensitive: str
    warning: str


class CompatibilityResponse(BaseModel):
    """Response from the compatibility check endpoint."""
    compatible_groups: list[list[str]]
    incompatible_pairs: list[CompatibilityPair]
    recommendation: str


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
