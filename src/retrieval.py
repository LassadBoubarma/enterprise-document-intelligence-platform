from __future__ import annotations
import numpy as np
from .access_control import can_access
from .models import Chunk, SearchResult

def _minmax(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values
    lo, hi = float(values.min()), float(values.max())
    if abs(hi - lo) < 1e-12:
        return np.ones_like(values, dtype=float) if hi > 0 else np.zeros_like(values, dtype=float)
    return (values - lo) / (hi - lo)

class HybridRetriever:
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        semantic_weight: float = 0.70,
        bm25_weight: float = 0.30,
        enable_reranker: bool = True,
    ) -> None:
        from sentence_transformers import SentenceTransformer
        self.embedding_model_name = embedding_model
        self.reranker_model_name = reranker_model
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight
        self.enable_reranker = enable_reranker
        self.embedder = SentenceTransformer(embedding_model)
        self._reranker = None
        self.chunks: list[Chunk] = []
        self.embeddings: np.ndarray | None = None
        self._tokenized: list[list[str]] = []
        self.bm25 = None

    def _get_reranker(self):
        if not self.enable_reranker:
            return None
        if self._reranker is None:
            from sentence_transformers import CrossEncoder
            self._reranker = CrossEncoder(self.reranker_model_name)
        return self._reranker

    @staticmethod
    def _tokenise(text: str) -> list[str]:
        return [t.lower() for t in text.split() if t.strip()]

    def build_index(self, chunks: list[Chunk]) -> None:
        from rank_bm25 import BM25Okapi
        if not chunks:
            raise ValueError("No chunks supplied")
        self.chunks = list(chunks)
        texts = [c.text for c in chunks]
        self.embeddings = np.asarray(
            self.embedder.encode(texts, normalize_embeddings=True, show_progress_bar=False),
            dtype=np.float32,
        )
        self._tokenized = [self._tokenise(t) for t in texts]
        self.bm25 = BM25Okapi(self._tokenized)

    def search(self, query: str, user_role: str, top_k: int = 5, candidate_k: int = 20) -> list[SearchResult]:
        if self.embeddings is None or not self.chunks or self.bm25 is None:
            raise RuntimeError("Index not built")
        allowed_idx = [i for i, c in enumerate(self.chunks) if can_access(user_role, c.allowed_roles)]
        if not allowed_idx:
            return []
        q = np.asarray(
            self.embedder.encode([query], normalize_embeddings=True, show_progress_bar=False)[0],
            dtype=np.float32,
        )
        semantic_all = self.embeddings @ q
        bm25_all = np.asarray(self.bm25.get_scores(self._tokenise(query)), dtype=float)
        semantic = semantic_all[allowed_idx]
        bm25 = bm25_all[allowed_idx]
        semantic_norm = _minmax(semantic)
        bm25_norm = _minmax(bm25)
        hybrid = self.semantic_weight * semantic_norm + self.bm25_weight * bm25_norm
        local_order = np.argsort(hybrid)[::-1][:min(candidate_k, len(allowed_idx))]
        candidates = []
        for local_pos in local_order:
            gi = allowed_idx[int(local_pos)]
            candidates.append(SearchResult(
                chunk=self.chunks[gi],
                semantic_score=float(semantic[int(local_pos)]),
                bm25_score=float(bm25[int(local_pos)]),
                hybrid_score=float(hybrid[int(local_pos)]),
            ))
        rr = self._get_reranker()
        if rr is not None and candidates:
            scores = rr.predict([[query, r.chunk.text] for r in candidates])
            for r, score in zip(candidates, scores):
                r.rerank_score = float(score)
            candidates.sort(key=lambda r: r.final_score, reverse=True)
        return candidates[:top_k]
