"""
Pydantic schemas for Findings and Evidence.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class EvidenceSchema(BaseModel):
    id: str
    evidence_type: str
    title: str
    description: str
    raw_reference: str
    data_provenance: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FindingSchema(BaseModel):
    id: str
    investigation_id: str
    detector_id: str
    title: str
    severity: str  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    status: str  # confirmed_observation, suspicious_pattern, unverified_intelligence, insufficient_evidence
    explanation: str
    detection_method: str
    confidence: float
    confidence_basis: str
    counterevidence: Optional[str] = None
    alternative_explanations: Optional[List[str]] = None
    limitations: Optional[str] = None
    recommended_next_step: Optional[str] = None
    evidence_ids: Optional[List[str]] = None
    relevant_tx_hashes: Optional[List[str]] = None
    relevant_addresses: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FindingListResponse(BaseModel):
    investigation_id: str
    total: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    findings: List[FindingSchema]
