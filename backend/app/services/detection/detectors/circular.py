"""
Detector for Circular Transfer Loops (round-tripping and wash patterns).
"""
from typing import List
from app.services.detection.base import BaseDetector, DetectionFindingResult
from app.services.blockchain.adapter import NormalizedTransaction
from app.schemas.graph import GraphResponse
from app.services.graph.algorithms import GraphAlgorithms


class CircularTransferDetector(BaseDetector):
    @property
    def detector_id(self) -> str:
        return "DET_CIRCULAR_LOOP"

    @property
    def name(self) -> str:
        return "Circular Transfer Loop / Round-Tripping"

    @property
    def description(self) -> str:
        return "Identifies asset paths where funds transferred downstream return to an originating address or upstream node in the sub-graph."

    def detect(
        self,
        target_identifier: str,
        transactions: List[NormalizedTransaction],
        graph: GraphResponse
    ) -> List[DetectionFindingResult]:
        findings = []
        target_lower = target_identifier.lower()

        edges = [(e.source_address.lower(), e.target_address.lower()) for e in graph.edges]
        cycles = GraphAlgorithms.detect_cycles(edges)

        # Filter cycles involving target
        target_cycles = [c for c in cycles if target_lower in c]

        if target_cycles:
            primary_cycle = target_cycles[0]
            cycle_str = " -> ".join([addr[:10] + "..." for addr in primary_cycle])
            
            # Find txs on cycle
            cycle_txs = []
            for i in range(len(primary_cycle) - 1):
                u, v = primary_cycle[i], primary_cycle[i+1]
                for tx in transactions:
                    if tx.from_address and tx.to_address:
                        if tx.from_address.lower() == u and tx.to_address.lower() == v:
                            cycle_txs.append(tx.tx_hash)

            findings.append(
                DetectionFindingResult(
                    detector_id=self.detector_id,
                    title="Circular Transfer Pattern (Round-Tripping Loop)",
                    severity="HIGH",
                    status="suspicious_pattern",
                    explanation=(
                        f"A closed transfer loop was detected in the transaction graph involving {len(primary_cycle)-1} hops: "
                        f"{cycle_str}. Funds originating from the subject returned via intermediate counterparties. "
                        "Circular topologies are frequently utilized for artificial volume generation (wash trading), "
                        "churning to simulate transaction history, or liquidity recycling."
                    ),
                    detection_method="Directed graph cycle detection (DFS back-edge analysis)",
                    confidence=0.92,
                    confidence_basis=f"Confirmed closed directed loop in graph of length {len(primary_cycle)-1} nodes.",
                    counterevidence="Decentralized arbitrage execution, loan repayments to originating vault, or collateral redemption loops.",
                    alternative_explanations=[
                        "Arbitrage bot circular trade across decentralized liquidity pools",
                        "Collateral loan borrowing and repayment in same transaction or block",
                        "Testing transaction return by cooperating counterparty"
                    ],
                    limitations="Transfers prove movement of value, but not common intent or beneficial ownership.",
                    recommended_next_step="Inspect input data of transactions in the cycle to verify if smart contract automation triggered the return loop.",
                    relevant_tx_hashes=cycle_txs,
                    relevant_addresses=primary_cycle,
                    evidence_payload={
                        "cycle_path": primary_cycle,
                        "hop_count": len(primary_cycle) - 1,
                        "cycle_tx_hashes": cycle_txs
                    }
                )
            )

        return findings
