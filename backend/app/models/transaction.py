"""
Transaction database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(64), primary_key=True, index=True)
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    chain_id = Column(Integer, nullable=False, default=1)
    tx_hash = Column(String(66), nullable=False, index=True)
    block_number = Column(Integer, nullable=False, index=True)
    block_timestamp = Column(Integer, nullable=False, index=True)
    
    from_address = Column(String(42), nullable=False, index=True)
    to_address = Column(String(42), nullable=True, index=True)
    value_wei = Column(String(78), nullable=False, default="0")
    value_eth = Column(Float, nullable=False, default=0.0)
    asset_symbol = Column(String(32), nullable=False, default="ETH")
    token_address = Column(String(42), nullable=True)
    
    gas_used = Column(Integer, nullable=True)
    gas_price_gwei = Column(Float, nullable=True)
    is_error = Column(Boolean, default=False)
    tx_type = Column(String(64), default="native_transfer")
    
    provider = Column(String(64), nullable=False, default="rpc")
    source_url = Column(String(512), nullable=True)
    raw_data = Column(JSON, nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="transactions")

    __table_args__ = (
        UniqueConstraint("investigation_id", "tx_hash", name="uq_investigation_tx_hash"),
    )
