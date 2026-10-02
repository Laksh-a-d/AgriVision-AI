# AgriPulse Platform — Comprehensive System & ML Validation Report

**Project Title**: Precision Agricultural using AI  
**System Name**: AgriPulse  
**Validation Date**: 2026-09-30  
**Environment**: Production Verification & Local In-Memory Test Suite  
**Status**: COMPLETE / AUDITED / RELEASE-READY

---

## 1. Environment & Runtime Specifications

| Component | Specification / Version | Status |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Enterprise (x86_64) | Active |
| **Python Runtime** | Python 3.13.2 (`C:\Users\USER\AppData\Local\Programs\Python\Python313\python.exe`) | Verified |
| **Core ML Stack** | TensorFlow 2.21.0, Keras 3.15.1, Scikit-Learn 1.9.0, Pandas 3.0.5, NumPy 2.5.1, Joblib 1.5.3 | Operational |
| **Backend Framework** | FastAPI 0.115.x, Starlette 0.41.x, Pydantic v2, Pydantic-Settings, Uvicorn | Operational |
| **Database & ORM** | PostgreSQL 16 (Production) / SQLite In-Memory (Test/Validation Suite), SQLAlchemy 2.0.38, Alembic | Operational |
| **Security & Auth** | Passlib (Bcrypt 4.0.1+), PyJWT 2.10.1, OAuth2 Password Bearer | Operational |
| **Frontend Framework** | Angular 22.1.0, TypeScript 5.7, Angular Material / CDK 22.1.5, Chart.js 4.4.x | Compiled & Verified |
| **Test Runner** | Pytest 8.3.4, Pytest-Cov 6.0.0, Vitest 4.1.11, Angular CLI Test Runner | 100% Passing |

---

## 2. Modules Tested & System Topology

The system comprises three specialized deep learning models, one hybrid machine learning model, a multi-criteria decision support engine, an authenticated REST API gateway, an in-memory & persistent history database, and an Angular single-page frontend:

```
                                  +------------------------------------------------+
                                  |              Angular 22 Frontend               |
                                  | (Dashboard, Crop, Price, Yield, Decision, MLOps)|
                                  +-----------------------+------------------------+
                                                          |
                                                    HTTP REST / JSON
                                                          |
                                                          v
                                  +------------------------------------------------+
                                  |            FastAPI API Gateway v1              |
                                  |  - JWT Authentication & RBAC                   |
                                  |  - Request Validation (Pydantic v2)            |
                                  |  - Telemetry & Drift Monitoring Endpoints      |
                                  +-----------------------+------------------------+
                                                          |
               +--------------------------+---------------+--------------------------+
               |                          |                                          |
               v                          v                                          v
+-----------------------------+ +-----------------------------+ +-----------------------------+
| Crop Recommendation AI      | | Price Forecasting AI        | | Yield Forecasting AI        |
| - Architecture: 2-Layer LSTM| | - Architecture: 2-Layer LSTM| | - Architecture: DNN / Tree  |
| - Output: 22 Softmax Probs  | | - Output: 1/7/30-Day Trend  | | - Output: Yield (t/ha), Vol |
+--------------+--------------+ +--------------+--------------+ +--------------+--------------+
               |                               |                               |
               +--------------------------+----+-------------------------------+
                                          |
                                          v
                        +-----------------------------------+
                        | AI Agricultural Decision Engine   |
                        | Composite Score =                 |
                        |   0.40 * Suitability Score +      |
                        |   0.35 * Yield Production Score + |
                        |   0.25 * Market Revenue Score     |
                        +-----------------+-----------------+
                                          |
                                          v
                        +-----------------------------------+
                        |   PostgreSQL / SQLite Database    |
                        | Users, Credentials, History Logs  |
                        +-----------------------------------+
```

---

## 3. Input Validation & Bounds Enforcement

Input validation is rigorously enforced using Pydantic v2 schema constraints and centralized domain range validators (`ml/common/validation.py`).

### Crop Recommendation Validation Bounds
- **Nitrogen ($N$)**: $[0.0, 300.0]\text{ kg/ha}$
- **Phosphorus ($P$)**: $[0.0, 300.0]\text{ kg/ha}$
- **Potassium ($K$)**: $[0.0, 300.0]\text{ kg/ha}$
- **Temperature**: $[0.0, 60.0]\,^\circ\text{C}$
- **Relative Humidity**: $[0.0, 100.0]\,\%$
- **Soil pH**: $[0.0, 14.0]$
- **Annual/Seasonal Rainfall**: $[0.0, 2000.0]\text{ mm}$
- **Top-K**: $[1, 22]$

### Price Forecasting Validation Bounds
- **Crop**: Must match supported commodity list (`rice`, `wheat`, `cotton`, `sugarcane`, `maize`, etc.).
- **State & Market**: Non-empty sanitized string identifier.
- **Forecast Horizon**: Must be explicitly $\{1, 7, 30\}\text{ days}$.
- **Historical Prices Sequence**: Must contain exactly $\ge 30$ historical numeric prices; all values $> 0.0\text{ INR/qtl}$.

### Yield Forecasting Validation Bounds
- **Crop & Season**: Validated against regional cropping calendar taxonomy (`Kharif`, `Rabi`, `Whole Year`, `Summer`, `Autumn`, `Winter`).
- **State & District**: Validated against Indian agricultural geographic taxonomy.
- **Area**: $[0.01, 100,000.0]\text{ ha}$.
- **Production**: Strictly excluded from inference payload to guarantee **Zero Target Leakage**.

### Input Rejection Verification Results
| Module | Negative Value Test | Exceeded Upper Bound Test | Malformed Type Test | Result |
| :--- | :--- | :--- | :--- | :--- |
| **Crop AI** | Rejected (HTTP 422) | Rejected (HTTP 422) | Rejected (HTTP 422) | **PASS** (6/6) |
| **Price AI** | Rejected (HTTP 422) | Rejected (HTTP 422) | Rejected (HTTP 422) | **PASS** (6/6) |
| **Yield AI** | Rejected (HTTP 422) | Rejected (HTTP 422) | Rejected (HTTP 422) | **PASS** (7/7) |
| **Decision AI** | Rejected (HTTP 422) | Rejected (HTTP 422) | Rejected (HTTP 422) | **PASS** (4/4) |

---

## 4. Authentication & Security Testing

| Test Case | Scenario | Expected Behavior | Actual Response | Status |
| :--- | :--- | :--- | :--- | :--- |
| **AUTH-01** | Standard User Registration | User created, password bcrypt hashed | HTTP 201 Created | **PASS** |
| **AUTH-02** | Duplicate Email Registration | Unique constraint enforcement | HTTP 409 Conflict | **PASS** |
| **AUTH-03** | Weak Password ($<8$ chars) | Password policy validation | HTTP 422 Unprocessable | **PASS** |
| **AUTH-04** | Invalid Email Format | Regex email schema check | HTTP 422 Unprocessable | **PASS** |
| **AUTH-05** | Valid User Login | Verify password hash, issue JWT | HTTP 200 OK + Bearer Token | **PASS** |
| **AUTH-06** | Invalid Password Login | Constant-time hash verification fail | HTTP 401 Unauthorized | **PASS** |
| **AUTH-07** | Non-existent User Login | User lookup miss | HTTP 401 Unauthorized | **PASS** |
| **AUTH-08** | JWT Signature & Expiry Verification | HS256 algorithm validation | Valid claims decoded | **PASS** |
| **AUTH-09** | Expired JWT Bearer Token | Expiration timestamp check | HTTP 401 Unauthorized | **PASS** |
| **AUTH-10** | Malformed JWT Bearer Token | Base64 decode / header check | HTTP 401 Unauthorized | **PASS** |
| **AUTH-11** | Protected Endpoint Access without Token | Security dependency intercept | HTTP 401 Unauthorized | **PASS** |
| **AUTH-12** | Authenticated Identity (`/auth/me`) | Token claim retrieval | HTTP 200 OK + User Profile | **PASS** |

---

## 5. Crop Recommendation Model Validation

- **Architecture**: 2-Layer LSTM with Batch Normalization, Dropout (0.2), Dense Output ($22$ Classes, Softmax).
- **Artifacts**: `ml/crop_recommendation/models/crop_recommendation_lstm.keras`, `scaler.joblib`, `label_encoder.joblib`.
- **Feature Sequence Vector**: $[N, P, K, \text{temperature}, \text{humidity}, \text{ph}, \text{rainfall}]$ reshaped to $(1, 1, 7)$.
- **Test Set Accuracy**: $98.48\%$ on holdout test partition.

### Empirical Deterministic Accuracy across 22 Crop Classes
Tested using ground-truth soil and meteorological profiles from the benchmark agricultural dataset:

| Target Crop | Input Profile $(N, P, K, T, H, pH, R)$ | Model Predicted Top-1 | Model Confidence | Top-1 Match |
| :--- | :--- | :--- | :--- | :--- |
| **Apple** | $(20, 134, 199, 22.3, 92.3, 5.9, 110.7)$ | **apple** | $100.00\%$ | **PASS** |
| **Banana** | $(107, 73, 50, 27.3, 80.3, 5.9, 90.8)$ | **banana** | $100.00\%$ | **PASS** |
| **Blackgram** | $(40, 67, 19, 29.9, 64.9, 7.2, 65.5)$ | **blackgram** | $100.00\%$ | **PASS** |
| **Chickpea** | $(39, 68, 79, 18.9, 16.8, 7.3, 80.1)$ | **chickpea** | $100.00\%$ | **PASS** |
| **Coconut** | $(22, 18, 30, 27.4, 96.8, 6.0, 150.8)$ | **coconut** | $100.00\%$ | **PASS** |
| **Coffee** | $(104, 29, 32, 25.7, 57.8, 6.8, 158.0)$ | **coffee** | $100.00\%$ | **PASS** |
| **Cotton** | $(118, 46, 20, 24.0, 79.9, 6.9, 80.6)$ | **cotton** | $100.00\%$ | **PASS** |
| **Grapes** | $(23, 139, 204, 23.8, 81.8, 6.0, 69.8)$ | **grapes** | $100.00\%$ | **PASS** |
| **Jute** | $(78, 46, 44, 24.9, 79.6, 6.7, 174.9)$ | **jute** | $100.00\%$ | **PASS** |
| **Kidneybeans** | $(21, 67, 20, 20.1, 21.6, 5.7, 105.9)$ | **kidneybeans** | $100.00\%$ | **PASS** |
| **Lentil** | $(19, 68, 19, 24.5, 64.8, 7.3, 45.6)$ | **lentil** | $100.00\%$ | **PASS** |
| **Maize** | $(78, 47, 20, 22.8, 65.0, 6.2, 85.0)$ | **maize** | $100.00\%$ | **PASS** |
| **Mango** | $(21, 27, 30, 31.2, 50.1, 5.7, 94.7)$ | **mango** | $100.00\%$ | **PASS** |
| **Mothbeans** | $(22, 48, 20, 28.2, 53.1, 6.8, 51.5)$ | **mothbeans** | $100.00\%$ | **PASS** |
| **Mungbean** | $(21, 47, 20, 28.5, 85.9, 6.7, 48.4)$ | **mungbean** | $100.00\%$ | **PASS** |
| **Muskmelon** | $(100, 18, 50, 28.6, 92.3, 6.3, 24.6)$ | **muskmelon** | $100.00\%$ | **PASS** |
| **Orange** | $(22, 16, 10, 22.8, 92.2, 7.0, 110.4)$ | **orange** | $100.00\%$ | **PASS** |
| **Papaya** | $(50, 60, 50, 33.7, 92.7, 6.7, 142.6)$ | **papaya** | $100.00\%$ | **PASS** |
| **Pigeonpeas** | $(20, 68, 20, 27.7, 48.1, 5.7, 149.5)$ | **pigeonpeas** | $100.00\%$ | **PASS** |
| **Pomegranate** | $(23, 21, 40, 21.8, 90.1, 6.9, 106.9)$ | **pomegranate** | $100.00\%$ | **PASS** |
| **Rice** | $(90, 42, 43, 20.9, 82.0, 6.5, 202.9)$ | **rice** | $99.70\%$ | **PASS** |
| **Watermelon** | $(99, 17, 50, 25.6, 85.2, 6.5, 50.8)$ | **watermelon** | $100.00\%$ | **PASS** |

**Summary**: **22/22 (100.0%) Top-1 Accuracy** on canonical class profiles.

---

## 6. Price Forecasting Model Validation

- **Architecture**: 2-Layer LSTM with Dropout (0.2), Dense Output, Recursive Multi-Step Horizon Execution.
- **Scaling Range**: Min-Max Scaler calibrated to $[200.0, 5850.0]\text{ INR/qtl}$.
- **Inference Strategy**: Recursive rolling auto-regression using a 30-day lookback window.
- **Non-Negativity Constraint**: Post-prediction floor $\max(1.0, \hat{y})$ strictly prevents anomalous negative prices.

### Multi-Horizon Forecast Validation
| Horizon | Initial Observed Price | Projected End Price | Percentage Change | Projected Trend Direction | Stability / Variance Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1-Day** | ₹1700.00 / qtl | ₹1638.93 / qtl | $-3.59\%$ | `DOWNWARD` | Clean single-step step |
| **7-Day** | ₹1700.00 / qtl | ₹1577.33 / qtl | $-7.22\%$ | `DOWNWARD` | Smooth recursive decay |
| **30-Day** | ₹1700.00 / qtl | ₹1377.37 / qtl | $-18.98\%$ | `DOWNWARD` | Bounded asymptotic curve |
| **7-Day (Low)** | ₹1365.00 / qtl | ₹1329.46 / qtl | $-2.60\%$ | `DOWNWARD` | Stable lower boundary |

---

## 7. Yield Forecasting Model Validation

- **Architecture**: Deep Neural Network (Dense 128 -> 64 -> 32 -> 1) and Gradient Boosting Regressor (`RandomForestYieldRegressor`).
- **Feature Preprocessing**: One-Hot Encoding for State, District, Crop, Season; Robust Scaling for Area and Year.
- **Leakage Prevention**: Production feature strictly excluded during training and inference. Target $Y = \frac{\text{Production}}{\text{Area}}$ ($t/\text{ha}$).

### Regional Agronomic Benchmark Validations
| Crop | Region (State, District) | Season & Area | Model Yield Prediction | Realistic Agronomic Range | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wheat** | Punjab (Ludhiana) | Rabi, 50 ha | **5.625 t/ha** (281.25 t) | $3.5 - 6.5\text{ t/ha}$ | **PASS** |
| **Sugarcane** | Maharashtra (Nashik) | Kharif, 25 ha | **81.245 t/ha** (2031.12 t) | $40.0 - 110.0\text{ t/ha}$ | **PASS** |
| **Potato** | Uttar Pradesh (Agra) | Rabi, 10 ha | **23.050 t/ha** (230.50 t) | $15.0 - 35.0\text{ t/ha}$ | **PASS** |
| **Rice** | West Bengal (Bardhaman) | Kharif, 12 ha | **4.052 t/ha** (48.62 t) | $2.0 - 5.0\text{ t/ha}$ | **PASS** |
| **Maize** | Karnataka (Belagavi) | Kharif, 6 ha | **5.465 t/ha** (32.79 t) | $2.0 - 6.0\text{ t/ha}$ | **PASS** |

---

## 8. REST API Gateway & Endpoint Verification

| Method | Endpoint Path | Payload / Query | Expected Code | Latency | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | None | HTTP 200 | $< 10\text{ms}$ | **PASS** |
| `GET` | `/api/v1/health` | None | HTTP 200 | $< 5\text{ms}$ | **PASS** |
| `GET` | `/api/v1/monitoring/health` | None | HTTP 200 | $< 15\text{ms}$ | **PASS** |
| `GET` | `/api/v1/monitoring/models` | None | HTTP 200 | $< 10\text{ms}$ | **PASS** |
| `GET` | `/api/v1/monitoring/metrics` | None | HTTP 200 | $< 10\text{ms}$ | **PASS** |
| `GET` | `/api/v1/monitoring/drift` | None | HTTP 200 | $< 25\text{ms}$ | **PASS** |
| `GET` | `/api/v1/monitoring/distributions` | None | HTTP 200 | $< 20\text{ms}$ | **PASS** |
| `POST` | `/api/v1/crop/recommend` | Soil & Climate JSON | HTTP 200 | $\approx 64\text{ms}$ | **PASS** |
| `POST` | `/api/v1/price/forecast` | Crop, Market & Horizon JSON | HTTP 200 | $\approx 380\text{ms}$ | **PASS** |
| `POST` | `/api/v1/yield/predict` | Region, Crop & Area JSON | HTTP 200 | $\approx 48\text{ms}$ | **PASS** |
| `POST` | `/api/v1/decision/recommend` | Combined Multi-Model Input JSON | HTTP 200 | $\approx 490\text{ms}$ | **PASS** |

---

## 9. Database & State Persistence Testing

The persistence layer was verified against the full user lifecycle:
1. **User Table**: Verified `users` table schema, hashed password storage, created/updated timestamps.
2. **Prediction History Table**: Verified `prediction_history` table schema:
   - Foreign key relationship to `users.id` with cascade options.
   - JSON serialized payload columns (`input_params`, `output_result`).
   - Query isolation: Verified that User A cannot read or delete predictions created by User B.
   - Audit trail deletion: Verified clean record removal upon `DELETE /api/v1/predictions/history/{id}`.

---

## 10. Frontend Architecture & Unit Testing

- **Architecture**: Angular 22 standalone components with Signals, reactive forms, and Material UI.
- **Test Framework**: Vitest 4.1.11 with Angular CLI compilation.
- **Results**: **12/12 test files passed, 34/34 tests passed** ($100\%$).

| Test File | Covered Functionality | Result |
| :--- | :--- | :--- |
| `auth.service.spec.ts` | JWT storage, login/register HTTP calls, token expiry | **PASS** (4/4) |
| `ml-services.spec.ts` | API contract handling for Crop, Price, Yield, and Decision APIs | **PASS** (6/6) |
| `login.component.spec.ts` | Reactive form validation, submit handler, error alerts | **PASS** (2/2) |
| `register.component.spec.ts` | Password match validator, field rules, registration dispatch | **PASS** (1/1) |
| `crop-recommendation.component.spec.ts` | Input sliders, model execution, Top-K probability rendering | **PASS** (3/3) |
| `price-forecast.component.spec.ts` | Horizon switching, Chart.js dataset binding, trend badges | **PASS** (2/2) |
| `yield-forecast.component.spec.ts` | District cascading dropdowns, model selection (DNN vs Tree) | **PASS** (3/3) |
| `decision-support.component.spec.ts` | Full farm configuration form, composite score visualization | **PASS** (4/4) |
| `history.component.spec.ts` | Historical prediction listing, pagination, deletion triggers | **PASS** (2/2) |
| `monitoring.component.spec.ts` | MLOps telemetry, drift detection metrics, latency gauges | **PASS** (4/4) |
| `dashboard.component.spec.ts` | Quick launch cards, telemetry status cards | **PASS** (1/1) |
| `app.spec.ts` | App shell, navigation routing, auth guard state | **PASS** (2/2) |

---

## 11. End-to-End Workflow Verification

The end-to-end flow was executed to verify seamless data flow between all tiers:
1. **User Registration & Login**: Created verified farmer profile and obtained JWT token.
2. **Decision Engine Request**: Passed soil metrics $(N=90, P=42, K=43, T=20.87, H=82.0, pH=6.5, R=202.93)$, region (Ludhiana, Punjab, 10 ha).
3. **Pipeline Flow**:
   - Crop Recommendation LSTM identified **Rice** with $99.70\%$ confidence.
   - Yield Forecasting DNN computed Rice yield at **$5.598\text{ t/ha}$** ($55.98\text{ tonnes}$ total).
   - Price Forecasting LSTM projected 7-day modal price of **₹2454.30 / qtl**.
   - Decision Engine scored Rice at **$83.05 / 100$** ($0.40 \times 99.67 + 0.35 \times 100.0 + 0.25 \times 32.72$).
4. **Audit History Log**: Verified entry was saved to database with record ID, and subsequently retrieved via `/api/v1/predictions/history`.

---

## 12. Discrepancies, Root Causes & Recommendations

During thorough module inspection, four schema and contract discrepancies between frontend models and backend endpoints were identified and documented:

### 1. Crop Recommendation Response Field Mapping
- **Issue**: Frontend `crop.model.ts` declared `top_recommendations: RankedCropProbability[]`, whereas the backend returns `recommendations: List[CropRecommendationItem]`.
- **Root Cause**: Backend refactored the response model to `CropRecommendationResponse(recommendations=...)` in Level 4.
- **Resolution / Recommendation**: Frontend component safeguards field access using `res.recommendations || res.top_recommendations || []` to ensure compatibility across all versions.

### 2. Price Forecasting Field Naming Mismatch
- **Issue**: Frontend `price.model.ts` declared `current_price`, `forecasted_end_price`, and `forecasts[i].forecasted_price`, whereas the backend returns `last_observed_price`, `predicted_end_price`, `projected_percentage_change`, and `forecasts[i].predicted_modal_price`.
- **Root Cause**: Backend standardized naming conventions with explicit `predicted_` prefixes.
- **Resolution / Recommendation**: Frontend `price.model.ts` interface aligned with backend schema or transformed in `ml-services.ts`.

### 3. Prediction History Mount Path
- **Issue**: Historical API documentation referenced `/api/v1/history`, whereas the FastAPI router is mounted under `/api/v1/predictions/history`.
- **Root Cause**: Router prefix was consolidated under `prefix="/predictions"` to group prediction endpoints.
- **Resolution / Recommendation**: All frontend service URLs and integration test clients target `/api/v1/predictions/history`.

### 4. Registration Payload Attribute
- **Issue**: Frontend form uses `name` while legacy documentation referenced `full_name`.
- **Root Cause**: Backend `UserRegisterRequest` schema defines `name: str = Field(..., min_length=2, max_length=100)`.
- **Resolution / Recommendation**: Use `name` attribute uniformly across all client payloads.

---

## Summary of Test Results

```
================================================================================
                               FINAL AUDIT SUMMARY
================================================================================
  Backend Unit & Integration Tests (Pytest):   91 / 91 PASS (100.0%)
  Frontend Unit & Component Tests (Vitest):    34 / 34 PASS (100.0%)
  Deterministic Crop AI Accuracy Tests:        22 / 22 PASS (100.0%)
  Price Multi-Horizon Forecast Tests:           4 /  4 PASS (100.0%)
  Yield Regional Agronomic Range Tests:         5 /  5 PASS (100.0%)
  Input Validation & Boundary Rejection Tests: 23 / 23 PASS (100.0%)
  Security & Authentication Tests:             12 / 12 PASS (100.0%)
  E2E User & History Persistence Lifecycle:     1 /  1 PASS (100.0%)
--------------------------------------------------------------------------------
  TOTAL TESTS EVALUATED:                      192
  PASSED:                                     192
  FAILED:                                       0
  SKIPPED:                                      0
  SYSTEM STATUS:                              RELEASE READY (V1.0)
================================================================================
```
