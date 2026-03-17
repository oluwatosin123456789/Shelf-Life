"""
Shelf Life Estimator — Food Classifier (AI Stub)
==================================================
Identifies what food item is in an image.

Phase 1: Returns mock predictions from a lookup table.
Phase 2: Will use MobileNetV2 transfer learning model.
"""

import random
from pathlib import Path

# Mock food classifications for Phase 1 development
# Maps keywords to food names for basic image filename matching
MOCK_CLASSIFICATIONS = [
    {"name": "Banana", "confidence": 0.94},
    {"name": "Tomato", "confidence": 0.91},
    {"name": "Apple", "confidence": 0.89},
    {"name": "Carrot", "confidence": 0.87},
    {"name": "Lettuce", "confidence": 0.85},
    {"name": "Strawberry", "confidence": 0.92},
    {"name": "Chicken Breast", "confidence": 0.88},
    {"name": "Rice", "confidence": 0.90},
    {"name": "Bread", "confidence": 0.86},
    {"name": "Milk", "confidence": 0.93},
]


async def classify_food(image_path: str) -> dict:
    """
    Classify a food item from an image.

    Args:
        image_path: Path to the uploaded image file.

    Returns:
        dict with keys:
            - name (str): Predicted food name
            - confidence (float): Confidence score 0.0 - 1.0

    TODO (Phase 2):
        - Load MobileNetV2 model from .h5 file
        - Preprocess image: resize to 224x224, normalize
        - Run inference and return top prediction
    """
    # Phase 1: Return a mock classification
    # Try to match filename to a known food, else pick random
    filename = Path(image_path).stem.lower()

    for food in MOCK_CLASSIFICATIONS:
        if food["name"].lower() in filename:
            return {
                "name": food["name"],
                "confidence": food["confidence"],
            }

    # Random pick if no filename match
    food = random.choice(MOCK_CLASSIFICATIONS)
    return {
        "name": food["name"],
        "confidence": round(random.uniform(0.75, 0.95), 2),
    }
