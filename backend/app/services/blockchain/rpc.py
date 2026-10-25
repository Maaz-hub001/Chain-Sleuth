"""
EVM JSON-RPC Adapter.
Direct read-only communication with Ethereum nodes (Ankr, Infura, Alchemy, or local Geth).
"""
import time
import httpx
from typing import List, Optional, Tuple, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.services.blockchain.adapter import BlockchainAdapter, NormalizedTransaction, CoverageSummary


class RpcAdapter(BlockchainAdapter):
    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or settings.EVM_RPC_URL
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS

    async def _rpc_call(self, method: str, params: list) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(self.rpc_url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                if "error" in data:
                    raise Exception(data["error"].get("message", "RPC error"))
                return data.get("result")
            raise Exception(f"RPC HTTP {resp.status_code}")

    async def get_transactions(
        self,
        address: str,
        chain_id: int = 1,
        max_results: int = 100
    ) -> Tuple[List[NormalizedTransaction], CoverageSummary]:
        # Note on standard JSON-RPC node architecture:
        # Standard EVM JSON-RPC nodes do NOT have eth_getTransactionsByAddress without debug/trace/erigon indexing.
        # This is an honest architectural limitation clearly communicated in coverage summary.
        return [], CoverageSummary(
            provider="evm_json_rpc",
            network_name="ethereum_mainnet",
            chain_id=chain_id,
            coverage_level="rpc_bounded",
            is_complete=False,
            transactions_retrieved=0,
            limitations=[
                "Standard EVM JSON-RPC nodes do not index historical transactions by wallet address. "
                "Indexed explorer adapters (Blockscout/Etherscan) or archival tracing nodes are required for address histories."
            ]
        )

    async def get_transaction_by_hash(
        self,
        tx_hash: str,
        chain_id: int = 1
    ) -> Tuple[Optional[NormalizedTransaction], CoverageSummary]:
        limitations = []
        try:
            tx_data = await self._rpc_call("eth_getTransactionByHash", [tx_hash])
            if not tx_data:
                return None, CoverageSummary(
                    provider="evm_json_rpc",
                    network_name="ethereum_mainnet",
                    chain_id=chain_id,
                    coverage_level="not_found",
                    is_complete=True,
                    transactions_retrieved=0,
                    limitations=["Transaction hash not found in current block horizon."]
                )

            # Retrieve block for timestamp
            block_num_hex = tx_data.get("blockNumber")
            block_num = int(block_num_hex, 16) if block_num_hex else 0
            block_timestamp = int(time.time())
            if block_num > 0:
                block_data = await self._rpc_call("eth_getBlockByNumber", [block_num_hex, False])
                if block_data and "timestamp" in block_data:
                    block_timestamp = int(block_data["timestamp"], 16)

            val_hex = tx_data.get("value", "0x0")
            val_wei = str(int(val_hex, 16))
            val_eth = float(val_wei) / 1e18

            norm_tx = NormalizedTransaction(
                chain_id=chain_id,
                tx_hash=tx_hash,
                block_number=block_num,
                block_timestamp=block_timestamp,
                from_address=tx_data.get("from"),
                to_address=tx_data.get("to"),
                value_wei=val_wei,
                value_eth=val_eth,
                asset_symbol="ETH",
                gas_used=int(tx_data.get("gas", "0x0"), 16),
                gas_price_gwei=int(tx_data.get("gasPrice", "0x0"), 16) / 1e9 if tx_data.get("gasPrice") else None,
                tx_type="contract_interaction" if tx_data.get("input") and tx_data.get("input") != "0x" else "native_transfer",
                provider="evm_json_rpc",
                source_url=f"https://etherscan.io/tx/{tx_hash}",
                raw_data=tx_data
            )
            return norm_tx, CoverageSummary(
                provider="evm_json_rpc",
                network_name="ethereum_mainnet",
                chain_id=chain_id,
                coverage_level="full_indexed",
                is_complete=True,
                transactions_retrieved=1,
                limitations=[]
            )
        except Exception as e:
            logger.warning(f"RPC get_transaction_by_hash failed: {e}")
            return None, CoverageSummary(
                provider="evm_json_rpc",
                network_name="ethereum_mainnet",
                chain_id=chain_id,
                coverage_level="error",
                is_complete=False,
                transactions_retrieved=0,
                limitations=[str(e)]
            )

    async def health_check(self) -> Dict[str, Any]:
        t0 = time.time()
        try:
            block_hex = await self._rpc_call("eth_blockNumber", [])
            latency = round((time.time() - t0) * 1000, 2)
            current_block = int(block_hex, 16)
            return {
                "status": "operational",
                "latency_ms": latency,
                "details": f"Connected to RPC node. Latest block: {current_block}"
            }
        except Exception as e:
            return {
                "status": "error",
                "latency_ms": None,
                "details": f"RPC connection failed: {str(e)}"
            }
