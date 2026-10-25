"""
Pydantic schemas for Threat Intelligence documents and RAG queries.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class IntelligenceDocumentCreate(BaseModel):
    title: str
    publisher: str
    source_url: Optional[str] = None
    publication_date: Optional[str] = None
    document_type: str = "advisory"
    trust_classification: str = "verified_research"
    summary: Optional[str] = None
    content: str


class IntelligenceDocumentSchema(BaseModel):
    id: str
    title: str
    publisher: str
    source_url: Optional[str] = None
    publication_date: Optional[str] = None
    retrieved_at: datetime
    content_hash: str
    document_type: str
    trust_classification: str
    summary: Optional[str] = None
    chunk_count: int
    is_indexed: bool

    class Config:
        from_attributes = True


class IntelligenceSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=10)
    filter_doc_type: Optional[str] = None


class IntelligenceSearchResultItem(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    publisher: str
    source_url: Optional[str] = None
    snippet: str
    similarity_score: float
    retrieval_method: str  # "vector_cosine", "keyword_bm25", "hybrid"


class IntelligenceSearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[IntelligenceSearchResultItem]
