import sys
from pathlib import Path
sys.path.insert(0, r"D:\FINAL FINAL YEAR PROJECT")
sys.path.insert(0, r"D:\FINAL FINAL YEAR PROJECT\backend")

from ml.crop_recommendation.model.predict import predict_all_crop_probabilities
from ml.crop_recommendation.agronomic_suitability import calculate_crop_agronomic_suitability

def test_scenario(name, inputs):
    raw_preds = predict_all_crop_probabilities(
        n=inputs["N"], p=inputs["P"], k=inputs["K"],
        temperature=inputs["temperature"], humidity=inputs["humidity"],
        ph=inputs["ph"], rainfall=inputs["rainfall"]
    )
    
    print(f"\n=======================================================")
    print(f"  SCENARIO: {name}")
    print(f"  Inputs: {inputs}")
    print(f"=======================================================")
    
    # Evaluate all crops
    evaluated = []
    for p in raw_preds:
        crop = p["crop"]
        prob = p["probability"]
        agro = calculate_crop_agronomic_suitability(
            crop, inputs["N"], inputs["P"], inputs["K"],
            inputs["temperature"], inputs["humidity"], inputs["ph"], inputs["rainfall"]
        )
        
        # Quadrant classification
        is_strong_ml = prob >= 0.05  # >= 5%
        is_mod_ml = (prob >= 0.005) and (prob < 0.05)  # 0.5% - 5%
        is_strong_agro = agro["agronomic_score"] >= 75.0
        
        if is_strong_ml and is_strong_agro:
            quadrant = "Strong ML + Strong Agronomy"
        elif is_strong_ml and not is_strong_agro:
            quadrant = "Strong ML + Weak Agronomy"
        elif (not is_strong_ml) and is_strong_agro:
            quadrant = "Weak ML + Strong Agronomy (Plausible, Low Confidence)"
        else:
            quadrant = "Weak ML + Weak Agronomy"
            
        evaluated.append({
            "crop": crop,
            "prob": prob,
            "agro": agro["agronomic_score"],
            "feasible": agro["is_feasible"],
            "quadrant": quadrant,
            "rationale": agro["rationale"]
        })
        
    # Strategy A: Legacy Additive 50/50
    legacy = sorted(evaluated, key=lambda x: 0.50*(x["prob"]*100) + 0.50*x["agro"], reverse=True)[:5]
    print("\n[Strategy A: Legacy Additive 50/50 (Unfiltered)]")
    for idx, r in enumerate(legacy):
        comp = 0.50*(r["prob"]*100) + 0.50*r["agro"]
        print(f"  #{idx+1} {r['crop']:12s} | Prob={r['prob']*100:5.2f}% | Agro={r['agro']:5.1f} | Comp={comp:5.2f} | [{r['quadrant']}]")
        
    # Strategy B: Two-Stage Filter (Model Probability Floor tau=0.5%, rank by 60/40)
    # Stage 1: Filter candidates with prob >= 0.5% & feasible
    primary_pool = [c for c in evaluated if c["prob"] >= 0.005 and c["feasible"]]
    if len(primary_pool) < 5:
        # Fallback to remaining top by probability
        rem = [c for c in evaluated if c not in primary_pool]
        rem.sort(key=lambda x: x["prob"], reverse=True)
        primary_pool.extend(rem[:(5 - len(primary_pool))])
        
    # Stage 2: Rank by validated 60/40 composite
    strat_b = sorted(primary_pool, key=lambda x: 0.60*(x["prob"]*100) + 0.40*x["agro"], reverse=True)[:5]
    print("\n[Strategy B: Scientifically Gated Candidate Filter (tau=0.5%) + 60/40 Composite]")
    for idx, r in enumerate(strat_b):
        comp = 0.60*(r["prob"]*100) + 0.40*r["agro"]
        print(f"  #{idx+1} {r['crop']:12s} | Prob={r['prob']*100:5.2f}% | Agro={r['agro']:5.1f} | Comp={comp:5.2f} | [{r['quadrant']}]")

test_scenario(
    "Balangir, Odisha (Kharif Season)",
    {"N": 65.0, "P": 35.0, "K": 30.0, "temperature": 29.0, "humidity": 80.0, "ph": 6.2, "rainfall": 1350.0}
)

test_scenario(
    "Balangir, Odisha (Rabi Season)",
    {"N": 30.0, "P": 55.0, "K": 35.0, "temperature": 20.5, "humidity": 40.0, "ph": 6.6, "rainfall": 480.0}
)
