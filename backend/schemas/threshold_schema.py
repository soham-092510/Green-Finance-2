# =====================================================================
# GREEN-FINANCE — THRESHOLD_SCHEMA.PY (PYDANTIC SCHEMAS)
# =====================================================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ThresholdUpdateRequest(BaseModel):
    service_name: str
    criticality: Optional[str] = "CRITICAL"
    risk_appetite: Optional[str] = "LOW"
    baseline_mean_j: Optional[float] = 0.70
    baseline_std_j: Optional[float] = 0.03
    warning_sigma: Optional[float] = 2.0
    critical_sigma: Optional[float] = 3.0
    max_residual_percent: Optional[float] = 6.0
    measurement_uncertainty_percent: Optional[float] = 4.0
    alert_persistence_windows: Optional[int] = 3
    carbon_intensity_g_kwh: Optional[float] = 700.0


class ThresholdEvaluationRequest(BaseModel):
    service_name: str
    current_energy_per_tx_j: float
    current_residual_percent: Optional[float] = 5.0
    latency_ms: Optional[float] = 45.0
    cpu_utilization_pct: Optional[float] = 40.0
