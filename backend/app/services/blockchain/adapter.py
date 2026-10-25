"""
Base Blockchain Data Adapter interface and normalized models.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedTransaction:
    chain_id: int
    tx_hash: str
    block_number: int
    block_timestamp: int
    from_address: str
    to_address: Optional[str]
    value_wei: str
    value_eth: float
    asset_symbol: str = "ETH"
    token_address: Optional[str] = None
    gas_used: Optional[int] = None
    gas_price_gwei: Optional[float] = None
    is_error: bool = False
    tx_type: str = "native_transfer"
    provider: str = "adapter"
    source_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class CoverageSummary:
    provider: str
    network_name: str
    chain_id: int
    coverage_level: str  # "full_indexed", "partial_recent", "rpc_bounded", "synthetic_demo"
    is_complete: bool
    transactions_retrieved: int
    limitations: List[str] = field(default_factory=list)
    data_retrieved_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class BlockchainAdapter(ABC):
    """Abstract interface for blockchain data providers."""

    @abstractmethod
    async def get_transactions(
        self,
        address: str,
        chain_id: int = 1,
        max_results: int = 100
    ) -> tuple[List[NormalizedTransaction], CoverageSummary]:
        """Retrieves normalized transactions for a wallet address."""
        pass

    @abstractmethod
    async def get_transaction_by_hash(
        self,
        tx_hash: str,
        chain_id: int = 1
    ) -> tuple[Optional[NormalizedTransaction], CoverageSummary]:
        """Retrieves a single transaction by hash."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Checks provider connectivity and latency."""
        pass
