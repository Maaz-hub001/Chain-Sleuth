"""
Tests for Threat Intelligence RAG Service and Citations.
"""
from app.services.rag.service import RagService


def test_rag_starter_corpus_loaded():
    rag = RagService()
    docs = rag.get_all_documents()
    assert len(docs) >= 3
    titles = [d["title"] for d in docs]
    assert any("Tornado Cash" in t for t in titles)


def test_rag_search_retrieves_relevant_advisory():
    rag = RagService()
    results = rag.search_intelligence("Tornado Cash zk-SNARKs mixer deposit", top_k=2)
    assert len(results) > 0
    top = results[0]
    assert "Tornado Cash" in top["title"]
    assert top["similarity_score"] > 0.3
    assert top["source_url"] is not None


def test_rag_ingest_custom_advisory():
    rag = RagService()
    doc = rag.ingest_document(
        doc_id="test-doc-999",
        title="Custom Exploiter Technique Advisory",
        publisher="ChainSleuth Security",
        content="Flash loan reentrancy vulnerability exploited in decentralized lending vault.",
        source_url="https://example.com/advisory",
        document_type="advisory"
    )
    assert doc["id"] == "test-doc-999"
    assert doc["chunk_count"] >= 1

    search_res = rag.search_intelligence("Flash loan reentrancy lending vault", top_k=1)
    assert len(search_res) > 0
    assert search_res[0]["document_id"] == "test-doc-999"
