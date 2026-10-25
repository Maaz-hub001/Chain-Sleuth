"""
Blockscout Explorer API Adapter.
Public, open-source indexed blockchain data provider.
"""
import time
import httpx
from typing import List, Optional, Tuple, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.services.blockchain.adapter import BlockchainAdapter, NormalizedTransaction, CoverageSummary


class BlockscoutAdapter(BlockchainAdapter):
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.BLOCKSCOUT_API_URL).rstrip("/")
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS

    async def get_transactions(
        self,
        address: str,
        chain_id: int = 1,
        max_results: int = 100
    ) -> Tuple[List[NormalizedTransaction], CoverageSummary]:
        limitations = []
        normalized_txs = []
        
        # Blockscout v2 / v1 module API
        url = f"{self.base_url}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset={max_results}&sort=desc"
        
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
                            try:
                                val_eth = float(val_wei) / 1e18
                            except Exception:
                                val_eth = 0.0
                            
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
                                provider="blockscout_indexed",
                                source_url=f"https://eth.blockscout.com/tx/{item.get('hash')}",
                                raw_data={"input": item.get("input"), "contractAddress": item.get("contractAddress")}
                            )
                            normalized_txs.append(tx)
                    else:
                        limitations.append(f"Blockscout returned non-success: {data.get('message')}")
                else:
                    limitations.append(f"Blockscout returned HTTP {resp.status_code}")
        except Exception as e:
            logger.warning(f"Blockscout query failed for {address}: {e}")
            limitations.append(f"Network error querying Blockscout API: {str(e)}")

        coverage = CoverageSummary(
            provider="blockscout_indexed",
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
        url = f"{self.base_url}?module=transaction&action=gettxinfo&txhash={tx_hash}"
        limitations = []
        tx = None
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    item = data.get("result", {})
                    if item and isinstance(item, dict):
                        val_wei = item.get("value", "0")
                        val_eth = float(val_wei) / 1e18 if val_wei else 0.0
                        tx = NormalizedTransaction(
                            chain_id=chain_id,
                            tx_hash=tx_hash,
                            block_number=int(item.get("blockNumber", 0)),
                            block_timestamp=int(item.get("timeStamp", 0)),
                            from_address=item.get("from"),
                            to_address=item.get("to"),
                            value_wei=val_wei,
                            value_eth=val_eth,
                            asset_symbol="ETH",
                            provider="blockscout_indexed",
                            source_url=f"https://eth.blockscout.com/tx/{tx_hash}",
                            raw_data=item
                        )
                else:
                    limitations.append(f"Blockscout HTTP {resp.status_code}")
        except Exception as e:
            limitations.append(str(e))

        coverage = CoverageSummary(
            provider="blockscout_indexed",
            network_name="ethereum_mainnet",
            chain_id=chain_id,
            coverage_level="full_indexed" if tx else "not_found",
            is_complete=tx is not None,
            transactions_retrieved=1 if tx else 0,
            limitations=limitations
        )
        return tx, coverage

    async def health_check(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}?module=stats&action=ethprice")
                latency = round((time.time() - t0) * 1000, 2)
                if resp.status_code == 200:
                    return {
                        "status": "operational",
                        "latency_ms": latency,
                        "details": "Blockscout public API responding normally"
                    }
                return {
                    "status": "degraded",
                    "latency_ms": latency,
                    "details": f"HTTP {resp.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "latency_ms": None,
                "details": f"Connection error: {str(e)}"
            }
