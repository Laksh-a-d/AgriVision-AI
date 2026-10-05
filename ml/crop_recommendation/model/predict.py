import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import math
import json
from typing import Dict, List, Any, Union
import numpy as np
import joblib
import tensorflow as tf

from ml.crop_recommendation.model.model_utils import reshape_tabular_to_sequence
from ml.crop_recommendation.config import RANGE_CONSTRAINTS
from ml.common.paths import CROP_REC_DIR

MODEL_DIR = CROP_REC_DIR / "model"

# Global cache for loaded model and artifacts
_MODEL_CACHE: Dict[str, Any] = {
    "model": None,
    "scaler": None,
    "label_encoder": None,
    "class_names": None
}


def load_inference_artifacts(model_dir: Path = MODEL_DIR) -> Dict[str, Any]:
    """
    Loads and caches the serialized LSTM model, StandardScaler, LabelEncoder, and class metadata.
    """
    global _MODEL_CACHE
    if _MODEL_CACHE["model"] is not None:
        return _MODEL_CACHE

    model_path = model_dir / "crop_recommendation_lstm.keras"
    scaler_path = model_dir / "scaler.joblib"
    le_path = model_dir / "label_encoder.joblib"
    classes_path = model_dir / "classes.json"

    if not model_path.exists() or not scaler_path.exists():
        raise FileNotFoundError(
            f"Trained model artifacts not found in {model_dir}. "
            f"Please run train_lstm.py first."
        )

    _MODEL_CACHE["model"] = tf.keras.models.load_model(model_path)
    _MODEL_CACHE["scaler"] = joblib.load(scaler_path)
    
    if le_path.exists():
        _MODEL_CACHE["label_encoder"] = joblib.load(le_path)
    if classes_path.exists():
        with open(classes_path, "r") as f:
            _MODEL_CACHE["class_names"] = json.load(f)

    return _MODEL_CACHE


def validate_crop_inputs(
    n: Union[int, float],
    p: Union[int, float],
    k: Union[int, float],
    temperature: Union[int, float],
    humidity: Union[int, float],
    ph: Union[int, float],
    rainfall: Union[int, float]
) -> Dict[str, float]:
    """
    Validates input parameters for crop recommendation:
    - Rejects non-numeric, None, NaN, or Infinite inputs.
    - Rejects physiologically impossible agronomic values.
    Returns cleaned dictionary of float values.
    """
    raw_inputs = {
        "N": n,
        "P": p,
        "K": k,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall
    }

    validated = {}
    for param_name, val in raw_inputs.items():
        if val is None:
            raise ValueError(f"Input '{param_name}' cannot be None or missing.")

        try:
            float_val = float(val)
        except (ValueError, TypeError):
            raise ValueError(f"Input '{param_name}' must be a valid real number, got: {val}")

        if math.isnan(float_val) or math.isinf(float_val):
            raise ValueError(f"Input '{param_name}' cannot be NaN or Infinite.")

        # Range bounds verification
        bounds = RANGE_CONSTRAINTS.get(param_name, {"min": 0.0, "max": 3500.0})
        min_bound = bounds["min"]
        max_bound = bounds["max"]

        if not (min_bound <= float_val <= max_bound):
            raise ValueError(
                f"Input '{param_name}' value {float_val} is outside acceptable range "
                f"[{min_bound}, {max_bound}]."
            )

        validated[param_name] = float_val

    return validated


def predict_all_crop_probabilities(
    n: Union[int, float],
    p: Union[int, float],
    k: Union[int, float],
    temperature: Union[int, float],
    humidity: Union[int, float],
    ph: Union[int, float],
    rainfall: Union[int, float]
) -> List[Dict[str, Any]]:
    """
    Runs LSTM inference and returns unmanipulated softmax probabilities for all crop classes.
    """
    clean_inputs = validate_crop_inputs(n, p, k, temperature, humidity, ph, rainfall)
    artifacts = load_inference_artifacts()
    model = artifacts["model"]
    scaler = artifacts["scaler"]
    class_names = artifacts["class_names"]

    # Transform features (1, 7) using pre-fitted StandardScaler
    feature_vector = np.array([[
        clean_inputs["N"],
        clean_inputs["P"],
        clean_inputs["K"],
        clean_inputs["temperature"],
        clean_inputs["humidity"],
        clean_inputs["ph"],
        clean_inputs["rainfall"]
    ]])
    scaled_vector = scaler.transform(feature_vector)

    # Reshape to LSTM sequence format (1, timesteps=7, features=1)
    seq_input = reshape_tabular_to_sequence(scaled_vector)

    # Run neural inference
    prob_dist = model.predict(seq_input, verbose=0)[0]
    total_prob = float(np.sum(prob_dist))
    if not (0.98 <= total_prob <= 1.02):
        raise ValueError(f"Inference output is not a valid probability distribution (sum={total_prob}).")

    all_preds = []
    for idx, prob in enumerate(prob_dist):
        crop_name = class_names[idx] if class_names else f"crop_{idx}"
        all_preds.append({
            "crop": crop_name,
            "probability": round(float(prob), 4)
        })

    return all_preds


def predict_crop_recommendation(
    n: Union[int, float],
    p: Union[int, float],
    k: Union[int, float],
    temperature: Union[int, float],
    humidity: Union[int, float],
    ph: Union[int, float],
    rainfall: Union[int, float],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Generates top-k crop recommendations sorted strictly by raw model probability.
    """
    all_preds = predict_all_crop_probabilities(n, p, k, temperature, humidity, ph, rainfall)
    all_preds.sort(key=lambda x: x["probability"], reverse=True)
    return all_preds[:top_k]


if __name__ == "__main__":
    sample_input = {
        "n": 35,
        "p": 70,
        "k": 45,
        "temperature": 26.0,
        "humidity": 68.0,
        "ph": 6.7,
        "rainfall": 850.0
    }
    print(f"Sample Input (Soybean conditions): {sample_input}")
    preds = predict_crop_recommendation(**sample_input, top_k=5)
    print("\nTop 5 Crop Recommendations:")
    for p in preds:
        print(f"  - {p['crop']:15s}: {p['probability'] * 100:.2f}%")
