"""
Threat Intelligence and RAG Search API Routes.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import validate_public_url
from app.services.rag.service import rag_service
from app.schemas.intelligence import (
    IntelligenceDocumentSchema,
    IntelligenceDocumentCreate,
    IntelligenceSearchRequest,
    IntelligenceSearchResponse,
    IntelligenceSearchResultItem
)

router = APIRouter(prefix="/intelligence", tags=["Threat Intelligence"])


@router.get("/documents")
def list_intelligence_documents():
    return rag_service.get_all_documents()


@router.post("/documents")
def ingest_intelligence_document(req: IntelligenceDocumentCreate):
    # SSRF protection
    clean_url = None
    if req.source_url:
        clean_url = validate_public_url(req.source_url)

    doc_id = f"intel-{uuid.uuid4().hex[:8]}"
    result = rag_service.ingest_document(
        doc_id=doc_id,
        title=req.title,
        publisher=req.publisher,
        content=req.content,
        source_url=clean_url,
        publication_date=req.publication_date,
        document_type=req.document_type,
        trust_classification=req.trust_classification
    )
    return result


@router.post("/search", response_model=IntelligenceSearchResponse)
def search_intelligence(req: IntelligenceSearchRequest):
    results = rag_service.search_intelligence(
        query=req.query,
        top_k=req.top_k,
        filter_doc_type=req.filter_doc_type
    )

    items = [
        IntelligenceSearchResultItem(
            document_id=r["document_id"],
            chunk_id=r["chunk_id"],
            title=r["title"],
            publisher=r["publisher"],
            source_url=r["source_url"],
            snippet=r["snippet"],
            similarity_score=r["similarity_score"],
            retrieval_method=r["retrieval_method"]
        )
        for r in results
    ]

    return IntelligenceSearchResponse(
        query=req.query,
        total_results=len(items),
        results=items
    )
