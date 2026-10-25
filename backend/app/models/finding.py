"""
Finding database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(64), primary_key=True, index=True)
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    detector_id = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    severity = Column(String(32), nullable=False, default="MEDIUM")  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(64), nullable=False, default="suspicious_pattern")  # confirmed_observation, suspicious_pattern, unverified_intelligence, insufficient_evidence
    
    explanation = Column(Text, nullable=False)
    detection_method = Column(String(128), nullable=False)
    confidence = Column(Float, nullable=False, default=0.8)
    confidence_basis = Column(Text, nullable=False)
    
    counterevidence = Column(Text, nullable=True)
    alternative_explanations = Column(JSON, nullable=True)  # List of strings
    limitations = Column(Text, nullable=True)
    recommended_next_step = Column(Text, nullable=True)
    
    # Associated identifiers
    evidence_ids = Column(JSON, nullable=True)  # List of string IDs
    relevant_tx_hashes = Column(JSON, nullable=True)  # List of tx hashes
    relevant_addresses = Column(JSON, nullable=True)  # List of addresses
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="findings")
    evidence_items = relationship("Evidence", back_populates="finding", cascade="all, delete-orphan")
