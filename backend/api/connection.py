# =====================================================================
# GREEN-FINANCE — CONNECTION.PY (API ROUTER)
# =====================================================================
# Purpose: Endpoints for Real Financial Application Telemetry Onboarding:
#          - POST /connection/test: Non-disruptive connectivity handshake
#          - POST /connection/connect: Initialize enterprise connection profile
#          - GET /connection/status: Current connection step and state
#          - GET /connection/discover/services: Auto-discovered microservices
#          - GET /connection/discover/traces: Privacy-preserving traces (no PII)
#          - POST /connection/advance-step: 4-step onboarding state transitions
#          - GET /connection/realtime: Live fleet energy, residual, and fidelity
#          - GET /connection/efficiency: Service efficiency vs historical baseline
# =====================================================================

from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Optional, Any
from backend.schemas.connection_schema import (
    ConnectRequest, TestConnectionRequest, ConnectionStatusResponse, IngestTraceRequest
)
from backend.services.connection_service import connection_manager

router = APIRouter(prefix="/connection", tags=["Enterprise Application Connection (Mode 2)"])


@router.post("/test", summary="Test reachability of Prometheus and OpenTelemetry endpoints")
def test_connection_endpoints(payload: TestConnectionRequest) -> Dict[str, Any]:
    """
    Executes a non-intrusive network handshake to verify that the banking
    cluster's Prometheus and OpenTelemetry endpoints are responding.
    """
    return connection_manager.provider.test_connection(
        prometheus_url=payload.prometheus_url,
        otel_endpoint=payload.otel_endpoint
    )


@router.post("/connect", summary="Connect Green-Finance to an external financial application")
def connect_application(payload: ConnectRequest) -> Dict[str, Any]:
    """
    Step 1: Connects the platform to the target financial infrastructure.
    Sets up the application profile and discovers available telemetry endpoints.
    """
    return connection_manager.connect(
        app_name=payload.application_name,
        environment=payload.environment,
        prometheus_url=payload.prometheus_url,
        otel_endpoint=payload.otel_endpoint
    )


@router.get("/status", summary="Get connection lifecycle status and onboarding step")
def get_connection_status() -> Dict[str, Any]:
    """
    Returns active connection metadata, current onboarding step (1 to 4),
    and telemetry stream health.
    """
    return connection_manager.get_status()


@router.post("/advance-step", summary="Advance the 4-step connection onboarding wizard")
def advance_connection_step(target_step: int) -> Dict[str, Any]:
    """
    Advances the connection lifecycle state:
    1: Connect -> 2: Auto-Discover -> 3: Trace Mapping -> 4: Off-Peak Baseline -> 5: Active Monitoring.
    """
    return connection_manager.complete_step(target_step)


@router.get("/discover/services", summary="Auto-discover microservices and container pods")
def discover_services() -> List[Dict[str, Any]]:
    """
    Step 2: Auto-discovers financial microservices (e.g. Payment, Ledger, Fraud, Auth)
    and their running container pods from Kubernetes/Docker labels.
    """
    return connection_manager.provider.get_services()


@router.get("/discover/traces", summary="Ingest live transaction traces (Zero Financial PII)")
def discover_transaction_traces(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Step 3: Observes distributed traces flowing through OpenTelemetry.
    PRIVACY GUARANTEE: Collects only trace ID, span duration, and service call paths.
    Never touches customer names, balances, cards, or transaction amounts.
    """
    return connection_manager.provider.get_transactions(limit=limit)


@router.get("/realtime", summary="Get live real-world energy and attribution metrics")
def get_realtime_connection_metrics() -> Dict[str, Any]:
    """
    Returns real-time host power, container cgroups allocation,
    unaccounted residual, and attribution fidelity for the connected cluster.
    """
    return connection_manager.provider.get_live_power()


@router.get("/efficiency", summary="Financial microservice efficiency vs historical baseline")
def get_service_efficiency_breakdown() -> List[Dict[str, Any]]:
    """
    Returns per-service normalized energy per transaction (Joules/tx)
    compared against historical baselines to flag efficiency regressions.
    """
    return connection_manager.provider.get_efficiency_breakdown()


@router.post("/ingest-trace", summary="Directly ingest transaction trace from a real payment application")
def ingest_payment_transaction_trace(payload: IngestTraceRequest) -> Dict[str, Any]:
    """
    Directly ingests a completed payment transaction trace emitted by a real external
    banking application, payment gateway, or microservice.
    Attributes container energy, calculates carbon emissions (Scope 2), evaluates
    against Basel risk thresholds, and logs an audited record.
    """
    return connection_manager.provider.ingest_external_transaction(
        transaction_id=payload.transaction_id,
        trace_id=payload.trace_id,
        transaction_type=payload.transaction_type or "PAYMENT",
        services=payload.services,
        duration_ms=payload.duration_ms or 120.0,
        cpu_utilization_pct=payload.cpu_utilization_pct or 45.0,
        grid_carbon_factor_g_kwh=payload.grid_carbon_factor_g_kwh or 700.0,
        sender_bank_id=payload.sender_bank_id,
        recipient_bank_id=payload.recipient_bank_id,
        amount=payload.amount,
        energy_joules=payload.energy_joules,
        carbon_grams=payload.carbon_grams,
        audit_hash=payload.audit_hash
    )

