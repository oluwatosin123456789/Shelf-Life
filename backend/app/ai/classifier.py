"""
Shelf Life Estimator — Fruit Classifier (AI Stub)
===================================================
Identifies what fruit is in an image.

Phase 1: Returns mock predictions from a lookup table.
Phase 2: Will use MobileNetV2 transfer learning model trained on Fruits-360.
"""

import random
from pathlib import Path

# Mock fruit classifications for Phase 1 development
MOCK_CLASSIFICATIONS = [
    {"name": "Apple", "confidence": 0.94},
    {"name": "Banana", "confidence": 0.96},
    {"name": "Orange", "confidence": 0.91},
    {"name": "Strawberry", "confidence": 0.92},
    {"name": "Mango", "confidence": 0.89},
    {"name": "Grape", "confidence": 0.87},
    {"name": "Pineapple", "confidence": 0.88},
    {"name": "Watermelon", "confidence": 0.93},
    {"name": "Avocado", "confidence": 0.85},
    {"name": "Peach", "confidence": 0.86},
    {"name": "Lemon", "confidence": 0.90},
    {"name": "Blueberry", "confidence": 0.91},
    {"name": "Kiwi", "confidence": 0.88},
    {"name": "Papaya", "confidence": 0.84},
    {"name": "Cherry", "confidence": 0.90},
    {"name": "Pear", "confidence": 0.87},
    {"name": "Pomegranate", "confidence": 0.85},
    {"name": "Dragon Fruit", "confidence": 0.83},
    {"name": "Guava", "confidence": 0.82},
    {"name": "Coconut", "confidence": 0.91},
]


async def classify_food(image_path: str) -> dict:
    """
    Classify a fruit from an image.

    Args:
        image_path: Path to the uploaded image file.

    Returns:
        dict with keys:
            - name (str): Predicted fruit name
            - confidence (float): Confidence score 0.0 - 1.0

    TODO (Phase 2):
        - Load MobileNetV2 model trained on Fruits-360 dataset
        - Preprocess image: resize to 224x224, normalize
        - Run inference and return top prediction
    """
    # Phase 1: Return a mock classification
    # Try to match filename to a known fruit, else pick random
    filename = Path(image_path).stem.lower()

    for fruit in MOCK_CLASSIFICATIONS:
        if fruit["name"].lower() in filename:
            return {
                "name": fruit["name"],
                "confidence": fruit["confidence"],
            }

    # Random pick if no filename match
    fruit = random.choice(MOCK_CLASSIFICATIONS)
    return {
        "name": fruit["name"],
        "confidence": round(random.uniform(0.75, 0.95), 2),
    }
