# AgriPulse: Precision Agriculture Using Deep Learning

**Project**: AgriPulse  
**Current Version**: `0.1.0`  
**Current Level**: `LEVEL 1 — Environment & Application Setup` (COMPLETED)  

AgriPulse is an intelligent, software-only precision agriculture platform designed to empower farmers and agricultural stakeholders with data-driven decision support. Utilizing deep learning (LSTM architectures), predictive modeling, and real-time data integration, AgriPulse assists in crop selection, market price forecasting, yield estimation, profitability analysis, and weather monitoring without requiring physical IoT or field hardware.

---

## 🚀 Quickstart & Development Instructions

### 1. Prerequisites
- **Python**: Version 3.11+ (Python 3.13+ supported)
- **Node.js**: Version 18+ (v26+ supported) & **npm**
- **Angular CLI**: Version 17+ (v22+ supported)
- **PostgreSQL**: Version 15+ (v17.10 verified and running)

---

### 2. Environment Configuration
AgriPulse uses environment variables for configuration. A template is provided at `.env.example`:

```bash
# In the project root (or backend directory)
cp .env.example .env
```

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://postgres:password@localhost:5432/agripulse_db`)
- `JWT_SECRET`: Secret key for authentication tokens
- `WEATHER_API_KEY`: API key for external weather provider
- `CORS_ORIGINS`: Allowed client origins (default: `http://localhost:4200`)
- `ENVIRONMENT`: `development` or `production`

---

### 3. Backend Setup & Startup

#### A. Virtual Environment Setup
```powershell
# Navigate to backend directory
cd "D:\FINAL FINAL YEAR PROJECT\backend"

# Activate the virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# (If virtual environment needs to be created afresh)
# python -m venv .venv
# .\.venv\Scripts\pip install -r requirements.txt
```

#### B. Starting the FastAPI Backend
```powershell
# Start Uvicorn development server with hot-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

#### C. Running Backend Tests
```powershell
pytest
```

---

### 4. Frontend Setup & Startup

#### A. Frontend Installation
```powershell
# Navigate to Angular project directory
cd "D:\FINAL FINAL YEAR PROJECT\frontend\agripulse-ui"

# Install dependencies (if not already installed)
npm install
```

#### B. Starting the Angular Application
```powershell
# Start Angular development server
npm start
# or: ng serve --open
```
- The application will be accessible at: `http://localhost:4200`
- The landing page connects to `http://localhost:8000/api/health` and reflects live backend connectivity (`Backend Connected` / `Backend Offline`).

---

### 5. PostgreSQL Database Configuration & Migrations

- PostgreSQL service `postgresql-x64-17` is verified running locally.
- Alembic is initialized in `backend/alembic/` and configured to dynamically use `settings.DATABASE_URL` and `app.config.database.Base`.
- Database migrations command:
```powershell
cd "D:\FINAL FINAL YEAR PROJECT\backend"
alembic upgrade head
```

---

## 🏛️ Planned Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│      Angular 17+ | Angular Material | Chart.js / ng2-charts  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / REST / JSON (JWT Auth)
┌──────────────────────────────▼──────────────────────────────┐
│                    Application / API Layer                  │
│             FastAPI | Pydantic | SQLAlchemy 2.0             │
├──────────────────────────────┬──────────────────────────────┤
│       Business Logic         │       Deep Learning Core     │
│  - Auth & Role Guard         │  - Crop Recommendation LSTM  │
│  - Profitability Engine      │  - Price Forecasting LSTM    │
│  - Harvest Cycle Calculator  │  - Yield Forecasting LSTM    │
│  - Weather Integration       │  - Model Explainability/SHAP │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQL / ORM Queries
┌──────────────────────────────▼──────────────────────────────┐
│                      Data Persistence                       │
│               PostgreSQL Database & Alembic                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Domain | Technology | Status |
| :--- | :--- | :--- |
| **Frontend** | Angular 22, TypeScript, RxJS | Scaffolding & Health Client Connected |
| **Backend** | Python 3.13, FastAPI, Uvicorn, Pydantic | Foundation & Health API Operational |
| **Database** | PostgreSQL 17, SQLAlchemy, Alembic | Engine & Migration Harness Ready |
| **Testing** | Pytest, TestClient, Requests | Test Suite Active (2/2 Passed) |
| **Machine Learning** | TensorFlow, Keras, Scikit-learn, LSTM | Architecture planned (Level 2) |

---

## 🗺️ Development Roadmap

- [x] **Level 0 — Project Foundation** *(Completed)*
- [x] **Level 1 — Environment & Application Setup** *(Completed)*
  - FastAPI backend setup with health endpoint (`GET /api/health`).
  - Angular standalone frontend setup with live backend health monitor.
  - PostgreSQL database engine and Alembic migration harness configuration.
  - Pydantic environment settings and automated test suite.
- [ ] **Level 2 — Database Schema & Data Modeling**
- [ ] **Level 3 — Machine Learning Pipeline & Training**
- [ ] **Level 4 — Backend API Development & Business Logic**
- [ ] **Level 5 — Frontend UI & Dashboard Features**
- [ ] **Level 6 — Integration, Verification & Deployment**

---

## 📁 Repository Structure

```
FINAL FINAL YEAR PROJECT/
├── backend/
│   ├── .venv/                      # Python virtual environment
│   ├── alembic/                    # Database migration scripts & env.py
│   ├── alembic.ini                 # Alembic configuration
│   ├── app/
│   │   ├── auth/                   # Security & JWT guards (future)
│   │   ├── config/                 # Settings & Database configuration
│   │   ├── models/                 # SQLAlchemy ORM models (future)
│   │   ├── routes/                 # API route endpoints (future)
│   │   ├── schemas/                # Pydantic schemas (future)
│   │   ├── services/               # Business logic & ML inference (future)
│   │   └── main.py                 # FastAPI application root & /api/health
│   ├── tests/                      # Pytest test suite
│   ├── pytest.ini                  # Pytest configuration
│   └── requirements.txt            # Python dependencies
├── frontend/
│   └── agripulse-ui/               # Angular SPA application
│       ├── src/
│       │   ├── app/
│       │   │   ├── core/           # Core interceptors and guards
│       │   │   ├── features/       # Feature modules (farmer/admin)
│       │   │   ├── guards/         # Auth/Role route guards
│       │   │   ├── layout/         # Header, sidebar, footer components
│       │   │   ├── models/         # TypeScript interfaces (HealthResponse)
│       │   │   ├── services/       # ApiService & state management
│       │   │   └── shared/         # Reusable UI widgets
│       │   └── environments/       # Environment configs (API_BASE_URL)
│       └── package.json            # Frontend dependencies
├── database/                       # Database scripts & seed data
├── docs/                           # Architectural specifications & plans
├── ml/                             # Machine learning models & pipelines
└── tests/                          # Integration test suites
```
