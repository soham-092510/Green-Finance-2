# =====================================================================
# GREEN-FINANCE — THRESHOLDS.PY (API ROUTER)
# =====================================================================
# Purpose: Endpoints for Basel-Aligned Dynamic Threshold Engine:
#          - GET /thresholds/configs: List all configured service profiles
#          - POST /thresholds/config: Update service risk appetite & criticality
#          - GET /thresholds/alerts: Active explainable alerts
#          - POST /thresholds/evaluate: Evaluate telemetry against dynamic thresholds
# =====================================================================

from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Optional, Any
from backend.schemas.threshold_schema import ThresholdUpdateRequest, ThresholdEvaluationRequest
from backend.services.threshold_service import threshold_engine

router = APIRouter(prefix="/thresholds", tags=["Dynamic Risk Threshold Engine"])


@router.get("/configs", summary="List all service dynamic risk threshold configurations")
def get_threshold_configs() -> List[Dict[str, Any]]:
    """
    Returns configured thresholds for each financial service (Payment, Ledger, Auth, etc.)
    including bank risk appetite, criticality, sigma sensitivity, and persistence rules.
    """
    return threshold_engine.get_all_configs()


@router.post("/config", summary="Update dynamic threshold parameters for a service")
def update_threshold_config(payload: ThresholdUpdateRequest) -> Dict[str, Any]:
    """
    Updates the risk parameters for a specific service:
    - Service Criticality: CRITICAL, MEDIUM, LOW
    - Bank Risk Appetite: LOW, MEDIUM, HIGH
    - Multi-window Alert Persistence target (e.g. 3 consecutive windows)
    """
    updated = threshold_engine.update_config(
        service_name=payload.service_name,
        updates=payload.model_dump(exclude_unset=True)
    )
    return updated.to_dict()


@router.get("/alerts", summary="Get active explainable alerts with root-cause diagnostics")
def get_active_alerts() -> List[Dict[str, Any]]:
    """
    Returns active WARNING or CRITICAL alerts.
    Includes mathematical rationale, baseline comparison, and root-cause indicators.
    """
    return threshold_engine.get_active_alerts()


@router.post("/evaluate", summary="Evaluate a live telemetry sample against dynamic thresholds")
def evaluate_telemetry_sample(payload: ThresholdEvaluationRequest) -> Dict[str, Any]:
    """
    Tests an incoming sample against dynamic thresholds, applies persistence filtering,
    and returns comprehensive explainable diagnostics.
    """
    return threshold_engine.evaluate_sample(
        service_name=payload.service_name,
        current_energy_per_tx_j=payload.current_energy_per_tx_j,
        current_residual_percent=payload.current_residual_percent or 5.0,
        latency_ms=payload.latency_ms or 45.0,
        cpu_utilization_pct=payload.cpu_utilization_pct or 40.0
    )
