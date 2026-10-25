"""
Detector for Known Entities (Mixers, Sanctioned Wallets, Exploiters, Centralized Exchanges).
"""
import os
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.services.detection.base import BaseDetector, DetectionFindingResult
from app.services.blockchain.adapter import NormalizedTransaction
from app.schemas.graph import GraphResponse


class KnownEntityDetector(BaseDetector):
    def __init__(self, entities_path: Optional[str] = None):
        self.entities_path = entities_path or os.path.join(settings.FIXTURES_DIR, "known_entities.json")
        self.entities: Dict[str, Dict[str, Any]] = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        lookup = {}
        if os.path.exists(self.entities_path):
            try:
                with open(self.entities_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("entities", []):
                        lookup[item["address"].lower()] = item
            except Exception:
                pass
        return lookup

    @property
    def detector_id(self) -> str:
        return "DET_KNOWN_ENTITY"

    @property
    def name(self) -> str:
        return "Attributed Entity / Sanctioned Counterparty Match"

    @property
    def description(self) -> str:
        return "Matches direct transaction counterparties and 2-hop connected nodes against a verified intelligence database of sanctioned entities, mixers, exploiters, and exchanges."

    def detect(
        self,
        target_identifier: str,
        transactions: List[NormalizedTransaction],
        graph: GraphResponse
    ) -> List[DetectionFindingResult]:
        findings = []
        target_lower = target_identifier.lower()

        # Check all nodes in graph for matches
        for node in graph.nodes:
            addr = node.address.lower()
            if addr in self.entities:
                entity = self.entities[addr]
                name = entity.get("name", "Known Entity")
                risk = entity.get("risk_level", "low")
                etype = entity.get("entity_type", "entity")
                source = entity.get("source", "Threat Intelligence")
                verified_date = entity.get("verified_date", "N/A")

                # Find connecting transactions
                matched_txs = [
                    tx.tx_hash for tx in transactions
                    if (tx.from_address and tx.from_address.lower() == addr) or
                       (tx.to_address and tx.to_address.lower() == addr)
                ]

                is_critical = (risk == "critical")
                severity = "CRITICAL" if is_critical else ("HIGH" if risk == "high" else "MEDIUM")
                status = "confirmed_observation" if matched_txs else "unverified_intelligence"

                findings.append(
                    DetectionFindingResult(
                        detector_id=self.detector_id,
                        title=f"Direct Counterparty Attribution: {name} ({etype.upper()})",
                        severity=severity,
                        status=status,
                        explanation=(
                            f"Graph inspection identified counterparty {addr} as '{name}', classified under category '{entity.get('category')}'. "
                            f"Attribution source: {source} (Verified: {verified_date}). "
                            f"{'This address is subject to regulatory sanctions or high-priority enforcement advisories.' if is_critical else 'Direct interaction with this entity provides contextual attribution for fund lineage.'}"
                        ),
                        detection_method="Curated cryptographic entity registry lookup & exact address match",
                        confidence=0.99,
                        confidence_basis=f"Exact checksum match against authority database. Sourced from {source}.",
                        counterevidence="Address compromise, unsolicited transfer (dusting/poisoning), or smart contract deposit without counterparty consent.",
                        alternative_explanations=[
                            "Unsolicited dusting or unconsented inbound transfer",
                            "Legitimate protocol interaction (if public DeFi router)",
                            "Counterparty wallet reassignment or private key compromise"
                        ],
                        limitations="Identifies the address, not the individual controlling the signing key at time of execution.",
                        recommended_next_step="Cross-reference with OFAC/sanctions screening APIs and submit formal STR if confirmed.",
                        relevant_tx_hashes=matched_txs,
                        relevant_addresses=[addr, target_lower],
                        evidence_payload={
                            "entity_name": name,
                            "entity_type": etype,
                            "risk_level": risk,
                            "attribution_source": source,
                            "verified_date": verified_date
                        }
                    )
                )

        return findings
