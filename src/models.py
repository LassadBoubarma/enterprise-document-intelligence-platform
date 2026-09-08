from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

@dataclass
class DocumentPage:
    document_id: str
    title: str
    source: str
    page: int
    text: str
    allowed_roles: List[str] = field(default_factory=lambda: ["all"])

@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    title: str
    source: str
    page: int
    text: str
    allowed_roles: List[str]

@dataclass
class SearchResult:
    chunk: Chunk
    semantic_score: float
    bm25_score: float
    hybrid_score: float
    rerank_score: float | None = None

    @property
    def final_score(self) -> float:
        return float(self.rerank_score if self.rerank_score is not None else self.hybrid_score)
