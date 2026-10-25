"""
Threat intelligence document and chunk models.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class IntelligenceDocument(Base):
    __tablename__ = "intelligence_documents"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    publisher = Column(String(128), nullable=False)
    source_url = Column(String(512), nullable=True)
    publication_date = Column(String(32), nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    content_hash = Column(String(64), nullable=False, index=True)  # SHA-256 of raw content
    document_type = Column(String(64), default="advisory")  # advisory, exploit_analysis, typology_report
    trust_classification = Column(String(64), default="verified_research")
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    
    chunk_count = Column(Integer, default=0)
    is_indexed = Column(Boolean, default=False)
    extra_metadata = Column(JSON, nullable=True)

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), ForeignKey("intelligence_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    embedding_json = Column(JSON, nullable=True)  # Float array stored as JSON for SQLite/PG compatibility
    keywords = Column(JSON, nullable=True)  # Extracted terms for BM25/keyword indexing

    # Relationships
    document = relationship("IntelligenceDocument", back_populates="chunks")
