# AgriPulse: Implementation Plan & Project Roadmap

## Project Overview
- **Project Name**: AgriPulse
- **Project Title**: Precision Agriculture Using Deep Learning
- **Scope**: Fully Software-Only Precision Agriculture System
- **Core Philosophy**: Zero hardware dependencies (no IoT, Arduino, Raspberry Pi, soil sensors, or drones).

---

## Phase-by-Phase Roadmap

```
Level 0: Project Foundation                                [ COMPLETED ]
   │
   ▼
Level 1: Environment & Application Setup                   [ COMPLETED ]
   │
   ▼
Level 2: Dataset Acquisition, Validation & Preprocessing   [ COMPLETED ]
   │
   ▼
Level 3: Deep Learning Model Implementation & Training     [ UPCOMING  ]
   │
   ▼
Level 4: Backend API & Service Layer                       [ UPCOMING  ]
   │
   ▼
Level 5: Frontend Development & Visualization              [ UPCOMING  ]
   │
   ▼
Level 6: Integration, Verification & Deployment            [ UPCOMING  ]
```

---

### Level 0: Foundation & Environment Setup (Completed)
- [x] Create standardized project directory structure.
- [x] Initialize Git version control and setup `.gitignore`.
- [x] Establish `.env.example` security guidelines.
- [x] Create comprehensive documentation framework (`README.md`, `ARCHITECTURE.md`, `PROJECT_PLAN.md`).

---

### Level 1: Environment & Application Setup (Completed)
- [x] Create Python virtual environment (`backend/.venv`) using Python 3.13+.
- [x] Install foundation backend dependencies (`fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `alembic`, `psycopg2-binary`, `python-dotenv`, `pytest`, `httpx`).
- [x] Generate `backend/requirements.txt`.
- [x] Implement FastAPI main app with `/api/health` endpoint and CORS middleware.
- [x] Create Pydantic settings configuration (`backend/app/config/settings.py`).
- [x] Establish SQLAlchemy engine and session dependency (`backend/app/config/database.py`).
- [x] Initialize and configure Alembic migration harness (`backend/alembic/`).
- [x] Create Angular frontend project (`frontend/agripulse-ui`) with structured folders.
- [x] Configure Angular environments (`API_BASE_URL = http://localhost:8000/api`).
- [x] Implement Angular `ApiService` for health checking and dynamic connection status display.
- [x] Verify backend tests (2/2 Pytest passed), Angular build (100% success), and live HTTP/CORS communication.

---

### Level 2: Dataset Acquisition, Validation & Preprocessing (Completed)
- [x] Acquire real, verified public agricultural datasets for all three modules:
  - **Dataset A (Crop Recommendation)**: 2,200 rows, 8 columns, 22 balanced crop classes.
  - **Dataset B (Price Forecasting)**: 20,500 Agmarknet records across 22 mandis, 18-year timeline (2004–2022).
  - **Dataset C (Yield Forecasting)**: 246,091 district-level crop production records from DES India (1997–2015).
- [x] Build reusable validation framework (`ml/common/validation.py`) for missing values, duplicates, datatypes, and range checks.
- [x] Implement portable path management (`ml/common/paths.py`) with zero hardcoded paths.
- [x] Create modular validation scripts (`validate_dataset.py`) for all 3 modules.
- [x] Build leakage-free preprocessing pipelines (`preprocessing.py`) fitting scalers strictly on training partitions and preserving chronological order for time-series.
- [x] Generate EDA visual plots (`ml/*/results/eda/*.png`) for class distributions, feature correlations, price curves, and yield trends.
- [x] Create comprehensive data documentation (`docs/datasets/DATASET_REPORT.md` and dataset `README.md` files).

---

### Level 3: Deep Learning Model Implementation & Training
**Objective**: Develop, train, evaluate, and persist deep learning (LSTM) models for recommendation, price forecasting, and yield estimation.

**Key Deliverables**:
1. **Crop Recommendation LSTM Network**:
   - Multi-class neural network classifier for top-5 ranking and probability outputs.
   - Evaluation metrics: Accuracy, Precision, Recall, F1-Score, Confusion Matrix.
2. **Crop Price Forecasting LSTM Network**:
   - Time-series sliding-window recurrent neural network for multi-day ahead price forecasting.
   - Price trend direction classifier and percentage change calculation.
   - Evaluation metrics: RMSE, MAE, MAPE.
3. **Crop Yield Forecasting Model**:
   - Deep regression model for spatial-temporal yield estimation ($\text{Tonnes/Hectare}$).
   - Evaluation metrics: $R^2$ Score, RMSE, MAE.
4. **Model Serialization & Explainability**:
   - Model artifact serialization (`.keras` format, scaler `.joblib`).
   - SHAP/Feature attribution utilities where appropriate.

---

### Level 4: Backend API & Service Layer (FastAPI)
**Objective**: Build REST API endpoints with Pydantic schemas, dependency injection, and model inference services.

---

### Level 5: Frontend Development & Data Visualization (Angular)
**Objective**: Build interactive UI with Angular Material, Chart.js visualizers, and Farmer/Admin views.

---

### Level 6: Integration, Verification & Deployment
**Objective**: Comprehensive end-to-end testing, Docker containerization, and final user documentation.
