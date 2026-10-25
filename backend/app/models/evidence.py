"""
Evidence item database model.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Evidence(Base):
    __tablename__ = "evidence_records"

    id = Column(String(64), primary_key=True, index=True)
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    finding_id = Column(String(64), ForeignKey("findings.id", ondelete="SET NULL"), nullable=True, index=True)
    
    evidence_type = Column(String(64), nullable=False)  # on_chain_transaction, graph_path, threat_intelligence, address_label
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    
    raw_reference = Column(String(256), nullable=False)  # tx_hash, address, or document_id
    data_provenance = Column(String(128), nullable=False)  # e.g., "etherscan_api", "rpc_node", "threat_intel_rag"
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    investigation = relationship("Investigation", back_populates="evidence_records")
    finding = relationship("Finding", back_populates="evidence_items")
