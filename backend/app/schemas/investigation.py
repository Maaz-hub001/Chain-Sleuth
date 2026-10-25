"""
Pydantic schemas for Investigations.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class InvestigationCreate(BaseModel):
    target_identifier: str = Field(..., description="EVM wallet address or transaction hash")
    network_name: str = Field(default="ethereum_mainnet", description="Network name")
    chain_id: int = Field(default=1, description="EVM Chain ID")
    investigation_type: str = Field(
        default="comprehensive",
        description="Type: wallet_overview, transaction_tracing, connected_wallet, suspicious_pattern, comprehensive"
    )
    max_depth: int = Field(default=2, ge=1, le=3, description="Graph exploration depth")
    max_transactions: int = Field(default=100, ge=10, le=500, description="Max transactions to process")
    investigator_notes: Optional[str] = Field(None, max_length=1000, description="Investigator notes")
    use_demo_fixture: bool = Field(default=False, description="Use reproducible test fixture if offline")


class InvestigationResponse(BaseModel):
    id: str
    target_identifier: str
    target_type: str
    network_name: str
    chain_id: int
    investigation_type: str
    status: str
    error_message: Optional[str] = None
    max_depth: int
    max_transactions: int
    investigator_notes: Optional[str] = None
    coverage_summary: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvestigationStatusResponse(BaseModel):
    id: str
    status: str
    target_identifier: str
    findings_count: int = 0
    transactions_count: int = 0
    nodes_count: int = 0
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
