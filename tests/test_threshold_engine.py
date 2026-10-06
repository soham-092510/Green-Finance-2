# =====================================================================
# GREEN-FINANCE — TEST_THRESHOLD_ENGINE.PY (UNIT & INTEGRATION TESTS)
# =====================================================================
# Purpose: Comprehensive test suite validating:
#          1. Shared Calculation Core (Energy, Carbon, Attribution, Anomaly, Audit)
#          2. Basel-Aligned Dynamic Threshold Engine & Explainable Alerts
#          3. Persistence Window Filter (N >= 3 consecutive breaches)
#          4. Connection Manager & Privacy-Preserving Telemetry Provider
#          5. Simulation Sandbox & Scenario Fault Injection
# =====================================================================

import unittest
from backend.services.shared_engine import (
    EnergyEngine, CarbonEngine, AttributionEngine, AnomalyEngine, AuditEngine
)
from backend.services.threshold_service import threshold_engine, DynamicThresholdConfig
from backend.services.connection_service import connection_manager, RealTelemetryProvider
from backend.services.simulation_service import simulation_service


class TestSharedAndThresholdEngine(unittest.TestCase):

    def test_01_energy_and_carbon_math(self):
        """Tests energy and carbon conversions."""
        # 1000 Joules at 700 g/kWh
        kwh = EnergyEngine.joules_to_kwh(3600000.0)
        self.assertEqual(kwh, 1.0)

        joules = EnergyEngine.kwh_to_joules(1.0)
        self.assertEqual(joules, 3600000.0)

        # Carbon grams: 1 kWh * 700 g/kWh = 700 g
        carbon_g = CarbonEngine.calculate_carbon_grams(3600000.0, 700.0)
        self.assertEqual(carbon_g, 700.0)

        # Normalized energy per transaction
        energy_per_tx = EnergyEngine.calculate_energy_per_transaction(700.0, 1000)
        self.assertAlmostEqual(energy_per_tx, 0.70, places=4)

    def test_02_attribution_conservation_waterfall(self):
        """Tests physical conservation equation: E_host - (E_cont + E_idle) = Residual."""
        res = AttributionEngine.evaluate_conservation(
            host_joules=1000.0,
            container_joules=800.0,
            idle_joules=150.0,
            tolerance_target_pct=6.0
        )
        self.assertEqual(res["accounted_energy_joules"], 950.0)
        self.assertEqual(res["residual_joules"], 50.0)
        self.assertEqual(res["residual_percent"], 5.0)
        self.assertEqual(res["attribution_fidelity_percent"], 95.0)
        self.assertEqual(res["status"], "PASS")

        # Test failure condition (> 6% residual)
        res_fail = AttributionEngine.evaluate_conservation(
            host_joules=1000.0,
            container_joules=750.0,
            idle_joules=150.0,
            tolerance_target_pct=6.0
        )
        self.assertEqual(res_fail["residual_percent"], 10.0)
        self.assertEqual(res_fail["status"], "ATTRIBUTION_DRIFT")

    def test_03_repeatability_cv(self):
        """Tests Coefficient of Variation (CV = sigma / mu * 100)."""
        samples = [0.70, 0.71, 0.69, 0.70, 0.72]
        stats = AttributionEngine.calculate_cv(samples)
        self.assertGreater(stats["mean"], 0.69)
        self.assertLess(stats["cv_percent"], 5.0)
        self.assertTrue(stats["is_stable"])

    def test_04_dynamic_threshold_calculation_by_criticality(self):
        """Tests that CRITICAL services have tighter dynamic threshold bands than LOW services."""
        cfg_crit = DynamicThresholdConfig(
            service_name="payment-service",
            criticality="CRITICAL",
            risk_appetite="LOW",
            baseline_mean_j=0.70,
            baseline_std_j=0.03
        )
        t_crit = cfg_crit.compute_effective_thresholds()

        cfg_low = DynamicThresholdConfig(
            service_name="analytics-service",
            criticality="LOW",
            risk_appetite="HIGH",
            baseline_mean_j=0.70,
            baseline_std_j=0.03
        )
        t_low = cfg_low.compute_effective_thresholds()

        # Critical service should trigger warning earlier (lower warning Joules)
        self.assertLess(t_crit["warning_energy_j"], t_low["warning_energy_j"])
        self.assertLess(t_crit["critical_energy_j"], t_low["critical_energy_j"])

    def test_05_multi_window_persistence_filter(self):
        """
        Tests that an alert does NOT immediately trigger CRITICAL on a single spike,
        but triggers once persisted across configured consecutive windows (N=3).
        """
        # Reset counter
        threshold_engine._consecutive_breaches["payment-service"] = 0

        # Sample 1: Spike to 0.95J (Critical instant, but persistence = 1/3 -> Warning)
        res1 = threshold_engine.evaluate_sample(
            service_name="payment-service",
            current_energy_per_tx_j=0.95,
            current_residual_percent=5.0
        )
        self.assertEqual(res1["consecutive_breaches"], 1)
        self.assertFalse(res1["is_persistent"])
        self.assertEqual(res1["level"], "WARNING")  # Soft warning on first occurrence

        # Sample 2: Second breach
        res2 = threshold_engine.evaluate_sample(
            service_name="payment-service",
            current_energy_per_tx_j=0.95,
            current_residual_percent=5.0
        )
        self.assertEqual(res2["consecutive_breaches"], 2)
        self.assertFalse(res2["is_persistent"])

        # Sample 3: Third breach -> PERSISTENCE REACHED -> CRITICAL
        res3 = threshold_engine.evaluate_sample(
            service_name="payment-service",
            current_energy_per_tx_j=0.95,
            current_residual_percent=5.0
        )
        self.assertEqual(res3["consecutive_breaches"], 3)
        self.assertTrue(res3["is_persistent"])
        self.assertEqual(res3["level"], "CRITICAL")
        self.assertIn("breached critical", res3["explanation"]["summary"].lower())

    def test_06_explainable_alert_diagnostics(self):
        """Verifies explainability metadata structure."""
        res = threshold_engine.evaluate_sample(
            service_name="payment-service",
            current_energy_per_tx_j=0.92,
            current_residual_percent=7.5,
            latency_ms=145.0,
            cpu_utilization_pct=82.0
        )
        exp = res["explanation"]
        self.assertIn("summary", exp)
        self.assertGreaterEqual(len(exp["reasons"]), 1)
        self.assertGreaterEqual(len(exp["root_causes"]), 1)
        self.assertIn("remediation_actions", exp)

    def test_07_audit_digest_cryptography(self):
        """Tests SHA-256 tamper-evident digest creation and verification."""
        data = {"report_id": "EVR-001", "fidelity": 95.8, "status": "PASS"}
        digest = AuditEngine.generate_digest(data)
        self.assertTrue(AuditEngine.verify_digest(data, digest))

        # Tampered data should fail verification
        tampered = {"report_id": "EVR-001", "fidelity": 98.0, "status": "PASS"}
        self.assertFalse(AuditEngine.verify_digest(tampered, digest))

    def test_08_connection_onboarding_lifecycle(self):
        """Tests 4-step onboarding wizard and privacy guarantee."""
        # Handshake test
        test_res = connection_manager.provider.test_connection()
        self.assertIn(test_res["status"], ("CONNECTED", "REACHABLE_FALLBACK"))

        # Connect
        conn_res = connection_manager.connect(
            app_name="TestBank-Cluster",
            environment="Production",
            prometheus_url="http://localhost:9090",
            otel_endpoint="http://localhost:4318"
        )
        self.assertEqual(conn_res["step"], 2)

        # Service discovery
        services = connection_manager.provider.get_services()
        self.assertGreaterEqual(len(services), 4)

        # Trace discovery: verify ZERO financial PII (no accounts, cards, names)
        traces = connection_manager.provider.get_transactions(limit=5)
        self.assertEqual(len(traces), 5)
        for t in traces:
            self.assertIn("transaction_id", t)
            self.assertIn("trace_id", t)
            self.assertIn("service_path", t)
            self.assertNotIn("account_number", t)
            self.assertNotIn("card_number", t)
            self.assertNotIn("customer_name", t)

        # Advance step to 4 (baseline calibrated)
        status_4 = connection_manager.complete_step(4)
        self.assertTrue(status_4["baseline_calibrated"])
        self.assertTrue(status_4["monitoring_active"])

    def test_09_simulation_sandbox_scenarios(self):
        """Tests synthetic scenarios, batch workload, and what-if evaluation."""
        state = simulation_service.get_state()
        self.assertIn("NORMAL", state["active_scenario"])

        # Switch to Payment Spike
        switched = simulation_service.set_scenario("PAYMENT_SPIKE")
        self.assertEqual(switched["active_scenario"], "PAYMENT_SPIKE")

        # Run 100 transactions
        batch = simulation_service.generate_workload(count=100)
        self.assertEqual(batch["transactions_executed"], 100)
        self.assertGreater(batch["batch_total_energy_j"], 0)

        # What-if analysis
        what_if = simulation_service.evaluate_what_if(
            transaction_multiplier=2.0,
            energy_optimization_percent=-20.0,
            target_grid_factor_g_kwh=25.0
        )
        self.assertGreater(what_if["impact"]["carbon_reduction_kg"], 0)


if __name__ == "__main__":
    unittest.main()
