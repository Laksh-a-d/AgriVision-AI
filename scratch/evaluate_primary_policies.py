import sys
from pathlib import Path
sys.path.insert(0, r"D:\FINAL FINAL YEAR PROJECT")
sys.path.insert(0, r"D:\FINAL FINAL YEAR PROJECT\backend")

import json
import numpy as np
import pandas as pd
from ml.crop_recommendation.model.predict import load_inference_artifacts
from ml.crop_recommendation.model.model_utils import reshape_tabular_to_sequence
from ml.crop_recommendation.agronomic_suitability import (
    calculate_crop_agronomic_suitability,
    ICAR_CROP_ENVELOPES
)
from sklearn.model_selection import train_test_split
from ml.crop_recommendation.config import (
    RAW_DATA_PATH, FEATURE_COLUMNS, TARGET_COLUMN,
    TRAIN_RATIO, VAL_RATIO, TEST_RATIO, RANDOM_STATE
)

# Load dataset and recreate stratified test split as raw DataFrame
df = pd.read_csv(RAW_DATA_PATH)
val_test_ratio = VAL_RATIO + TEST_RATIO
train_df, temp_df = train_test_split(df, test_size=val_test_ratio, random_state=RANDOM_STATE, stratify=df[TARGET_COLUMN])
relative_test_ratio = TEST_RATIO / val_test_ratio
val_df, test_df = train_test_split(temp_df, test_size=relative_test_ratio, random_state=RANDOM_STATE, stratify=temp_df[TARGET_COLUMN])

artifacts = load_inference_artifacts()
model = artifacts["model"]
scaler = artifacts["scaler"]
class_names = artifacts["class_names"]

# Vectorized batch prediction on test set (540 samples)
X_raw = test_df[FEATURE_COLUMNS].values
X_scaled = scaler.transform(X_raw)
X_seq = reshape_tabular_to_sequence(X_scaled)
all_prob_dists = model.predict(X_seq, batch_size=64, verbose=0)

policies = [
    {"name": "Policy 1: P >= 0.5%", "tau": 0.005, "w_m": 0.60, "w_a": 0.40},
    {"name": "Policy 2: P >= 1.0%", "tau": 0.010, "w_m": 0.60, "w_a": 0.40},
    {"name": "Policy 3: P >= 2.0%", "tau": 0.020, "w_m": 0.60, "w_a": 0.40},
    {"name": "Policy 4: P >= 5.0%", "tau": 0.050, "w_m": 0.60, "w_a": 0.40},
    {"name": "Policy 5: P >= 2.0% (50/50)", "tau": 0.020, "w_m": 0.50, "w_a": 0.50},
    {"name": "Policy 6: P >= 2.0% (70/30)", "tau": 0.020, "w_m": 0.70, "w_a": 0.30},
    {"name": "Policy 7: P >= 2.0% (Multiplicative)", "tau": 0.020, "type": "mult", "alpha": 0.60}
]

results = []
n_samples = len(test_df)

for pol in policies:
    top1_hits = 0
    top3_hits = 0
    top5_hits = 0
    primary_counts = []
    zero_prob_in_primary = 0  # < 0.1%
    low_prob_in_primary = 0   # < 1.0%
    total_primary_recs = 0
    feasible_primary_recs = 0
    
    for row_idx, (_, row) in enumerate(test_df.iterrows()):
        true_label = row[TARGET_COLUMN]
        prob_dist = all_prob_dists[row_idx]
        
        candidates = []
        for idx, p in enumerate(prob_dist):
            crop = class_names[idx]
            p_val = float(p)
            agro = calculate_crop_agronomic_suitability(
                crop, float(row["N"]), float(row["P"]), float(row["K"]),
                float(row["temperature"]), float(row["humidity"]), float(row["ph"]), float(row["rainfall"])
            )
            
            if pol.get("type") == "mult":
                score = ((p_val * 100.0) ** pol["alpha"]) * (max(1.0, agro["agronomic_score"]) ** (1.0 - pol["alpha"]))
            else:
                score = pol["w_m"] * (p_val * 100.0) + pol["w_a"] * agro["agronomic_score"]
                
            candidates.append({
                "crop": crop,
                "prob": p_val,
                "agro": agro["agronomic_score"],
                "score": score,
                "feasible": agro["is_feasible"]
            })
            
        # Separate into Primary and Secondary (NO FORCED BACKFILL TO 5)
        primary = [c for c in candidates if c["prob"] >= pol["tau"] and c["feasible"]]
        primary.sort(key=lambda x: x["score"], reverse=True)
        primary = primary[:5]  # Cap at max 5
        primary_counts.append(len(primary))
        
        primary_crops = [c["crop"] for c in primary]
        
        # Check Top-1, Top-3, Top-5 retention in primary
        if len(primary_crops) > 0 and primary_crops[0] == true_label:
            top1_hits += 1
        if true_label in primary_crops[:3]:
            top3_hits += 1
        if true_label in primary_crops[:5]:
            top5_hits += 1
            
        for c in primary:
            total_primary_recs += 1
            if c["prob"] < 0.001:
                zero_prob_in_primary += 1
            if c["prob"] < 0.010:
                low_prob_in_primary += 1
            if c["feasible"]:
                feasible_primary_recs += 1
                
    results.append({
        "Policy": pol["name"],
        "Top-1 Acc": f"{top1_hits / n_samples * 100:.2f}%",
        "Top-3 Acc": f"{top3_hits / n_samples * 100:.2f}%",
        "Top-5 Acc": f"{top5_hits / n_samples * 100:.2f}%",
        "Avg Primary Count": f"{np.mean(primary_counts):.2f}",
        "Min/Max Primary": f"{np.min(primary_counts)} - {np.max(primary_counts)}",
        "Zero-Prob (<0.1%) in Primary": f"{zero_prob_in_primary / max(1, total_primary_recs) * 100:.2f}%",
        "Low-Prob (<1.0%) in Primary": f"{low_prob_in_primary / max(1, total_primary_recs) * 100:.2f}%",
        "Primary Feasibility Rate": f"{feasible_primary_recs / max(1, total_primary_recs) * 100:.2f}%"
    })

res_df = pd.DataFrame(results)
print("\n" + "=" * 110)
print("   EMPIRICAL EVALUATION OF PRIMARY-RECOMMENDATION POLICIES (N=540 TEST SET)")
print("=" * 110)
print(res_df.to_string(index=False))
