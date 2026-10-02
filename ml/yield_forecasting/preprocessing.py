import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ml.yield_forecasting.config import (
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
    COL_STATE,
    COL_DISTRICT,
    COL_YEAR,
    COL_SEASON,
    COL_CROP,
    COL_AREA,
    COL_PRODUCTION,
    COL_YIELD,
    BENCHMARK_CROPS,
    TRAIN_MAX_YEAR,
    VAL_MAX_YEAR
)

# Explicit Feature Definitions - Production is STRICTLY EXCLUDED to prevent target leakage
CATEGORICAL_FEATURES = [COL_STATE, COL_DISTRICT, COL_CROP, COL_SEASON]
NUMERICAL_FEATURES = [COL_AREA, COL_YEAR]
FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES



# Per-crop agronomic yield ceilings and floors (Tonnes/Hectare)
# Calibrated against Directorate of Economics & Statistics, Ministry of Agriculture & Farmers Welfare, and ICAR
CROP_YIELD_CEILINGS = {
    "Rice":           8.0,   # High-yielding Punjab irrigated max ~6-7 t/ha
    "Wheat":          7.5,   # High-yielding Punjab/Haryana max ~6.0-6.5 t/ha
    "Maize":          8.0,   # High-yielding Karnataka/Bihar hybrid max ~7-8 t/ha
    "Sugarcane":    130.0,   # High-yielding Maharashtra irrigated max ~110-130 t/ha
    "Cotton":         1.5,   # Official India lint max ~0.8-1.2 t/ha (800-1200 kg lint/ha)
    "Potato":        50.0,   # UP/Punjab/Gujarat commercial max ~35-45 t/ha
    "Onion":         40.0,   # Nashik/Maharashtra irrigated max ~30-38 t/ha
    "Soyabean":       3.5,   # MP/Maharashtra black soil max ~2.5-3.0 t/ha
    "Groundnut":      4.5,   # Gujarat/Tamil Nadu max ~3.0-4.0 t/ha
    "Gram":           3.0,   # MP/Rajasthan pulse max ~2.0-2.5 t/ha
    "Bajra":          3.5,   # Rajasthan/Gujarat hybrid max ~2.5-3.0 t/ha
    "Jowar":          3.5,   # Maharashtra/Karnataka max ~2.5-3.0 t/ha
}

CROP_YIELD_FLOORS = {
    "Rice":          0.3,
    "Wheat":         0.3,
    "Maize":         0.3,
    "Sugarcane":    15.0,
    "Cotton":        0.05,
    "Potato":        2.0,
    "Onion":         2.0,
    "Soyabean":      0.2,
    "Groundnut":     0.2,
    "Gram":          0.1,
    "Bajra":         0.1,
    "Jowar":         0.1
}


def load_and_clean_yield_data(file_path=RAW_DATA_PATH) -> pd.DataFrame:
    """
    Loads raw crop production dataset and applies rigorous agronomic cleaning:
    1. Normalizes text formatting (title-case for states, districts, seasons).
    2. Maps crop names (e.g. 'Cotton(lint)' -> 'Cotton').
    3. Converts Cotton production from Bales (170 kg) to Tonnes (1 bale = 0.17 tonnes),
       matching standard Indian agricultural statistics (DES / PIB).
    4. Computes Yield = Production / Area (Tonnes per Hectare).
    5. Applies per-crop agronomic ceilings and floors to eliminate physical recording errors.
    6. Sorts strictly chronologically by Crop_Year.
    """
    df = pd.read_csv(file_path)

    # 1. Clean string categorical columns
    for col in [COL_STATE, COL_DISTRICT, COL_SEASON, COL_CROP]:
        df[col] = df[col].astype(str).str.strip()

    # Standardize casing to match user inputs and UI constants (Title Case)
    df[COL_STATE] = df[COL_STATE].str.title()
    df[COL_DISTRICT] = df[COL_DISTRICT].str.title()
    df[COL_SEASON] = df[COL_SEASON].str.title()

    # Map Cotton(lint) -> Cotton
    df.loc[df[COL_CROP].str.lower() == "cotton(lint)", COL_CROP] = "Cotton"
    df.loc[df[COL_CROP].str.lower() == "cotton", COL_CROP] = "Cotton"

    # 2. Filter valid physical area and non-null, non-negative production
    valid_mask = (df[COL_AREA] > 0) & (df[COL_PRODUCTION].notnull()) & (df[COL_PRODUCTION] >= 0)
    df_clean = df[valid_mask].copy()

    # 3. Filter to benchmark crops
    df_clean = df_clean[df_clean[COL_CROP].isin(BENCHMARK_CROPS)].copy()

    # 4. In the raw DES dataset, Cotton production was recorded in Bales (1 bale = 170 kg = 0.17 tonnes).
    # Convert Cotton production to metric Tonnes so all crops have identical Tonne units.
    cotton_mask = df_clean[COL_CROP] == "Cotton"
    df_clean.loc[cotton_mask, COL_PRODUCTION] = df_clean.loc[cotton_mask, COL_PRODUCTION] * 0.17

    # 5. Compute Yield (Tonnes / Hectare)
    df_clean[COL_YIELD] = df_clean[COL_PRODUCTION] / df_clean[COL_AREA]

    # 6. Apply per-crop agronomic ceilings and floors
    keep_mask = pd.Series(True, index=df_clean.index)
    for crop in BENCHMARK_CROPS:
        if crop in CROP_YIELD_CEILINGS and crop in CROP_YIELD_FLOORS:
            crop_rows = df_clean[COL_CROP] == crop
            out_of_bounds = crop_rows & (
                (df_clean[COL_YIELD] > CROP_YIELD_CEILINGS[crop]) |
                (df_clean[COL_YIELD] < CROP_YIELD_FLOORS[crop])
            )
            keep_mask = keep_mask & ~out_of_bounds
    df_clean = df_clean[keep_mask].copy()

    # 7. Sort strictly chronologically
    df_clean = df_clean.sort_values(by=[COL_YEAR, COL_STATE, COL_CROP]).reset_index(drop=True)

    print(f"[Preprocessing] Raw: {len(df):,} -> Cleaned benchmark records: {len(df_clean):,} "
          f"(removed {len(df) - len(df_clean):,} rows)")
    return df_clean



def prepare_yield_splits(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits the crop yield dataset strictly chronologically based on Crop_Year:
    - Train: Crop_Year <= 2011 (1997-2011)
    - Validation: 2012 <= Crop_Year <= 2013 (2012-2013)
    - Test: Crop_Year >= 2014 (2014-2015)
    """
    train_df = df[df[COL_YEAR] <= TRAIN_MAX_YEAR].copy()
    val_df = df[(df[COL_YEAR] > TRAIN_MAX_YEAR) & (df[COL_YEAR] <= VAL_MAX_YEAR)].copy()
    test_df = df[df[COL_YEAR] > VAL_MAX_YEAR].copy()
    
    return train_df, val_df, test_df


def build_and_fit_preprocessor(
    train_df: pd.DataFrame
) -> ColumnTransformer:
    """
    Builds and fits a ColumnTransformer ONLY on the training partition:
    - StandardScaler on numerical features [Area, Crop_Year]
    - OneHotEncoder on categorical features [State_Name, District_Name, Crop, Season]
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False, min_frequency=10), CATEGORICAL_FEATURES)
        ]
    )
    preprocessor.fit(train_df[FEATURE_COLUMNS])
    return preprocessor


def process_and_save_yield(
    raw_path=RAW_DATA_PATH,
    processed_path=PROCESSED_DATA_PATH
) -> Dict[str, Any]:
    """
    Executes end-to-end yield dataset preprocessing and saves cleaned dataset.
    """
    df_clean = load_and_clean_yield_data(raw_path)
    
    # Save processed dataset
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(processed_path, index=False)
    
    train_df, val_df, test_df = prepare_yield_splits(df_clean)
    preprocessor = build_and_fit_preprocessor(train_df)
    
    metadata = {
        "raw_total_records": 246091,
        "cleaned_benchmark_records": len(df_clean),
        "benchmark_crops": BENCHMARK_CROPS,
        "features_used": FEATURE_COLUMNS,
        "leakage_check_production_excluded": True,
        "train_records": len(train_df),
        "val_records": len(val_df),
        "test_records": len(test_df),
        "year_splits": {
            "train_years": f"<= {TRAIN_MAX_YEAR} (1997-{TRAIN_MAX_YEAR})",
            "val_years": f"{TRAIN_MAX_YEAR + 1} - {VAL_MAX_YEAR}",
            "test_years": f">= {VAL_MAX_YEAR + 1} (2014-2015)"
        },
        "encoded_feature_dimensions": int(preprocessor.transform(train_df[FEATURE_COLUMNS][:5]).shape[1]),
        "processed_file": str(processed_path)
    }
    
    print(f"Crop Yield preprocessing complete: {len(df_clean):,} cleaned benchmark records.")
    print(f"Partitions (Chronological) -> Train: {len(train_df):,}, Val: {len(val_df):,}, Test: {len(test_df):,}")
    print(f"Features Encoded: {metadata['encoded_feature_dimensions']} columns (Production strictly excluded).")
    print(f"Processed dataset saved to: {processed_path.name}")
    return metadata


if __name__ == "__main__":
    process_and_save_yield()
