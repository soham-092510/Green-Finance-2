# =====================================================================
# GREEN-FINANCE — CONNECTION_SCHEMA.PY (PYDANTIC SCHEMAS)
# =====================================================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ConnectRequest(BaseModel):
    application_name: str = Field(default="CoreBanking-Cluster", description="Name of financial application")
    environment: str = Field(default="Production", description="Staging, UAT, or Production")
    prometheus_url: str = Field(default="http://localhost:9090", description="Prometheus PromQL HTTP endpoint")
    otel_endpoint: str = Field(default="http://localhost:4318", description="OpenTelemetry collector endpoint")
    integration_type: str = Field(default="opentelemetry", description="opentelemetry, prometheus, or kubernetes")


class TestConnectionRequest(BaseModel):
    prometheus_url: Optional[str] = "http://localhost:9090"
    otel_endpoint: Optional[str] = "http://localhost:4318"


class ConnectionStatusResponse(BaseModel):
    connection_id: str
    app_name: str
    environment: str
    step: int
    monitoring_active: bool
    baseline_calibrated: bool
    connected: bool
    discovered_services_count: int


class IngestTraceRequest(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction or idempotency identifier (e.g. TXN-99824)")
    trace_id: Optional[str] = Field(None, description="OpenTelemetry traceparent or trace ID")
    transaction_type: Optional[str] = Field(default="PAYMENT", description="Transaction type (PAYMENT, UPI, TRANSFER, AUTH, SETTLEMENT)")
    services: Optional[List[str]] = Field(default=["auth-service", "payment-service", "ledger-service"], description="List of financial microservices traversed by the request")
    duration_ms: Optional[float] = Field(default=120.0, description="End-to-end request latency in milliseconds")
    cpu_utilization_pct: Optional[float] = Field(default=45.0, description="Average container CPU utilization during processing")
    grid_carbon_factor_g_kwh: Optional[float] = Field(default=700.0, description="Regional grid carbon intensity factor (g CO2e / kWh)")
    sender_bank_id: Optional[str] = Field(default="HDFC9999", description="Source bank identifier")
    recipient_bank_id: Optional[str] = Field(default="MAH123", description="Recipient bank identifier")
    amount: Optional[float] = Field(default=1000.0, description="Transaction amount in INR")
    energy_joules: Optional[float] = Field(default=None, description="Attributed energy in Joules")
    carbon_grams: Optional[float] = Field(default=None, description="Estimated carbon in grams")
    audit_hash: Optional[str] = Field(default=None, description="Cryptographic SHA-256 digest")

