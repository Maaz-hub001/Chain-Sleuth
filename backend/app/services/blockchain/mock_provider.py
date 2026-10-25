"""
Mock / Demo Fixture Adapter.
Provides deterministic, verifiable test traces (e.g., Lazarus / Ronin sample, Tornado Cash mixer interaction)
with honest labeling that the data is an offline demonstrator fixture.
"""
import json
import os
from typing import List, Optional, Tuple, Dict, Any
from app.core.config import settings
from app.services.blockchain.adapter import BlockchainAdapter, NormalizedTransaction, CoverageSummary


class DemoFixtureAdapter(BlockchainAdapter):
    def __init__(self, fixture_path: Optional[str] = None):
        self.fixture_path = fixture_path or os.path.join(settings.FIXTURES_DIR, "sample_investigation_wallet.json")

    def _load_fixture(self) -> Dict[str, Any]:
        if os.path.exists(self.fixture_path):
            with open(self.fixture_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    async def get_transactions(
        self,
        address: str,
        chain_id: int = 1,
        max_results: int = 100
    ) -> Tuple[List[NormalizedTransaction], CoverageSummary]:
        data = self._load_fixture()
        txs = []
        for item in data.get("transactions", []):
            tx = NormalizedTransaction(
                chain_id=chain_id,
                tx_hash=item["tx_hash"],
                block_number=item["block_number"],
                block_timestamp=item["block_timestamp"],
                from_address=item["from_address"],
                to_address=item["to_address"],
                value_wei=item["value_wei"],
                value_eth=item["value_eth"],
                asset_symbol=item.get("asset_symbol", "ETH"),
                gas_used=item.get("gas_used"),
                gas_price_gwei=item.get("gas_price_gwei"),
                is_error=item.get("is_error", False),
                tx_type=item.get("tx_type", "native_transfer"),
                provider="demo_fixture",
                source_url=item.get("source_url")
            )
            txs.append(tx)

        coverage = CoverageSummary(
            provider="demo_fixture",
            network_name="demo_sandbox",
            chain_id=chain_id,
            coverage_level="synthetic_demo",
            is_complete=True,
            transactions_retrieved=len(txs),
            limitations=[
                "DEMO MODE: These records are loaded from data/fixtures/sample_investigation_wallet.json "
                "for offline demonstration, testing, and multi-hop laundering pattern analysis."
            ]
        )
        return txs[:max_results], coverage

    async def get_transaction_by_hash(
        self,
        tx_hash: str,
        chain_id: int = 1
    ) -> Tuple[Optional[NormalizedTransaction], CoverageSummary]:
        data = self._load_fixture()
        for item in data.get("transactions", []):
            if item["tx_hash"].lower() == tx_hash.lower():
                tx = NormalizedTransaction(
                    chain_id=chain_id,
                    tx_hash=item["tx_hash"],
                    block_number=item["block_number"],
                    block_timestamp=item["block_timestamp"],
                    from_address=item["from_address"],
                    to_address=item["to_address"],
                    value_wei=item["value_wei"],
                    value_eth=item["value_eth"],
                    asset_symbol=item.get("asset_symbol", "ETH"),
                    gas_used=item.get("gas_used"),
                    gas_price_gwei=item.get("gas_price_gwei"),
                    is_error=item.get("is_error", False),
                    tx_type=item.get("tx_type", "native_transfer"),
                    provider="demo_fixture",
                    source_url=item.get("source_url")
                )
                return tx, CoverageSummary(
                    provider="demo_fixture",
                    network_name="demo_sandbox",
                    chain_id=chain_id,
                    coverage_level="synthetic_demo",
                    is_complete=True,
                    transactions_retrieved=1,
                    limitations=["DEMO MODE: Record loaded from verified test fixture."]
                )

        return None, CoverageSummary(
            provider="demo_fixture",
            network_name="demo_sandbox",
            chain_id=chain_id,
            coverage_level="not_found",
            is_complete=True,
            transactions_retrieved=0,
            limitations=["Transaction hash not found in demo fixture."]
        )

    async def health_check(self) -> Dict[str, Any]:
        exists = os.path.exists(self.fixture_path)
        return {
            "status": "operational" if exists else "degraded",
            "latency_ms": 0.5,
            "details": "Demo Fixture Provider ready (offline test records available)" if exists else "Fixture file missing"
        }
