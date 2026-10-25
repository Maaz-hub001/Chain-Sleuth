"""
Graph node and edge database models.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class WalletNode(Base):
    __tablename__ = "wallet_nodes"

    id = Column(String(64), primary_key=True, index=True)
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    chain_id = Column(Integer, nullable=False, default=1)
    address = Column(String(42), nullable=False, index=True)
    label = Column(String(128), nullable=True)
    entity_type = Column(String(64), default="wallet")  # target, wallet, contract, mixer, exchange, sanctioned
    risk_score = Column(Float, default=0.0)
    is_target = Column(Boolean, default=False)
    in_degree = Column(Integer, default=0)
    out_degree = Column(Integer, default=0)
    total_inflow_eth = Column(Float, default=0.0)
    total_outflow_eth = Column(Float, default=0.0)
    metadata_json = Column(JSON, nullable=True)

    # Relationships
    investigation = relationship("Investigation", back_populates="nodes")

    __table_args__ = (
        UniqueConstraint("investigation_id", "address", name="uq_investigation_wallet_address"),
    )


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id = Column(String(64), primary_key=True, index=True)
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_address = Column(String(42), nullable=False, index=True)
    target_address = Column(String(42), nullable=False, index=True)
    tx_hash = Column(String(66), nullable=False, index=True)
    value_eth = Column(Float, default=0.0)
    asset_symbol = Column(String(32), default="ETH")
    block_timestamp = Column(Integer, nullable=False)
    edge_metadata = Column(JSON, nullable=True)

    # Relationships
    investigation = relationship("Investigation", back_populates="edges")
