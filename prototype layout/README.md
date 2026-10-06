# 🖥️ GreenFinance: Prototype Layout & Evaluation Guide

This directory contains the standalone **Enterprise Financial Observability Dashboard UI** ready for local evaluation, academic demonstrations, and jury vivas.

---

## ⚡ Quick Start: Serve Prototype Locally

```powershell
# Run local HTTP server on port 8085
python -m http.server 8085 --directory "prototype layout"
```
👉 Access the Dashboard: **[http://localhost:8085](http://localhost:8085)**

---

## 🌟 Key Features Demonstrated in the Prototype

### 1. Seamless Dual-Mode Operation
Use the mode switch pill at the top of the screen:
- **🧪 Mode 1: Simulation Sandbox**: Demonstrates full synthetic banking operations (`auth-service`, `payment-service`, `ledger-service`, `fraud-service`, `notification-service`), fault-injection scenarios, 0-workload baseline calibration, and repeatable benchmark CV testing.
- **🔗 Mode 2: Enterprise Connection Layer**: Interactive 4-step onboarding wizard connecting to live OpenTelemetry and Prometheus telemetry without collecting sensitive banking PII.

### 2. Basel III & RBI-Aligned Dynamic Risk Thresholds
- Microservice criticality tuning (`CRITICAL` vs `MEDIUM` vs `LOW`).
- Bank risk appetite selection (`LOW` vs `MEDIUM` vs `HIGH`).
- Multi-window persistence filter ($N \ge 3$ consecutive 15-second windows) to eliminate false alarms.
- **"Explain Why Alert Happened" Diagnostics Modal** breaking down exact mathematical formulas, observed deviations, root-cause contributors, and remediation protocols.

### 3. Physical Energy Conservation & Attribution Fidelity
- Interactive Waterfall chart demonstrating:
  $$P_{host} = \sum P_{container} + P_{idle} + P_{residual}$$
- Enforces the project's $\le 6.0\%$ residual loss target ($\ge 94.0\%$ attribution fidelity).

### 4. Interactive "What-If?" Scenario Simulator
- Sliders for workload scaling ($1.0\times$ to $5.0\times$), software efficiency optimization, and grid carbon transitions (e.g. 700 g/kWh Indian Grid vs 25 g/kWh Clean PPA).

### 5. Official Energy Validation Certificate (EVR)
- Formal compliance certificate featuring SHA-256 cryptographic verification for auditable reporting.
