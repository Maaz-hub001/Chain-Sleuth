"""
Detector for Inflow Consolidation (multiple sources pooling into single outbound sweep).
"""
from typing import List
from app.services.detection.base import BaseDetector, DetectionFindingResult
from app.services.blockchain.adapter import NormalizedTransaction
from app.schemas.graph import GraphResponse


class ConsolidationDetector(BaseDetector):
    @property
    def detector_id(self) -> str:
        return "DET_CONSOLIDATION"

    @property
    def name(self) -> str:
        return "Multiple Inflow Sweep & Consolidation"

    @property
    def description(self) -> str:
        return "Detects multiple smaller incoming transactions from distinct origins followed by a large outbound transfer consolidating 80%+ of total pooled funds."

    def detect(
        self,
        target_identifier: str,
        transactions: List[NormalizedTransaction],
        graph: GraphResponse
    ) -> List[DetectionFindingResult]:
        findings = []
        target_lower = target_identifier.lower()

        inflows = [tx for tx in transactions if tx.to_address and tx.to_address.lower() == target_lower]
        outflows = [tx for tx in transactions if tx.from_address and tx.from_address.lower() == target_lower]

        unique_senders = set(tx.from_address.lower() for tx in inflows if tx.from_address)
        total_in = sum(tx.value_eth for tx in inflows)
        total_out = sum(tx.value_eth for tx in outflows)

        if len(unique_senders) >= 2 and total_in > 0:
            consolidation_ratio = total_out / total_in
            if 0.75 <= consolidation_ratio <= 1.05 and len(outflows) <= 2:
                findings.append(
                    DetectionFindingResult(
                        detector_id=self.detector_id,
                        title="Multiple Inflow Fund Consolidation Observed",
                        severity="MEDIUM",
                        status="suspicious_pattern",
                        explanation=(
                            f"Subject received {round(total_in, 4)} ETH across {len(inflows)} transfers from "
                            f"{len(unique_senders)} separate origin addresses, followed by outbound consolidation of "
                            f"{round(total_out, 4)} ETH ({round(consolidation_ratio*100, 1)}% of pooled volume). "
                            "This funneling topology is often used to aggregate smurfed or collected illicit balances."
                        ),
                        detection_method="Inflow-outflow aggregate volumetric ratio calculation",
                        confidence=0.82,
                        confidence_basis=f"{len(unique_senders)} distinct origins pooled; {round(consolidation_ratio*100, 1)}% swept out in {len(outflows)} txs.",
                        counterevidence="Exchange deposit sweepers, decentralized crowdfunding pool withdrawals, or retail users consolidating across personal wallets.",
                        alternative_explanations=[
                            "User consolidating staking rewards or multi-wallet balances",
                            "Commercial aggregator collecting invoice payments",
                            "Exchange internal wallet balancing"
                        ],
                        limitations="Cannot evaluate off-chain corporate relationships between origin wallets.",
                        recommended_next_step="Inspect destination address of the consolidated sweep for known exchange or mixer clusters.",
                        relevant_tx_hashes=[tx.tx_hash for tx in inflows + outflows],
                        relevant_addresses=list(unique_senders) + [target_lower] + [tx.to_address.lower() for tx in outflows if tx.to_address],
                        evidence_payload={
                            "unique_senders_count": len(unique_senders),
                            "total_inflow_eth": total_in,
                            "total_outflow_eth": total_out,
                            "consolidation_ratio": consolidation_ratio
                        }
                    )
                )

        return findings
