"""
ICAR & TNAU Agronomic Suitability Engine for Crop Recommendation.

Provides scientifically defensible, biophysically grounded crop suitability scoring
based on official packages of practices from:
1. ICAR (Indian Council of Agricultural Research) Handbook of Agriculture
2. TNAU Agritech Portal (Crop Production Guidelines)
3. ICAR-CRIDA (Central Research Institute for Dryland Agriculture)
4. IMD (India Meteorological Department) Agro-climatic Rainfall Norms
"""

import math
from typing import Dict, Any, List, Tuple, Optional

# Verified ICAR / TNAU Crop Biophysical Envelopes
# Format: (min_tolerable, opt_low, opt_high, max_tolerable)
ICAR_CROP_ENVELOPES: Dict[str, Dict[str, Tuple[float, float, float, float]]] = {
    "rice": {
        "N": (30.0, 60.0, 100.0, 140.0),
        "P": (15.0, 35.0, 55.0, 80.0),
        "K": (15.0, 30.0, 50.0, 70.0),
        "temperature": (18.0, 22.0, 32.0, 38.0),
        "humidity": (60.0, 75.0, 90.0, 98.0),
        "ph": (4.8, 5.5, 7.2, 8.0),
        "rainfall": (950.0, 1300.0, 2200.0, 3200.0)
    },
    "wheat": {
        "N": (50.0, 90.0, 130.0, 160.0),
        "P": (20.0, 45.0, 65.0, 90.0),
        "K": (15.0, 30.0, 50.0, 70.0),
        "temperature": (8.0, 14.0, 24.0, 30.0),
        "humidity": (30.0, 45.0, 65.0, 80.0),
        "ph": (5.5, 6.2, 7.5, 8.2),
        "rainfall": (250.0, 400.0, 750.0, 1000.0)
    },
    "maize": {
        "N": (40.0, 70.0, 110.0, 150.0),
        "P": (20.0, 35.0, 60.0, 80.0),
        "K": (10.0, 20.0, 40.0, 55.0),
        "temperature": (15.0, 20.0, 30.0, 36.0),
        "humidity": (40.0, 55.0, 75.0, 88.0),
        "ph": (5.2, 6.0, 7.2, 8.0),
        "rainfall": (400.0, 600.0, 950.0, 1300.0)
    },
    "soybean": {
        "N": (10.0, 25.0, 45.0, 65.0),
        "P": (35.0, 55.0, 85.0, 110.0),
        "K": (20.0, 35.0, 55.0, 75.0),
        "temperature": (18.0, 22.0, 30.0, 36.0),
        "humidity": (45.0, 60.0, 78.0, 90.0),
        "ph": (5.5, 6.2, 7.3, 8.0),
        "rainfall": (500.0, 700.0, 1050.0, 1400.0)
    },
    "cotton": {
        "N": (60.0, 95.0, 135.0, 170.0),
        "P": (20.0, 35.0, 55.0, 80.0),
        "K": (15.0, 30.0, 55.0, 75.0),
        "temperature": (18.0, 24.0, 34.0, 40.0),
        "humidity": (35.0, 50.0, 70.0, 82.0),
        "ph": (5.8, 6.5, 8.0, 8.8),
        "rainfall": (450.0, 650.0, 1000.0, 1350.0)
    },
    "chickpea": {
        "N": (10.0, 20.0, 45.0, 60.0),
        "P": (30.0, 50.0, 75.0, 95.0),
        "K": (15.0, 30.0, 50.0, 70.0),
        "temperature": (10.0, 15.0, 25.0, 32.0),
        "humidity": (15.0, 25.0, 45.0, 65.0),
        "ph": (5.8, 6.5, 7.8, 8.6),
        "rainfall": (250.0, 380.0, 650.0, 850.0)
    },
    "pigeonpeas": {
        "N": (10.0, 20.0, 38.0, 55.0),
        "P": (25.0, 45.0, 70.0, 90.0),
        "K": (10.0, 22.0, 42.0, 60.0),
        "temperature": (18.0, 23.0, 32.0, 38.0),
        "humidity": (35.0, 48.0, 68.0, 82.0),
        "ph": (5.5, 6.0, 7.4, 8.2),
        "rainfall": (450.0, 650.0, 950.0, 1300.0)
    },
    "sorghum": {
        "N": (30.0, 55.0, 85.0, 110.0),
        "P": (15.0, 28.0, 48.0, 65.0),
        "K": (10.0, 20.0, 40.0, 55.0),
        "temperature": (18.0, 25.0, 35.0, 42.0),
        "humidity": (20.0, 35.0, 60.0, 75.0),
        "ph": (5.8, 6.5, 8.0, 8.8),
        "rainfall": (300.0, 450.0, 750.0, 1050.0)
    },
    "pearl_millet": {
        "N": (25.0, 45.0, 75.0, 95.0),
        "P": (10.0, 20.0, 40.0, 55.0),
        "K": (8.0, 15.0, 32.0, 45.0),
        "temperature": (20.0, 26.0, 36.0, 44.0),
        "humidity": (15.0, 25.0, 50.0, 68.0),
        "ph": (6.0, 6.8, 8.2, 9.0),
        "rainfall": (200.0, 320.0, 580.0, 800.0)
    },
    "groundnut": {
        "N": (10.0, 20.0, 38.0, 55.0),
        "P": (25.0, 42.0, 68.0, 85.0),
        "K": (20.0, 35.0, 58.0, 75.0),
        "temperature": (18.0, 23.0, 31.0, 36.0),
        "humidity": (35.0, 50.0, 70.0, 85.0),
        "ph": (5.5, 6.0, 7.2, 8.0),
        "rainfall": (400.0, 550.0, 850.0, 1150.0)
    },
    "mustard": {
        "N": (40.0, 65.0, 95.0, 125.0),
        "P": (20.0, 35.0, 55.0, 75.0),
        "K": (15.0, 25.0, 45.0, 60.0),
        "temperature": (8.0, 13.0, 22.0, 28.0),
        "humidity": (30.0, 42.0, 62.0, 78.0),
        "ph": (5.5, 6.3, 7.5, 8.2),
        "rainfall": (250.0, 350.0, 600.0, 850.0)
    },
    "sunflower": {
        "N": (35.0, 55.0, 80.0, 105.0),
        "P": (25.0, 42.0, 68.0, 85.0),
        "K": (20.0, 32.0, 52.0, 70.0),
        "temperature": (16.0, 21.0, 30.0, 36.0),
        "humidity": (30.0, 45.0, 65.0, 80.0),
        "ph": (5.8, 6.5, 7.8, 8.5),
        "rainfall": (350.0, 500.0, 800.0, 1100.0)
    },
    "sugarcane": {
        "N": (80.0, 120.0, 160.0, 200.0),
        "P": (25.0, 45.0, 75.0, 95.0),
        "K": (40.0, 70.0, 110.0, 150.0),
        "temperature": (18.0, 24.0, 34.0, 42.0),
        "humidity": (50.0, 65.0, 82.0, 92.0),
        "ph": (5.5, 6.2, 7.6, 8.4),
        "rainfall": (950.0, 1350.0, 2200.0, 3000.0)
    },
    "mungbean": {
        "N": (8.0, 15.0, 30.0, 42.0),
        "P": (25.0, 40.0, 60.0, 78.0),
        "K": (10.0, 18.0, 30.0, 45.0),
        "temperature": (20.0, 25.0, 33.0, 38.0),
        "humidity": (40.0, 52.0, 72.0, 85.0),
        "ph": (5.5, 6.2, 7.3, 8.0),
        "rainfall": (300.0, 450.0, 700.0, 950.0)
    },
    "blackgram": {
        "N": (10.0, 18.0, 32.0, 45.0),
        "P": (25.0, 42.0, 62.0, 80.0),
        "K": (10.0, 18.0, 32.0, 46.0),
        "temperature": (20.0, 24.0, 33.0, 38.0),
        "humidity": (40.0, 55.0, 75.0, 88.0),
        "ph": (5.8, 6.3, 7.4, 8.2),
        "rainfall": (350.0, 500.0, 750.0, 1000.0)
    },
    "lentil": {
        "N": (8.0, 15.0, 28.0, 40.0),
        "P": (25.0, 42.0, 65.0, 82.0),
        "K": (10.0, 18.0, 30.0, 45.0),
        "temperature": (10.0, 15.0, 24.0, 30.0),
        "humidity": (25.0, 38.0, 58.0, 75.0),
        "ph": (5.8, 6.4, 7.6, 8.4),
        "rainfall": (250.0, 350.0, 600.0, 850.0)
    },
    "jute": {
        "N": (40.0, 65.0, 95.0, 125.0),
        "P": (20.0, 35.0, 55.0, 75.0),
        "K": (20.0, 35.0, 55.0, 75.0),
        "temperature": (22.0, 25.0, 34.0, 38.0),
        "humidity": (65.0, 75.0, 88.0, 95.0),
        "ph": (5.5, 6.2, 7.2, 8.0),
        "rainfall": (1100.0, 1350.0, 2000.0, 2800.0)
    },
    "coffee": {
        "N": (60.0, 85.0, 120.0, 150.0),
        "P": (15.0, 25.0, 45.0, 65.0),
        "K": (15.0, 25.0, 42.0, 60.0),
        "temperature": (14.0, 18.0, 28.0, 34.0),
        "humidity": (55.0, 68.0, 84.0, 92.0),
        "ph": (5.0, 5.8, 6.8, 7.5),
        "rainfall": (1200.0, 1500.0, 2400.0, 3200.0)
    },
    "banana": {
        "N": (60.0, 90.0, 130.0, 160.0),
        "P": (30.0, 50.0, 75.0, 95.0),
        "K": (30.0, 45.0, 65.0, 85.0),
        "temperature": (18.0, 24.0, 34.0, 40.0),
        "humidity": (60.0, 72.0, 88.0, 96.0),
        "ph": (5.5, 6.2, 7.5, 8.2),
        "rainfall": (1000.0, 1400.0, 2200.0, 3000.0)
    },
    "mothbeans": {
        "N": (8.0, 15.0, 30.0, 42.0),
        "P": (20.0, 35.0, 55.0, 75.0),
        "K": (8.0, 15.0, 30.0, 42.0),
        "temperature": (22.0, 27.0, 36.0, 42.0),
        "humidity": (15.0, 25.0, 50.0, 68.0),
        "ph": (6.0, 6.8, 8.2, 8.9),
        "rainfall": (200.0, 300.0, 550.0, 750.0)
    },
    "kidneybeans": {
        "N": (10.0, 18.0, 32.0, 45.0),
        "P": (50.0, 70.0, 95.0, 115.0),
        "K": (30.0, 45.0, 62.0, 80.0),
        "temperature": (18.0, 23.0, 32.0, 38.0),
        "humidity": (60.0, 72.0, 88.0, 95.0),
        "ph": (5.2, 6.0, 7.2, 8.0),
        "rainfall": (900.0, 1200.0, 1700.0, 2400.0)
    },
    "mango": {
        "N": (10.0, 18.0, 32.0, 45.0),
        "P": (15.0, 25.0, 40.0, 55.0),
        "K": (15.0, 25.0, 42.0, 58.0),
        "temperature": (18.0, 24.0, 34.0, 42.0),
        "humidity": (35.0, 48.0, 70.0, 85.0),
        "ph": (5.0, 5.8, 7.2, 8.0),
        "rainfall": (600.0, 900.0, 1450.0, 2100.0)
    },
    "grapes": {
        "N": (10.0, 18.0, 32.0, 45.0),
        "P": (95.0, 120.0, 145.0, 160.0),
        "K": (160.0, 185.0, 210.0, 225.0),
        "temperature": (12.0, 18.0, 30.0, 38.0),
        "humidity": (30.0, 42.0, 65.0, 78.0),
        "ph": (5.5, 6.2, 7.3, 8.2),
        "rainfall": (350.0, 500.0, 800.0, 1150.0)
    },
    "apple": {
        "N": (10.0, 18.0, 32.0, 48.0),
        "P": (95.0, 120.0, 145.0, 160.0),
        "K": (160.0, 185.0, 210.0, 225.0),
        "temperature": (4.0, 10.0, 20.0, 26.0),
        "humidity": (40.0, 55.0, 72.0, 85.0),
        "ph": (5.0, 5.8, 6.8, 7.5),
        "rainfall": (650.0, 850.0, 1300.0, 1750.0)
    },
    "orange": {
        "N": (10.0, 18.0, 30.0, 45.0),
        "P": (8.0, 15.0, 25.0, 38.0),
        "K": (5.0, 10.0, 18.0, 28.0),
        "temperature": (12.0, 18.0, 32.0, 38.0),
        "humidity": (35.0, 48.0, 68.0, 82.0),
        "ph": (5.5, 6.2, 7.5, 8.2),
        "rainfall": (500.0, 700.0, 1100.0, 1500.0)
    },
    "papaya": {
        "N": (25.0, 45.0, 65.0, 85.0),
        "P": (30.0, 52.0, 72.0, 90.0),
        "K": (28.0, 45.0, 65.0, 85.0),
        "temperature": (18.0, 23.0, 33.0, 38.0),
        "humidity": (50.0, 65.0, 82.0, 92.0),
        "ph": (5.5, 6.2, 7.4, 8.2),
        "rainfall": (750.0, 1100.0, 1600.0, 2200.0)
    },
    "coconut": {
        "N": (10.0, 18.0, 32.0, 45.0),
        "P": (8.0, 14.0, 22.0, 32.0),
        "K": (18.0, 28.0, 42.0, 58.0),
        "temperature": (20.0, 24.0, 32.0, 36.0),
        "humidity": (65.0, 75.0, 88.0, 96.0),
        "ph": (5.0, 5.8, 7.2, 8.0),
        "rainfall": (1000.0, 1400.0, 2200.0, 3000.0)
    },
    "pomegranate": {
        "N": (10.0, 18.0, 32.0, 48.0),
        "P": (8.0, 14.0, 22.0, 32.0),
        "K": (20.0, 35.0, 52.0, 68.0),
        "temperature": (15.0, 22.0, 35.0, 42.0),
        "humidity": (20.0, 32.0, 55.0, 72.0),
        "ph": (5.8, 6.6, 7.8, 8.6),
        "rainfall": (300.0, 450.0, 750.0, 1000.0)
    },
    "watermelon": {
        "N": (60.0, 85.0, 110.0, 135.0),
        "P": (10.0, 18.0, 28.0, 40.0),
        "K": (30.0, 42.0, 58.0, 72.0),
        "temperature": (18.0, 24.0, 33.0, 38.0),
        "humidity": (35.0, 45.0, 62.0, 75.0),
        "ph": (5.5, 6.0, 7.0, 7.8),
        "rainfall": (300.0, 420.0, 650.0, 880.0)
    },
    "muskmelon": {
        "N": (60.0, 85.0, 110.0, 135.0),
        "P": (8.0, 16.0, 26.0, 38.0),
        "K": (30.0, 42.0, 58.0, 72.0),
        "temperature": (18.0, 24.0, 34.0, 39.0),
        "humidity": (30.0, 42.0, 60.0, 72.0),
        "ph": (5.5, 6.0, 7.0, 7.8),
        "rainfall": (280.0, 380.0, 600.0, 820.0)
    }
}

# Agronomic Feature Importance Weights for Suitability Index
FEATURE_WEIGHTS = {
    "rainfall": 0.25,
    "temperature": 0.20,
    "ph": 0.15,
    "humidity": 0.15,
    "N": 0.10,
    "P": 0.075,
    "K": 0.075
}

# Crop Seasonality Mapping based on official ICAR crop calendars
CROP_SEASON_MAP: Dict[str, List[str]] = {
    "rice": ["Kharif", "Summer"],
    "wheat": ["Rabi"],
    "maize": ["Kharif", "Rabi", "Zaid", "Whole Year"],
    "soybean": ["Kharif"],
    "cotton": ["Kharif"],
    "chickpea": ["Rabi"],
    "pigeonpeas": ["Kharif"],
    "sorghum": ["Kharif", "Rabi"],
    "pearl_millet": ["Kharif"],
    "groundnut": ["Kharif", "Rabi", "Zaid"],
    "mustard": ["Rabi"],
    "sunflower": ["Kharif", "Rabi", "Zaid"],
    "sugarcane": ["Whole Year", "Kharif"],
    "mungbean": ["Kharif", "Zaid"],
    "blackgram": ["Kharif", "Rabi"],
    "lentil": ["Rabi"],
    "jute": ["Kharif"],
    "coffee": ["Whole Year"],
    "banana": ["Whole Year"],
    "mango": ["Whole Year"],
    "grapes": ["Whole Year"],
    "watermelon": ["Zaid", "Kharif"],
    "muskmelon": ["Zaid", "Kharif"],
    "apple": ["Whole Year"],
    "orange": ["Whole Year"],
    "papaya": ["Whole Year"],
    "coconut": ["Whole Year"],
    "pomegranate": ["Whole Year"],
    "kidneybeans": ["Kharif", "Rabi"],
    "mothbeans": ["Kharif"]
}

PERENNIAL_CROPS = {
    "apple", "banana", "coconut", "coffee", "grapes", "mango", "orange", "papaya", "pomegranate", "sugarcane"
}


def _discriminative_membership(value: float, envelope: Tuple[float, float, float, float]) -> float:
    """
    Computes a continuous, discriminative fuzzy membership degree mu in [0.0, 1.0].
    - Peak optimum (1.0) attained at the exact center of the optimal range.
    - Parabolic decay between center and [opt_low, opt_high] (attaining 0.85 at boundaries).
    - Linear ramp up between min_tolerable and opt_low (0.0 to 0.85).
    - Linear ramp down between opt_high and max_tolerable (0.85 to 0.0).
    - 0.0 if value < min_tolerable or value > max_tolerable.
    """
    min_tol, opt_low, opt_high, max_tol = envelope
    
    if value < min_tol or value > max_tol:
        return 0.0
        
    opt_center = (opt_low + opt_high) / 2.0
    half_width = max(1e-5, (opt_high - opt_low) / 2.0)
    
    # 1. Inside optimal band: Parabolic curve from 1.0 (center) down to 0.85 (edges)
    if opt_low <= value <= opt_high:
        rel_dist = abs(value - opt_center) / half_width  # in [0, 1]
        return round(1.0 - 0.15 * (rel_dist ** 2), 4)
        
    # 2. Sub-optimal lower transition zone: [min_tol, opt_low) -> ramps 0.0 to 0.85
    if min_tol <= value < opt_low:
        if opt_low == min_tol:
            return 0.85
        ratio = (value - min_tol) / (opt_low - min_tol)
        return round(max(0.0, 0.85 * ratio), 4)
        
    # 3. Sub-optimal upper transition zone: (opt_high, max_tol] -> ramps 0.85 down to 0.0
    if opt_high < value <= max_tol:
        if max_tol == opt_high:
            return 0.85
        ratio = (max_tol - value) / (max_tol - opt_high)
        return round(max(0.0, 0.85 * ratio), 4)
        
    return 0.0


def calculate_crop_agronomic_suitability(
    crop_name: str,
    n: float,
    p: float,
    k: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
    season: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates individual crop suitability against ICAR validated envelopes.
    Returns:
        {
            "agronomic_score": float (0.0 to 100.0),
            "suitability_level": str ("Highly Suitable", "Suitable", "Moderately Suitable", "Marginally Suitable"),
            "is_feasible": bool,
            "is_perennial": bool,
            "is_season_compatible": bool,
            "feature_scores": Dict[str, float],
            "limiting_factors": List[str],
            "rationale": str
        }
    """
    norm_crop = crop_name.lower().replace(" ", "_")
    is_perennial = norm_crop in PERENNIAL_CROPS
    
    # Season compatibility check
    is_season_compatible = True
    if season and norm_crop in CROP_SEASON_MAP:
        allowed_seasons = CROP_SEASON_MAP[norm_crop]
        if "Whole Year" not in allowed_seasons and season not in allowed_seasons:
            is_season_compatible = False
            
    if norm_crop not in ICAR_CROP_ENVELOPES:
        return {
            "agronomic_score": 50.0,
            "suitability_level": "Moderately Suitable",
            "is_feasible": True,
            "is_perennial": is_perennial,
            "is_season_compatible": is_season_compatible,
            "feature_scores": {},
            "limiting_factors": [],
            "rationale": f"Agronomic envelopes pending publication for {crop_name}."
        }
        
    envelope = ICAR_CROP_ENVELOPES[norm_crop]
    inputs = {
        "N": n,
        "P": p,
        "K": k,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall
    }
    
    feature_scores = {}
    limiting_factors = []
    optimal_factors = []
    
    for feat, val in inputs.items():
        score = _discriminative_membership(val, envelope[feat])
        feature_scores[feat] = round(score, 3)
        min_tol, opt_low, opt_high, max_tol = envelope[feat]
        
        if score < 0.35:
            if val < min_tol:
                limiting_factors.append(f"{feat} ({val:.1f}) below min tolerable ({min_tol:.1f})")
            elif val > max_tol:
                limiting_factors.append(f"{feat} ({val:.1f}) exceeds max tolerable ({max_tol:.1f})")
            else:
                limiting_factors.append(f"{feat} ({val:.1f}) suboptimal for {crop_name}")
        elif score >= 0.85:
            optimal_factors.append(feat)
            
    # Weighted composite agronomic score
    composite_score = sum(feature_scores[feat] * FEATURE_WEIGHTS[feat] for feat in inputs)
    agronomic_score = round(composite_score * 100.0, 1)
    
    # Apply seasonal incompatibility penalty if strictly off-season
    if not is_season_compatible:
        agronomic_score = round(agronomic_score * 0.40, 1)
        limiting_factors.insert(0, f"Off-season: {crop_name} is typically grown in {', '.join(CROP_SEASON_MAP[norm_crop])}, not {season}")
        
    # Classify qualitative suitability level
    if agronomic_score >= 80.0:
        suitability_level = "Highly Suitable"
    elif agronomic_score >= 60.0:
        suitability_level = "Suitable"
    elif agronomic_score >= 38.0:
        suitability_level = "Moderately Suitable"
    else:
        suitability_level = "Marginally Suitable"
        
    # Build human-readable agronomic rationale
    crop_display = crop_name.replace("_", " ").title()
    if is_perennial:
        perennial_prefix = "[Perennial Crop: Preliminary suitability] "
    else:
        perennial_prefix = ""
        
    if agronomic_score >= 80.0:
        rationale = f"{perennial_prefix}Excellent biophysical match: {', '.join(optimal_factors[:3])} within optimal ICAR ranges for {crop_display}."
    elif agronomic_score >= 60.0:
        if limiting_factors:
            rationale = f"{perennial_prefix}Good suitability for {crop_display}; note: {limiting_factors[0]}."
        else:
            rationale = f"{perennial_prefix}Good overall agro-climatic conditions for {crop_display}."
    elif agronomic_score >= 38.0:
        rationale = f"{perennial_prefix}Moderate suitability for {crop_display}. Constrained by: {', '.join(limiting_factors[:2])}."
    else:
        rationale = f"{perennial_prefix}Marginal suitability: {', '.join(limiting_factors[:2])} outside recommended ICAR envelope."
        
    return {
        "agronomic_score": agronomic_score,
        "suitability_level": suitability_level,
        "is_feasible": agronomic_score >= 30.0 and is_season_compatible,
        "is_perennial": is_perennial,
        "is_season_compatible": is_season_compatible,
        "feature_scores": feature_scores,
        "limiting_factors": limiting_factors,
        "rationale": rationale
    }


def rank_recommendations_with_suitability(
    raw_model_predictions: List[Dict[str, Any]],
    n: float,
    p: float,
    k: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
    season: Optional[str] = None,
    top_k: int = 5,
    min_prob_threshold: float = 0.010  # Validated 1.0% primary candidate floor
) -> List[Dict[str, Any]]:
    """
    Scientifically defensible two-tier candidate filtering and ranking pipeline:
    1. Evaluates all 30 crops across neural model probability and ICAR biophysical envelopes.
    2. Classifies candidates into:
       - PRIMARY: P_model >= 1.0%, agronomic feasibility (S_agro >= 30), and season compatibility.
       - SECONDARY / PRELIMINARY: Agronomically viable (S_agro >= 50) but weak model support or perennial screening.
    3. Does NOT force dummy backfill into the PRIMARY list.
    4. Computes validated 60/40 composite score: 0.60 * (P_model * 100) + 0.40 * S_agro.
    """
    evaluated_candidates = []
    
    for item in raw_model_predictions:
        crop = item["crop"]
        prob = float(item["probability"])
        
        agro_eval = calculate_crop_agronomic_suitability(
            crop_name=crop,
            n=n,
            p=p,
            k=k,
            temperature=temperature,
            humidity=humidity,
            ph=ph,
            rainfall=rainfall,
            season=season
        )
        
        # Validated 60/40 composite score
        composite = round(0.60 * (prob * 100.0) + 0.40 * agro_eval["agronomic_score"], 2)
        
        # 4-Quadrant Classification
        is_strong_ml = prob >= 0.05  # >= 5% probability
        is_strong_agro = agro_eval["agronomic_score"] >= 75.0
        
        if is_strong_ml and is_strong_agro:
            quadrant = "Strong ML + Strong Agronomy"
        elif is_strong_ml and not is_strong_agro:
            quadrant = "Strong ML + Weak Agronomy"
        elif (not is_strong_ml) and is_strong_agro:
            quadrant = "Weak ML + Strong Agronomy (Plausible, Low Confidence)"
        else:
            quadrant = "Weak ML + Weak Agronomy"
            
        is_perennial = agro_eval["is_perennial"]
        is_season_comp = agro_eval["is_season_compatible"]
        is_feasible = agro_eval["is_feasible"]
        
        # Primary candidate criteria: Meaningful model probability + agronomic feasibility + season compatibility
        # For perennial crops, require high model confidence (>= 5%) to qualify as primary, else preliminary
        if prob >= min_prob_threshold and is_feasible and is_season_comp:
            if is_perennial and prob < 0.05:
                recommendation_level = "PRELIMINARY"
                is_primary = False
            else:
                recommendation_level = "PRIMARY"
                is_primary = True
        elif is_perennial and agro_eval["agronomic_score"] >= 45.0:
            recommendation_level = "PRELIMINARY"
            is_primary = False
        elif agro_eval["agronomic_score"] >= 45.0:
            recommendation_level = "SECONDARY"
            is_primary = False
        else:
            recommendation_level = "EXCLUDED"
            is_primary = False
            
        evaluated_candidates.append({
            "crop": crop,
            "probability": prob,
            "model_score": round(prob, 4),
            "agronomic_score": agro_eval["agronomic_score"],
            "composite_score": composite,
            "suitability": agro_eval["suitability_level"],
            "is_feasible": is_feasible,
            "is_perennial": is_perennial,
            "is_season_compatible": is_season_comp,
            "is_primary": is_primary,
            "recommendation_level": recommendation_level,
            "quadrant": quadrant,
            "rationale": agro_eval["rationale"]
        })
        
    # Separate Primary and Secondary
    primary_pool = [c for c in evaluated_candidates if c["is_primary"]]
    primary_pool.sort(key=lambda x: x["composite_score"], reverse=True)
    
    secondary_pool = [c for c in evaluated_candidates if not c["is_primary"] and c["recommendation_level"] != "EXCLUDED"]
    # Sort secondary pool by composite score
    secondary_pool.sort(key=lambda x: x["composite_score"], reverse=True)
    
    # Assign ranks to primary
    for idx, cand in enumerate(primary_pool[:top_k]):
        cand["rank"] = idx + 1
        
    # Assign ranks to secondary
    for idx, cand in enumerate(secondary_pool[:top_k]):
        cand["rank"] = len(primary_pool[:top_k]) + idx + 1
        
    # Combined list starts with primary candidates (variable length), followed by secondary candidates
    combined = primary_pool[:top_k] + secondary_pool[:top_k]
    return combined
