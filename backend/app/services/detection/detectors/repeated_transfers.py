"""
Detector for Repeated Identical / Structuring Transfers (Smurfing).
"""
from typing import List
from collections import defaultdict
from app.services.detection.base import BaseDetector, DetectionFindingResult
from app.services.blockchain.adapter import NormalizedTransaction
from app.schemas.graph import GraphResponse


class RepeatedTransfersDetector(BaseDetector):
    @property
    def detector_id(self) -> str:
        return "DET_REPEATED_STRUCTURING"

    @property
    def name(self) -> str:
        return "Repeated Structured Transfers (Smurfing Candidate)"

    @property
    def description(self) -> str:
        return "Identifies multiple transfers of identical or near-identical amounts within a short window, characteristic of structuring."

    def detect(
        self,
        target_identifier: str,
        transactions: List[NormalizedTransaction],
        graph: GraphResponse
    ) -> List[DetectionFindingResult]:
        findings = []
        target_lower = target_identifier.lower()

        # Group by sender-recipient pair or amount buckets
        amount_groups = defaultdict(list)
        for tx in transactions:
            if tx.value_eth > 0.05:
                # Round to 1 decimal place to capture near-identical tranches (e.g. 15.0 ETH, 14.8 ETH)
                rounded_val = round(tx.value_eth, 0)
                amount_groups[rounded_val].append(tx)

        for amt, group in amount_groups.items():
            if len(group) >= 2:
                timestamps = [t.block_timestamp for t in group]
                time_span = max(timestamps) - min(timestamps)
                if time_span <= 3600:  # within 1 hour
                    tx_hashes = [t.tx_hash for t in group]
                    addrs = set()
                    for t in group:
                        if t.from_address:
                            addrs.add(t.from_address.lower())
                        if t.to_address:
                            addrs.add(t.to_address.lower())

                    findings.append(
                        DetectionFindingResult(
                            detector_id=self.detector_id,
                            title=f"Structured Repeated Transfers ({amt} ETH Tranches)",
                            severity="MEDIUM",
                            status="suspicious_pattern",
                            explanation=(
                                f"Detected {len(group)} transactions of approximately {amt} ETH executed within "
                                f"{time_span} seconds ({round(time_span/60, 1)} minutes). Dividing larger amounts into "
                                "consistent sub-threshold tranches (smurfing/structuring) is a classic tactic used to evade "
                                "single-transaction threshold reporting or automated anomaly triggers."
                            ),
                            detection_method="Value clustering & temporal proximity evaluation",
                            confidence=0.84,
                            confidence_basis=f"{len(group)} transactions clustered around {amt} ETH within {time_span}s.",
                            counterevidence="Recurring automated subscription/DCA orders, scheduled staking operations, or fixed-denomination payouts.",
                            alternative_explanations=[
                                "Algorithmic DCA (Dollar-Cost-Averaging) execution",
                                "Fixed collateral installment deposit",
                                "Automated server hosting or subscription renewal"
                            ],
                            limitations="Threshold slicing is heuristic; does not guarantee intentional regulatory structuring without KYC context.",
                            recommended_next_step="Inspect destination addresses to assess whether funds are reaching centralized exchange deposit wallets.",
                            relevant_tx_hashes=tx_hashes,
                            relevant_addresses=list(addrs),
                            evidence_payload={
                                "cluster_amount_eth": amt,
                                "matched_tx_count": len(group),
                                "time_span_seconds": time_span
                            }
                        )
                    )
                    break

        return findings
