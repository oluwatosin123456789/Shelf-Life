"""
Shelf Life Estimator — Fruit Classifier (AI Stub)
===================================================
Identifies what fruit is in an image.

Phase 1 (current): Returns mock predictions.
  - DEMO_MODE = True: always returns a fixed fruit (for pitch demos)
  - DEMO_MODE = False: filename matching or random
Phase 2: Will use MobileNetV2 transfer learning model trained on Fruits-360.
"""

import os
import random
from pathlib import Path


# ============================================
# DEMO MODE — set to False when real AI is ready
# ============================================
# When True, the classifier always returns the DEMO_FRUIT
# so the pitch demo is 100% predictable.
# Change DEMO_FRUIT to whatever fruit you want to demo with.

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
DEMO_FRUIT = os.getenv("DEMO_FRUIT", "banana").lower()

MOCK_CLASSIFICATIONS: dict[str, float] = {
    "apple": 0.94,
    "banana": 0.96,
    "orange": 0.91,
    "strawberry": 0.92,
    "mango": 0.89,
    "grape": 0.87,
    "pineapple": 0.88,
    "watermelon": 0.93,
    "avocado": 0.85,
    "peach": 0.86,
    "lemon": 0.90,
    "blueberry": 0.91,
    "kiwi": 0.88,
    "papaya": 0.84,
    "cherry": 0.90,
    "pear": 0.87,
    "pomegranate": 0.85,
    "dragon fruit": 0.83,
    "guava": 0.82,
    "coconut": 0.91,
}

_FRUIT_NAMES = list(MOCK_CLASSIFICATIONS.keys())


async def classify_fruit(image_path: str) -> dict:
    """
    Classify a fruit from an image.

    In DEMO_MODE, always returns DEMO_FRUIT for predictable pitch demos.
    Otherwise falls back to filename matching or random selection.

    TODO (Phase 2):
        - Load MobileNetV2 model trained on Fruits-360 dataset
        - Preprocess image: resize to 224x224, normalize
        - Run inference and return top prediction
    """
    # --- DEMO MODE: always return the demo fruit ---
    if DEMO_MODE:
        confidence = MOCK_CLASSIFICATIONS.get(DEMO_FRUIT, 0.92)
        return {
            "name": DEMO_FRUIT.title(),
            "confidence": confidence,
        }

    # --- Normal mode: try filename matching ---
    filename = Path(image_path).stem.lower()

    for fruit_name, confidence in MOCK_CLASSIFICATIONS.items():
        if fruit_name in filename:
            return {
                "name": fruit_name.title(),
                "confidence": confidence,
            }

    # Random pick if no match
    chosen = random.choice(_FRUIT_NAMES)
    return {
        "name": chosen.title(),
        "confidence": round(random.uniform(0.75, 0.95), 2),
    }
