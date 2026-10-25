"""
Embedding & Vectorization providers: Hybrid Local Term/N-Gram Vectorizer and optional OpenAI.
"""
import re
import math
import hashlib
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings


class LocalHybridVectorizer:
    """
    Lightweight, deterministic local text vectorizer combining term-frequency
    and hashing vectorization to produce fixed-dimensional normalized float vectors
    without external heavy models or cloud dependencies.
    """
    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        return [w for w in cleaned.split() if len(w) > 2]

    def embed_text(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.dimension

        vec = [0.0] * self.dimension
        for token in tokens:
            # Deterministic bucket hashing
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign

        # L2 normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 5) for x in vec]
        return vec

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, dot))


class OpenAIEmbedder:
    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or settings.EMBEDDING_API_KEY
        self.model = model

    async def embed_text(self, text: str) -> List[float]:
        if not self.api_key:
            return LocalHybridVectorizer().embed_text(text)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"input": text, "model": self.model}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["data"][0]["embedding"]
        except Exception:
            pass
        return LocalHybridVectorizer().embed_text(text)
