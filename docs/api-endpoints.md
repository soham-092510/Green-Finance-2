# 📡 GreenFinance: REST API Reference & Endpoints

Complete reference of all HTTP API endpoints provided by the GreenFinance platform, categorized by operational domain.

**Base URL**: `http://127.0.0.1:8000`  
**Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
**ReDoc Spec**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 1. Enterprise Application Connection Endpoints (`/connection`)

Used in **Mode 2 (Connection Mode)** to onboard and monitor real-world financial microservice clusters.

### `POST /connection/test`
Performs a non-intrusive network handshake to verify that the banking cluster's Prometheus and OpenTelemetry endpoints are responding.
- **Request Body**:
  ```json
  {
    "prometheus_url": "http://localhost:9090",
    "otel_endpoint": "http://localhost:4318"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "CONNECTED",
    "prometheus_reachable": true,
    "prometheus_latency_ms": 18.4,
    "opentelemetry_reachable": true,
    "opentelemetry_latency_ms": 14.2,
    "services_discovered_count": 6,
    "telemetry_driver": "Kepler RAPL eBPF + Prometheus TimeSeries"
  }
  ```

### `POST /connection/connect`
Step 1: Connects the platform to the target financial infrastructure and registers the application profile.
- **Request Body**:
  ```json
  {
    "application_name": "CoreBanking-Cluster",
    "environment": "Production",
    "prometheus_url": "http://localhost:9090",
    "otel_endpoint": "http://localhost:4318",
    "integration_type": "opentelemetry"
  }
  ```

### `GET /connection/status`
Returns active connection metadata, current onboarding step (1 to 4), and telemetry stream health.

### `POST /connection/advance-step?target_step=N`
Advances the connection lifecycle state through the 4-step onboarding wizard.

### `GET /connection/discover/services`
Step 2: Auto-discovers financial microservices (`payment-service`, `ledger-service`, `fraud-service`, `auth-service`, `notification-service`, `account-service`) and container pod resource allocations.

### `GET /connection/discover/traces?limit=20`
Step 3: Streams live OpenTelemetry distributed traces.
- **Privacy Assurance**: Contains ZERO customer financial PII. Only trace ID, span duration, and service call paths.

### `GET /connection/realtime`
Returns real-time host power (W), container power (W), idle power (W), residual loss (W), and attribution fidelity (%).

### `GET /connection/efficiency`
Returns service-by-service normalized energy per transaction (Joules/tx) compared against historical baselines to flag efficiency regressions.

---

## 2. Basel-Aligned Dynamic Threshold Engine (`/thresholds`)

### `GET /thresholds/configs`
Lists active dynamic threshold configurations for all financial microservices.
- **Sample Item**:
  ```json
  {
    "service_name": "payment-service",
    "criticality": "CRITICAL",
    "risk_appetite": "LOW",
    "baseline_mean_j": 0.70,
    "baseline_std_j": 0.03,
    "warning_sigma": 2.0,
    "critical_sigma": 3.0,
    "max_residual_percent": 6.0,
    "alert_persistence_windows": 3,
    "computed_thresholds": {
      "warning_energy_j": 0.7486,
      "critical_energy_j": 0.7729,
      "uncertainty_margin_j": 0.028
    }
  }
  ```

### `POST /thresholds/config`
Updates risk appetite, criticality, or sigma sensitivity for a specific service.

### `GET /thresholds/alerts`
Returns active alerts with full **Explainable Diagnostics** (mathematical rationale, baseline comparison, persistence counter, root cause factors).

### `POST /thresholds/evaluate`
Evaluates a live telemetry sample against dynamic thresholds, enforcing the multi-window persistence filter ($N \ge 3$).

---

## 3. Synthetic Banking Sandbox Endpoints (`/simulation`)

Used in **Mode 1 (Simulation Mode)** for zero-dependency demos, academic testing, and fault injection.

### `GET /simulation/state`
Returns the current simulation parameters, cumulative energy/carbon, and active scenario.

### `POST /simulation/scenario`
Switches the active simulation scenario:
- `NORMAL`: Healthy baseline operations
- `TRAFFIC_SPIKE`: Workload surge (+300% transactions)
- `PAYMENT_SPIKE`: Payment service CPU inefficiency (+30% energy/tx)
- `LEDGER_BOTTLENECK`: DB lock contention and prolonged latency
- `TELEMETRY_DRIFT`: Unaccounted load causing residual > 6%
- `TELEMETRY_NOISE`: High frequency sensor fluctuation
- `HIGH_CARBON_GRID`: Data center failover to coal grid (820 g/kWh)

### `POST /simulation/workload`
Executes a batch of $N$ simulated banking transactions, calculating energy attribution, repeatability CV %, and Scope 2 carbon.

### `POST /simulation/what-if`
Projects hypothetical energy and carbon savings under traffic scaling, code optimization, or green power purchase agreements (PPAs).

---

## 4. Telemetry Attribution & Accuracy Endpoints (`/accuracy`)

### `GET /accuracy/current`
Returns live energy conservation breakdown:
- Host Power (W)
- Container Power (W)
- Idle Baseline Power (W)
- Residual Loss (W)
- Attribution Fidelity (%)
- Status: `PASS` (Residual $\le 6.0\%$) or `ATTRIBUTION_DRIFT`

### `POST /accuracy/run-validation`
Executes a complete formal energy validation test run and records an immutable `ValidationRun` in the database.

### `GET /accuracy/report`
Generates an official, auditable **Energy Validation Report (EVR)** with SHA-256 digital signature.

---

## 5. 0-Workload Idle Baseline Calibration Endpoints (`/baseline`)

### `POST /baseline/start?duration_seconds=30`
Initiates 0-transaction idle power calibration.

### `GET /baseline/status`
Polls real-time calibration progress, recording sample count, mean power, standard deviation, and CV %.

### `POST /baseline/lock`
Locks the calibrated idle baseline profile into the system database.

### `GET /baseline/current`
Retrieves the currently active locked baseline profile.

---

## 6. Simulated Banking & Double-Entry Ledger (`/payment` & `/ledger`)

### `POST /payment/transfer`
Executes an atomic bank transfer with double-entry ledger bookkeeping. Captures container energy, attributes carbon, and records SHA-256 audit hash.

### `POST /payment/benchmark`
Runs standardized batch transactions to measure repeatability Coefficient of Variation ($CV \le 5.0\%$).

### `GET /payment/accounts`
Lists registered bank accounts and balances (`HDFC9999`, `MAH123`, `IDF892`, `SBIN456`).

### `GET /ledger/audit`
Returns the complete double-entry carbon and monetary ledger with balance sheet verification.
