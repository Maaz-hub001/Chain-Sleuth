"""
In-memory vector store with hybrid keyword + cosine search.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.services.rag.embeddings import LocalHybridVectorizer


@dataclass
class IndexedChunk:
    chunk_id: str
    document_id: str
    title: str
    publisher: str
    source_url: Optional[str]
    document_type: str
    content: str
    vector: List[float]
    keywords: List[str]


class InMemoryVectorStore:
    def __init__(self):
        self.chunks: Dict[str, IndexedChunk] = {}
        self.vectorizer = LocalHybridVectorizer()

    def add_chunk(self, chunk: IndexedChunk):
        self.chunks[chunk.chunk_id] = chunk

    def search_hybrid(
        self,
        query: str,
        top_k: int = 3,
        filter_doc_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query_vec = self.vectorizer.embed_text(query)
        query_words = set(w.lower() for w in query.split() if len(w) > 2)

        scored_results = []
        for c in self.chunks.values():
            if filter_doc_type and c.document_type != filter_doc_type:
                continue

            # Vector similarity
            cos_sim = self.vectorizer.cosine_similarity(query_vec, c.vector)

            # Keyword overlap
            content_lower = c.content.lower()
            keyword_hits = sum(1 for w in query_words if w in content_lower)
            kw_score = min(1.0, keyword_hits / max(1, len(query_words)))

            # Hybrid weighted score: 60% vector + 40% keyword
            hybrid_score = round(0.6 * cos_sim + 0.4 * kw_score, 4)

            scored_results.append({
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "title": c.title,
                "publisher": c.publisher,
                "source_url": c.source_url,
                "document_type": c.document_type,
                "content": c.content,
                "similarity_score": hybrid_score,
                "retrieval_method": "hybrid"
            })

        scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_results[:top_k]

    def clear(self):
        self.chunks.clear()
