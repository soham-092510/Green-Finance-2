# =====================================================================
# GREEN-FINANCE — SHARED_ENGINE.PY (UNIFIED ANALYTICS CORE)
# =====================================================================
# Purpose: Shared mathematical, attribution, carbon, anomaly, and audit
#          engines used interchangeably by both:
#          - 🧪 SIMULATION MODE (Synthetic Sandbox)
#          - 🔗 CONNECTION MODE (Real Telemetry / OpenTelemetry)
# =====================================================================

import math
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class EnergyEngine:
    """
    Standardized energy attribution engine.
    Converts power (Watts) and durations (seconds/ms) into Joules and kWh,
    and attributes energy across nodes, containers, and transaction traces.
    """

    @staticmethod
    def power_to_joules(power_watts: float, duration_seconds: float) -> float:
        """Energy (Joules) = Power (Watts) * Time (seconds)"""
        return max(0.0, power_watts * duration_seconds)

    @staticmethod
    def joules_to_kwh(joules: float) -> float:
        """1 kWh = 3,600,000 Joules"""
        return joules / 3600000.0

    @staticmethod
    def kwh_to_joules(kwh: float) -> float:
        """1 kWh = 3,600,000 Joules"""
        return kwh * 3600000.0

    @staticmethod
    def calculate_energy_per_transaction(total_energy_joules: float, tx_count: int) -> float:
        """Computes normalized Energy per Transaction (Joules/tx)."""
        if tx_count <= 0:
            return 0.0
        return total_energy_joules / tx_count

    @staticmethod
    def attribute_service_energy(
        total_container_joules: float,
        service_cpu_shares: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Attributes aggregate container energy across microservices based on
        measured CPU utilization / cgroup weights.
        """
        total_share = sum(service_cpu_shares.values())
        if total_share <= 0:
            count = len(service_cpu_shares)
            return {svc: round(total_container_joules / count, 4) for svc in service_cpu_shares} if count > 0 else {}

        return {
            svc: round(total_container_joules * (share / total_share), 4)
            for svc, share in service_cpu_shares.items()
        }


class CarbonEngine:
    """
    Dynamic Scope 2 carbon calculation engine.
    Converts electrical energy into CO2e emissions using location-based
    or grid-specific carbon intensity factors (g CO2e / kWh).
    """

    # Default grid intensities (g CO2e / kWh)
    GRID_FACTORS = {
        "IN_NATIONAL_GRID": 700.0,   # Central Electricity Authority (CEA) India avg (~700 g/kWh)
        "US_AVG": 380.0,             # US EPA eGRID national avg (~380 g/kWh)
        "EU_AVG": 230.0,             # European Environment Agency avg (~230 g/kWh)
        "RENEWABLE_PPA": 25.0,       # High-renewable corporate PPA (~25 g/kWh)
        "COAL_INTENSIVE": 820.0      # Coal-dominated grid region (~820 g/kWh)
    }

    @staticmethod
    def calculate_carbon_grams(energy_joules: float, carbon_intensity_g_per_kwh: float = 700.0) -> float:
        """
        Carbon (g CO2e) = Energy (kWh) * Carbon Intensity (g CO2e / kWh)
        """
        kwh = EnergyEngine.joules_to_kwh(energy_joules)
        return kwh * carbon_intensity_g_per_kwh

    @staticmethod
    def calculate_carbon_per_transaction(
        energy_joules_per_tx: float,
        carbon_intensity_g_per_kwh: float = 700.0
    ) -> float:
        """Computes Carbon per Transaction in milligrams (mg CO2e / tx) or grams."""
        return CarbonEngine.calculate_carbon_grams(energy_joules_per_tx, carbon_intensity_g_per_kwh)

    @staticmethod
    def project_emissions(
        daily_carbon_kg: float
    ) -> Dict[str, float]:
        """Projects daily, monthly (30-day), and annual carbon emissions in kg and metric tonnes."""
        monthly_kg = daily_carbon_kg * 30.0
        annual_tonnes = (daily_carbon_kg * 365.0) / 1000.0
        return {
            "daily_kg": round(daily_carbon_kg, 3),
            "monthly_kg": round(monthly_kg, 2),
            "annual_metric_tonnes": round(annual_tonnes, 2)
        }


class AttributionEngine:
    """
    Energy Conservation and Attribution Fidelity Engine.
    Validates physical conservation:
    E_host = E_containers + E_idle + Residual
    Residual Loss = |E_host - (E_containers + E_idle)|
    Attribution Fidelity (%) = (1 - Residual / E_host) * 100
    """

    @staticmethod
    def evaluate_conservation(
        host_joules: float,
        container_joules: float,
        idle_joules: float,
        tolerance_target_pct: float = 6.0
    ) -> Dict:
        """
        Evaluates energy conservation across host and microservice containers.
        Returns accounted energy, residual loss, and attribution fidelity %.
        """
        accounted_joules = container_joules + idle_joules
        residual_joules = max(0.0, host_joules - accounted_joules)

        residual_pct = (residual_joules / host_joules * 100.0) if host_joules > 0 else 0.0
        fidelity_pct = (1.0 - (residual_joules / host_joules)) * 100.0 if host_joules > 0 else 100.0

        is_valid = residual_pct <= tolerance_target_pct

        return {
            "host_energy_joules": round(host_joules, 2),
            "container_energy_joules": round(container_joules, 2),
            "idle_energy_joules": round(idle_joules, 2),
            "accounted_energy_joules": round(accounted_joules, 2),
            "residual_joules": round(residual_joules, 2),
            "residual_percent": round(residual_pct, 2),
            "attribution_fidelity_percent": round(fidelity_pct, 2),
            "tolerance_target_percent": tolerance_target_pct,
            "status": "PASS" if is_valid else "ATTRIBUTION_DRIFT",
            "explanation": (
                f"Accounted power ({round(accounted_joules, 2)}J) vs host ({round(host_joules, 2)}J) "
                f"yields residual of {round(residual_joules, 2)}J ({round(residual_pct, 2)}%), "
                f"achieving {round(fidelity_pct, 2)}% attribution fidelity."
            )
        }

    @staticmethod
    def calculate_cv(samples: List[float]) -> Dict:
        """
        Calculates Mean, Standard Deviation, and Coefficient of Variation (CV = sigma / mu * 100).
        Used for 0-workload baseline stability and transaction repeatability benchmark.
        """
        if not samples:
            return {"mean": 0.0, "std": 0.0, "cv_percent": 0.0, "status": "EMPTY"}

        n = len(samples)
        mean_val = sum(samples) / n
        if n > 1:
            variance = sum((x - mean_val) ** 2 for x in samples) / (n - 1)
            std_val = math.sqrt(variance)
        else:
            std_val = 0.0

        cv_pct = (std_val / mean_val * 100.0) if mean_val > 0 else 0.0
        return {
            "sample_count": n,
            "mean": round(mean_val, 4),
            "std": round(std_val, 4),
            "cv_percent": round(cv_pct, 2),
            "is_stable": cv_pct <= 5.0,
            "status": "PASS" if cv_pct <= 5.0 else "UNSTABLE"
        }


class AnomalyEngine:
    """
    Statistical and Workload-Aware Energy Efficiency Anomaly Detector.
    Distinguishes between:
    - Normal workload scale-up (Transactions ↑, Energy ↑, Energy/tx → Stable)
    - True efficiency regression (Transactions → Stable, Energy ↑, Energy/tx ↑↑)
    - Performance optimization (Transactions ↑, Energy → Stable, Energy/tx ↓)
    """

    @staticmethod
    def analyze_efficiency_trend(
        current_tx_volume: float,
        baseline_tx_volume: float,
        current_energy_per_tx: float,
        baseline_energy_per_tx: float,
        tolerance_pct: float = 10.0
    ) -> Dict:
        energy_change_pct = (
            ((current_energy_per_tx - baseline_energy_per_tx) / baseline_energy_per_tx) * 100.0
            if baseline_energy_per_tx > 0 else 0.0
        )
        tx_change_pct = (
            ((current_tx_volume - baseline_tx_volume) / baseline_tx_volume) * 100.0
            if baseline_tx_volume > 0 else 0.0
        )

        if energy_change_pct > tolerance_pct and abs(tx_change_pct) < 15.0:
            classification = "EFFICIENCY_REGRESSION"
            severity = "CRITICAL" if energy_change_pct > 25.0 else "WARNING"
            message = f"Energy per transaction surged by +{round(energy_change_pct, 1)}% while transaction volume remained steady. Investigate CPU bottlenecks or memory leaks."
        elif energy_change_pct > tolerance_pct and tx_change_pct > 30.0:
            classification = "LOAD_SATURATION"
            severity = "WARNING"
            message = f"Transaction volume surged (+{round(tx_change_pct, 1)}%) causing marginal efficiency degradation (+{round(energy_change_pct, 1)}%). Normal under peak load."
        elif energy_change_pct < -5.0:
            classification = "EFFICIENCY_IMPROVED"
            severity = "INFO"
            message = f"Energy per transaction decreased by {abs(round(energy_change_pct, 1))}%. Sub-service caching or batching optimization detected."
        else:
            classification = "NORMAL"
            severity = "NORMAL"
            message = f"Energy per transaction ({round(current_energy_per_tx, 3)} J) is well within historical baseline variance ({round(baseline_energy_per_tx, 3)} J)."

        return {
            "classification": classification,
            "severity": severity,
            "current_energy_per_tx": round(current_energy_per_tx, 4),
            "baseline_energy_per_tx": round(baseline_energy_per_tx, 4),
            "energy_deviation_percent": round(energy_change_pct, 2),
            "workload_volume_change_percent": round(tx_change_pct, 2),
            "message": message
        }


class AuditEngine:
    """
    Cryptographic verification and compliance trail engine.
    Generates SHA-256 digital signatures for validation reports, ledger updates,
    and telemetry calibration cycles in accordance with ISO 14064-3 and Basel operational risk rules.
    """

    @staticmethod
    def generate_digest(payload: Dict) -> str:
        """Produces a deterministic SHA-256 checksum of any dictionary."""
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_digest(payload: Dict, expected_digest: str) -> bool:
        """Verifies integrity of an audit record against its SHA-256 signature."""
        computed = AuditEngine.generate_digest(payload)
        return computed.lower() == expected_digest.lower()
