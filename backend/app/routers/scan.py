"""
Shelf Life Estimator — Scan Router
====================================
Handles image upload, AI classification, freshness assessment,
and shelf life estimation for fruits.

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
from app.models.schema import Fruit
from app.schemas.schemas import ScanResultResponse
from app.ai.classifier import classify_fruit
from app.ai.freshness import assess_freshness
from app.ai.estimator import estimate_shelf_life, recommend_best_storage

settings = get_settings()

router = APIRouter(prefix="/api/scan", tags=["Scan"])


@router.post(
    "/",
    response_model=ScanResultResponse,
    summary="Scan a fruit",
    description="Upload an image of a fruit. The AI will identify it, "
    "assess its freshness, and estimate shelf life for all storage methods.",
)
async def scan_fruit(
    image: UploadFile = File(..., description="Image of the fruit to scan"),
    db: AsyncSession = Depends(get_db),
):
    """
    Full scan pipeline:
    1. Save uploaded image
    2. Classify fruit (AI Model 1)
    3. Assess freshness (AI Model 2)
    4. Look up base shelf life from database
    5. Calculate estimated shelf life (weighted multi-factor)
    6. Generate storage recommendation
    7. Return complete results
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

    # --- Step 1: Classify the fruit ---
    classification = await classify_fruit(str(file_path))
    fruit_name = classification["name"]
    confidence = classification["confidence"]

    # --- Step 2: Assess freshness ---
    freshness = await assess_freshness(str(file_path))
    freshness_score = freshness["score"]
    freshness_label = freshness["label"]

    # --- Step 3: Look up fruit in database ---
    result = await db.execute(
        select(Fruit).where(Fruit.name.ilike(fruit_name))
    )
    fruit = result.scalar_one_or_none()

    if not fruit:
        # If AI-identified fruit isn't in our database, try a fuzzy match
        result = await db.execute(
            select(Fruit).where(Fruit.name.ilike(f"%{fruit_name}%"))
        )
        fruit = result.scalar_one_or_none()

    if not fruit:
        # Still not found — clean up uploaded file and return error
        os.remove(file_path)
        raise HTTPException(
            status_code=404,
            detail=f"Fruit '{fruit_name}' identified by AI but not found in our database. "
            "Please try manual selection instead.",
        )

    # --- Step 4: Estimate shelf life (upgraded multi-factor formula) ---
    shelf_life = estimate_shelf_life(
        shelf_life_room_temp=fruit.shelf_life_room_temp_days,
        shelf_life_fridge=fruit.shelf_life_fridge_days,
        shelf_life_freezer=fruit.shelf_life_freezer_days,
        freshness_score=freshness_score,
        optimal_temp_min=fruit.optimal_temp_min,
        optimal_temp_max=fruit.optimal_temp_max,
    )

    # --- Step 5: Generate storage recommendation ---
    recommendation = recommend_best_storage(shelf_life, current_method="room_temp")

    # --- Step 6: Return complete results ---
    return ScanResultResponse(
        fruit=fruit,
        classification_confidence=confidence,
        freshness_score=freshness_score,
        freshness_label=freshness_label,
        estimated_shelf_life=shelf_life,
        recommended_storage=recommendation,
        storage_tips=fruit.storage_tips,
        image_path=str(file_path),
    )


you can do all things 