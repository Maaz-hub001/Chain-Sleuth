"""
Pydantic schemas for Provider Health and Application Settings.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ProviderStatus(BaseModel):
    name: str
    category: str  # "blockchain_rpc", "explorer_api", "llm", "vector_store"
    status: str  # "operational", "not_configured", "degraded", "error"
    endpoint_display: str
    details: Optional[str] = None
    response_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    providers_summary: Dict[str, str]


class ProvidersHealthResponse(BaseModel):
    timestamp: str
    providers: List[ProviderStatus]


class ProviderTestRequest(BaseModel):
    provider_name: str
    endpoint_url: Optional[str] = None
    api_key: Optional[str] = None


class ProviderTestResponse(BaseModel):
    provider_name: str
    success: bool
    status: str
    message: str
    latency_ms: Optional[float] = None
