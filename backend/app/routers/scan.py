"""
Shelf Life Estimator — Scan Router
====================================
Handles image upload, AI classification, freshness assessment,
and shelf life estimation.

This is the main "brain" endpoint of the application.
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.schema import FoodItem
from app.schemas.schemas import ScanResultResponse
from app.ai.classifier import classify_food
from app.ai.freshness import assess_freshness
from app.ai.estimator import estimate_shelf_life

settings = get_settings()

router = APIRouter(prefix="/api/scan", tags=["Scan"])


@router.post(
    "/",
    response_model=ScanResultResponse,
    summary="Scan a food item",
    description="Upload an image of food. The AI will identify it, "
    "assess its freshness, and estimate shelf life for all storage methods.",
)
async def scan_food(
    image: UploadFile = File(..., description="Image of the food item to scan"),
    db: AsyncSession = Depends(get_db),
):
    """
    Full scan pipeline:
    1. Save uploaded image
    2. Classify food (AI Model 1)
    3. Assess freshness (AI Model 2)
    4. Look up base shelf life from database
    5. Calculate estimated shelf life
    6. Return complete results
    """
    # --- Validate file type ---
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {image.content_type}. "
            f"Allowed: {', '.join(allowed_types)}",
        )

    # --- Validate file size ---
    max_size = settings.max_upload_size_mb * 1024 * 1024  # Convert to bytes
    contents = await image.read()
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
        )

    # --- Save uploaded image ---
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_ext = Path(image.filename).suffix if image.filename else ".jpg"
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    # --- Step 1: Classify the food ---
    classification = await classify_food(str(file_path))
    food_name = classification["name"]
    confidence = classification["confidence"]

    # --- Step 2: Assess freshness ---
    freshness = await assess_freshness(str(file_path))
    freshness_score = freshness["score"]
    freshness_label = freshness["label"]

    # --- Step 3: Look up food in database ---
    result = await db.execute(
        select(FoodItem).where(FoodItem.name.ilike(food_name))
    )
    food_item = result.scalar_one_or_none()

    if not food_item:
        # If AI-identified food isn't in our database, try a fuzzy match
        result = await db.execute(
            select(FoodItem).where(FoodItem.name.ilike(f"%{food_name}%"))
        )
        food_item = result.scalar_one_or_none()

    if not food_item:
        # Still not found — clean up uploaded file and return error
        os.remove(file_path)
        raise HTTPException(
            status_code=404,
            detail=f"Food '{food_name}' identified by AI but not found in our database. "
            "Please try manual selection instead.",
        )

    # --- Step 4: Estimate shelf life ---
    shelf_life = estimate_shelf_life(
        shelf_life_room_temp=food_item.shelf_life_room_temp_days,
        shelf_life_fridge=food_item.shelf_life_fridge_days,
        shelf_life_freezer=food_item.shelf_life_freezer_days,
        freshness_score=freshness_score,
    )

    # --- Step 5: Return complete results ---
    return ScanResultResponse(
        food_item=food_item,
        classification_confidence=confidence,
        freshness_score=freshness_score,
        freshness_label=freshness_label,
        estimated_shelf_life=shelf_life,
        storage_tips=food_item.storage_tips,
        image_path=str(file_path),
    )
