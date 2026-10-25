"""
Deterministic Detection Engine: coordinates and executes all detectors,
links findings to atomic evidence records, and compiles risk summaries.
"""
import uuid
from typing import List, Dict, Any, Tuple
from app.services.detection.base import BaseDetector, DetectionFindingResult
from app.services.detection.detectors.fan_in_out import FanInOutDetector
from app.services.detection.detectors.rapid_movement import RapidMovementDetector
from app.services.detection.detectors.consolidation import ConsolidationDetector
from app.services.detection.detectors.circular import CircularTransferDetector
from app.services.detection.detectors.repeated_transfers import RepeatedTransfersDetector
from app.services.detection.detectors.known_entity import KnownEntityDetector
from app.services.blockchain.adapter import NormalizedTransaction
from app.schemas.graph import GraphResponse
from app.schemas.finding import FindingSchema, EvidenceSchema


class DetectionEngine:
    def __init__(self):
        self.detectors: List[BaseDetector] = [
            KnownEntityDetector(),
            CircularTransferDetector(),
            RapidMovementDetector(),
            FanInOutDetector(),
            ConsolidationDetector(),
            RepeatedTransfersDetector(),
        ]

    def run_all(
        self,
        investigation_id: str,
        target_identifier: str,
        transactions: List[NormalizedTransaction],
        graph: GraphResponse
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Executes all registered detection rules.
        Returns:
            findings_dicts: List of dictionaries matching Finding model
            evidence_dicts: List of dictionaries matching Evidence model
        """
        findings_out = []
        evidence_out = []

        seen_finding_keys = set()

        for detector in self.detectors:
            try:
                results: List[DetectionFindingResult] = detector.detect(target_identifier, transactions, graph)
                for res in results:
                    dedup_key = f"{res.detector_id}:{res.title}"
                    if dedup_key in seen_finding_keys:
                        continue
                    seen_finding_keys.add(dedup_key)

                    finding_id = f"find-{uuid.uuid4().hex[:12]}"
                    linked_evidence_ids = []

                    # 1. Create on-chain transaction evidence items
                    for tx_hash in res.relevant_tx_hashes[:5]:
                        ev_id = f"ev-{uuid.uuid4().hex[:10]}"
                        linked_evidence_ids.append(ev_id)
                        evidence_out.append({
                            "id": ev_id,
                            "investigation_id": investigation_id,
                            "finding_id": finding_id,
                            "evidence_type": "on_chain_transaction",
                            "title": f"Transaction Evidence: {tx_hash[:10]}...",
                            "description": f"Observed on-chain transaction referenced in finding '{res.title}'.",
                            "raw_reference": tx_hash,
                            "data_provenance": "blockchain_record",
                            "payload": {"tx_hash": tx_hash}
                        })

                    # 2. Create address counterparty evidence item
                    for addr in res.relevant_addresses[:4]:
                        ev_id = f"ev-{uuid.uuid4().hex[:10]}"
                        linked_evidence_ids.append(ev_id)
                        evidence_out.append({
                            "id": ev_id,
                            "investigation_id": investigation_id,
                            "finding_id": finding_id,
                            "evidence_type": "address_node",
                            "title": f"Address Node: {addr[:10]}...",
                            "description": f"Network address involved in pattern: {addr}",
                            "raw_reference": addr,
                            "data_provenance": "graph_node",
                            "payload": {"address": addr}
                        })

                    findings_out.append({
                        "id": finding_id,
                        "investigation_id": investigation_id,
                        "detector_id": res.detector_id,
                        "title": res.title,
                        "severity": res.severity,
                        "status": res.status,
                        "explanation": res.explanation,
                        "detection_method": res.detection_method,
                        "confidence": res.confidence,
                        "confidence_basis": res.confidence_basis,
                        "counterevidence": res.counterevidence,
                        "alternative_explanations": res.alternative_explanations,
                        "limitations": res.limitations,
                        "recommended_next_step": res.recommended_next_step,
                        "evidence_ids": linked_evidence_ids,
                        "relevant_tx_hashes": res.relevant_tx_hashes,
                        "relevant_addresses": res.relevant_addresses
                    })

            except Exception as e:
                # Resilient execution: one detector failing does not break the entire engine
                continue

        return findings_out, evidence_out


detection_engine = DetectionEngine()
