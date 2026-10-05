import sys
from pathlib import Path
sys.path.insert(0, r"D:\FINAL FINAL YEAR PROJECT")
sys.path.insert(0, r"D:\FINAL FINAL YEAR PROJECT\backend")

import json
from app.schemas.crop import CropRecommendationRequest
from app.services.crop_recommendation_service import CropRecommendationService
from ml.crop_recommendation.model.predict import predict_all_crop_probabilities

print("=" * 80)
print("  AGRIPULSE SUBSYSTEM 3A — COMPREHENSIVE DIAGNOSTIC & SENSITIVITY SUITE")
print("=" * 80)

# 1. 15+ Diverse Regional Scenarios Across India
scenarios = [
    {
        "id": "SC-01",
        "name": "Vidarbha Soybean/Cotton (Nagpur, Maharashtra)",
        "state": "Maharashtra", "district": "Nagpur",
        "N": 35.0, "P": 70.0, "K": 45.0, "temperature": 26.0, "humidity": 68.0, "ph": 6.7, "rainfall": 1050.0
    },
    {
        "id": "SC-02",
        "name": "Punjab Rabi Wheat (Ludhiana, Punjab)",
        "state": "Punjab", "district": "Ludhiana",
        "N": 110.0, "P": 55.0, "K": 38.0, "temperature": 18.5, "humidity": 55.0, "ph": 6.8, "rainfall": 650.0
    },
    {
        "id": "SC-03",
        "name": "Bengal Gangetic Alluvium (Bardhaman, West Bengal)",
        "state": "West Bengal", "district": "Bardhaman",
        "N": 80.0, "P": 45.0, "K": 40.0, "temperature": 25.0, "humidity": 82.0, "ph": 6.3, "rainfall": 1600.0
    },
    {
        "id": "SC-04",
        "name": "Rajasthan Arid Pearl Millet / Bajra (Jodhpur, Rajasthan)",
        "state": "Rajasthan", "district": "Jodhpur",
        "N": 60.0, "P": 30.0, "K": 25.0, "temperature": 31.0, "humidity": 42.0, "ph": 7.6, "rainfall": 450.0
    },
    {
        "id": "SC-05",
        "name": "Maharashtra Sugarcane Belt (Kolhapur, Maharashtra)",
        "state": "Maharashtra", "district": "Kolhapur",
        "N": 140.0, "P": 60.0, "K": 90.0, "temperature": 28.0, "humidity": 72.0, "ph": 6.8, "rainfall": 1650.0
    },
    {
        "id": "SC-06",
        "name": "Madhya Pradesh Malwa Chickpea (Indore, Madhya Pradesh)",
        "state": "Madhya Pradesh", "district": "Indore",
        "N": 32.0, "P": 65.0, "K": 40.0, "temperature": 20.0, "humidity": 35.0, "ph": 7.3, "rainfall": 600.0
    },
    {
        "id": "SC-07",
        "name": "Gujarat Saurashtra Groundnut (Rajkot, Gujarat)",
        "state": "Gujarat", "district": "Rajkot",
        "N": 28.0, "P": 55.0, "K": 48.0, "temperature": 26.5, "humidity": 60.0, "ph": 6.4, "rainfall": 700.0
    },
    {
        "id": "SC-08",
        "name": "Haryana Mustard Belt (Hisar, Haryana)",
        "state": "Haryana", "district": "Hisar",
        "N": 80.0, "P": 45.0, "K": 35.0, "temperature": 18.0, "humidity": 52.0, "ph": 6.9, "rainfall": 480.0
    },
    {
        "id": "SC-09",
        "name": "Karnataka Maize / Fodder (Dharwad, Karnataka)",
        "state": "Karnataka", "district": "Dharwad",
        "N": 90.0, "P": 48.0, "K": 30.0, "temperature": 24.5, "humidity": 65.0, "ph": 6.5, "rainfall": 750.0
    },
    {
        "id": "SC-10",
        "name": "Marathwada Sorghum / Jowar (Aurangabad, Maharashtra)",
        "state": "Maharashtra", "district": "Aurangabad",
        "N": 70.0, "P": 38.0, "K": 30.0, "temperature": 29.5, "humidity": 48.0, "ph": 7.4, "rainfall": 600.0
    },
    {
        "id": "SC-11",
        "name": "Himachal Apple Highlands (Shimla, Himachal Pradesh)",
        "state": "Himachal Pradesh", "district": "Shimla",
        "N": 26.0, "P": 134.0, "K": 196.0, "temperature": 15.5, "humidity": 62.0, "ph": 6.2, "rainfall": 1050.0
    },
    {
        "id": "SC-12",
        "name": "Maharashtra Grape Vineyards (Nashik, Maharashtra)",
        "state": "Maharashtra", "district": "Nashik",
        "N": 25.0, "P": 132.0, "K": 198.0, "temperature": 24.0, "humidity": 54.0, "ph": 6.6, "rainfall": 680.0
    },
    {
        "id": "SC-13",
        "name": "Kerala Coastal Coconut (Alappuzha, Kerala)",
        "state": "Kerala", "district": "Alappuzha",
        "N": 25.0, "P": 18.0, "K": 35.0, "temperature": 27.5, "humidity": 82.0, "ph": 6.4, "rainfall": 1750.0
    },
    {
        "id": "SC-14",
        "name": "Western Ghats Coffee (Kodagu, Karnataka)",
        "state": "Karnataka", "district": "Kodagu",
        "N": 102.0, "P": 35.0, "K": 32.0, "temperature": 22.5, "humidity": 75.0, "ph": 6.2, "rainfall": 1750.0
    },
    {
        "id": "SC-15",
        "name": "Assam Floodplain Jute (Kamrup, Assam)",
        "state": "Assam", "district": "Kamrup",
        "N": 82.0, "P": 46.0, "K": 40.0, "temperature": 27.0, "humidity": 80.0, "ph": 6.7, "rainfall": 1450.0
    },
    {
        "id": "SC-16",
        "name": "Vidarbha Cash Cotton (Yavatmal, Maharashtra)",
        "state": "Maharashtra", "district": "Yavatmal",
        "N": 118.0, "P": 45.0, "K": 42.0, "temperature": 29.0, "humidity": 58.0, "ph": 7.2, "rainfall": 800.0
    }
]

print(f"\nEvaluating {len(scenarios)} Diverse Scenarios...")
top1_crops = []
results_table = []

for sc in scenarios:
    req = CropRecommendationRequest(
        N=sc["N"], P=sc["P"], K=sc["K"],
        temperature=sc["temperature"], humidity=sc["humidity"], ph=sc["ph"], rainfall=sc["rainfall"],
        state=sc["state"], district=sc["district"], top_k=5
    )
    res = CropRecommendationService.recommend(req)
    top1 = res.recommended_crop
    top1_crops.append(top1)
    recs = [f"#{r.rank} {r.crop} ({r.model_score*100:.1f}% prob, {r.agronomic_score:.0f} agro, {r.suitability})" for r in res.recommendations]
    
    results_table.append({
        "id": sc["id"],
        "name": sc["name"],
        "state": sc["state"],
        "district": sc["district"],
        "inputs": f"N={sc['N']}, P={sc['P']}, K={sc['K']}, T={sc['temperature']}, H={sc['humidity']}, pH={sc['ph']}, R={sc['rainfall']}",
        "top1": top1,
        "confidence": res.confidence,
        "suitability": res.suitability,
        "top5": [r.crop for r in res.recommendations],
        "detailed": recs
    })
    
    print(f"\n[{sc['id']}] {sc['name']}")
    print(f"   Inputs: N={sc['N']}, P={sc['P']}, K={sc['K']}, T={sc['temperature']}C, H={sc['humidity']}%, pH={sc['ph']}, R={sc['rainfall']}mm")
    print(f"   Top-1 Recommended: {top1.upper()} (Prob: {res.confidence*100:.1f}%, Suitability: {res.suitability})")
    for r in recs:
        print(f"      {r}")

unique_top1 = list(set(top1_crops))
print("\n" + "=" * 80)
print(f"DIAGNOSTIC SUMMARY: {len(unique_top1)} Distinct Crops in Top-1 Position across {len(scenarios)} Scenarios:")
print(f"Unique Top-1 Crops: {unique_top1}")
print("=" * 80)

# 2. Sensitivity Analysis (Single variable perturbations)
print("\n--- SENSITIVITY TESTING (One Variable at a Time) ---")
base_sc = {
    "N": 35.0, "P": 70.0, "K": 45.0, "temperature": 26.0, "humidity": 68.0, "ph": 6.7, "rainfall": 850.0
}
print(f"Base Condition (Optimal Soybean): {base_sc}")

# Perturbations
tests = [
    ("Base (Soybean)", base_sc),
    ("High Nitrogen N=120 (Shift toward Cotton/Maize)", {**base_sc, "N": 120.0}),
    ("High Potassium K=195 & High P=130 (Shift toward Grapes/Apple)", {**base_sc, "K": 195.0, "P": 130.0}),
    ("Cool Temp T=18C, Low Rain R=500mm (Shift toward Wheat/Chickpea)", {**base_sc, "temperature": 18.0, "rainfall": 500.0}),
    ("High Rain R=1800mm, High Hum H=85% (Shift toward Rice/Sugarcane/Jute)", {**base_sc, "rainfall": 1800.0, "humidity": 85.0}),
    ("Arid Condition T=32C, H=35%, R=400mm (Shift toward Pearl Millet/Mothbeans)", {**base_sc, "temperature": 32.0, "humidity": 35.0, "rainfall": 400.0}),
    ("Alkaline Soil pH=8.2, Low Rain R=500mm (Shift toward Chickpea/Sorghum)", {**base_sc, "ph": 8.2, "rainfall": 500.0})
]

for label, p_inputs in tests:
    req = CropRecommendationRequest(
        N=p_inputs["N"], P=p_inputs["P"], K=p_inputs["K"],
        temperature=p_inputs["temperature"], humidity=p_inputs["humidity"],
        ph=p_inputs["ph"], rainfall=p_inputs["rainfall"], top_k=3
    )
    res = CropRecommendationService.recommend(req)
    top_str = ", ".join([f"{r.crop} ({r.model_score*100:.1f}%)" for r in res.recommendations])
    print(f"  [{label}] -> Top: {top_str}")

# 3. Location/District Sensitivity
print("\n--- LOCATION CONTEXT SENSITIVITY (Same Soil, Different Climate/Districts) ---")
soil = {"N": 40.0, "P": 60.0, "K": 50.0, "ph": 6.8}
districts = [
    ("Nagpur (Vidarbha)", "Maharashtra", "Nagpur", 28.0, 65.0, 1050.0),
    ("Nashik (Western)", "Maharashtra", "Nashik", 24.0, 54.0, 680.0),
    ("Ludhiana (Punjab)", "Punjab", "Ludhiana", 18.5, 55.0, 650.0),
    ("Jodhpur (Thar Arid)", "Rajasthan", "Jodhpur", 31.0, 42.0, 450.0),
    ("Bardhaman (Bengal Floodplain)", "West Bengal", "Bardhaman", 26.0, 82.0, 1600.0)
]

for d_name, state, district, temp, hum, rain in districts:
    req = CropRecommendationRequest(
        N=soil["N"], P=soil["P"], K=soil["K"], ph=soil["ph"],
        temperature=temp, humidity=hum, rainfall=rain,
        state=state, district=district, top_k=3
    )
    res = CropRecommendationService.recommend(req)
    top_crops_str = ", ".join([f"{r.crop} ({r.model_score*100:.1f}%, agro={r.agronomic_score})" for r in res.recommendations])
    print(f"  Soil + {d_name} (T={temp}C, H={hum}%, R={rain}mm) -> Top: {top_crops_str}")

print("\n" + "=" * 80)
print("  ALL DIAGNOSTICS EXECUTED CLEANLY")
print("=" * 80)
