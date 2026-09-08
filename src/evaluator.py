from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv

@dataclass
class RetrievalMetrics:
    total: int
    hit_at_1: float
    hit_at_3: float
    hit_at_5: float
    mrr: float

def reciprocal_rank(ranked_document_ids: list[str], expected_document_id: str) -> float:
    for idx, doc_id in enumerate(ranked_document_ids, start=1):
        if doc_id == expected_document_id:
            return 1.0 / idx
    return 0.0

def hit_at_k(ranked_document_ids: list[str], expected_document_id: str, k: int) -> float:
    return float(expected_document_id in ranked_document_ids[:k])

def load_eval_questions(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def evaluate_retriever(retriever, rows: list[dict[str, str]], top_k: int = 5):
    per_query = []
    for row in rows:
        results = retriever.search(row["question"], row["role"], top_k=top_k, candidate_k=max(20, top_k))
        ranked = [r.chunk.document_id for r in results]
        expected = row["expected_document_id"]
        per_query.append({
            "question": row["question"],
            "role": row["role"],
            "expected_document_id": expected,
            "ranked_document_ids": ranked,
            "hit@1": hit_at_k(ranked, expected, 1),
            "hit@3": hit_at_k(ranked, expected, 3),
            "hit@5": hit_at_k(ranked, expected, 5),
            "rr": reciprocal_rank(ranked, expected),
        })
    n = len(per_query)
    if n == 0:
        metrics = RetrievalMetrics(0, 0.0, 0.0, 0.0, 0.0)
    else:
        metrics = RetrievalMetrics(
            total=n,
            hit_at_1=sum(r["hit@1"] for r in per_query) / n,
            hit_at_3=sum(r["hit@3"] for r in per_query) / n,
            hit_at_5=sum(r["hit@5"] for r in per_query) / n,
            mrr=sum(r["rr"] for r in per_query) / n,
        )
    return metrics, per_query
