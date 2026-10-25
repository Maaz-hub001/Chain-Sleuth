"""
Threat Intelligence RAG Service: document ingestion, indexing, and hybrid retrieval.
"""
import os
import glob
import json
import hashlib
import uuid
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.services.rag.embeddings import LocalHybridVectorizer
from app.services.rag.store import InMemoryVectorStore, IndexedChunk


class RagService:
    def __init__(self, knowledge_base_dir: Optional[str] = None):
        self.knowledge_base_dir = knowledge_base_dir or settings.KNOWLEDGE_BASE_DIR
        self.store = InMemoryVectorStore()
        self.vectorizer = LocalHybridVectorizer()
        self._load_starter_corpus()

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        words = text.split()
        if len(words) <= chunk_size:
            return [text]

        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks

    def ingest_document(
        self,
        doc_id: str,
        title: str,
        publisher: str,
        content: str,
        source_url: Optional[str] = None,
        publication_date: Optional[str] = None,
        document_type: str = "advisory",
        trust_classification: str = "verified_research"
    ) -> Dict[str, Any]:
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        chunks = self._chunk_text(content, chunk_size=120, overlap=30)

        indexed_count = 0
        for idx, text_chunk in enumerate(chunks):
            chunk_id = f"{doc_id}-chk-{idx}"
            vec = self.vectorizer.embed_text(text_chunk)
            keywords = [w.lower() for w in text_chunk.split() if len(w) > 3][:10]

            item = IndexedChunk(
                chunk_id=chunk_id,
                document_id=doc_id,
                title=title,
                publisher=publisher,
                source_url=source_url,
                document_type=document_type,
                content=text_chunk,
                vector=vec,
                keywords=keywords
            )
            self.store.add_chunk(item)
            indexed_count += 1

        return {
            "id": doc_id,
            "title": title,
            "publisher": publisher,
            "source_url": source_url,
            "publication_date": publication_date,
            "content_hash": content_hash,
            "document_type": document_type,
            "trust_classification": trust_classification,
            "chunk_count": indexed_count,
            "content": content
        }

    def _load_starter_corpus(self):
        """Loads and indexes starter threat intelligence documents from disk."""
        if not os.path.exists(self.knowledge_base_dir):
            return

        pattern = os.path.join(self.knowledge_base_dir, "*.json")
        doc_files = glob.glob(pattern)
        for filepath in doc_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.ingest_document(
                        doc_id=data.get("id", f"doc-{uuid.uuid4().hex[:8]}"),
                        title=data.get("title", "Untitled Intelligence"),
                        publisher=data.get("publisher", "ChainSleuth Intel"),
                        content=data.get("content", ""),
                        source_url=data.get("source_url"),
                        publication_date=data.get("publication_date"),
                        document_type=data.get("document_type", "advisory"),
                        trust_classification=data.get("trust_classification", "verified_authority")
                    )
            except Exception as e:
                logger.warning(f"Failed to ingest knowledge base doc {filepath}: {e}")

        logger.info(f"RAG Service initialized with {len(self.store.chunks)} indexed chunks.")

    def search_intelligence(
        self,
        query: str,
        top_k: int = 3,
        filter_doc_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = self.store.search_hybrid(query, top_k=top_k, filter_doc_type=filter_doc_type)
        return [
            {
                "document_id": r["document_id"],
                "chunk_id": r["chunk_id"],
                "title": r["title"],
                "publisher": r["publisher"],
                "source_url": r["source_url"],
                "snippet": r["content"],
                "similarity_score": r["similarity_score"],
                "retrieval_method": r["retrieval_method"]
            }
            for r in results
        ]

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Returns metadata for all distinct documents currently loaded."""
        seen = {}
        for c in self.store.chunks.values():
            if c.document_id not in seen:
                seen[c.document_id] = {
                    "id": c.document_id,
                    "title": c.title,
                    "publisher": c.publisher,
                    "source_url": c.source_url,
                    "document_type": c.document_type,
                    "chunk_count": sum(1 for x in self.store.chunks.values() if x.document_id == c.document_id)
                }
        return list(seen.values())


rag_service = RagService()
