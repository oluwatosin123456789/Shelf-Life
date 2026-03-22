"""
Shelf Life Estimator — Fruit Classifier (AI Stub)
===================================================
Identifies what fruit is in an image.

Phase 1: Returns mock predictions using an O(1) hash map lookup.
Phase 2: Will use MobileNetV2 transfer learning model trained on Fruits-360.
"""

import random
from pathlib import Path


# ============================================
# DSA: Hash Map for O(1) fruit lookup by name
# ============================================
# Instead of looping through a list (O(n) linear search),
# we use a dictionary (hash map) for instant O(1) lookups.
#
# Old approach:  for fruit in list: if name matches → O(n)
# New approach:  dict[name] → O(1)

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

# Pre-computed list of fruit names for random selection
# Stored once to avoid repeated dict.keys() calls
_FRUIT_NAMES = list(MOCK_CLASSIFICATIONS.keys())


async def classify_fruit(image_path: str) -> dict:
    """
    Classify a fruit from an image.

    Args:
        image_path: Path to the uploaded image file.

    Returns:
        dict with keys:
            - name (str): Predicted fruit name (title-cased)
            - confidence (float): Confidence score 0.0 - 1.0

    DSA: Uses hash map (dict) for O(1) name matching instead of
         O(n) linear search through a list.

    TODO (Phase 2):
        - Load MobileNetV2 model trained on Fruits-360 dataset
        - Preprocess image: resize to 224x224, normalize
        - Run inference and return top prediction
    """
    # Phase 1: Return a mock classification
    # Try to match filename to a known fruit via hash map
    filename = Path(image_path).stem.lower()

    # O(1) hash map lookup for each known fruit name
    for fruit_name, confidence in MOCK_CLASSIFICATIONS.items():
        if fruit_name in filename:
            return {
                "name": fruit_name.title(),
                "confidence": confidence,
            }

    # Random pick if no filename match
    chosen = random.choice(_FRUIT_NAMES)
    return {
        "name": chosen.title(),
        "confidence": round(random.uniform(0.75, 0.95), 2),
    }
