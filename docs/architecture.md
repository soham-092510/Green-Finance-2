# 🌱 GreenFinance: System Architecture & Technical Specification

## 1. Executive Summary & Vision

**GreenFinance** is an enterprise-grade digital carbon and energy observability platform designed specifically for banking and financial microservice architectures. Modern financial institutions process billions of transactions daily across distributed cloud and container clusters. While carbon accounting platforms typically estimate emissions using high-level financial spend or static cloud billing averages, GreenFinance operates at the **telemetry and kernel observability layer**.

The platform provides fine-grained, empirical observability into electrical energy consumption (Joules/Watts) and translates it dynamically into **Scope 2 carbon emissions ($g CO_2e$)** per microservice, per API endpoint, and per individual financial transaction.

### Dual-Mode Operational Architecture

To serve both demonstration/academic validation and real-world banking integration, GreenFinance operates across two unified modes powered by a shared mathematical and compliance core:

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

---

## 2. Shared Analytics & Mathematical Core

At the foundation of GreenFinance is a shared calculation engine that enforces strict physical energy conservation and banking risk compliance.

### 2.1 Physical Energy Conservation & Attribution Fidelity
A physical computer server consumes total power $P_{host}$ measured via hardware RAPL (Running Average Power Limit) or platform power meters. This power is split among running containers, the operating system kernel/idle background, and un-instrumented hardware overhead:

$$P_{host} = \sum_{i=1}^{n} P_{container, i} + P_{idle} + P_{residual}$$

Where:
- $P_{host}$: Total host platform power (Watts or Joules over time window $\Delta t$).
- $\sum P_{container, i}$: Aggregate active energy consumed by containerized banking microservices (`payment-service`, `ledger-service`, `auth-service`, `fraud-service`, etc.).
- $P_{idle}$: Empirical baseline idle power measured during a 0-transaction workload calibration window ($\mu_{idle}$).
- $P_{residual}$: Residual loss representing measurement error, hypervisor overhead, and unallocated bus power.

The **Attribution Fidelity** metric measures the degree to which energy is fully accounted for without physical leakage:

$$\text{Residual Loss (\%)} = \left(\frac{P_{residual}}{P_{host}}\right) \times 100 = \left(\frac{P_{host} - (\sum P_{container} + P_{idle})}{P_{host}}\right) \times 100$$

$$\text{Attribution Fidelity (\%)} = \left(1 - \frac{P_{residual}}{P_{host}}\right) \times 100$$

- **Target Tolerance**: The platform enforces a strict $\le 6.0\%$ residual tolerance target ($\ge 94.0\%$ attribution fidelity).
- When residual exceeds $6.0\%$, the system flags an `ATTRIBUTION_DRIFT` state for audit review.

### 2.2 Workload Repeatability & Statistical Consistency
Measurement repeatability across standardized transactions is quantified using the **Coefficient of Variation ($CV$)**:

$$CV = \left(\frac{\sigma}{\mu}\right) \times 100$$

Where:
- $\mu$: Arithmetic mean of energy measurements across $N$ identical transaction benchmarks.
- $\sigma$: Sample standard deviation:
  $$\sigma = \sqrt{\frac{1}{N - 1} \sum_{k=1}^{N} (E_k - \mu)^2}$$

- **Stability Benchmark**: The system requires $CV \le 5.0\%$ under stable testing conditions to certify repeatability.

### 2.3 Exponential Moving Average (EMA) Telemetry Smoothing
Raw hardware RAPL counters fluctuate at high frequencies due to thread scheduling. An EMA filter ($\alpha = 0.2$) is applied over 15-second telemetry sampling intervals to filter out transient noise without introducing latency lag:

$$S_t = \alpha \cdot Y_t + (1 - \alpha) \cdot S_{t-1}$$

Where $Y_t$ is the instantaneous raw reading and $S_t$ is the smoothed metric.

---

## 3. Basel-Aligned Dynamic Threshold Engine

Banks do not operate on arbitrary static numbers (such as "energy > 20 J is bad"). Financial risk management frameworks—including **Basel Committee on Banking Supervision (BCBS) Operational Risk Principles** and the **Reserve Bank of India (RBI) Climate Risk Stress-Testing Guidance**—mandate that risk indicators and tolerance boundaries must be:
1. Aligned with approved risk appetite.
2. Calibrated to service criticality and historical baseline.
3. Accounting for measurement uncertainty.
4. Supported by escalation and audit procedures.

### The 8 Banking Threshold Configurations

| # | Configuration Parameter | Financial Banking Rationale | Implementation in GreenFinance |
| :--- | :--- | :--- | :--- |
| **1** | **Bank Risk Appetite** | Dictates organizational tolerance for deviation (`LOW`, `MEDIUM`, `HIGH`). | Scales dynamic threshold multipliers ($\theta_{risk} = 0.90$ for LOW appetite). |
| **2** | **Service Criticality** | Stricter controls on core settlement systems vs non-critical reporting. | Categorized into `CRITICAL` (Payment, Ledger, Auth, Fraud), `MEDIUM` (Notification), `LOW` (Analytics). |
| **3** | **Historical Baseline** | Normal operational profile established over time ($\mu, \sigma$). | Measured empirical baseline per service ($0.70 \text{ J}$ for Payment, $0.40 \text{ J}$ for Ledger). |
| **4** | **Variability / Multipliers** | Statistical boundaries reflecting natural workload distribution. | Warning threshold at $\mu + 2\sigma$; Critical threshold at $\mu + 3\sigma$. |
| **5** | **Measurement Uncertainty** | Recognizes lack of physical meters inside virtualized cloud containers. | $\pm 4.0\%$ uncertainty annotation attached to all derived metrics. |
| **6** | **Normalized Workload** | Workload spikes shouldn't falsely trigger efficiency alerts. | Evaluates **Energy per Transaction (J/tx)** rather than gross Watts. |
| **7** | **Time Window & Smoothing** | Prevents one-off millisecond spikes from creating alert fatigue. | 15-second telemetry sampling window with $\alpha = 0.2$ EMA smoothing. |
| **8** | **Multi-Window Persistence** | Distinguishes transient anomalies from persistent operational failures. | Alert triggers only after persisting for $N \ge 3$ consecutive windows (45 seconds). |

### Mathematical Threshold Formulation

$$\text{Threshold}_{Warning} = \mu_{baseline} + \left(k_w \cdot \sigma_{baseline} \cdot \gamma_{crit} \cdot \theta_{risk}\right)$$

$$\text{Threshold}_{Critical} = \mu_{baseline} + \left(k_c \cdot \sigma_{baseline} \cdot \gamma_{crit} \cdot \theta_{risk}\right)$$

Where:
- $k_w = 2.0, k_c = 3.0$
- $\gamma_{crit} = 0.90$ for `CRITICAL`, $1.00$ for `MEDIUM`, $1.15$ for `LOW`
- $\theta_{risk} = 0.90$ for `LOW`, $1.00$ for `MEDIUM`, $1.15$ for `HIGH`

### Explainable Alert Diagnostics ("Explain Why Alert Happened")

When a threshold is breached, the platform generates a structured diagnostic breakdown:
```json
{
  "service": "payment-service",
  "status": "CRITICAL",
  "observed_energy_per_tx": 0.910,
  "baseline_mean": 0.700,
  "deviation_percent": 30.0,
  "persistence_count": "4 / 3 windows (60 seconds)",
  "root_causes": [
    "High container CPU saturation (82%) in container cgroup",
    "Elevated request latency (145 ms) prolonging container power draw"
  ],
  "remediation": [
    "Verify container cgroup CPU limits for payment-service",
    "Inspect microservice trace spans in OpenTelemetry / Jaeger"
  ]
}
```

---

## 4. Mode 2: Enterprise Financial Application Connection

### 4.1 Zero-PII Telemetry Architecture
Connecting an observability platform to a bank requires strict compliance with banking secrecy, PCI-DSS, and data privacy regulations. **GreenFinance explicitly excludes all financial payloads.**

```text
               INSPECTED BY GREENFINANCE         NEVER ACCESSED (STRICTLY PROHIBITED)
               ─────────────────────────         ────────────────────────────────────
               ✓ Trace ID & Span ID              ✗ Customer Name & Aadhaar/PAN
               ✓ Microservice Call Path          ✗ Bank Account Numbers (IBAN/IFSC)
               ✓ Span Duration & Latency         ✗ Account Balances & Credit Limits
               ✓ Container CPU/RAM cgroups       ✗ Card Numbers (PAN) & CVV
               ✓ Timestamp & HTTP Status         ✗ Transaction Monetary Amounts
```

### 4.2 The 4-Step Connection Onboarding Wizard

```text
┌────────────────┐     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│     STEP 1     │     │     STEP 2     │     │     STEP 3     │     │     STEP 4     │
│    CONNECT     ├───► │  AUTO-DISCOVER ├───► │ TRACE DISCOVERY├───► │ OFF-PEAK BASE  │
│   ENDPOINTS    │     │  MICROSERVICES │     │   (ZERO PII)   │     │  CALIBRATION   │
└────────────────┘     └────────────────┘     └────────────────┘     └────────────────┘
```

1. **Step 1: Connect Endpoints**: Non-intrusive handshake verifying connectivity with Prometheus HTTP API (`http://prometheus:9090`) and OpenTelemetry Collector (`http://otel-collector:4318`).
2. **Step 2: Auto-Discovery**: Automatically enumerates banking pods, namespaces, container labels, and cgroup resource allocations.
3. **Step 3: Trace Mapping**: Listens to OpenTelemetry spans, mapping transaction lifecycles (`API Gateway -> Auth -> Fraud -> Payment -> Ledger`) and attributing container power per hop.
4. **Step 4: Off-Peak Baseline**: Calibrates the host's idle power under 0-traffic or maintenance conditions, establishing $\mu_{idle}$ and locking the profile.

---

## 5. Technology Stack & Deployment Architecture

- **Backend**: FastAPI (Python 3.11+), SQLAlchemy ORM, Pydantic v2 Settings & Models.
- **Telemetry Ingestion**: Kepler (Kubernetes-based Efficient Power Level Exporter via eBPF/RAPL), Prometheus PromQL time-series scraper, OpenTelemetry OTLP receiver.
- **Database & Ledger**: SQLite (local dev) / PostgreSQL (production), double-entry transaction journals with SHA-256 tamper-evident digital signatures.
- **Frontend UI**: Pure HTML5/CSS3/JavaScript (ES6+) with Chart.js, designed as a responsive, zero-dependency financial terminal.
- **Compliance Alignment**: IEEE 830-1998 Software Requirements Specification, ISO 14064-3 GHG Verification, Basel III Operational Risk Management, RBI Climate Risk Stress-Testing.
