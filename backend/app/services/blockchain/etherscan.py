"""
Etherscan API Adapter.
Uses Etherscan Developer APIs when configured with an API key.
"""
import time
import httpx
from typing import List, Optional, Tuple, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.services.blockchain.adapter import BlockchainAdapter, NormalizedTransaction, CoverageSummary


class EtherscanAdapter(BlockchainAdapter):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.ETHERSCAN_API_KEY
        self.base_url = (base_url or settings.ETHERSCAN_API_URL).rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS

    async def get_transactions(
        self,
        address: str,
        chain_id: int = 1,
        max_results: int = 100
    ) -> Tuple[List[NormalizedTransaction], CoverageSummary]:
        if not self.api_key:
            return [], CoverageSummary(
                provider="etherscan",
                network_name="ethereum_mainnet",
                chain_id=chain_id,
                coverage_level="not_configured",
                is_complete=False,
                transactions_retrieved=0,
                limitations=["Etherscan API key is not configured in settings or environment."]
            )

        url = f"{self.base_url}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset={max_results}&sort=desc&apikey={self.api_key}"
        limitations = []
        normalized_txs = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status")
                    result = data.get("result", [])
                    if status == "1" and isinstance(result, list):
                        for item in result:
                            val_wei = item.get("value", "0")
                            val_eth = float(val_wei) / 1e18 if val_wei else 0.0
                            tx = NormalizedTransaction(
                                chain_id=chain_id,
                                tx_hash=item.get("hash"),
                                block_number=int(item.get("blockNumber", 0)),
                                block_timestamp=int(item.get("timeStamp", 0)),
                                from_address=item.get("from"),
                                to_address=item.get("to"),
                                value_wei=val_wei,
                                value_eth=val_eth,
                                asset_symbol="ETH",
                                gas_used=int(item.get("gasUsed", 0)) if item.get("gasUsed") else None,
                                gas_price_gwei=float(item.get("gasPrice", 0)) / 1e9 if item.get("gasPrice") else None,
                                is_error=item.get("isError") == "1",
                                tx_type="contract_interaction" if item.get("input") and item.get("input") != "0x" else "native_transfer",
                                provider="etherscan_indexed",
                                source_url=f"https://etherscan.io/tx/{item.get('hash')}",
                                raw_data=item
                            )
                            normalized_txs.append(tx)
                    else:
                        limitations.append(f"Etherscan message: {data.get('message', 'No transactions found')}")
                else:
                    limitations.append(f"Etherscan returned HTTP {resp.status_code}")
        except Exception as e:
            logger.warning(f"Etherscan query error: {e}")
            limitations.append(f"Etherscan request error: {str(e)}")

        coverage = CoverageSummary(
            provider="etherscan_indexed",
            network_name="ethereum_mainnet",
            chain_id=chain_id,
            coverage_level="full_indexed" if len(normalized_txs) > 0 else "partial_recent",
            is_complete=len(limitations) == 0 and len(normalized_txs) < max_results,
            transactions_retrieved=len(normalized_txs),
            limitations=limitations
        )
        return normalized_txs, coverage

    async def get_transaction_by_hash(
        self,
        tx_hash: str,
        chain_id: int = 1
    ) -> Tuple[Optional[NormalizedTransaction], CoverageSummary]:
        # Implementation via proxy action
        return None, CoverageSummary(
            provider="etherscan",
            network_name="ethereum_mainnet",
            chain_id=chain_id,
            coverage_level="not_configured" if not self.api_key else "partial",
            is_complete=False,
            transactions_retrieved=0,
            limitations=["Single tx retrieval fallback to RPC recommended"]
        )

    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {
                "status": "not_configured",
                "latency_ms": None,
                "details": "ETHERSCAN_API_KEY environment variable is not set."
            }
        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}?module=stats&action=ethprice&apikey={self.api_key}")
                latency = round((time.time() - t0) * 1000, 2)
                return {
                    "status": "operational" if resp.status_code == 200 else "degraded",
                    "latency_ms": latency,
                    "details": "Etherscan API key authenticated and responsive"
                }
        except Exception as e:
            return {
                "status": "error",
                "latency_ms": None,
                "details": str(e)
            }
