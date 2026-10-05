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

print(f"Stratified Test Set: {len(test_df)} records across {test_df[TARGET_COLUMN].nunique()} classes.")

# Load inference artifacts
artifacts = load_inference_artifacts()
model = artifacts["model"]
scaler = artifacts["scaler"]
class_names = artifacts["class_names"]

# 1. Batch inference on test set (540 samples)
X_raw = test_df[FEATURE_COLUMNS].values
X_scaled = scaler.transform(X_raw)
X_seq = reshape_tabular_to_sequence(X_scaled)
print(f"Running vectorized inference for all {len(test_df)} test samples...")
all_prob_dists = model.predict(X_seq, batch_size=64, verbose=0)
print("Vectorized inference complete.")

strategies = [
    {"name": "1. Unfiltered Additive (50/50)", "type": "additive", "tau": 0.0, "w_model": 0.50, "w_agro": 0.50},
    {"name": "2. Unfiltered Additive (60/40)", "type": "additive", "tau": 0.0, "w_model": 0.60, "w_agro": 0.40},
    {"name": "3. Unfiltered Additive (70/30)", "type": "additive", "tau": 0.0, "w_model": 0.70, "w_agro": 0.30},
    {"name": "4. Relevance Filter (tau=0.5%) + 50/50", "type": "filtered", "tau": 0.005, "w_model": 0.50, "w_agro": 0.50},
    {"name": "5. Relevance Filter (tau=0.5%) + 60/40", "type": "filtered", "tau": 0.005, "w_model": 0.60, "w_agro": 0.40},
    {"name": "6. Relevance Filter (tau=0.5%) + 70/30", "type": "filtered", "tau": 0.005, "w_model": 0.70, "w_agro": 0.30},
    {"name": "7. Relevance Filter (tau=1.0%) + 60/40", "type": "filtered", "tau": 0.010, "w_model": 0.60, "w_agro": 0.40},
    {"name": "8. Relevance Filter (tau=1.0%) + 70/30", "type": "filtered", "tau": 0.010, "w_model": 0.70, "w_agro": 0.30},
    {"name": "9. Relevance Filter (tau=2.0%) + 60/40", "type": "filtered", "tau": 0.020, "w_model": 0.60, "w_agro": 0.40},
    {"name": "10. Multiplicative Gating (alpha=0.6)", "type": "multiplicative", "alpha": 0.60},
    {"name": "11. Multiplicative Gating (alpha=0.7)", "type": "multiplicative", "alpha": 0.70},
    {"name": "12. Soft Gated Agronomy (p_gate=2%) + 60/40", "type": "soft_gated", "w_model": 0.60, "w_agro": 0.40, "p_gate": 0.02}
]

def rank_candidates(prob_dist, row_inputs, strat, top_k=5):
    evaluated = []
    for idx, prob in enumerate(prob_dist):
        crop = class_names[idx]
        prob_float = float(prob)
        agro = calculate_crop_agronomic_suitability(
            crop, row_inputs["N"], row_inputs["P"], row_inputs["K"],
            row_inputs["temperature"], row_inputs["humidity"], row_inputs["ph"], row_inputs["rainfall"]
        )
        
        if strat["type"] in ["additive", "filtered"]:
            score = strat["w_model"] * (prob_float * 100.0) + strat["w_agro"] * agro["agronomic_score"]
        elif strat["type"] == "multiplicative":
            p_val = max(1e-6, prob_float * 100.0)
            a_val = max(1.0, agro["agronomic_score"])
            score = (p_val ** strat["alpha"]) * (a_val ** (1.0 - strat["alpha"]))
        elif strat["type"] == "soft_gated":
            gate = min(1.0, prob_float / strat["p_gate"])
            effective_agro = agro["agronomic_score"] * gate
            score = strat["w_model"] * (prob_float * 100.0) + strat["w_agro"] * effective_agro
            
        evaluated.append({
            "crop": crop,
            "prob": prob_float,
            "agro": agro["agronomic_score"],
            "score": score,
            "feasible": agro["is_feasible"]
        })
        
    if strat["type"] == "filtered":
        # Candidate selection: require prob >= tau AND feasibility
        eligible = [c for c in evaluated if c["prob"] >= strat["tau"] and c["feasible"]]
        if len(eligible) < top_k:
            remaining = [c for c in evaluated if c not in eligible]
            remaining.sort(key=lambda x: x["prob"], reverse=True)
            eligible.extend(remaining[:(top_k - len(eligible))])
        eligible.sort(key=lambda x: x["score"], reverse=True)
        return eligible[:top_k]
    else:
        evaluated.sort(key=lambda x: x["score"], reverse=True)
        return evaluated[:top_k]

# Evaluate on all 540 test samples
results_summary = []
for strat in strategies:
    top1_correct = 0
    top3_correct = 0
    top5_correct = 0
    zero_prob_in_top5 = 0  # prob < 0.1%
    low_prob_in_top5 = 0   # prob < 1.0%
    total_top5_crops = 0
    feasible_top5_count = 0
    
    for row_idx, (_, row) in enumerate(test_df.iterrows()):
        inputs = {
            "N": float(row["N"]), "P": float(row["P"]), "K": float(row["K"]),
            "temperature": float(row["temperature"]), "humidity": float(row["humidity"]),
            "ph": float(row["ph"]), "rainfall": float(row["rainfall"])
        }
        true_label = row["label"]
        prob_dist = all_prob_dists[row_idx]
        
        top_recs = rank_candidates(prob_dist, inputs, strat, top_k=5)
        top_crops = [r["crop"] for r in top_recs]
        
        if top_crops[0] == true_label:
            top1_correct += 1
        if true_label in top_crops[:3]:
            top3_correct += 1
        if true_label in top_crops[:5]:
            top5_correct += 1
            
        for r in top_recs:
            total_top5_crops += 1
            if r["prob"] < 0.001:  # < 0.1%
                zero_prob_in_top5 += 1
            if r["prob"] < 0.010:  # < 1.0%
                low_prob_in_top5 += 1
            if r["feasible"]:
                feasible_top5_count += 1
                
    n_samples = len(test_df)
    results_summary.append({
        "Strategy": strat["name"],
        "Top-1 Acc": f"{top1_correct / n_samples * 100:.2f}%",
        "Top-3 Acc": f"{top3_correct / n_samples * 100:.2f}%",
        "Top-5 Acc": f"{top5_correct / n_samples * 100:.2f}%",
        "Zero-Prob (<0.1%) Rate": f"{zero_prob_in_top5 / total_top5_crops * 100:.2f}%",
        "Low-Prob (<1.0%) Rate": f"{low_prob_in_top5 / total_top5_crops * 100:.2f}%",
        "Agro Feasibility Rate": f"{feasible_top5_count / total_top5_crops * 100:.2f}%"
    })

res_df = pd.DataFrame(results_summary)
print("\n" + "=" * 100)
print("   EMPIRICAL BENCHMARK OF 12 CANDIDATE-FILTERING & RANKING STRATEGIES (N=540 TEST SET)")
print("=" * 100)
print(res_df.to_string(index=False))
