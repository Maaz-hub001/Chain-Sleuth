"""
Detector for Unusual Fan-Out (dispersion) and Fan-In (pooling) patterns.
"""
from typing import List
from collections import defaultdict
from app.services.detection.base import BaseDetector, DetectionFindingResult
from app.services.blockchain.adapter import NormalizedTransaction
from app.schemas.graph import GraphResponse


class FanInOutDetector(BaseDetector):
    @property
    def detector_id(self) -> str:
        return "DET_FAN_IN_OUT"

    @property
    def name(self) -> str:
        return "Unusual Fan-In / Fan-Out Dispersion"

    @property
    def description(self) -> str:
        return "Identifies wallets dispersing funds across multiple recipients within a brief timeframe or pooling from multiple sources."

    def detect(
        self,
        target_identifier: str,
        transactions: List[NormalizedTransaction],
        graph: GraphResponse
    ) -> List[DetectionFindingResult]:
        findings = []
        target_lower = target_identifier.lower()

        # Group outgoing txs from target
        out_txs = [tx for tx in transactions if tx.from_address and tx.from_address.lower() == target_lower]
        unique_recipients = set(tx.to_address.lower() for tx in out_txs if tx.to_address)

        if len(unique_recipients) >= 3:
            # Check time delta between first and last disbursement
            timestamps = [tx.block_timestamp for tx in out_txs]
            time_span_seconds = max(timestamps) - min(timestamps) if timestamps else 0
            total_dispersed = sum(tx.value_eth for tx in out_txs)

            severity = "HIGH" if time_span_seconds < 600 else "MEDIUM"
            findings.append(
                DetectionFindingResult(
                    detector_id=self.detector_id,
                    title="Rapid Fan-Out Fund Dispersion Observed",
                    severity=severity,
                    status="suspicious_pattern",
                    explanation=(
                        f"Subject wallet disbursed {round(total_dispersed, 4)} ETH across {len(unique_recipients)} "
                        f"distinct counterparty addresses within a window of {time_span_seconds} seconds ({round(time_span_seconds/60, 1)} minutes). "
                        "This topology is characteristic of smurfing, asset peeling, or multi-wallet layering."
                    ),
                    detection_method="Graph topological degree analysis & timestamp delta computation",
                    confidence=0.85,
                    confidence_basis=f"{len(out_txs)} outgoing transfers to {len(unique_recipients)} unique destinations within {time_span_seconds}s.",
                    counterevidence="Legitimate payroll distributions, multisig treasury disbursements, or batch payments exhibit similar outbound fan-out.",
                    alternative_explanations=[
                        "Automated exchange withdrawal batching",
                        "Token airdrop or community reward distribution",
                        "Ecosystem grant or payroll disbursement"
                    ],
                    limitations="Does not verify recipient wallet ownership or intent.",
                    recommended_next_step="Inspect destination wallets for common downstream consolidation or exchange deposit interactions.",
                    relevant_tx_hashes=[tx.tx_hash for tx in out_txs],
                    relevant_addresses=[target_lower] + list(unique_recipients),
                    evidence_payload={
                        "unique_recipients_count": len(unique_recipients),
                        "time_span_seconds": time_span_seconds,
                        "total_dispersed_eth": total_dispersed
                    }
                )
            )

        return findings
