"""
Pydantic schemas for Transactions.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class TransactionSchema(BaseModel):
    id: str
    investigation_id: str
    chain_id: int
    tx_hash: str
    block_number: int
    block_timestamp: int
    from_address: str
    to_address: Optional[str] = None
    value_wei: str
    value_eth: float
    asset_symbol: str
    token_address: Optional[str] = None
    gas_used: Optional[int] = None
    gas_price_gwei: Optional[float] = None
    is_error: bool
    tx_type: str
    provider: str
    source_url: Optional[str] = None
    retrieved_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    investigation_id: str
    total: int
    transactions: List[TransactionSchema]
