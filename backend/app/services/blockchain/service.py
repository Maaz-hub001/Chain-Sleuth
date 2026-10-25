"""
Blockchain Service: coordinates providers, validates targets, and normalizes transaction data.
"""
from typing import List, Optional, Tuple, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.core.security import validate_evm_address, validate_tx_hash, validate_target_identifier
from app.services.blockchain.adapter import BlockchainAdapter, NormalizedTransaction, CoverageSummary
from app.services.blockchain.blockscout import BlockscoutAdapter
from app.services.blockchain.etherscan import EtherscanAdapter
from app.services.blockchain.rpc import RpcAdapter
from app.services.blockchain.mock_provider import DemoFixtureAdapter


class BlockchainService:
    def __init__(self):
        self.blockscout = BlockscoutAdapter()
        self.etherscan = EtherscanAdapter()
        self.rpc = RpcAdapter()
        self.demo = DemoFixtureAdapter()

    def get_adapter(self, provider_preference: Optional[str] = None, use_demo: bool = False) -> BlockchainAdapter:
        if use_demo:
            return self.demo
        if provider_preference == "etherscan" and settings.ETHERSCAN_API_KEY:
            return self.etherscan
        if provider_preference == "rpc":
            return self.rpc
        # Default: Blockscout open indexed API
        return self.blockscout

    async def fetch_target_transactions(
        self,
        target_identifier: str,
        chain_id: int = 1,
        max_transactions: int = 100,
        use_demo: bool = False
    ) -> Tuple[List[NormalizedTransaction], CoverageSummary, str]:
        """
        Determines target type (address or transaction), retrieves data using appropriate adapter,
        and falls back honestly if provider fails or if demo fixture is requested.
        """
        clean_target, target_type = validate_target_identifier(target_identifier)

        if use_demo or target_identifier.lower() == "0x742d35cc6634c0532925a3b844bc454e4438f44e".lower():
            logger.info(f"Using Demo Fixture Adapter for target: {clean_target}")
            if target_type == "address":
                txs, cov = await self.demo.get_transactions(clean_target, chain_id, max_transactions)
            else:
                tx, cov = await self.demo.get_transaction_by_hash(clean_target, chain_id)
                txs = [tx] if tx else []
            return txs, cov, target_type

        # Live retrieval attempt via Blockscout, then RPC
        if target_type == "address":
            txs, cov = await self.blockscout.get_transactions(clean_target, chain_id, max_transactions)
            if not txs and settings.ETHERSCAN_API_KEY:
                logger.info(f"Blockscout returned 0 txs; falling back to Etherscan for {clean_target}")
                txs, cov = await self.etherscan.get_transactions(clean_target, chain_id, max_transactions)
            return txs, cov, target_type
        else:
            # Single transaction hash lookup
            tx, cov = await self.rpc.get_transaction_by_hash(clean_target, chain_id)
            if not tx:
                tx, cov = await self.blockscout.get_transaction_by_hash(clean_target, chain_id)
            return [tx] if tx else [], cov, target_type

    async def get_all_providers_health(self) -> List[Dict[str, Any]]:
        """Queries health status across all configured adapters."""
        results = []
        
        # 1. RPC
        rpc_health = await self.rpc.health_check()
        results.append({
            "name": "EVM Public RPC",
            "category": "blockchain_rpc",
            "status": rpc_health["status"],
            "endpoint_display": settings.EVM_RPC_URL,
            "details": rpc_health["details"],
            "response_time_ms": rpc_health.get("latency_ms")
        })

        # 2. Blockscout
        bs_health = await self.blockscout.health_check()
        results.append({
            "name": "Blockscout Explorer API",
            "category": "explorer_api",
            "status": bs_health["status"],
            "endpoint_display": settings.BLOCKSCOUT_API_URL,
            "details": bs_health["details"],
            "response_time_ms": bs_health.get("latency_ms")
        })

        # 3. Etherscan
        es_health = await self.etherscan.health_check()
        results.append({
            "name": "Etherscan Developer API",
            "category": "explorer_api",
            "status": es_health["status"],
            "endpoint_display": settings.ETHERSCAN_API_URL,
            "details": es_health["details"],
            "response_time_ms": es_health.get("latency_ms")
        })

        # 4. Demo Provider
        demo_health = await self.demo.health_check()
        results.append({
            "name": "Local Sandbox Demo Fixture",
            "category": "demo_provider",
            "status": demo_health["status"],
            "endpoint_display": "local://data/fixtures/sample_investigation_wallet.json",
            "details": demo_health["details"],
            "response_time_ms": demo_health.get("latency_ms")
        })

        return results


blockchain_service = BlockchainService()
