"""
Base interface and data contracts for deterministic detection rules.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from app.services.blockchain.adapter import NormalizedTransaction
from app.schemas.graph import GraphResponse


@dataclass
class DetectionFindingResult:
    detector_id: str
    title: str
    severity: str  # "INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"
    status: str    # "confirmed_observation", "suspicious_pattern", "unverified_intelligence", "insufficient_evidence"
    explanation: str
    detection_method: str
    confidence: float
    confidence_basis: str
    counterevidence: Optional[str] = None
    alternative_explanations: List[str] = field(default_factory=list)
    limitations: Optional[str] = None
    recommended_next_step: Optional[str] = None
    relevant_tx_hashes: List[str] = field(default_factory=list)
    relevant_addresses: List[str] = field(default_factory=list)
    evidence_payload: Dict[str, Any] = field(default_factory=dict)


class BaseDetector(ABC):
    @property
    @abstractmethod
    def detector_id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def detect(
        self,
        target_identifier: str,
        transactions: List[NormalizedTransaction],
        graph: GraphResponse
    ) -> List[DetectionFindingResult]:
        pass
