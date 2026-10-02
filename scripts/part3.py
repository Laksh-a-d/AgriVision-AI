# -*- coding: utf-8 -*-
"""
AgriPulse Blue Book Builder - Part 3: Chapter 3 (Requirement Gathering, Analysis and Planning)
"""

CHAPTER_3 = """
---
<div style="page-break-after: always;"></div>

# Chapter 3
# Requirement Gathering, Analysis and Planning

## 3.1 Requirement Specification
The requirements for the AgriPulse platform were gathered through systematic analysis of agricultural extension workflows, farmer decision patterns, and production software standards. Requirements are categorized into Functional Requirements (FR) and Non-Functional Requirements (NFR).

### 3.1.1 Functional Requirements (FR)
*Table 3.1: Functional Requirements Specification (FR-01 to FR-10)*

| Requirement ID | Requirement Name | Description | Priority |
| :--- | :--- | :--- | :---: |
| **FR-01** | User Authentication & Profile Management | The system shall allow users to register with name, unique email, and strong password (Bcrypt hashed), log in to acquire a stateless JWT access token, view their profile, and log out. | High |
| **FR-02** | Soil-Based Crop Recommendation | The system shall accept 7 continuous soil nutrient ($N, P, K, \text{pH}$) and climatic inputs (temperature, humidity, rainfall), validate agronomic boundaries, and return top-$k$ crop recommendations with Softmax probabilities. | High |
| **FR-03** | Time-Series Market Price Forecasting | The system shall accept a commodity name, APMC mandi market, and a 30-day historical daily price sequence, predicting future modal prices across 1, 7, and 30-day horizons with trend direction (`UPWARD`, `DOWNWARD`, `STABLE`). | High |
| **FR-04** | Regional Crop Yield Forecasting | The system shall accept State, District, Crop, Season, Cultivation Area (hectares), and Crop Year, predicting productivity (Tonnes/Hectare) and total estimated harvest tonnage. | High |
| **FR-05** | Multi-Modal Decision Support Synthesis | The system shall orchestrate the Crop, Yield, and Price models, calculate a weighted composite Decision Score ($0\text{--}100$), rank top candidate alternatives, and formulate dynamic 4-pillar explainability text. | High |
| **FR-06** | Prediction History Audit & Tenant Isolation | The system shall automatically persist authenticated prediction records in PostgreSQL with input parameters, output results, and latency metrics, allowing users to view, filter, paginate, and delete their own history. | Medium |
| **FR-07** | MLOps Model Registry Metadata | The system shall provide an endpoint returning versions, training datasets, input features, and verified evaluation metrics ($R^2$, accuracy, RMSE) for all deployed models without path leakage. | Medium |
| **FR-08** | API Performance Telemetry Tracking | The system shall capture in-memory request counts, HTTP status code distributions, success/error rates, and latency metrics (min, mean, max, p50, p95). | Medium |
| **FR-09** | Statistical Covariate Data Drift Monitoring | The system shall evaluate input distributions from recent inference logs against baseline training distributions, computing normalized Z-shift scores and classifying drift health. | Medium |
| **FR-10** | Prediction Output Distribution Analytics | The system shall aggregate prediction outputs across subsystems, summarizing recommended crop frequencies, predicted yield statistics, and price trend percentages. | Low |

### 3.1.2 Non-Functional Requirements (NFR)
*Table 3.2: Non-Functional Requirements Specification (NFR-01 to NFR-08)*

| Requirement ID | Attribute | Specification Metric / Standard |
| :--- | :--- | :--- |
| **NFR-01** | Performance & Latency | Standalone ML inference latency shall not exceed $100\text{ms}$ for Crop Recommendation and Yield Forecasting; multi-model Decision Support shall complete within $< 2.0\text{ seconds}$. |
| **NFR-02** | Reliability & Availability | The system shall maintain $\ge 99.5\%$ operational uptime; preloaded model memory shall ensure zero cold-start model loading failures. |
| **NFR-03** | Security & Data Privacy | Passwords must be hashed using Bcrypt (12 rounds); API communication must enforce Bearer JWT authentication (HS256); SQL queries must be parameterized to eliminate SQL injection. |
| **NFR-04** | Input Validation & Robustness | All API endpoints shall enforce strict Pydantic schema validation, rejecting non-numeric, NaN, Infinite, negative, or physiologically impossible agronomic inputs with structured HTTP 422 errors. |
| **NFR-05** | Scalability & Concurrency | The asynchronous FastAPI ASGI server and connection pool (`pool_size=10, max_overflow=20`) shall sustain $\ge 150\text{ requests/second}$ for telemetry and $> 15\text{ requests/second}$ for neural inference. |
| **NFR-06** | Usability & Responsiveness | The Angular 18+ frontend shall feature a responsive UI accessible on desktop and tablet viewports, rendering interactive Chart.js graphs and real-time form validation indicators. |
| **NFR-07** | Portability & Containerization | The platform shall be packaged into isolated Docker containers orchestrated via Docker Compose, guaranteeing identical execution across development, staging, and production environments. |
| **NFR-08** | Maintainability & Code Quality | The backend shall achieve 100% test pass rates across automated Pytest suites; the frontend shall pass all Vitest component tests; CI/CD shall run automated GitHub Actions on every commit. |

---

## 3.2 Feasibility Study
A four-dimensional feasibility analysis was conducted prior to system development:

### 3.2.1 Technical Feasibility
- **Deep Learning Frameworks**: TensorFlow 2.21, Keras, and Scikit-Learn provide robust, mature APIs for developing Bidirectional LSTMs, recursive time-series models, and dense neural regressors.
- **Backend Architecture**: FastAPI provides high-performance asynchronous Python execution (based on Starlette and Pydantic), allowing seamless integration of TensorFlow C++ runtimes with asynchronous REST route handling.
- **Frontend Framework**: Angular 18+ (upgraded to Angular 22 LTS compatibility) provides enterprise-grade TypeScript architecture, standalone components, and Angular Signals for reactive UI updates without third-party state libraries.
- **Hardware Viability**: Inference runs efficiently on standard x86-64 multi-core CPUs without requiring dedicated high-end GPU hardware in production.
- **Conclusion**: Technically feasible with 100% open-source software libraries.

### 3.2.2 Operational Feasibility
- The user interface is structured with intuitive sliders, regional dropdown selectors (33 States, 646 Districts), preset buttons, and visual charts, enabling farmers, extension officers, and agronomists to operate the system with minimal technical training.
- Dynamic explainability text translates complex neural probability distributions into clear agronomic recommendations.
- **Conclusion**: Operationally feasible with high user accessibility.

### 3.2.3 Economic Feasibility
- **Development & Licensing Cost**: All core frameworks (Python, FastAPI, Angular, PostgreSQL, Docker, Chart.js) are licensed under permissive open-source licenses (MIT, Apache 2.0, BSD), incurring zero commercial software licensing costs.
- **Infrastructure Overhead**: Containerized packaging allows lightweight deployment on low-cost virtual private servers (VPS) or cloud instances (2 vCPUs, 4GB RAM).
- **Return on Investment (ROI)**: Substantial economic value is generated for cultivators by preventing crop loss and optimizing market selling times.
- **Conclusion**: Economically feasible with high cost efficiency.

### 3.2.4 Schedule & Legal Feasibility
- **Schedule**: The project was planned across 9 structured development levels (Level 0 Foundation through Level 8 MLOps & Release), completed within the academic calendar.
- **Legal & Data Governance**: Datasets are derived from public open-government repositories (ICAR, AGMARKNET, DES India) under Open Government Data (OGD) license compliance.
- **Conclusion**: Schedule and legal compliance fully satisfied.

---

## 3.3 Methodology
The development of AgriPulse adhered to a hybrid methodology combining **CRISP-DM (Cross-Industry Standard Process for Data Mining)** for machine learning pipelines with **Agile Scrum** for software engineering.

```mermaid
flowchart TD
    subgraph "CRISP-DM AI Pipeline"
        D1["1. Domain Understanding"] --> D2["2. Data Acquisition & Validation"]
        D2 --> D3["3. Data Preprocessing & Scaling"]
        D3 --> D4["4. Deep Neural Modeling"]
        D4 --> D5["5. Evaluation & Verification"]
        D5 --> D6["6. Model Serialization & Export"]
    end

    subgraph "Agile Scrum Platform Engineering"
        S1["Sprint 1: Architecture & DB Foundation"] --> S2["Sprint 2: Backend REST API & Services"]
        S2 --> S3["Sprint 3: JWT Auth & Prediction History"]
        S3 --> S4["Sprint 4: Angular 18+ SPA Dashboard"]
        S4 --> S5["Sprint 5: Decision Support Synthesis"]
        S5 --> S6["Sprint 6: Docker & MLOps Monitoring"]
    end

    D6 --> S2
```
*Figure 3.1: AgriPulse Engineering Lifecycle (CRISP-DM + Agile Scrum)*

### 3.3.1 Machine Learning Lifecycle (CRISP-DM)
1. **Domain Understanding**: Formulation of agronomic decision parameters, target variables, and performance criteria.
2. **Data Acquisition & Verification**: Extraction and integrity verification of 2,200 ICAR crop records, 15,000+ AGMARKNET mandi records, and 84,183 DES yield records.
3. **Data Preprocessing & Feature Engineering**: Application of StandardScaler, MinMaxScaler, and OneHotEncoder without data leakage across train/validation/test splits.
4. **Model Architecture & Training**: Iterative neural development (LSTM, Bi-LSTM, DNN Regressors) with Adam optimization, early stopping, and learning rate schedules.
5. **Model Evaluation**: Rigorous empirical benchmarking calculating classification accuracy, macro F1-score, $R^2$, RMSE, and MAE.
6. **Model Deployment**: Export of serialized `.keras` weights and `.joblib` preprocessors for backend runtime integration.

### 3.3.2 Software Engineering Lifecycle (Agile Scrum)
Development progressed through two-week sprints:
- **Sprint 1 (Levels 0–1)**: Repository foundation, directory structure, coding standards, and virtual environments.
- **Sprint 2 (Levels 2–3)**: Dataset acquisition, EDA, neural network training, and model serialization.
- **Sprint 3 (Level 4)**: Asynchronous FastAPI backend, route endpoints, Pydantic schemas, and model manager preloading.
- **Sprint 4 (Level 5)**: PostgreSQL relational schemas, Bcrypt hashing, JWT authentication, and prediction audit logging.
- **Sprint 5 (Level 6)**: Angular 18+ standalone SPA, reactive Signals, Chart.js integrations, and auth guards.
- **Sprint 6 (Level 7)**: Multi-modal agricultural decision support engine, scoring synthesizer, and dynamic XAI generator.
- **Sprint 7 (Level 8 & Release)**: MLOps telemetry, Z-shift data drift monitor, model registry, Docker Compose containerization, and GitHub Actions CI/CD automation.

---

## 3.4 Technology Stack
*Table 3.3: Technology Stack Specification & Architectural Roles*

| Technology / Library | Version | Category | Architectural Role in AgriPulse |
| :--- | :---: | :--- | :--- |
| **Python** | 3.11+ | Programming Language | Core backend language, data processing, and ML training runtime. |
| **FastAPI** | 0.141.1 | Backend Framework | Asynchronous ASGI REST API gateway, route orchestration, dependency injection. |
| **Uvicorn** | 0.52.4 | ASGI Web Server | Lightning-fast asynchronous HTTP server handling concurrent requests. |
| **TensorFlow / Keras** | 2.21.0 | Deep Learning Engine | Execution of Bidirectional LSTM, Price LSTM, and Yield DNN neural graphs. |
| **Scikit-Learn** | 1.9.0 | Machine Learning Tools | Preprocessing scalers (StandardScaler, MinMaxScaler, OneHotEncoder) and metrics. |
| **Pandas & NumPy** | 3.0.5 / 2.3.5 | Data Manipulation | High-performance tabular data processing, sequence reshaping, numerical math. |
| **SQLAlchemy** | 2.0.52 | ORM & Persistence | Database abstraction, connection pooling, transactional session management. |
| **PostgreSQL** | 15 / 16 | Relational Database | Production persistence for user accounts and immutable prediction history logs. |
| **PyJWT & Bcrypt** | 2.13.0 / 5.0.0| Security & Cryptography| RFC 7519 JWT generation/decoding (HS256) and 12-round password hashing. |
| **Pydantic** | 2.13.4 | Schema Validation | Strict request/response data validation and automatic OpenAPI documentation. |
| **Angular** | 18+ / 22.1.7 | Frontend Framework | Standalone SPA architecture, Angular Signals reactivity, and component views. |
| **TypeScript** | 5.4+ | Frontend Language | Strongly typed client-side logic, data models, and API service interfaces. |
| **Chart.js / ng2-charts**| 4.5.1 / 10.0.0| Data Visualization | Client-side rendering of radar charts, time-series line graphs, and bar charts. |
| **Nginx** | Alpine | Web Server & Reverse Proxy| Serving compiled Angular static assets and reverse-proxying API calls in Docker. |
| **Docker & Compose** | Latest | Containerization | Multi-container encapsulation (`agripulse_backend`, `agripulse_frontend`, `db`). |
| **Pytest & Vitest** | 9.1.1 / 4.0.8 | Quality Assurance | Automated backend and frontend unit/integration test runners. |
| **GitHub Actions** | CI/CD | DevOps Automation | Continuous integration pipeline executing tests and verifying Docker builds. |

---

## 3.5 Gantt Chart and Process Model
The project schedule followed a structured phase breakdown across 8 core levels of execution:

```
Month 1                  Month 2                  Month 3                  Month 4
[=== Phase 1: Level 0-2 ===]
                         [=== Phase 2: Level 3-4 ===]
                                                  [=== Phase 3: Level 5-6 ===]
                                                                           [=== Phase 4: Level 7-8 ===]
```
*Figure 3.2: Project Implementation Timeline & Phase Milestones*

*Table 3.4: Development Phase Milestones & Deliverable Schedule*

| Phase | Milestone / Level | Key Deliverables | Duration |
| :--- | :--- | :--- | :---: |
| **Phase 1** | Level 0: Foundation & Governance<br>Level 1: Tooling & Environment<br>Level 2: Data Acquisition & EDA | Project repository setup, coding standards, dataset acquisition (ICAR, AGMARKNET, DES), exploratory data analysis. | 3 Weeks |
| **Phase 2** | Level 3A: Crop Recommendation LSTM<br>Level 3B: Price Forecasting LSTM<br>Level 3C: Yield Forecasting DNN<br>Level 4: FastAPI REST API Backend | Neural network modeling, training, evaluation, `.keras` weight serialization, FastAPI route development, model preloading. | 4 Weeks |
| **Phase 3** | Level 5: Database & Authentication<br>Level 6: Angular 18+ Frontend UI | PostgreSQL schema design, Bcrypt/JWT security, Angular SPA development, Signals integration, Chart.js dashboards. | 4 Weeks |
| **Phase 4** | Level 7: Decision Support Engine<br>Level 8: MLOps, Monitoring & Docker | Multi-criteria scoring engine, dynamic XAI, API telemetry, data drift monitoring, Docker packaging, CI/CD pipeline. | 3 Weeks |

---

## 3.6 System Analysis (Functional, Structural, and Behavioral Models)
System analysis models the functional hierarchy, structural object layout, and dynamic behavioral states of AgriPulse.

### 3.6.1 Functional Model
The functional decomposition model organizes platform capabilities into three operational tiers:

```
                             AgriPulse Platform
                                     │
     ┌───────────────────────────────┼───────────────────────────────┐
     ▼                               ▼                               ▼
[ User & Security ]         [ Predictive AI Engines ]      [ Governance & Ops ]
  ├── User Registration       ├── Crop Recommendation (LSTM) ├── Model Registry
  ├── Bcrypt Login            ├── Price Forecasting (LSTM)   ├── Telemetry Metrics
  ├── Profile Management      ├── Yield Estimation (DNN)     ├── Z-Shift Data Drift
  └── Prediction Audit Trail  └── Decision Support Engine    └── Output Distributions
```
*Figure 3.3: Functional Decomposition Hierarchy of AgriPulse Platform*

### 3.6.2 Structural Model
The structural model captures the relationships between software layers:
- **Presentation Layer**: Angular standalone components (`DecisionSupportComponent`, `CropRecommendationComponent`, `PriceForecastComponent`, `YieldForecastComponent`, `MonitoringComponent`, `HistoryComponent`, `LoginComponent`, `RegisterComponent`).
- **Service Layer**: Asynchronous business services (`CropRecommendationService`, `PriceForecastingService`, `YieldForecastingService`, `DecisionService`, `PredictionService`, `ModelRegistryService`, `DriftMonitoringService`, `MetricsCollector`).
- **Domain & Persistence Layer**: SQLAlchemy entities (`User`, `PredictionHistory`) mapped to PostgreSQL tables with connection pooling.
- **Model Inference Layer**: Cached TensorFlow models and Scikit-Learn transformers managed via the singleton `ModelManager`.

### 3.6.3 Behavioral Model
The behavioral model represents system state transitions:
1. **Unauthenticated State**: Guest users can access public landing pages, register accounts, and view API documentation.
2. **Authenticated State**: Authenticated users obtain a Bearer JWT, unlocking access to execute inference pipelines, retrieve tenant-isolated prediction histories, delete records, and access MLOps monitoring.
3. **Inference Execution State**: Upon form submission, the UI transitions to a reactive loading state, dispatches an HTTP POST request, awaits backend computation ($< 1.7\text{s}$ for DSS), updates Angular Signal state, and dynamically renders Chart.js visualizations.
"""
