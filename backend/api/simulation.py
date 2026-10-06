# =====================================================================
# GREEN-FINANCE — SIMULATION.PY (API ROUTER)
# =====================================================================
# Purpose: Endpoints for Synthetic Banking Sandbox (Mode 1):
#          - GET /simulation/state: Current simulation state and active scenario
#          - POST /simulation/scenario: Switch scenario (Normal, Spike, Drift, etc.)
#          - POST /simulation/workload: Execute synthetic batch transactions
#          - POST /simulation/what-if: Evaluate architectural & grid what-if scenarios
# =====================================================================

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from backend.services.simulation_service import simulation_service

router = APIRouter(prefix="/simulation", tags=["Simulation Sandbox (Mode 1)"])


class ScenarioSwitchRequest(BaseModel):
    scenario: str = Field(default="NORMAL", description="NORMAL, TRAFFIC_SPIKE, PAYMENT_SPIKE, LEDGER_BOTTLENECK, TELEMETRY_DRIFT, TELEMETRY_NOISE, HIGH_CARBON_GRID")


class WorkloadRequest(BaseModel):
    count: int = Field(default=500, description="Number of synthetic transactions (10 to 10000)")
    amount: float = Field(default=1000.0, description="Nominal transaction amount in INR")


class WhatIfRequest(BaseModel):
    transaction_multiplier: float = Field(default=1.5, description="Workload scale factor")
    energy_optimization_percent: float = Field(default=-15.0, description="Expected efficiency gain %")
    target_grid_factor_g_kwh: float = Field(default=25.0, description="Target grid carbon intensity (e.g. 25 g/kWh for green PPA)")


@router.get("/state", summary="Get current simulation state and active scenario")
def get_simulation_state() -> Dict[str, Any]:
    """
    Returns the current simulation parameters, cumulative energy/carbon,
    and active fault-injection scenario.
    """
    return simulation_service.get_state()


@router.post("/scenario", summary="Switch the active simulation scenario")
def set_simulation_scenario(payload: ScenarioSwitchRequest) -> Dict[str, Any]:
    """
    Switches the active simulation scenario:
    - NORMAL: Healthy baseline operations
    - TRAFFIC_SPIKE: Workload surge (+300% transactions)
    - PAYMENT_SPIKE: Payment service CPU inefficiency (+30% energy/tx)
    - LEDGER_BOTTLENECK: DB lock contention and prolonged latency
    - TELEMETRY_DRIFT: Un-instrumented load causing residual > 6%
    - TELEMETRY_NOISE: High frequency sensor fluctuation
    - HIGH_CARBON_GRID: Data center failover to coal grid (820 g/kWh)
    """
    return simulation_service.set_scenario(payload.scenario)


@router.post("/workload", summary="Generate a synthetic batch of banking transactions")
def generate_simulation_workload(payload: WorkloadRequest) -> Dict[str, Any]:
    """
    Executes a batch of N simulated transactions under the active scenario,
    computing energy attribution, repeatability CV %, and carbon emissions.
    """
    return simulation_service.generate_workload(
        count=payload.count,
        amount=payload.amount
    )


@router.post("/what-if", summary="Evaluate What-If infrastructure & carbon projections")
def evaluate_what_if_scenario(payload: WhatIfRequest) -> Dict[str, Any]:
    """
    Projects energy and carbon deltas under hypothetical traffic growth,
    code optimization, and green power purchase agreements (PPAs).
    """
    return simulation_service.evaluate_what_if(
        transaction_multiplier=payload.transaction_multiplier,
        energy_optimization_percent=payload.energy_optimization_percent,
        target_grid_factor_g_kwh=payload.target_grid_factor_g_kwh
    )
