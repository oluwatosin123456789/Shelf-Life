"""
Shelf Life Estimator — Estimation Engine
==========================================
Calculates estimated shelf life based on:
  - Food type (base shelf life for each storage method)
  - Freshness score (from AI visual assessment)
  - Storage method (room temp, fridge, freezer)

Formula:
    estimated_days = base_shelf_life[storage_method] × freshness_score
"""


def estimate_shelf_life(
    shelf_life_room_temp: float,
    shelf_life_fridge: float,
    shelf_life_freezer: float,
    freshness_score: float,
) -> dict[str, float]:
    """
    Calculate estimated remaining shelf life for all storage methods.

    Args:
        shelf_life_room_temp: Base shelf life at room temperature (days).
        shelf_life_fridge: Base shelf life refrigerated (days).
        shelf_life_freezer: Base shelf life frozen (days).
        freshness_score: Visual freshness score from AI (0.0 - 1.0).

    Returns:
        dict mapping storage method to estimated days remaining.
        Example: {"room_temp": 3.5, "fridge": 10.0, "freezer": 120.0}
    """
    return {
        "room_temp": round(shelf_life_room_temp * freshness_score, 1),
        "fridge": round(shelf_life_fridge * freshness_score, 1),
        "freezer": round(shelf_life_freezer * freshness_score, 1),
    }


def get_days_for_method(
    shelf_life_estimates: dict[str, float],
    storage_method: str,
) -> float:
    """
    Get the estimated days remaining for a specific storage method.

    Args:
        shelf_life_estimates: Output from estimate_shelf_life().
        storage_method: One of "room_temp", "fridge", "freezer".

    Returns:
        Estimated days remaining as a float.

    Raises:
        ValueError: If storage_method is not recognized.
    """
    if storage_method not in shelf_life_estimates:
        raise ValueError(
            f"Invalid storage method: '{storage_method}'. "
            f"Must be one of: {list(shelf_life_estimates.keys())}"
        )
    return shelf_life_estimates[storage_method]
