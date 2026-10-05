import sys
from pathlib import Path
sys.path.insert(0, r"D:\FINAL FINAL YEAR PROJECT")
sys.path.insert(0, r"D:\FINAL FINAL YEAR PROJECT\backend")

import numpy as np
import pandas as pd
from ml.crop_recommendation.model.predict import predict_all_crop_probabilities
from ml.crop_recommendation.agronomic_suitability import (
    calculate_crop_agronomic_suitability,
    ICAR_CROP_ENVELOPES
)

# 1. Inspect raw probabilities for Balangir Kharif
inputs = {
    'n': 65.0, 'p': 35.0, 'k': 30.0,
    'temperature': 29.0, 'humidity': 80.0, 'ph': 6.2, 'rainfall': 1350.0
}
raw_preds = predict_all_crop_probabilities(**inputs)

print("=== RAW MODEL PROBABILITIES FOR BALANGIR KHARIF ===")
for p in sorted(raw_preds, key=lambda x: x['probability'], reverse=True):
    crop = p['crop']
    prob = p['probability']
    agro = calculate_crop_agronomic_suitability(crop, inputs['n'], inputs['p'], inputs['k'],
                                               inputs['temperature'], inputs['humidity'], inputs['ph'], inputs['rainfall'])
    if prob >= 0.0001:
        print(f"  {crop:15s}: Model={prob*100:6.2f}%, Agro={agro['agronomic_score']:5.1f}, Rationale={agro['rationale']}")
