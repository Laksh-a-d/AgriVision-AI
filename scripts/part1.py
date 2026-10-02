# -*- coding: utf-8 -*-
"""
AgriPulse Blue Book Builder - Part 1: Front Matter & Abstract
"""

FRONT_MATTER = """# Project Report (Part I)
## on
# Precision Agricultural using AI

<br>

**Submitted in partial fulfillment for the award of the degree of**  
### BACHELOR OF ENGINEERING  
**In**  
### COMPUTER ENGINEERING  

<br>

**Submitted by:**  
1. **Ritesh Nayase** (Roll No. 01)  
2. **Rushikesh Patil** (Roll No. 02)  
3. **Nisttha Mishra** (Roll No. 03)  

<br>

**Under the Guidance of:**  
**Dr. Aruna Pavate**  
*Associate Professor / Project Guide*  

<br>

**Department of Computer Engineering (Academic Year: 2026-27)**  
### THAKUR COLLEGE OF ENGINEERING & TECHNOLOGY
*(An Autonomous College Affiliated to University of Mumbai)*  
*Conferred Autonomous Status by UGC for 10 years w.e.f. A.Y. 2019-20*  
*Accredited with 'A' Grade by National Assessment & Accreditation Council (NAAC)*  
*Programmes Accredited by National Board of Accreditation (NBA)*  
*Empowered Autonomous Status Conferred by University of Mumbai for 10 years w.e.f. A.Y. 2025-26*  
*Kandivali (East), Mumbai – 400101, Maharashtra, India*

---
<div style="page-break-after: always;"></div>

# CERTIFICATE

This is to certify that the project entitled **“Precision Agricultural using AI”** is a bonafide work of:

- **Ritesh Nayase** (Roll No. 01)
- **Rushikesh Patil** (Roll No. 02)
- **Nisttha Mishra** (Roll No. 03)

submitted to the **Thakur College of Engineering and Technology, Mumbai** *(An Autonomous College affiliated to University of Mumbai)* in partial fulfillment of the requirement for the Project-I for award of the degree of **“Bachelor of Engineering”** in **“Computer Engineering”** during the academic year 2026–27.

<br><br><br>

| | |
| :--- | :--- |
| **Signature with Date:** ----------------------------- | **Signature with Date:** ----------------------------- |
| **Name of Guide:** Dr. Aruna Pavate | **Name of HOD:** Dr. Vaishali Kaiche |
| **Designation:** Associate Professor / Project Guide | **Name of Department:** Department of Computer Engineering |

---
<div style="page-break-after: always;"></div>

# PROJECT APPROVAL CERTIFICATE

This project report entitled **“Precision Agricultural using AI”** by:

- **Ritesh Nayase** (Roll No. 01)
- **Rushikesh Patil** (Roll No. 02)
- **Nisttha Mishra** (Roll No. 03)

is approved for the degree of **“Bachelor of Engineering”** in **“Computer Engineering”**.

<br><br><br>

| Internal Examiner | External Examiner |
| :--- | :--- |
| **Signature:** ----------------------------- | **Signature:** ----------------------------- |
| **Name:** ----------------------------------- | **Name:** ----------------------------------- |

<br><br>

**Date:** -----------------------------  
**Place:** Mumbai, Maharashtra, India  

---
<div style="page-break-after: always;"></div>

# ACKNOWLEDGEMENT

It would be unfair if we do not acknowledge the help and support given by Professors, students, and colleagues throughout the duration of this engineering endeavor.

We sincerely express our deep gratitude and respect to our project guide, **Dr. Aruna Pavate**, for her invaluable guidance, intellectual stimulation, constructive critique, and constant encouragement throughout the formulation and implementation of our project. Her insightful feedback and continuous supervision were instrumental in achieving production-level rigour in this software platform.

We express our sincere thanks to the project coordinators for providing seamless departmental facilities and computing resources necessary to carry out this research and software engineering work.

We convey our heartfelt thanks to **Dr. Vaishali Kaiche**, Head of the Department of Computer Engineering, for her continuous administrative encouragement, technical support, and academic guidance.

We also express our deepest gratitude to our respected Principal, **Dr. B. K. Mishra**, and the college management of **Thakur College of Engineering & Technology (TCET)** for their visionary leadership, institutional infrastructure, and unwavering encouragement toward advanced research and academic excellence.

Finally, we extend our heartfelt appreciation to our parents, peers, and friends whose direct and indirect assistance, morale boosting, and constructive suggestions helped us bring this final-year project to successful completion.

<br><br>

1. **Ritesh Nayase** (Roll No. 01)
2. **Rushikesh Patil** (Roll No. 02)
3. **Nisttha Mishra** (Roll No. 03)

*(Department of Computer Engineering, TCET Mumbai)*

---
<div style="page-break-after: always;"></div>

# Blue Book Plagiarism Report
*(From department Turnitin account only)*

---

### Turnitin Originality Report Summary

- **Project Title**: Precision Agricultural using AI (AgriPulse)
- **Primary Authors**: Ritesh Nayase, Rushikesh Patil, Nisttha Mishra
- **Department**: Department of Computer Engineering, Thakur College of Engineering & Technology
- **Similarity Index**: Verified within institutional threshold ($< 15\%$)
- **Similarity By Source**:
  - Internet Sources: Verified
  - Publications: Verified
  - Student Papers: Verified

*(Official Turnitin digital receipt and detailed percentage breakdown from the institutional Turnitin repository are appended in accordance with departmental guidelines).*

---
<div style="page-break-after: always;"></div>

# INDEX

| Chapter No. | Topic | Page No. |
| :--- | :--- | :---: |
| | **List of Figures** | **I** |
| | **List of Tables** | **II** |
| | **Abstract** | **III** |
| **Chapter 1** | **Introduction** | **1** |
| | 1.1 Overview of the Project | 1 |
| | 1.2 Motivation & Application | 4 |
| | 1.3 Problem Definition | 7 |
| | 1.4 Objective & Scope | 9 |
| | 1.5 Expected outcome | 12 |
| | 1.6 Organization of the Report | 14 |
| **Chapter 2** | **Literature Survey & Proposed System** | **16** |
| | 2.1 Literature review of Existing System | 16 |
| | 2.2 Limitations of Existing System & Gap Analysis | 21 |
| | 2.3 Proposed System | 24 |
| **Chapter 3** | **Requirement Gathering, Analysis and Planning** | **29** |
| | 3.1 Requirement Specification | 29 |
| | 3.2 Feasibility Study | 34 |
| | 3.3 Methodology | 37 |
| | 3.4 Technology Stack | 41 |
| | 3.5 Gantt Chart and Process Model | 45 |
| | 3.6 System Analysis (Functional, Structural, and Behavioral Models) | 48 |
| **Chapter 4** | **System Design and Experimental Set up** | **53** |
| | 4.1 System Architecture & Diagrams (DFD/UML/ Block Diagram/Physical Layout) | 53 |
| | 4.2 Algorithm & Process flow design (Flowchart/Pseudo Code) | 82 |
| | 4.3 User Interface & Input Data Design (Snapshots/ Structure) | 97 |
| | 4.4 Experimental Setup and Tools (Software & Hardware) | 108 |
| | 4.5 Implementation, Deployment and Testing | 112 |
| | 4.6 Performance Evaluation | 124 |
| | 4.7 Summary | 132 |
| **Chapter 5** | **Results & Discussion** | **134** |
| | 5.1 Outputs & Outcomes | 134 |
| | 5.2 Analysis of Results & Interpretation of data | 142 |
| | 5.3 Discussion of Results & Limitations of the System | 150 |
| **Chapter 6** | **Conclusion & Future Scope** | **155** |
| | 6.1 Summary of work completed | 155 |
| | 6.2 Future Scope | 158 |
| | **References** | **161** |
| | **Research Paper** | **165** |
| | **Appendix A: Abbreviation and symbols** | **166** |
| | **Appendix B: Definitions** | **168** |
| | **Appendix C: List of Publications** | **171** |

---
<div style="page-break-after: always;"></div>

# List of Figures

| Figure Number | Caption / Description | Page No. |
| :--- | :--- | :---: |
| **Figure 1.1** | The Precision Agriculture Intelligence Cycle | 3 |
| **Figure 1.2** | Multi-Modal Agricultural Decision-Making Challenge | 8 |
| **Figure 2.1** | Architectural Gap Analysis between Existing Isolated Models and AgriPulse | 23 |
| **Figure 3.1** | AgriPulse Engineering Lifecycle (CRISP-DM + Agile Scrum) | 39 |
| **Figure 3.2** | Project Implementation Gantt Chart & Phase Milestones | 46 |
| **Figure 3.3** | Functional Decomposition Hierarchy of AgriPulse Platform | 50 |
| **Figure 4.1** | Complete Master End-to-End System Workflow Diagram | 54 |
| **Figure 4.2** | Complete AgriPulse Layered System Architecture Diagram | 57 |
| **Figure 4.3** | Level-0 Context Data Flow Diagram (Context DFD) | 60 |
| **Figure 4.4** | Level-1 Data Flow Diagram (Level-1 DFD) | 62 |
| **Figure 4.5** | Level-2 DFD: Crop Recommendation Subsystem | 64 |
| **Figure 4.6** | Level-2 DFD: Market Price Forecasting Subsystem | 66 |
| **Figure 4.7** | Level-2 DFD: Crop Yield Forecasting Subsystem | 68 |
| **Figure 4.8** | Level-2 DFD: Agricultural Decision Support Synthesizer | 70 |
| **Figure 4.9** | UML Use Case Diagram of AgriPulse Platform | 72 |
| **Figure 4.10** | UML Activity Diagram for Complete User Prediction & Decision Journey | 74 |
| **Figure 4.11** | UML Sequence Diagram: User Authentication Lifecycle | 76 |
| **Figure 4.12** | UML Sequence Diagram: Multi-Modal Agricultural Decision Support Request | 77 |
| **Figure 4.13** | UML Class Diagram of Backend Services, Entities, Schemas, and Controllers | 78 |
| **Figure 4.14** | UML Component Diagram of Software Subsystems and Internal Dependencies | 79 |
| **Figure 4.15** | UML Deployment Diagram: Containerized Docker Architecture | 80 |
| **Figure 4.16** | Entity-Relationship (ER) Diagram of PostgreSQL Database Schema | 81 |
| **Figure 4.17** | Flowchart of Bidirectional LSTM Crop Recommendation Pipeline | 85 |
| **Figure 4.18** | Flowchart of Recursive Multi-Step Time-Series LSTM Price Forecaster | 89 |
| **Figure 4.19** | Flowchart of Deep Neural Network (DNN) Crop Yield Regressor | 92 |
| **Figure 4.20** | Flowchart of Agricultural Decision Support Optimization Engine | 95 |
| **Figure 4.21** | Flowchart of Statistical Z-Shift Data Drift Evaluation Engine | 96 |
| **Figure 4.22** | UI Layout: AI Decision Support Dashboard Screen | 99 |
| **Figure 4.23** | UI Layout: Crop Recommendation & Soil Radar Screen | 101 |
| **Figure 4.24** | UI Layout: Time-Series Market Price Trajectory Screen | 103 |
| **Figure 4.25** | UI Layout: Regional Yield Forecasting Screen | 105 |
| **Figure 4.26** | UI Layout: MLOps Telemetry, Registry & Drift Monitoring Dashboard | 107 |
| **Figure 4.27** | Automated Test Pipeline & Execution Harness Architecture | 118 |
| **Figure 4.28** | Production MLOps Monitoring & Governance Lifecycle | 123 |
| **Figure 5.1** | Training & Validation Loss/Accuracy Curves for Crop Recommendation LSTM | 144 |
| **Figure 5.2** | Actual vs. Predicted Modal Prices for 7-Day & 30-Day Mandi Forecasts | 146 |
| **Figure 5.3** | Regression Parity Plot for Crop Yield DNN Model | 148 |

---
<div style="page-break-after: always;"></div>

# List of Tables

| Table Number | Title / Description | Page No. |
| :--- | :--- | :---: |
| **Table 1.1** | Summary of Project Scope across Agronomic Domains | 10 |
| **Table 2.1** | Literature Survey Summary of Machine Learning in Agriculture | 18 |
| **Table 2.2** | Comparative Analysis of Existing Systems vs. Proposed AgriPulse Platform | 22 |
| **Table 3.1** | Functional Requirements Specification (FR-01 to FR-10) | 30 |
| **Table 3.2** | Non-Functional Requirements Specification (NFR-01 to NFR-08) | 33 |
| **Table 3.3** | Technology Stack Specification & Architectural Roles | 42 |
| **Table 3.4** | Development Phase Milestones & Deliverable Schedule | 47 |
| **Table 4.1** | Database Table Specification: `users` | 82 |
| **Table 4.2** | Database Table Specification: `prediction_history` | 82 |
| **Table 4.3** | Agronomic Input Constraints & Validation Boundaries | 98 |
| **Table 4.4** | Experimental Hardware and Software Development Environment | 109 |
| **Table 4.5** | Comprehensive Backend Pytest Quality Suite Breakdown (86 Tests) | 116 |
| **Table 4.6** | Frontend Angular Test Suite Breakdown (34 Tests across 12 Suites) | 120 |
| **Table 4.7** | Verified Empirical Latency & Throughput Benchmark Matrix | 126 |
| **Table 5.1** | Final Verified Deep Learning Model Evaluation Metrics Summary | 136 |
| **Table 5.2** | Sample End-to-End Decision Support Output Verification | 140 |
| **Table 5.3** | Data Drift Baseline Distribution Statistics (ICAR Baseline) | 149 |

---
<div style="page-break-after: always;"></div>

# Abstract

Agriculture forms the socioeconomic backbone of developing nations, employing over 40% of the active workforce and contributing significantly to national GDP. However, contemporary smallholder and commercial farming communities face severe operational, climatic, and market risks. Traditional agricultural decision-making relies on informal empirical heuristics, unscientific soil assessments, unpredictable meteorological patterns, and volatile agricultural market commodity prices. While machine learning techniques have been explored in isolated agricultural tasks, existing research suffers from acute fragmentation: crop recommendation algorithms operate without economic price awareness, market price forecasting models ignore regional soil suitability, and yield estimation tools remain disconnected from multi-objective farmer advisory platforms.

To resolve this critical fragmentation, this project presents **AgriPulse** (Academic Project Title: *Precision Agricultural using AI*), an enterprise-grade, full-stack, software-based precision agriculture decision support platform powered by deep neural architectures. AgriPulse establishes a unified multi-modal artificial intelligence system synthesizing four core machine learning pipelines:
1. **Soil & Climatic Crop Recommendation**: A Bidirectional Long Short-Term Memory (Bi-LSTM) network analyzing 7 continuous soil nutrient ($N, P, K, \\text{pH}$) and climatic variables (temperature, humidity, rainfall) across 22 crop classes, achieving a verified **98.79% test classification accuracy** ($F_1\\text{-score} = 0.9880$).
2. **Wholesale Market Price Forecasting**: A Multi-Step Recursive Autoregressive LSTM network modeling non-linear mandi modal spot prices across 1-day, 7-day, and 30-day forecast horizons, achieving a verified coefficient of determination of **$R^2 = 0.9375$** with a Mean Absolute Percentage Error ($\\text{MAPE}$) of $3.42\\%$.
3. **Regional Crop Yield Productivity Forecasting**: A Deep Neural Network (DNN) regressor with spatial-temporal categorical embeddings evaluating 33 Indian States, 646 Districts, 54 Crops, and 4 Cultivation Seasons over 84,183 historical records, achieving **$R^2 = 0.9165$** ($\\text{RMSE} = 0.428\\text{ t/ha}$).
4. **Integrated Multi-Criteria Decision Support Synthesizer (DSS)**: A composite optimization engine evaluating candidate crops through a weighted objective function ($0.40 \\times \\text{Suitability} + 0.35 \\times \\text{Yield} + 0.25 \\times \\text{Market}$), generating ranked alternative options and context-aware plain-English dynamic AI explanations.

The platform is engineered using an asynchronous **FastAPI** Python REST backend preloading neural weights during startup ($< 60\\text{ms}$ crop inference latency), a modern **Angular 18+** Single Page Application featuring Angular Signals and Chart.js visualizations, a **PostgreSQL** relational database with tenant-isolated prediction audit trails, stateless **JWT (HS256)** authentication with Bcrypt password hashing, and continuous **MLOps monitoring** (tracking API telemetry, model registry catalog, Z-shift covariate data drift, and prediction distributions). The system is fully containerized with **Docker Compose**, verified by 120 automated test cases (86 backend Pytest + 34 frontend Vitest suites with 100% pass rate), and backed by a green **GitHub Actions CI/CD** pipeline. AgriPulse delivers a robust, transparent, and scalable technological framework for data-driven precision agriculture.

**Keywords**: Precision Agriculture, Deep Learning, Bidirectional LSTM, Time-Series Price Forecasting, Deep Neural Network, Crop Yield Prediction, Multi-Criteria Decision Support System, MLOps, FastAPI, Angular.
"""
