"""
Detector for Rapid Relay Movement (Pass-through Transit Wallets).
"""
from typing import List
from app.services.detection.base import BaseDetector, DetectionFindingResult
from app.services.blockchain.adapter import NormalizedTransaction
from app.schemas.graph import GraphResponse


class RapidMovementDetector(BaseDetector):
    @property
    def detector_id(self) -> str:
        return "DET_RAPID_RELAY"

    @property
    def name(self) -> str:
        return "Rapid Relay / Intermediate Transit Wallet"

    @property
    def description(self) -> str:
        return "Detects intermediate addresses where incoming funds are forwarded downstream within a very short dwell time (< 30 minutes)."

    def detect(
        self,
        target_identifier: str,
        transactions: List[NormalizedTransaction],
        graph: GraphResponse
    ) -> List[DetectionFindingResult]:
        findings = []
        target_lower = target_identifier.lower()

        # Build address inflow and outflow timestamps
        inflows = [tx for tx in transactions if tx.to_address and tx.to_address.lower() == target_lower]
        outflows = [tx for tx in transactions if tx.from_address and tx.from_address.lower() == target_lower]

        for in_tx in inflows:
            for out_tx in outflows:
                if out_tx.block_timestamp >= in_tx.block_timestamp:
                    dwell_seconds = out_tx.block_timestamp - in_tx.block_timestamp
                    if dwell_seconds <= 1800:  # 30 minutes
                        ratio = min(out_tx.value_eth, in_tx.value_eth) / max(in_tx.value_eth, 0.0001)
                        if ratio > 0.5:
                            findings.append(
                                DetectionFindingResult(
                                    detector_id=self.detector_id,
                                    title="Rapid Relay Transit Pattern Detected",
                                    severity="HIGH" if dwell_seconds < 300 else "MEDIUM",
                                    status="suspicious_pattern",
                                    explanation=(
                                        f"Wallet received {in_tx.value_eth} ETH in block {in_tx.block_number} and "
                                        f"subsequently relayed {out_tx.value_eth} ETH downstream in block {out_tx.block_number} "
                                        f"after only {dwell_seconds} seconds ({round(dwell_seconds/60, 1)} minutes). "
                                        "Short asset dwell time is frequently observed in transit wallets, automated sweepers, or laundering chains."
                                    ),
                                    detection_method="Temporal inflow-outflow matching & dwell time threshold analysis",
                                    confidence=0.88,
                                    confidence_basis=f"Dwell delta: {dwell_seconds}s (<= 1800s threshold). In/out volume ratio: {round(ratio, 2)}.",
                                    counterevidence="Automated arbitrage bots, routing contracts, payment forwarders, or exchange hot wallet sweepers operate with near-zero dwell times.",
                                    alternative_explanations=[
                                        "DEX aggregator or smart contract router execution",
                                        "Automated merchant payment gateway forwarding",
                                        "User sweeping balance to a secure cold storage address"
                                    ],
                                    limitations="Cannot confirm automation versus manual user transaction without inspecting caller signatures.",
                                    recommended_next_step="Check whether the transit address holds a residual native gas balance or executes contract calls.",
                                    relevant_tx_hashes=[in_tx.tx_hash, out_tx.tx_hash],
                                    relevant_addresses=[in_tx.from_address.lower(), target_lower, out_tx.to_address.lower()],
                                    evidence_payload={
                                        "inflow_hash": in_tx.tx_hash,
                                        "outflow_hash": out_tx.tx_hash,
                                        "dwell_seconds": dwell_seconds,
                                        "inflow_eth": in_tx.value_eth,
                                        "outflow_eth": out_tx.value_eth
                                    }
                                )
                            )
                            # Single high-confidence match is sufficient per pair
                            return findings

        return findings
