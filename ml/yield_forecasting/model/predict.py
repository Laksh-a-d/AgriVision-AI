import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import math
import json
from typing import Dict, Any, Union, Optional
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf

from ml.yield_forecasting.config import (
    COL_STATE,
    COL_DISTRICT,
    COL_CROP,
    COL_SEASON,
    COL_AREA,
    COL_YEAR,
    BENCHMARK_CROPS
)
from ml.common.paths import YIELD_DIR

MODEL_DIR = YIELD_DIR / "model"

# Global inference cache
_YIELD_CACHE: Dict[str, Any] = {
    "dnn_model": None,
    "tree_model": None,
    "preprocessor": None,
    "metadata": None
}


def load_yield_inference_artifacts(model_dir: Path = MODEL_DIR) -> Dict[str, Any]:
    """
    Loads and caches the trained yield models (DNN and Gradient Boosting), preprocessor, and metadata.
    """
    global _YIELD_CACHE
    if _YIELD_CACHE["preprocessor"] is not None:
        return _YIELD_CACHE

    dnn_path = model_dir / "crop_yield_dnn.keras"
    tree_path = model_dir / "gradient_boosting_yield.joblib"
    prep_path = model_dir / "preprocessor.joblib"
    meta_path = model_dir / "metadata.json"

    if not prep_path.exists():
        raise FileNotFoundError(
            f"Fitted preprocessor not found in {model_dir}. Run training first."
        )

    _YIELD_CACHE["preprocessor"] = joblib.load(prep_path)

    if dnn_path.exists():
        _YIELD_CACHE["dnn_model"] = tf.keras.models.load_model(dnn_path)
    if tree_path.exists():
        _YIELD_CACHE["tree_model"] = joblib.load(tree_path)
    if meta_path.exists():
        with open(meta_path, "r") as f:
            _YIELD_CACHE["metadata"] = json.load(f)

    return _YIELD_CACHE


def clear_yield_cache():
    """Invalidates the in-memory inference cache to reload artifacts from disk."""
    global _YIELD_CACHE
    _YIELD_CACHE = {
        "dnn_model": None,
        "tree_model": None,
        "preprocessor": None,
        "metadata": None
    }


def normalize_crop_name(crop: str) -> str:
    """Normalizes various crop name formats to match trained model categories."""
    c = crop.strip()
    cl = c.lower()
    if "cotton" in cl:
        return "Cotton"
    if "soya" in cl or "soybean" in cl:
        return "Soyabean"
    if "paddy" in cl or "rice" in cl:
        return "Rice"
    for b in BENCHMARK_CROPS:
        if b.lower() == cl:
            return b
    return c.title()


def validate_yield_input(
    state: str,
    district: str,
    crop: str,
    season: str,
    area: Union[int, float],
    crop_year: int = 2024
) -> Dict[str, Any]:
    """
    Validates agricultural inputs for yield prediction:
    - Normalizes strings to Title Case to match OneHotEncoder categories.
    - Normalizes crop name (e.g. Cotton(lint) -> Cotton).
    - Verifies area is strictly positive.
    - Rejects NaN, Infinity, negative area.
    - Validates crop_year is a reasonable positive integer.
    """
    if not state or not isinstance(state, str) or not state.strip():
        raise ValueError("State name must be a non-empty string.")
    if not district or not isinstance(district, str) or not district.strip():
        raise ValueError("District name must be a non-empty string.")
    if not crop or not isinstance(crop, str) or not crop.strip():
        raise ValueError("Crop name must be a non-empty string.")
    if not season or not isinstance(season, str) or not season.strip():
        raise ValueError("Season must be a non-empty string.")

    try:
        area_float = float(area)
    except (ValueError, TypeError):
        raise ValueError(f"Area must be a valid numeric value, got: {area}")

    if math.isnan(area_float) or math.isinf(area_float):
        raise ValueError("Area cannot be NaN or Infinite.")
    if area_float <= 0:
        raise ValueError(f"Cultivated Area must be strictly positive in hectares (got: {area_float}).")

    try:
        year_int = int(crop_year)
    except (ValueError, TypeError):
        raise ValueError(f"Crop Year must be a valid integer, got: {crop_year}")

    if year_int < 1980 or year_int > 2050:
        raise ValueError(f"Crop Year out of valid range (1980-2050): {year_int}")

    return {
        COL_STATE: state.strip().title(),
        COL_DISTRICT: district.strip().title(),
        COL_CROP: normalize_crop_name(crop),
        COL_SEASON: season.strip().title(),
        COL_AREA: area_float,
        COL_YEAR: year_int
    }


# Agronomic yield bounds per crop (min, max in Tonnes/Hectare)
# Calibrated against official Indian government agricultural data (DES, PIB, ICAR)
CROP_AGRONOMIC_BOUNDS: Dict[str, Tuple[float, float]] = {
    "Rice":          (0.3,   8.0),
    "Wheat":         (0.3,   7.5),
    "Maize":         (0.3,   8.0),
    "Sugarcane":     (15.0, 130.0),
    "Cotton":        (0.05,  1.5),  # 50 to 1500 kg lint/ha (Maharashtra realistic avg: 0.25 - 0.40 t/ha)
    "Potato":        (2.0,  50.0),
    "Onion":         (2.0,  40.0),
    "Soyabean":      (0.2,   3.5),
    "Groundnut":     (0.2,   4.5),
    "Gram":          (0.1,   3.0),
    "Bajra":         (0.1,   3.5),
    "Jowar":         (0.1,   3.5),
}

TRAINING_MAX_YEAR = 2015


def predict_crop_yield(
    state: str,
    district: str,
    crop: str,
    season: str,
    area: Union[int, float],
    crop_year: int = 2024,
    model_type: str = "dnn"
) -> Dict[str, Any]:
    """
    Forecasts crop yield (Tonnes / Hectare) and total estimated harvest production (Tonnes).

    Parameters:
        state: State name (e.g. 'Punjab', 'Maharashtra', 'Uttar Pradesh').
        district: District name (e.g. 'Ludhiana', 'Nashik', 'Agra').
        crop: Agricultural crop name (e.g. 'Wheat', 'Rice', 'Sugarcane', 'Maize').
        season: Cultivation season ('Kharif', 'Rabi', 'Whole Year', 'Summer').
        area: Cultivated area in hectares.
        crop_year: Crop cultivation year.
        model_type: 'dnn' (Deep Neural Network) or 'tree' (Gradient Boosting).

    Returns:
        Structured prediction dictionary with predicted yield, total production, and units.
    """
    # 1. Validate inputs
    clean_input = validate_yield_input(state, district, crop, season, area, crop_year)

    # 2. Clamp crop_year to training distribution to prevent extrapolation drift.
    #    The model was trained on 1997–2015; a 2024 year z-score of ~4.8σ causes
    #    wildly wrong predictions. We silently clamp and note it in the response.
    raw_year = clean_input[COL_YEAR]
    clamped_year = min(raw_year, TRAINING_MAX_YEAR)
    clean_input[COL_YEAR] = clamped_year

    # 3. Load artifacts
    artifacts = load_yield_inference_artifacts()
    preprocessor = artifacts["preprocessor"]

    # 4. Transform inputs
    input_df = pd.DataFrame([clean_input])
    X_input = preprocessor.transform(input_df)

    # 5. Predict yield
    if model_type == "tree" and artifacts["tree_model"] is not None:
        raw_pred = float(artifacts["tree_model"].predict(X_input)[0])
        model_name = "Gradient Boosting Regressor"
    elif artifacts["dnn_model"] is not None:
        raw_pred = float(artifacts["dnn_model"].predict(X_input, verbose=0)[0, 0])
        model_name = "Deep Neural Network"
    elif artifacts["tree_model"] is not None:
        raw_pred = float(artifacts["tree_model"].predict(X_input)[0])
        model_name = "Gradient Boosting Regressor"
    else:
        raise RuntimeError("No trained yield model found.")

    # 6. Apply agronomic sanity bounds — clamp to realistic range for this crop.
    #    This catches any remaining model misbehaviour for unseen (state, district, crop)
    #    combinations and ensures the output is always physically plausible.
    crop_key = clean_input[COL_CROP]
    if crop_key in CROP_AGRONOMIC_BOUNDS:
        lo, hi = CROP_AGRONOMIC_BOUNDS[crop_key]
        predicted_yield = round(max(lo, min(hi, raw_pred)), 3)
    else:
        predicted_yield = round(max(0.0, raw_pred), 3)

    estimated_production = round(predicted_yield * clean_input[COL_AREA], 2)

    return {
        "state": clean_input[COL_STATE],
        "district": clean_input[COL_DISTRICT],
        "crop": clean_input[COL_CROP],
        "season": clean_input[COL_SEASON],
        "area_hectares": clean_input[COL_AREA],
        "crop_year": raw_year,                        # show what the user entered
        "predicted_yield_tonnes_per_hectare": predicted_yield,
        "estimated_total_production_tonnes": estimated_production,
        "unit": "Tonnes / Hectare",
        "model_used": model_name,
        "year_clamped": raw_year != clamped_year,     # transparency flag
    }



if __name__ == "__main__":
    test_cases = [
        {"state": "Punjab", "district": "Ludhiana", "crop": "Wheat", "season": "Rabi", "area": 50.0, "crop_year": 2024},
        {"state": "Maharashtra", "district": "Nashik", "crop": "Sugarcane", "season": "Kharif", "area": 25.0, "crop_year": 2024},
        {"state": "Uttar Pradesh", "district": "Agra", "crop": "Potato", "season": "Rabi", "area": 10.0, "crop_year": 2024}
    ]
    
    print("--- CROP YIELD FORECASTING INFERENCE SMOKE TEST ---")
    for tc in test_cases:
        res = predict_crop_yield(**tc)
        print(f"\nCrop: {res['crop']:10s} | State: {res['state']:15s} | District: {res['district']:10s}")
        print(f"  Area: {res['area_hectares']} ha -> Predicted Yield: {res['predicted_yield_tonnes_per_hectare']} Tonnes/ha")
        print(f"  Estimated Harvest Production: {res['estimated_total_production_tonnes']} Tonnes (Model: {res['model_used']})")
