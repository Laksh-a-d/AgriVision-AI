# AgriPulse: Master Machine Learning & AI System Overview

**Project**: AgriPulse — Precision Agriculture Using Deep Learning  
**Working Root**: `D:\FINAL FINAL YEAR PROJECT`  

---

## AI Subsystem Status Dashboard

| Module | Model Family | Task | Current Status | Validation Status | Production Artifact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Crop Recommendation** | **LSTM Neural Network** | Multiclass Classification & Top-5 Ranking | **IMPLEMENTED (COMPLETE)** | 98.48% Test Accuracy, 100% Top-5 Acc | `crop_recommendation_lstm.keras` |
| **2. Crop Price Forecasting** | LSTM / BiLSTM | Daily & Multi-Step Spot Price Forecasting | **NOT IMPLEMENTED** (Dataset Ready) | Dataset Cleaned & Resampled (Level 2) | Pending Level 3/4 |
| **3. Crop Yield Forecasting** | Deep Regressor / Random Forest | Regional Acreage & Yield (Tonnes/ha) Estimation | **NOT IMPLEMENTED** (Dataset Ready) | Dataset Cleaned & Resampled (Level 2) | Pending Level 3/4 |

---

## 1. Crop Recommendation AI Module (Implemented)

- **Dataset**: `ml/crop_recommendation/data/raw/crop_recommendation.csv` ($2,200$ samples, 22 balanced classes)
- **Features**: `N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`
- **Architecture**: LSTM Neural Network (`Input(7, 1)` $\rightarrow$ `LSTM(64)` $\rightarrow$ `Dense(64)` $\rightarrow$ `Softmax(22)`)
- **Performance**:
  - Test Accuracy: **$98.48\%$**
  - Top-3 Accuracy: **$100.00\%$**
  - Top-5 Accuracy: **$100.00\%$**
- **Inference Module**: `ml/crop_recommendation/model/predict.py`
- **Documentation**:
  - [Model Card](file:///D:/FINAL%20FINAL%20YEAR%20PROJECT/docs/ml/CROP_RECOMMENDATION_MODEL.md)
  - [Experiment Log](file:///D:/FINAL%20FINAL%20YEAR%20PROJECT/docs/ml/CROP_RECOMMENDATION_EXPERIMENTS.md)

---

## 2. Crop Price Forecasting AI Module (Upcoming)

- **Dataset**: `ml/price_forecasting/data/raw/agmarknet_commodity_prices.csv` ($20,500$ Agmarknet mandi records)
- **Scope**: Multi-year wholesale spot prices across 78 commodities and 22 mandis.
- **Preprocessing Status**: Completed (30-day sliding window sequences generated, strictly chronological).
- **Target Models**: LSTM / GRU / Bidirectional LSTM.

---

## 3. Crop Yield Forecasting AI Module (Upcoming)

- **Dataset**: `ml/yield_forecasting/data/raw/crop_production.csv` ($242,361$ cleaned historical district-level records)
- **Scope**: Production volume and acreage from 1997 to 2015 across 33 Indian states.
- **Preprocessing Status**: Completed (Yield computed in Tonnes/Hectare, chronological threshold split).
- **Target Models**: Deep Neural Regressor / Gradient Boosted Trees.
