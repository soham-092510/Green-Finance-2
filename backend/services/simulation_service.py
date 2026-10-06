# =====================================================================
# GREEN-FINANCE — SIMULATION_SERVICE.PY (SYNTHETIC FINANCE SANDBOX)
# =====================================================================
# Purpose: Zero-dependency simulated banking environment for testing,
#          demonstration, benchmark evaluation, and fault injection:
#          - Scenarios: Normal, Traffic Spike, Payment Spike, Ledger Bottleneck,
#            Telemetry Drift, Telemetry Noise, High Carbon Grid
#          - Batch Transaction Generator (10 to 10,000 txs)
#          - "What-If?" Scenario Simulator (before-vs-after delta)
# =====================================================================

import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from backend.services.shared_engine import EnergyEngine, CarbonEngine, AttributionEngine, AnomalyEngine


class SimulationService:
    """
    Manages synthetic simulation states, fault-injection scenarios,
    and batch banking transaction workloads.
    """

    SCENARIOS = {
        "NORMAL": {
            "name": "Normal Steady State",
            "description": "Standard banking operations with healthy baseline energy and 95%+ attribution fidelity.",
            "energy_multiplier": 1.0,
            "tx_rate_multiplier": 1.0,
            "residual_pct": 5.0,
            "grid_carbon_g_kwh": 700.0,
            "payment_energy_j": 0.70,
            "ledger_energy_j": 0.40,
            "auth_energy_j": 0.14,
            "fraud_energy_j": 0.52
        },
        "TRAFFIC_SPIKE": {
            "name": "High Load Traffic Spike",
            "description": "3x transaction burst; total energy scales proportionally, normalized energy/tx remains stable.",
            "energy_multiplier": 2.8,
            "tx_rate_multiplier": 3.0,
            "residual_pct": 5.2,
            "grid_carbon_g_kwh": 700.0,
            "payment_energy_j": 0.71,
            "ledger_energy_j": 0.41,
            "auth_energy_j": 0.15,
            "fraud_energy_j": 0.53
        },
        "PAYMENT_SPIKE": {
            "name": "Payment Inefficiency Anomaly",
            "description": "Payment service CPU utilization surges unexpectedly (+30% energy/tx), triggering a Basel critical alert.",
            "energy_multiplier": 1.35,
            "tx_rate_multiplier": 1.0,
            "residual_pct": 5.4,
            "grid_carbon_g_kwh": 700.0,
            "payment_energy_j": 0.91,
            "ledger_energy_j": 0.40,
            "auth_energy_j": 0.14,
            "fraud_energy_j": 0.52
        },
        "LEDGER_BOTTLENECK": {
            "name": "Ledger Database Lock Bottleneck",
            "description": "Lock contention on double-entry ledger rows causes prolonged transaction latency and elevated power.",
            "energy_multiplier": 1.4,
            "tx_rate_multiplier": 0.8,
            "residual_pct": 5.8,
            "grid_carbon_g_kwh": 700.0,
            "payment_energy_j": 0.70,
            "ledger_energy_j": 0.78,
            "auth_energy_j": 0.14,
            "fraud_energy_j": 0.52
        },
        "TELEMETRY_DRIFT": {
            "name": "Telemetry Attribution Residual Drift",
            "description": "Simulates un-instrumented background daemon consuming power; residual climbs to 8.4% (exceeding <=6% tolerance).",
            "energy_multiplier": 1.1,
            "tx_rate_multiplier": 1.0,
            "residual_pct": 8.4,
            "grid_carbon_g_kwh": 700.0,
            "payment_energy_j": 0.70,
            "ledger_energy_j": 0.40,
            "auth_energy_j": 0.14,
            "fraud_energy_j": 0.52
        },
        "TELEMETRY_NOISE": {
            "name": "High Frequency Measurement Noise",
            "description": "Fluctuations in RAPL sensor sampling without actual drift; demonstrates EMA smoothing filter efficacy.",
            "energy_multiplier": 1.0,
            "tx_rate_multiplier": 1.0,
            "residual_pct": 5.0,
            "grid_carbon_g_kwh": 700.0,
            "payment_energy_j": 0.70,
            "ledger_energy_j": 0.40,
            "auth_energy_j": 0.14,
            "fraud_energy_j": 0.52
        },
        "HIGH_CARBON_GRID": {
            "name": "Carbon Grid Shift (Coal-Heavy Grid)",
            "description": "Simulates data center failover to a coal-intensive regional grid (820 g/kWh), increasing emissions without energy change.",
            "energy_multiplier": 1.0,
            "tx_rate_multiplier": 1.0,
            "residual_pct": 5.0,
            "grid_carbon_g_kwh": 820.0,
            "payment_energy_j": 0.70,
            "ledger_energy_j": 0.40,
            "auth_energy_j": 0.14,
            "fraud_energy_j": 0.52
        }
    }

    def __init__(self):
        self.active_scenario_key = "NORMAL"
        self.tx_counter = 12450
        self.cumulative_energy_kwh = 38.42
        self.cumulative_carbon_kg = 26.89

    def get_state(self) -> Dict[str, Any]:
        """Returns the current simulation state."""
        scenario = self.SCENARIOS[self.active_scenario_key]
        return {
            "active_scenario": self.active_scenario_key,
            "scenario_metadata": scenario,
            "total_simulated_transactions": self.tx_counter,
            "cumulative_energy_kwh": round(self.cumulative_energy_kwh, 3),
            "cumulative_carbon_kg": round(self.cumulative_carbon_kg, 3),
            "current_residual_pct": scenario["residual_pct"],
            "attribution_fidelity_pct": round(100.0 - scenario["residual_pct"], 2),
            "available_scenarios": [
                {"key": k, "name": v["name"], "description": v["description"]}
                for k, v in self.SCENARIOS.items()
            ]
        }

    def set_scenario(self, scenario_key: str) -> Dict[str, Any]:
        """Switches the active simulation scenario."""
        key = scenario_key.upper()
        if key not in self.SCENARIOS:
            key = "NORMAL"
        self.active_scenario_key = key
        return self.get_state()

    def generate_workload(self, count: int = 500, amount: float = 1000.0) -> Dict[str, Any]:
        """
        Executes a batch of N simulated banking transactions under the active scenario.
        Computes energy attribution, repeatability CV, and carbon emissions.
        """
        scenario = self.SCENARIOS[self.active_scenario_key]
        base_energy = scenario["payment_energy_j"] + scenario["ledger_energy_j"] + scenario["auth_energy_j"]
        
        # Add slight natural Gaussian noise
        tx_energies = [random.gauss(base_energy, 0.02 * scenario["energy_multiplier"]) for _ in range(count)]
        cv_stats = AttributionEngine.calculate_cv(tx_energies)

        total_j = sum(tx_energies)
        total_kwh = EnergyEngine.joules_to_kwh(total_j)
        grid_factor = scenario["grid_carbon_g_kwh"]
        total_carbon_g = CarbonEngine.calculate_carbon_grams(total_j, grid_factor)

        # Update cumulative counters
        self.tx_counter += count
        self.cumulative_energy_kwh += total_kwh
        self.cumulative_carbon_kg += (total_carbon_g / 1000.0)

        return {
            "transactions_executed": count,
            "scenario": self.active_scenario_key,
            "mean_energy_per_tx_j": round(cv_stats["mean"], 4),
            "std_energy_per_tx_j": round(cv_stats["std"], 4),
            "repeatability_cv_percent": cv_stats["cv_percent"],
            "cv_status": "PASS (CV <= 5.0%)" if cv_stats["is_stable"] else "UNSTABLE (CV > 5.0%)",
            "batch_total_energy_j": round(total_j, 2),
            "batch_total_energy_kwh": round(total_kwh, 6),
            "batch_total_carbon_g": round(total_carbon_g, 4),
            "carbon_per_tx_mg": round((total_carbon_g / count) * 1000.0, 3),
            "cumulative_transactions": self.tx_counter,
            "cumulative_energy_kwh": round(self.cumulative_energy_kwh, 3),
            "cumulative_carbon_kg": round(self.cumulative_carbon_kg, 3)
        }

    def evaluate_what_if(
        self,
        transaction_multiplier: float = 1.5,
        energy_optimization_percent: float = -15.0,
        target_grid_factor_g_kwh: float = 25.0
    ) -> Dict[str, Any]:
        """
        'What-If?' Scenario Engine:
        Evaluates hypothetical bank infrastructure optimizations (e.g. code optimization, green PPA).
        """
        current_tx = self.tx_counter
        current_energy_kwh = self.cumulative_energy_kwh
        current_carbon_kg = self.cumulative_carbon_kg

        # Projected
        proj_tx = int(current_tx * transaction_multiplier)
        energy_factor = 1.0 + (energy_optimization_percent / 100.0)
        proj_energy_kwh = current_energy_kwh * transaction_multiplier * energy_factor
        proj_carbon_kg = (proj_energy_kwh * target_grid_factor_g_kwh) / 1000.0

        carbon_reduction_kg = max(0.0, (current_carbon_kg * transaction_multiplier) - proj_carbon_kg)
        carbon_reduction_pct = (carbon_reduction_kg / (current_carbon_kg * transaction_multiplier) * 100.0) if current_carbon_kg > 0 else 0.0

        return {
            "baseline": {
                "transactions": current_tx,
                "energy_kwh": round(current_energy_kwh, 2),
                "carbon_kg": round(current_carbon_kg, 2),
                "grid_factor_g_kwh": 700.0
            },
            "projected": {
                "transactions": proj_tx,
                "energy_kwh": round(proj_energy_kwh, 2),
                "carbon_kg": round(proj_carbon_kg, 2),
                "grid_factor_g_kwh": target_grid_factor_g_kwh
            },
            "impact": {
                "carbon_reduction_kg": round(carbon_reduction_kg, 2),
                "carbon_reduction_percent": round(carbon_reduction_pct, 1),
                "equivalent_trees_planted": round(carbon_reduction_kg / 21.0, 1)
            }
        }


# Singleton simulation service instance
simulation_service = SimulationService()
