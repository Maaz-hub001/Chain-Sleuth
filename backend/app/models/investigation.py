"""
Investigation database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base


class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(64), primary_key=True, index=True)
    target_identifier = Column(String(128), nullable=False, index=True)
    target_type = Column(String(32), nullable=False)  # "address" or "transaction"
    network_name = Column(String(64), nullable=False, default="ethereum_mainnet")
    chain_id = Column(Integer, nullable=False, default=1)
    investigation_type = Column(String(64), nullable=False, default="comprehensive")
    status = Column(String(32), nullable=False, default="pending", index=True)  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)

    # Scoping parameters
    max_depth = Column(Integer, default=2)
    max_transactions = Column(Integer, default=100)
    time_range_start = Column(DateTime, nullable=True)
    time_range_end = Column(DateTime, nullable=True)
    investigator_notes = Column(Text, nullable=True)

    # Summaries & statistics
    coverage_summary = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    transactions = relationship("Transaction", back_populates="investigation", cascade="all, delete-orphan")
    nodes = relationship("WalletNode", back_populates="investigation", cascade="all, delete-orphan")
    edges = relationship("GraphEdge", back_populates="investigation", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="investigation", cascade="all, delete-orphan")
    evidence_records = relationship("Evidence", back_populates="investigation", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="investigation", cascade="all, delete-orphan")
