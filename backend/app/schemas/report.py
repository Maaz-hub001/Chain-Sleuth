"""
Pydantic schemas for Investigation Reports and Tamper-Evident Verification.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ReportFindingItem(BaseModel):
    finding_id: str
    detector_id: str
    title: str
    severity: str
    status: str
    explanation: str
    evidence_ids: List[str]
    supporting_transactions: List[str]
    supporting_sources: List[str]
    confidence: float
    confidence_basis: str
    alternative_explanations: List[str]
    limitations: str


class ReportEvidenceItem(BaseModel):
    evidence_id: str
    evidence_type: str
    title: str
    description: str
    raw_reference: str
    data_provenance: str


class ReportStructuredPayload(BaseModel):
    report_id: str
    schema_version: str = "1.0.0"
    investigation_id: str
    generated_at: str
    chain_id: int
    network_name: str
    target_type: str
    target_identifier: str
    investigation_scope: Dict[str, Any]
    data_sources: List[str]
    coverage_summary: Dict[str, Any]
    observed_facts: List[str]
    findings: List[ReportFindingItem]
    supporting_evidence: List[ReportEvidenceItem]
    counterevidence: List[str]
    intelligence_references: List[Dict[str, Any]]
    graph_paths: List[Dict[str, Any]]
    unresolved_questions: List[str]
    limitations: List[str]
    recommended_next_steps: List[str]


class ReportResponse(BaseModel):
    id: str
    investigation_id: str
    schema_version: str
    canonical_version: str
    hash_algorithm: str
    report_hash: str
    target_identifier: str
    target_type: str
    chain_id: int
    network_name: str
    content_json: Dict[str, Any]
    markdown_content: str
    is_anchored: bool
    registry_chain_id: Optional[int] = None
    registry_contract_address: Optional[str] = None
    registry_tx_hash: Optional[str] = None
    anchored_timestamp: Optional[int] = None
    generated_at: datetime

    class Config:
        from_attributes = True


class ReportVerificationRequest(BaseModel):
    report_id: Optional[str] = None
    report_payload: Dict[str, Any]
    expected_hash: Optional[str] = None
    verify_on_chain: bool = False


class ReportVerificationResponse(BaseModel):
    is_valid: bool
    computed_hash: str
    claimed_hash: str
    hash_algorithm: str = "SHA-256"
    canonical_version: str = "1.0.0"
    mismatch_fields: List[str] = []
    
    # On-chain details
    on_chain_checked: bool = False
    on_chain_verified: bool = False
    on_chain_block: Optional[int] = None
    on_chain_reporter: Optional[str] = None
    on_chain_timestamp: Optional[int] = None
    registry_contract_address: Optional[str] = None
    
    status_summary: str
