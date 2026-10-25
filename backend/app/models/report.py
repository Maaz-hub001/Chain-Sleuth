"""
Investigation Report and Verification database models.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(64), primary_key=True, index=True)
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    schema_version = Column(String(16), default="1.0.0")
    canonical_version = Column(String(16), default="1.0.0")
    hash_algorithm = Column(String(32), default="SHA-256")
    report_hash = Column(String(64), nullable=False, index=True)  # Cryptographic SHA-256
    
    target_identifier = Column(String(128), nullable=False)
    target_type = Column(String(32), nullable=False)
    chain_id = Column(Integer, default=1)
    network_name = Column(String(64), default="ethereum_mainnet")
    
    content_json = Column(JSON, nullable=False)  # Complete structured canonical report payload
    markdown_content = Column(Text, nullable=False)
    
    # On-chain anchoring status
    is_anchored = Column(Boolean, default=False)
    registry_chain_id = Column(Integer, nullable=True)
    registry_contract_address = Column(String(42), nullable=True)
    registry_tx_hash = Column(String(66), nullable=True)
    anchored_timestamp = Column(Integer, nullable=True)
    
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="reports")
    verifications = relationship("ReportVerification", back_populates="report", cascade="all, delete-orphan")


class ReportVerification(Base):
    __tablename__ = "report_verifications"

    id = Column(String(64), primary_key=True, index=True)
    report_id = Column(String(64), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    computed_hash = Column(String(64), nullable=False)
    recorded_hash = Column(String(64), nullable=False)
    is_valid = Column(Boolean, nullable=False)
    
    on_chain_checked = Column(Boolean, default=False)
    on_chain_verified = Column(Boolean, default=False)
    on_chain_block = Column(Integer, nullable=True)
    on_chain_reporter = Column(String(42), nullable=True)
    
    verification_details = Column(JSON, nullable=True)

    # Relationships
    report = relationship("Report", back_populates="verifications")
