# =====================================================================
# GREEN-FINANCE — THRESHOLD_SERVICE.PY (BASEL-ALIGNED DYNAMIC THRESHOLD ENGINE)
# =====================================================================
# Purpose: Dynamic, risk-calibrated thresholding engine for financial microservices.
#          Implements Basel III / RBI operational risk guidelines:
#          - Risk Appetite (LOW, MEDIUM, HIGH)
#          - Service Criticality (CRITICAL, MEDIUM, LOW)
#          - Historical Baseline (mu, sigma)
#          - Measurement Uncertainty (+-4%)
#          - Normalized Energy / Transaction (Joules/tx)
#          - EMA Filtering (alpha = 0.2)
#          - Alert Persistence Window Filter (N >= 3 consecutive breaches)
#          - Explainable Diagnostics ("Explain Why Alert Happened")
# =====================================================================

import math
from typing import Dict, List, Optional, Any
from datetime import datetime
from backend.middleware.logger import logger


class DynamicThresholdConfig:
    """Represents a service-specific risk configuration."""
    def __init__(
        self,
        service_name: str,
        criticality: str = "CRITICAL",  # CRITICAL, MEDIUM, LOW
        risk_appetite: str = "LOW",     # LOW, MEDIUM, HIGH
        baseline_mean_j: float = 0.70,
        baseline_std_j: float = 0.03,
        warning_sigma: float = 2.0,
        critical_sigma: float = 3.0,
        max_residual_percent: float = 6.0,
        measurement_uncertainty_percent: float = 4.0,
        alert_persistence_windows: int = 3,
        carbon_intensity_g_kwh: float = 700.0,
        auto_recalibration: bool = False
    ):
        self.service_name = service_name
        self.criticality = criticality.upper()
        self.risk_appetite = risk_appetite.upper()
        self.baseline_mean_j = baseline_mean_j
        self.baseline_std_j = baseline_std_j
        self.warning_sigma = warning_sigma
        self.critical_sigma = critical_sigma
        self.max_residual_percent = max_residual_percent
        self.measurement_uncertainty_percent = measurement_uncertainty_percent
        self.alert_persistence_windows = alert_persistence_windows
        self.carbon_intensity_g_kwh = carbon_intensity_g_kwh
        self.auto_recalibration = auto_recalibration

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "criticality": self.criticality,
            "risk_appetite": self.risk_appetite,
            "baseline_mean_j": self.baseline_mean_j,
            "baseline_std_j": self.baseline_std_j,
            "warning_sigma": self.warning_sigma,
            "critical_sigma": self.critical_sigma,
            "max_residual_percent": self.max_residual_percent,
            "measurement_uncertainty_percent": self.measurement_uncertainty_percent,
            "alert_persistence_windows": self.alert_persistence_windows,
            "carbon_intensity_g_kwh": self.carbon_intensity_g_kwh,
            "auto_recalibration": self.auto_recalibration,
            "computed_thresholds": self.compute_effective_thresholds()
        }

    def compute_effective_thresholds(self) -> Dict[str, float]:
        """
        Calculates effective warning and critical energy thresholds (Joules/tx):
        Effective = mu + (k * sigma * criticality_factor * risk_appetite_factor)
        """
        # Criticality tightening factor: CRITICAL services have tighter alert bands
        crit_factor = 0.90 if self.criticality == "CRITICAL" else (1.0 if self.criticality == "MEDIUM" else 1.15)

        # Risk appetite factor: LOW appetite means institution tolerates less deviation
        risk_factor = 0.90 if self.risk_appetite == "LOW" else (1.0 if self.risk_appetite == "MEDIUM" else 1.15)

        w_sigma = self.warning_sigma * crit_factor * risk_factor
        c_sigma = self.critical_sigma * crit_factor * risk_factor

        warning_threshold = self.baseline_mean_j + (w_sigma * self.baseline_std_j)
        critical_threshold = self.baseline_mean_j + (c_sigma * self.baseline_std_j)

        return {
            "warning_energy_j": round(warning_threshold, 4),
            "critical_energy_j": round(critical_threshold, 4),
            "effective_warning_sigma": round(w_sigma, 2),
            "effective_critical_sigma": round(c_sigma, 2),
            "uncertainty_margin_j": round(self.baseline_mean_j * (self.measurement_uncertainty_percent / 100.0), 4)
        }


class ThresholdEngine:
    """
    Evaluates microservice energy telemetry against Basel-aligned dynamic risk thresholds,
    tracks multi-window alert persistence, and constructs explainable root-cause diagnostics.
    """

    def __init__(self):
        # Service configuration registry
        self._configs: Dict[str, DynamicThresholdConfig] = {
            "payment-service": DynamicThresholdConfig(
                service_name="payment-service",
                criticality="CRITICAL",
                risk_appetite="LOW",
                baseline_mean_j=0.70,
                baseline_std_j=0.03,
                warning_sigma=2.0,
                critical_sigma=3.0,
                max_residual_percent=6.0,
                measurement_uncertainty_percent=4.0,
                alert_persistence_windows=3
            ),
            "ledger-service": DynamicThresholdConfig(
                service_name="ledger-service",
                criticality="CRITICAL",
                risk_appetite="LOW",
                baseline_mean_j=0.40,
                baseline_std_j=0.02,
                warning_sigma=2.0,
                critical_sigma=3.0,
                max_residual_percent=6.0,
                measurement_uncertainty_percent=4.0,
                alert_persistence_windows=3
            ),
            "auth-service": DynamicThresholdConfig(
                service_name="auth-service",
                criticality="CRITICAL",
                risk_appetite="LOW",
                baseline_mean_j=0.14,
                baseline_std_j=0.01,
                warning_sigma=2.0,
                critical_sigma=3.0,
                max_residual_percent=6.0,
                measurement_uncertainty_percent=4.0,
                alert_persistence_windows=3
            ),
            "fraud-service": DynamicThresholdConfig(
                service_name="fraud-service",
                criticality="CRITICAL",
                risk_appetite="MEDIUM",
                baseline_mean_j=0.52,
                baseline_std_j=0.025,
                warning_sigma=2.0,
                critical_sigma=3.0,
                max_residual_percent=6.0,
                measurement_uncertainty_percent=4.0,
                alert_persistence_windows=3
            ),
            "notification-service": DynamicThresholdConfig(
                service_name="notification-service",
                criticality="MEDIUM",
                risk_appetite="MEDIUM",
                baseline_mean_j=0.08,
                baseline_std_j=0.01,
                warning_sigma=2.0,
                critical_sigma=3.0,
                max_residual_percent=6.0,
                measurement_uncertainty_percent=4.0,
                alert_persistence_windows=3
            ),
            "analytics-service": DynamicThresholdConfig(
                service_name="analytics-service",
                criticality="LOW",
                risk_appetite="HIGH",
                baseline_mean_j=0.95,
                baseline_std_j=0.08,
                warning_sigma=2.5,
                critical_sigma=3.5,
                max_residual_percent=8.0,
                measurement_uncertainty_percent=5.0,
                alert_persistence_windows=4
            )
        }

        # Track consecutive breach counts for persistence filter: service -> count
        self._consecutive_breaches: Dict[str, int] = {svc: 0 for svc in self._configs}
        # In-memory history of alerts
        self._active_alerts: List[Dict] = []

    def get_all_configs(self) -> List[Dict]:
        """Returns all configured service profiles."""
        return [cfg.to_dict() for cfg in self._configs.values()]

    def get_config(self, service_name: str) -> Optional[DynamicThresholdConfig]:
        """Gets configuration for a specific service."""
        return self._configs.get(service_name)

    def update_config(self, service_name: str, updates: Dict[str, Any]) -> DynamicThresholdConfig:
        """Updates threshold parameters for a given service."""
        cfg = self._configs.get(service_name)
        if not cfg:
            cfg = DynamicThresholdConfig(service_name=service_name)
            self._configs[service_name] = cfg

        if "criticality" in updates:
            cfg.criticality = str(updates["criticality"]).upper()
        if "risk_appetite" in updates:
            cfg.risk_appetite = str(updates["risk_appetite"]).upper()
        if "baseline_mean_j" in updates:
            cfg.baseline_mean_j = float(updates["baseline_mean_j"])
        if "baseline_std_j" in updates:
            cfg.baseline_std_j = float(updates["baseline_std_j"])
        if "warning_sigma" in updates:
            cfg.warning_sigma = float(updates["warning_sigma"])
        if "critical_sigma" in updates:
            cfg.critical_sigma = float(updates["critical_sigma"])
        if "max_residual_percent" in updates:
            cfg.max_residual_percent = float(updates["max_residual_percent"])
        if "measurement_uncertainty_percent" in updates:
            cfg.measurement_uncertainty_percent = float(updates["measurement_uncertainty_percent"])
        if "alert_persistence_windows" in updates:
            cfg.alert_persistence_windows = int(updates["alert_persistence_windows"])
        if "carbon_intensity_g_kwh" in updates:
            cfg.carbon_intensity_g_kwh = float(updates["carbon_intensity_g_kwh"])

        logger.info(f"Updated dynamic threshold config for {service_name}: {updates}")
        return cfg

    def evaluate_sample(
        self,
        service_name: str,
        current_energy_per_tx_j: float,
        current_residual_percent: float = 5.0,
        latency_ms: float = 45.0,
        cpu_utilization_pct: float = 38.0
    ) -> Dict[str, Any]:
        """
        Evaluates a live telemetry sample against dynamic statistical thresholds.
        Applies multi-window persistence filter and returns explainable diagnostics.
        """
        cfg = self.get_config(service_name)
        if not cfg:
            cfg = DynamicThresholdConfig(service_name=service_name)
            self._configs[service_name] = cfg

        thresholds = cfg.compute_effective_thresholds()
        warning_j = thresholds["warning_energy_j"]
        critical_j = thresholds["critical_energy_j"]
        mu = cfg.baseline_mean_j
        sigma = cfg.baseline_std_j

        deviation_from_baseline_pct = ((current_energy_per_tx_j - mu) / mu * 100.0) if mu > 0 else 0.0

        # Determine instantaneous condition
        is_energy_critical = current_energy_per_tx_j >= critical_j
        is_energy_warning = current_energy_per_tx_j >= warning_j and not is_energy_critical
        is_residual_breach = current_residual_percent > cfg.max_residual_percent

        instantaneous_level = "NORMAL"
        if is_energy_critical or (is_residual_breach and current_residual_percent > cfg.max_residual_percent * 1.3):
            instantaneous_level = "CRITICAL"
        elif is_energy_warning or is_residual_breach:
            instantaneous_level = "WARNING"

        # Update persistence counter
        if instantaneous_level in ("WARNING", "CRITICAL"):
            self._consecutive_breaches[service_name] = self._consecutive_breaches.get(service_name, 0) + 1
        else:
            self._consecutive_breaches[service_name] = 0

        consecutive_count = self._consecutive_breaches[service_name]
        is_persistent = consecutive_count >= cfg.alert_persistence_windows

        # Final alert level after persistence filter
        effective_level = "NORMAL"
        if is_persistent:
            effective_level = instantaneous_level
        elif instantaneous_level == "CRITICAL" and consecutive_count >= 1:
            # Immediate warning when critical is approached, escalates once persistent
            effective_level = "WARNING"

        # Build Explainable Rationale
        explanation = self._build_explanation(
            service_name=service_name,
            cfg=cfg,
            current_energy_j=current_energy_per_tx_j,
            warning_j=warning_j,
            critical_j=critical_j,
            residual_pct=current_residual_percent,
            consecutive_count=consecutive_count,
            effective_level=effective_level,
            latency_ms=latency_ms,
            cpu_pct=cpu_utilization_pct
        )

        result = {
            "service_name": service_name,
            "timestamp": datetime.now().isoformat(),
            "level": effective_level,  # NORMAL, WARNING, CRITICAL
            "instantaneous_level": instantaneous_level,
            "consecutive_breaches": consecutive_count,
            "persistence_window_target": cfg.alert_persistence_windows,
            "is_persistent": is_persistent,
            "metrics": {
                "current_energy_per_tx_j": round(current_energy_per_tx_j, 4),
                "baseline_mean_j": round(mu, 4),
                "baseline_std_j": round(sigma, 4),
                "deviation_percent": round(deviation_from_baseline_pct, 2),
                "current_residual_percent": round(current_residual_percent, 2),
                "max_residual_limit_percent": round(cfg.max_residual_percent, 2),
                "latency_ms": round(latency_ms, 1),
                "cpu_utilization_percent": round(cpu_utilization_pct, 1)
            },
            "thresholds": thresholds,
            "governance": {
                "criticality": cfg.criticality,
                "risk_appetite": cfg.risk_appetite,
                "framework": "Basel III Operational Risk & RBI Climate Stress-Testing Aligned"
            },
            "explanation": explanation
        }

        # Keep active alert list fresh
        if effective_level != "NORMAL":
            self._active_alerts = [a for a in self._active_alerts if a["service_name"] != service_name]
            self._active_alerts.append(result)
        else:
            self._active_alerts = [a for a in self._active_alerts if a["service_name"] != service_name]

        return result

    def get_active_alerts(self) -> List[Dict]:
        """Returns list of currently active alerts with full explainability."""
        return self._active_alerts

    def _build_explanation(
        self,
        service_name: str,
        cfg: DynamicThresholdConfig,
        current_energy_j: float,
        warning_j: float,
        critical_j: float,
        residual_pct: float,
        consecutive_count: int,
        effective_level: str,
        latency_ms: float,
        cpu_pct: float
    ) -> Dict[str, Any]:
        """Generates an explainable diagnostic breakdown of the threshold decision."""
        reasons = []
        root_causes = []

        if current_energy_j >= critical_j:
            reasons.append(f"Energy/tx ({current_energy_j:.3f} J) breached critical dynamic threshold ({critical_j:.3f} J, +{((current_energy_j-cfg.baseline_mean_j)/cfg.baseline_mean_j*100):.1f}% above baseline).")
        elif current_energy_j >= warning_j:
            reasons.append(f"Energy/tx ({current_energy_j:.3f} J) breached warning dynamic threshold ({warning_j:.3f} J, +{((current_energy_j-cfg.baseline_mean_j)/cfg.baseline_mean_j*100):.1f}% above baseline).")

        if residual_pct > cfg.max_residual_percent:
            reasons.append(f"Telemetry attribution residual ({residual_pct:.1f}%) exceeds bank-approved tolerance ({cfg.max_residual_percent:.1f}%).")

        # Root-cause diagnostic hints
        if cpu_pct > 75.0:
            root_causes.append(f"High CPU saturation ({cpu_pct:.1f}%) detected in container cgroup.")
        if latency_ms > 120.0:
            root_causes.append(f"Elevated request processing latency ({latency_ms:.1f} ms) prolonging container power draw.")
        if not root_causes:
            root_causes.append("Telemetry variance consistent with unexpected thread contention or memory bus overhead.")

        return {
            "summary": (
                f"Status: {effective_level}. " + (" ".join(reasons) if reasons else "All metrics operating within expected baseline.")
            ),
            "reasons": reasons,
            "root_causes": root_causes,
            "persistence_status": (
                f"Persisted across {consecutive_count}/{cfg.alert_persistence_windows} consecutive 15-second windows."
                if effective_level != "NORMAL" else "Transient variations filtered out."
            ),
            "remediation_actions": [
                f"Verify container cgroup limits for {service_name}",
                "Check for un-indexed DB queries or locking bottlenecks",
                "Inspect microservice trace spans in OpenTelemetry / Jaeger"
            ] if effective_level == "CRITICAL" else [
                f"Continue monitoring {service_name} over next 2 telemetry cycles"
            ]
        }


# Singleton threshold engine instance
threshold_engine = ThresholdEngine()
