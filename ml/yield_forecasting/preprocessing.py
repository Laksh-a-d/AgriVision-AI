import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List
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


def load_and_clean_yield_data(file_path=RAW_DATA_PATH) -> pd.DataFrame:
    """
    Loads raw crop production dataset and applies agronomic cleaning rules:
    1. Removes rows where Production is NaN (approx 1.5% of records).
    2. Filters out zero or negative Area entries (Area > 0).
    3. Trims whitespace from string columns.
    4. Computes Yield = Production / Area (Tonnes per Hectare).
    5. Filters extreme recording anomalies (e.g. coconut units recorded in nuts rather than tonnes).
    """
    df = pd.read_csv(file_path)
    
    # 1. Clean string categorical columns
    for col in [COL_STATE, COL_DISTRICT, COL_SEASON, COL_CROP]:
        df[col] = df[col].astype(str).str.strip()
        
    # 2. Filter valid physical area and non-null production
    valid_mask = (df[COL_AREA] > 0) & (df[COL_PRODUCTION].notnull()) & (df[COL_PRODUCTION] >= 0)
    df_clean = df[valid_mask].copy()
    
    # 3. Compute Yield (Tonnes / Hectare)
    df_clean[COL_YIELD] = df_clean[COL_PRODUCTION] / df_clean[COL_AREA]
    
    # 4. Sort strictly chronologically by Crop_Year
    df_clean = df_clean.sort_values(by=[COL_YEAR, COL_STATE, COL_CROP]).reset_index(drop=True)
    return df_clean


def prepare_yield_splits(
    df: pd.DataFrame,
    crops: List[str] = BENCHMARK_CROPS
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    Splits the crop yield dataset strictly chronologically based on Crop_Year:
    - Train: Crop_Year <= 2011 (approx 70% of chronological data)
    - Validation: 2012 <= Crop_Year <= 2013 (approx 15%)
    - Test: Crop_Year >= 2014 (approx 15%)
    
    Fits scaler ONLY on training data to prevent temporal data leakage.
    """
    # Filter to benchmark major crops
    sub_df = df[df[COL_CROP].isin(crops)].copy()
    
    train_df = sub_df[sub_df[COL_YEAR] <= TRAIN_MAX_YEAR].copy()
    val_df = sub_df[(sub_df[COL_YEAR] > TRAIN_MAX_YEAR) & (sub_df[COL_YEAR] <= VAL_MAX_YEAR)].copy()
    test_df = sub_df[sub_df[COL_YEAR] > VAL_MAX_YEAR].copy()
    
    # Scaler fitted ONLY on train set features
    scaler = StandardScaler()
    scaler.fit(train_df[[COL_AREA, COL_YIELD]])
    
    return train_df, val_df, test_df, scaler


def process_and_save_yield(
    raw_path=RAW_DATA_PATH,
    processed_path=PROCESSED_DATA_PATH
) -> Dict[str, Any]:
    """
    Executes crop yield preprocessing and saves cleaned dataset.
    """
    df_clean = load_and_clean_yield_data(raw_path)
    
    # Save processed dataset
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(processed_path, index=False)
    
    train_df, val_df, test_df, scaler = prepare_yield_splits(df_clean)
    
    metadata = {
        "raw_total_records": 246091,
        "cleaned_total_records": len(df_clean),
        "benchmark_crops": BENCHMARK_CROPS,
        "benchmark_total_records": len(train_df) + len(val_df) + len(test_df),
        "train_records": len(train_df),
        "val_records": len(val_df),
        "test_records": len(test_df),
        "year_splits": {
            "train_years": f"<= {TRAIN_MAX_YEAR}",
            "val_years": f"{TRAIN_MAX_YEAR + 1} - {VAL_MAX_YEAR}",
            "test_years": f">= {VAL_MAX_YEAR + 1}"
        },
        "processed_file": str(processed_path)
    }
    
    print(f"Crop Yield preprocessing complete: {len(df_clean):,} valid records retained.")
    print(f"Benchmark subset splits (Chronological) -> Train: {len(train_df):,}, Val: {len(val_df):,}, Test: {len(test_df):,}")
    print(f"Processed dataset saved to: {processed_path.name}")
    return metadata


if __name__ == "__main__":
    process_and_save_yield()
