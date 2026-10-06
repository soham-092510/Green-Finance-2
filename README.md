# 🌱 GreenFinance: Enterprise Digital Carbon & Energy Observability Platform

A production-grade, dual-mode **Digital Carbon & Energy Observability Platform** designed for banking and financial microservice architectures. Built with **FastAPI**, **SQLAlchemy ORM**, **OpenTelemetry**, **Prometheus**, and **Kepler RAPL eBPF**, GreenFinance attributes electrical energy consumption and Scope 2 carbon emissions directly to financial transactions while enforcing physical energy conservation ($\ge 94\%$ attribution fidelity) and **Basel III / RBI-aligned dynamic operational risk thresholds**.

---

## 🚀 Quick Start: Launching the Prototype

You can run both the interactive frontend dashboard and the FastAPI backend locally:

### 1. Launch the Frontend Observability Dashboard
```powershell
# Serve the frontend UI on port 8085
python -m http.server 8085 --directory "frontend"
```
👉 Access the UI at: **[http://localhost:8085](http://localhost:8085)**

### 2. Launch the FastAPI Backend
```powershell
# Activate local virtual environment
.\venv\Scripts\activate

# Start the uvicorn API server
.\venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000 --reload
```
👉 Access Interactive Swagger UI at: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**  
👉 Access ReDoc Specification at: **[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)**

### 3. Run Automated Verification Tests
```powershell
# Run complete test suite (16 tests verifying math, thresholds, and adapters)
.\venv\Scripts\python.exe -m unittest discover tests
```

---

## 🌟 Dual-Mode Architectural Overview

GreenFinance provides two distinct operating modes sharing an identical, scientifically rigorous mathematical and compliance engine:

```text
                           ┌────────────────────────────────────────┐
                           │    GREENFINANCE OBSERVABILITY PLATFORM │
                           └───────────────────┬────────────────────┘
                                               │
                    ┌──────────────────────────┴──────────────────────────┐
                    ▼                                                     ▼
      ┌───────────────────────────┐                         ┌───────────────────────────┐
      │  🧪 MODE 1: SIMULATION    │                         │  🔗 MODE 2: CONNECTION    │
      │         SANDBOX           │                         │      ENTERPRISE LAYER     │
      ├───────────────────────────┤                         ├───────────────────────────┤
      │ • Zero external deps      │                         │ • Live OpenTelemetry OTLP │
      │ • Synthetic bank cluster  │                         │ • Prometheus PromQL API   │
      │ • Fault injection lab     │                         │ • Kubernetes / cgroup v2  │
      │ • Benchmark CV evaluator  │                         │ • Zero PII Trace Mapping  │
      └─────────────┬─────────────┘                         └─────────────┬─────────────┘
                    │                                                     │
                    └──────────────────────────┬──────────────────────────┘
                                               │
                                               ▼
                              ┌─────────────────────────────────┐
                              │     SHARED ANALYTICS ENGINE     │
                              ├─────────────────────────────────┤
                              │ 1. EnergyEngine                 │
                              │ 2. CarbonEngine                 │
                              │ 3. AttributionEngine            │
                              │ 4. Basel ThresholdEngine        │
                              │ 5. AnomalyEngine                │
                              │ 6. Cryptographic AuditEngine    │
                              └────────────────┬────────────────┘
                                               │
                                               ▼
                              ┌─────────────────────────────────┐
                              │  DUAL-MODE UI & COMPLIANCE EVR  │
                              └─────────────────────────────────┘
```

### 🧪 Mode 1: Simulation Sandbox (Zero-Dependency)
- **Purpose**: Academic evaluation, university vivas, hackathon demonstrations (SIH), and offline algorithm benchmarking.
- **Simulated Financial Services**: Full simulation of core banking microservices (`auth-service`, `account-service`, `payment-service`, `fraud-service`, `ledger-service`, `notification-service`).
- **Workload Batch Generator**: Standardized batches ($10$ to $10,000$ transactions) calculating repeatability Coefficient of Variation ($CV \le 5.0\%$).
- **Scenario Fault Injection Lab**:
  - `NORMAL`: Steady-state baseline operations.
  - `TRAFFIC_SPIKE`: Workload surge (+300% transactions) proving normalized Energy/tx stability.
  - `PAYMENT_SPIKE`: CPU saturation (+30% energy/tx) triggering Basel critical alert.
  - `LEDGER_BOTTLENECK`: Row-lock contention causing latency and power surges.
  - `TELEMETRY_DRIFT`: Unaccounted load causing residual to exceed 6.0% tolerance.
  - `HIGH_CARBON_GRID`: Regional coal-grid transition (820 g/kWh) tripling emissions without energy increase.
- **"What-If?" Scenario Simulator**: Sliders to project future emissions under traffic growth, software optimization, and green power purchase agreements (PPAs).

### 🔗 Mode 2: Enterprise Connection Layer (Real Banking Telemetry)
- **Purpose**: Plug-and-play observability layer connecting directly to a financial institution's existing container and monitoring infrastructure.
- **4-Step Onboarding Wizard**:
  1. *Connect Endpoints*: Handshake verifying connectivity with Prometheus HTTP API and OpenTelemetry Collector.
  2. *Auto-Discovery*: Automatically identifies banking microservices and container pods.
  3. *Trace Mapping*: Ingests OpenTelemetry distributed traces to track request paths across microservices.
  4. *Off-Peak Baseline*: Calibrates 0-workload idle power ($\mu_{idle}$) during maintenance windows.
- **🔒 Privacy-Preserving Architecture (Zero Financial PII)**:
  - Collects **only**: Trace ID, span duration, microservice call graph, container cgroup CPU/RAM allocation, and timestamps.
  - **Never collects or stores**: Customer names, account numbers, balances, card numbers (PAN/CVV), or transaction monetary amounts.

---

## 📐 Scientific & Mathematical Foundations

### 1. Energy Conservation & Attribution Fidelity
The system enforces physical energy conservation across host infrastructure and container workloads:

$$P_{host} = \sum_{i=1}^{n} P_{container, i} + P_{idle} + P_{residual}$$

$$\text{Attribution Fidelity (\%)} = \left(1 - \frac{P_{residual}}{P_{host}}\right) \times 100$$

- **Target Tolerance**: Residual $\le 6.0\%$ ($\ge 94.0\%$ Attribution Fidelity).

### 2. Workload Repeatability Benchmark
Repeatability across identical transactions is measured using the Coefficient of Variation ($CV$):

$$CV = \left(\frac{\sigma}{\mu}\right) \times 100 \le 5.0\%$$

### 3. EMA Telemetry Smoothing Filter
High-frequency RAPL sensor variations are smoothed over 15-second telemetry sampling intervals using an Exponential Moving Average ($\alpha = 0.2$):

$$S_t = 0.2 \cdot Y_t + 0.8 \cdot S_{t-1}$$

---

## 🏛️ Basel III & RBI-Aligned Dynamic Risk Thresholds

Unlike naive systems with hardcoded static thresholds, GreenFinance implements an **8-factor dynamic threshold engine** aligned with **Basel Committee on Banking Supervision (BCBS)** operational risk standards and **Reserve Bank of India (RBI)** climate stress-testing guidelines:

1. **Bank Risk Appetite**: `LOW`, `MEDIUM`, `HIGH` scaling tolerance boundaries.
2. **Service Criticality**: `CRITICAL` (Payment, Ledger, Auth, Fraud), `MEDIUM` (Notification), `LOW` (Analytics).
3. **Historical Baseline**: Continuous empirical mean ($\mu$) and standard deviation ($\sigma$).
4. **Statistical Multipliers**: Warning ($\mu + 2\sigma$), Critical ($\mu + 3\sigma$).
5. **Measurement Uncertainty**: $\pm 4.0\%$ margin acknowledged to prevent false precision.
6. **Workload Normalization**: Normalized **Energy per Transaction (J/tx)** rather than total Watts.
7. **Time Window**: 15-second telemetry sampling interval.
8. **Multi-Window Persistence**: Alerts require $N \ge 3$ consecutive windows (45 seconds) to filter out transient noise.

### "Explain Why Alert Happened" Diagnostic Breakdown
Every alert provides complete mathematical transparency:
- Exact deviation percentage above baseline.
- Persistence counter status (e.g. 4/3 windows satisfied).
- Probable root causes (container CPU saturation %, latency surge ms).
- Recommended engineering remediation actions.

---

## 📁 Repository Structure

```text
Green-Finance-2/
├── backend/                        # FastAPI Backend Application
│   ├── api/                        # REST API Route Controllers
│   │   ├── connection.py           # Mode 2 Enterprise Connection Endpoints
│   │   ├── thresholds.py           # Basel Dynamic Risk Threshold Endpoints
│   │   ├── simulation.py           # Mode 1 Synthetic Sandbox Endpoints
│   │   ├── accuracy.py             # Attribution Fidelity & EVR Reports
│   │   ├── baseline.py             # 0-Workload Idle Calibration Endpoints
│   │   ├── payment.py              # Simulated Banking Microservices
│   │   ├── telemetry.py            # Kepler PromQL Query Pathways
│   │   ├── carbon.py               # Carbon Record Management
│   │   ├── credits.py              # Carbon Credit Trading & Offsetting
│   │   └── ledger.py               # Double-Entry Accounting Ledger
│   ├── services/                   # Business Logic & Core Engines
│   │   ├── shared_engine.py        # Unified Analytics Core (Energy, Carbon, Attribution, Anomaly, Audit)
│   │   ├── threshold_service.py    # Basel Dynamic Threshold Engine & Explainable Diagnostics
│   │   ├── connection_service.py   # Real Telemetry Provider & 4-Step Wizard Manager
│   │   ├── simulation_service.py   # Synthetic Sandbox & Scenario Fault Injection
│   │   ├── accuracy_service.py     # Energy Conservation & EVR Report Generation
│   │   └── baseline_service.py     # Idle Power Calibration & Drift Detection
│   ├── core/                       # App Configuration & Security (JWT, bcrypt)
│   ├── db/                         # SQLAlchemy Engine, Session, and Database Seeding
│   ├── models/                     # Database Models (User, Account, Accuracy, Ledger, etc.)
│   ├── schemas/                    # Pydantic Request/Response Validation Schemas
│   └── main.py                     # Central FastAPI Switchboard & Middleware
├── frontend/                       # Enterprise Financial Terminal UI
│   ├── index.html                  # Responsive Dual-Mode Dashboard Layout
│   ├── styles.css                  # Ultra-Premium Dark Slate Financial Theme
│   └── app.js                      # Dual-Mode State Machine & Chart.js Visualizations
├── prototype layout/               # Production UI Mirror for Layout Evaluation
├── docs/                           # Comprehensive Engineering Documentation
│   ├── architecture.md             # In-Depth System Architecture Specification
│   └── api-endpoints.md            # Complete REST API Endpoint Reference
├── tests/                          # Automated Unit & Integration Test Suites
│   ├── test_threshold_engine.py    # Tests for Shared Core, Basel Engine & OTel Provider
│   └── test_accuracy_engine.py     # Tests for Fidelity, Calibration & Repeatability
├── requirements.txt                # Python Dependencies
└── README.md                       # Master Documentation & Quickstart Guide
```

---

## 📜 Compliance & Verification Certification

GreenFinance generates an immutable **Energy Validation Certificate (EVR)** with a cryptographic SHA-256 digital signature:
- **IEEE 830-1998**: Conforms to formal Software Requirements Specification standards.
- **ISO 14064-3**: Compliant with Greenhouse Gas verification and reporting protocols.
- **GHG Protocol Scope 2**: Aligned with location-based and market-based grid carbon accounting.
- **Basel III & RBI Guidelines**: Follows principles for operational resilience and climate risk stress-testing.

---

## 👨‍💻 Project Team & Academic Credits

- **Institution**: Sardar Patel Institute of Technology (S.P.I.T.), Mumbai
- **Course**: Software Engineering (TE Sem V) — Academic Year 2025–2026
- **Project Group**: 13
- **Contributors**:
  - **Soham Haridas Gaikwad** (UID: 2024800030) — *Lead Developer: Backend Architecture, Basel Risk Engines, Observability & DevOps*
  - **Atharva Pramod Hule** (UID: 2024800038) — *Frontend UI, System Documentation & Integration*
  - **Laukik Vidyadhar Deshpande** (UID: 2024800023) — *Testing, Research & Comparative Analysis*
- **Supervisor**: Prof. Kirti Chaudhari, Department of Computer Science & Engineering
