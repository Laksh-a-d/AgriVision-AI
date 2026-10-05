# Crop Recommendation Dataset — ICAR & IMD Aligned Agronomic Benchmark

## 1. Overview
- **Dataset Name**: Indian Precision Agriculture Crop Recommendation Dataset (ICAR & IMD Aligned)
- **Domain**: Precision Agriculture / Soil & Environmental Agronomy
- **Authoritative Sources**:
  1. **ICAR (Indian Council of Agricultural Research)**: Handbook of Agriculture (6th Edition) & Crop Production Guidelines.
  2. **TNAU (Tamil Nadu Agricultural University) Agritech Portal**: Crop Production Guides (Cereals, Pulses, Oilseeds, Commercial, and Horticulture Crops).
  3. **ICAR-CRIDA (Central Research Institute for Dryland Agriculture)**: Climate & Soil Biophysical Requirements of Rainfed Crops.
  4. **IMD (India Meteorological Department)**: Long Period Average (LPA) Annual Rainfall Norms (1971–2020).
- **Date Updated**: 2026-10-05
- **License**: Open Access / Public Educational & Academic Research

## 2. Dataset Schema
- **Total Records**: 3,600 observations (120 observations per class)
- **Total Features**: 7 numerical input features + 1 categorical target label
- **Input Features**:
  1. `N` (Float, kg/ha): Available soil Nitrogen content (0 – 200 kg/ha)
  2. `P` (Float, kg/ha): Available soil Phosphorus ($P_2O_5$) content (0 – 200 kg/ha)
  3. `K` (Float, kg/ha): Available soil Potassium ($K_2O$) content (0 – 250 kg/ha)
  4. `temperature` (Float, °C): Ambient mean temperature during cultivation period (8.0 – 45.0 °C)
  5. `humidity` (Float, %): Relative atmospheric humidity (15.0 – 95.0 %)
  6. `ph` (Float): Soil reaction index (pH: 4.5 – 9.0)
  7. `rainfall` (Float, mm): **Annual / Full Crop-Cycle Cumulative Precipitation** (250 – 3,500 mm).
     *Note: Rainfall is strictly aligned with IMD Normal Annual Rainfall definitions to ensure 100% parity between training distributions and live weather/inference services.*
- **Target Classes (30 Crop Species)**:
  - **Cereals & Millets**: `rice`, `wheat`, `maize`, `sorghum`, `pearl_millet`
  - **Pulses**: `chickpea`, `pigeonpeas`, `mungbean`, `blackgram`, `lentil`, `kidneybeans`, `mothbeans`
  - **Oilseeds & Cash Crops**: `soybean`, `cotton`, `groundnut`, `mustard`, `sunflower`, `sugarcane`, `jute`, `coffee`
  - **Horticultural & Commercial Fruits**: `banana`, `mango`, `grapes`, `apple`, `orange`, `papaya`, `coconut`, `pomegranate`, `watermelon`, `muskmelon`

## 3. Directory Layout
- `raw/crop_recommendation.csv`: Master raw dataset (3,600 rows $\times$ 8 columns).
- `processed/crop_recommendation_processed.csv`: Validated and preprocessed dataset with encoded integer labels.

## 4. Quality & Statistical Integrity
- **Duplicate Records**: 0 exact duplicates.
- **Class Balance**: Perfectly balanced across 30 crops (120 samples each = 3.33% per class).
- **Missing / NaN Values**: 0 missing values.
- **Distribution Integrity**: Truncated Gaussian sampling bounded strictly within verified ICAR agronomic thresholds.

## 5. Scientific Limitations & Academic Scope
- **Domain-Synthesized Benchmark**: The 3,600-record dataset is domain-synthesized.
- **Benchmark Evaluation**: 81.85% Top-1 and 99.63% Top-5 are benchmark results, NOT real-world field accuracy.
- **Tabular Sequence Representation**: The BiLSTM processes seven ordered tabular agronomic features, not a true chronological time series.
- **Perennial Scope**: Perennial crop suitability is only macro-climatic/biophysical screening and requires additional field validation.
- **Academic Statement**: Subsystem 3A is technically validated against its domain-synthesized benchmark dataset and supported by rule-based agronomic evidence. Real-world field validation remains future work.
