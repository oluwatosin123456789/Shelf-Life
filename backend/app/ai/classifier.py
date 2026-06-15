"""
Fruit Classifier — Real inference using fresco_model.keras (MobileNetV2).

Trained on 4 fruit types across freshness stages:
  Apple, Banana, Carrot, Tomato (+ Expired class)

Each class name encodes the fruit type and a video-frame range.
Lower range numbers = earlier frames = fresher fruit.
"""

import os
import re

import numpy as np
from PIL import Image

os.environ.setdefault("KERAS_BACKEND", "numpy")
import keras  # noqa: E402  — backend env var must be set before import

from app.ai.freshness import get_freshness_label

# Class labels in the alphabetical order Keras flow_from_directory assigns them.
# 14 classes = 3 Apple + 4 Banana + 3 Carrot + 1 Expired + 3 Tomato
CLASS_NAMES = [
    "Apple(1-5)",    # 0
    "Apple(10-14)",  # 1
    "Apple(5-10)",   # 2
    "Banana(1-5)",   # 3
    "Banana(10-15)", # 4
    "Banana(15-20)", # 5
    "Banana(5-10)",  # 6
    "Carrot(1-2)",   # 7
    "Carrot(3-4)",   # 8
    "Expired",       # 9
    "Tomato(1-5)",   # 10
    "Tomato(10-15)", # 11
    "Tomato(5-10)",  # 12
    "carrot(5-6)",   # 13
]

# Freshness score per class.
# Lower range-start number = earlier in sequence = fresher fruit.
_FRESHNESS: dict[str, float] = {
    "Apple(1-5)":    0.90,
    "Apple(5-10)":   0.65,
    "Apple(10-14)":  0.35,
    "Banana(1-5)":   0.92,
    "Banana(5-10)":  0.68,
    "Banana(10-15)": 0.42,
    "Banana(15-20)": 0.18,
    "Carrot(1-2)":   0.90,
    "Carrot(3-4)":   0.60,
    "carrot(5-6)":   0.30,
    "Tomato(1-5)":   0.90,
    "Tomato(5-10)":  0.60,
    "Tomato(10-15)": 0.30,
    "Expired":       0.05,
}

_model = None


def _get_model():
    global _model
    if _model is None:
        from app.config import get_settings
        path = str(get_settings().classifier_model_file)
        _model = keras.models.load_model(path)
    return _model


def _preprocess(image_path: str) -> np.ndarray:
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)  # (1, 224, 224, 3)


def _parse_fruit_name(class_name: str) -> str:
    """Strip the '(X-Y)' suffix and title-case the result."""
    return re.sub(r"\(\d+-\d+\)", "", class_name).strip().title()


async def classify_fruit(image_path: str) -> dict:
    """
    Classify a fruit image using the trained fresco_model.keras.

    Returns:
        name            - Fruit name (title-cased, e.g. "Apple")
        confidence      - Softmax confidence for the top class (0-1)
        freshness_score - Estimated freshness score (0-1) derived from class stage
        freshness_label - Human-readable label ("Fresh", "Aging", etc.)
        expired         - True if the model predicts the Expired class
    """
    model = _get_model()
    arr = _preprocess(image_path)
    preds = model.predict(arr, verbose=0)
    idx = int(np.argmax(preds[0]))
    confidence = float(preds[0][idx])
    class_name = CLASS_NAMES[idx]
    freshness_score = _FRESHNESS.get(class_name, 0.70)

    return {
        "name": _parse_fruit_name(class_name),
        "confidence": round(confidence, 4),
        "freshness_score": freshness_score,
        "freshness_label": get_freshness_label(freshness_score),
        "expired": class_name == "Expired",
    }
