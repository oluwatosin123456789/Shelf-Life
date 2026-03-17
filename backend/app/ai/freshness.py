"""
Shelf Life Estimator — Freshness Assessor (AI Stub)
=====================================================
Judges the visual freshness/condition of food in an image.

Phase 1: Returns mock freshness scores.
Phase 2: Will use a custom CNN trained on fresh vs stale dataset.
"""

import random


# Freshness labels mapped to score ranges
FRESHNESS_LABELS = [
    (0.80, 1.00, "Fresh"),
    (0.60, 0.79, "Slightly Aged"),
    (0.40, 0.59, "Aging"),
    (0.20, 0.39, "Old"),
    (0.00, 0.19, "Spoiled"),
]


def get_freshness_label(score: float) -> str:
    """Convert a freshness score (0-1) to a human-readable label."""
    for low, high, label in FRESHNESS_LABELS:
        if low <= score <= high:
            return label
    return "Unknown"


async def assess_freshness(image_path: str) -> dict:
    """
    Assess the visual freshness of a food item from an image.

    Args:
        image_path: Path to the uploaded image file.

    Returns:
        dict with keys:
            - score (float): Freshness score 0.0 (spoiled) to 1.0 (perfectly fresh)
            - label (str): Human-readable freshness label

    TODO (Phase 2):
        - Load custom CNN / EfficientNet-B0 model
        - Preprocess image: resize to 224x224, normalize
        - Run inference and map output to 0-1 freshness score
    """
    # Phase 1: Return a mock freshness score
    # Skew toward fresh (most uploaded food should be relatively fresh)
    score = round(random.uniform(0.55, 0.98), 2)
    label = get_freshness_label(score)

    return {
        "score": score,
        "label": label,
    }
