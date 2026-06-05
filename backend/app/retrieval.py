from __future__ import annotations

import hashlib
import math
import re

import numpy as np

try:
    import faiss
except Exception:  # pragma: no cover - exercised only when faiss is unavailable
    faiss = None

from app.models import Citation
from app.pubmed import PubMedArticle


class VectorRetriever:
    def __init__(self, dimensions: int = 128):
        self.dimensions = dimensions
        self._chunks: list[tuple[PubMedArticle, str]] = []
        self._matrix: np.ndarray | None = None
        self._index = None

    def build(self, articles: list[PubMedArticle]) -> None:
        self._chunks = []
        vectors = []
        for article in articles:
            for chunk in chunk_text(article.abstract):
                self._chunks.append((article, chunk))
                vectors.append(embed_text(chunk, self.dimensions))
        self._matrix = np.array(vectors, dtype="float32") if vectors else np.empty((0, self.dimensions), dtype="float32")
        if faiss and len(self._matrix):
            self._index = faiss.IndexFlatIP(self.dimensions)
            self._index.add(self._matrix)

    def search(self, query: str, top_k: int = 4) -> list[Citation]:
        if self._matrix is None or not len(self._chunks):
            return []
        query_vector = embed_text(query, self.dimensions).reshape(1, -1)
        if self._index:
            scores, indexes = self._index.search(query_vector, min(top_k, len(self._chunks)))
            pairs = zip(indexes[0].tolist(), scores[0].tolist(), strict=False)
        else:
            raw_scores = self._matrix @ query_vector[0]
            top_indexes = np.argsort(raw_scores)[::-1][:top_k]
            pairs = ((int(index), float(raw_scores[index])) for index in top_indexes)
        citations = []
        for index, score in pairs:
            if index < 0:
                continue
            article, chunk = self._chunks[index]
            citations.append(
                Citation(
                    pmid=article.pmid,
                    title=article.title,
                    journal=article.journal,
                    year=article.year,
                    url=article.url,
                    snippet=chunk,
                    score=round(max(score, 0.0), 4),
                )
            )
        return citations


def chunk_text(text: str, max_words: int = 70) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    return [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)]


def embed_text(text: str, dimensions: int) -> np.ndarray:
    vector = np.zeros(dimensions, dtype="float32")
    tokens = re.findall(r"[a-zA-Z][a-zA-Z\-']+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "little") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(float(vector @ vector))
    return vector / norm if norm else vector
