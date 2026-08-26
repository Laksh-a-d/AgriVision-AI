# AgriPulse: Implementation Plan & Project Roadmap

## Project Overview
- **Project Name**: AgriPulse
- **Project Title**: Precision Agriculture Using Deep Learning
- **Scope**: Fully Software-Only Precision Agriculture System
- **Core Philosophy**: Zero hardware dependencies (no IoT, Arduino, Raspberry Pi, soil sensors, or drones).

---

## Phase-by-Phase Roadmap

```
Level 0: Project Foundation                        [ COMPLETED ]
   │
   ▼
Level 1: Environment & Application Setup           [ COMPLETED ]
   │
   ▼
Level 2: Database Schema & Data Modeling           [ UPCOMING  ]
   │
   ▼
Level 3: Machine Learning Pipeline & Training      [ UPCOMING  ]
   │
   ▼
Level 4: Backend API & Service Layer               [ UPCOMING  ]
   │
   ▼
Level 5: Frontend Development & Visualization      [ UPCOMING  ]
   │
   ▼
Level 6: Integration, Verification & Deployment    [ UPCOMING  ]
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
- [x] Create Angular frontend project (`frontend/agripulse-ui`) with structured folders (`core`, `shared`, `features`, `services`, `models`, `guards`, `layout`).
- [x] Configure Angular environments (`API_BASE_URL = http://localhost:8000/api`).
- [x] Implement Angular `ApiService` for health checking and dynamic connection status display (`Backend Connected` / `Backend Offline`).
- [x] Verify backend tests (2/2 Pytest passed), Angular build (100% success), and live HTTP/CORS communication.

---

### Level 2: Database Design & Migration Framework
**Objective**: Build a robust PostgreSQL schema supporting all system entities, relationships, constraints, and audit capabilities.

**Key Deliverables**:
1. **Entity Models**:
   - `users`: User profiles, credentials, role-based identifiers (`FARMER`, `ADMIN`), timestamps.
   - `farms`: Farm location metadata, total acreage, soil characteristics, owner associations.
   - `crop_information`: Master agronomic data, optimal NPK/pH/rainfall boundaries, harvest duration ranges, production cost benchmarks.
   - `market_prices`: Historical and reference commodity spot market prices.
   - `crop_predictions`: Crop recommendation inputs and ranked top-5 output probabilities.
   - `price_forecasts`: Time-series forecasting logs, projected values, trend percentages.
   - `yield_forecasts`: Estimated yield records, acreage context, historical comparison data.
   - `weather_records`: Ingested meteorological history (temperature, humidity, precipitation).
   - `prediction_history`: Unified log connecting users, farm contexts, and recommendation/forecast snapshots.
2. **Migrations & Seeding**:
   - Alembic migration script generation.
   - Initial database baseline migration (`alembic upgrade head`).
   - Seed scripts for crop catalog, harvest days, and initial cost metrics.

---

### Level 3: Machine Learning Pipelines & Deep Learning Models
**Objective**: Develop, preprocess, train, validate, and persist deep learning and time-series models.

**Key Deliverables**:
1. **Module 1: Crop Recommendation (LSTM-based)**:
   - Data preprocessing and feature normalization (N, P, K, Temperature, Humidity, pH, Rainfall).
   - LSTM architecture design for multi-class crop ranking.
   - Top-5 prediction confidence output generator.
   - Evaluation metrics: Accuracy, Precision, Recall, F1-Score, Confusion Matrix.
2. **Module 2: Price Forecasting (Time-Series LSTM)**:
   - Commodity market sequential price dataset formatting.
   - Strict chronological train/validation/test splitting (zero random shuffling).
   - Windowing and sequence generation for multi-day ahead price forecasting.
   - Trend estimation and percentage shift calculation.
   - Evaluation metrics: RMSE, MAE, MAPE.
3. **Module 3: Yield Forecasting (Time-Series Deep Learning)**:
   - Spatial-temporal dataset integration (crop, state, historical acreage, production).
   - Deep learning regressor implementation for yield per hectare.
   - Evaluation metrics: $R^2$ score, RMSE, MAE.
4. **Explainability & Model Artifacts**:
   - Model artifact serialization (`.keras`, scaler `.joblib`).
   - SHAP/Feature attribution utilities where appropriate.

---

### Level 4: Backend API & Service Layer (FastAPI)
**Objective**: Build high-performance REST APIs with strict Pydantic schemas, dependency injection, and business services.

**Key Deliverables**:
1. **Authentication & Authorization (`/api/v1/auth`)**:
   - JWT token generation, verification, password hashing with bcrypt.
   - Role-based route guards (`RoleChecker(["FARMER"])`, `RoleChecker(["ADMIN"])`).
2. **Prediction & Forecast Services (`/api/v1/recommendations`, `/api/v1/forecasts`)**:
   - Inference wrapper services loading serialized Keras models.
   - Integrated business logic:
     - **Revenue Calculation**: $\text{Yield} \times \text{Price}$
     - **Profitability Calculation**: $\text{Revenue} - \text{Production Cost}$
     - **Harvest Cycle Lookup**: Min/Max maturation days and window.
3. **External Weather Gateway (`/api/v1/weather`)**:
   - Asynchronous HTTP client to query external weather APIs.
4. **Farmer & Admin Management APIs (`/api/v1/farmer`, `/api/v1/admin`)**:
   - Farm CRUD, prediction history browsing, statistics aggregations.

---

### Level 5: Frontend Development & Data Visualization (Angular)
**Objective**: Build a responsive Angular Single Page Application (SPA) with Angular Material and Chart.js.

**Key Deliverables**:
1. **Architecture & State Management**:
   - Modular Angular structure: `core/`, `shared/`, `features/farmer/`, `features/admin/`.
   - HTTP interceptors for JWT token injection and error handling.
   - Route guards (`AuthGuard`, `RoleGuard`).
2. **Farmer Portal**:
   - **Interactive Recommendation Form**: N, P, K, pH, rainfall inputs with slider/number controls.
   - **Recommendation Visualizer**: Top-5 probability bar/radar charts.
   - **Price Forecast View**: Time-series line chart with projected trends and percentage change badges.
   - **Yield & Profitability Calculator**: Interactive acreage slider and net return projections.
   - **Weather Widget**: Real-time temperature, humidity, precipitation forecast.
   - **Prediction History**: Filterable, paginated data table.
3. **Admin Portal**:
   - System telemetry, user growth charts, prediction frequency heatmaps.
   - Crop reference management tables.

---

### Level 6: Verification, Integration Testing & Dockerization
**Objective**: Comprehensive testing across all layers and containerized deployment readiness.

**Key Deliverables**:
1. **Automated Testing Suite**:
   - Unit tests for backend services and Pydantic schemas.
   - FastAPI `TestClient` route integration tests.
   - ML model inference sanity checks and boundary value testing.
2. **Containerization**:
   - Multi-stage Dockerfile for Angular frontend (Nginx).
   - Dockerfile for FastAPI backend.
   - Orchestrated `docker-compose.yml` (PostgreSQL, Backend, Frontend).
3. **Project Documentation & User Manual**:
   - Final API OpenAPI documentation.
   - System operational guide.
