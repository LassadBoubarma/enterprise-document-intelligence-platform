from pathlib import Path
from src.chunking import pages_to_chunks
from src.evaluator import evaluate_retriever, load_eval_questions
from src.ingestion import load_sample_manifest
from src.retrieval import HybridRetriever

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

pages = load_sample_manifest(DATA)
chunks = pages_to_chunks(pages)
retriever = HybridRetriever(enable_reranker=True)
retriever.build_index(chunks)
rows = load_eval_questions(DATA / "eval_questions.csv")
metrics, details = evaluate_retriever(retriever, rows)

print(f"Questions: {metrics.total}")
print(f"Hit@1: {metrics.hit_at_1:.1%}")
print(f"Hit@3: {metrics.hit_at_3:.1%}")
print(f"Hit@5: {metrics.hit_at_5:.1%}")
print(f"MRR:   {metrics.mrr:.3f}")
print()

for row in details:
    print(row["question"])
    print("  expected:", row["expected_document_id"])
    print("  ranked:  ", " -> ".join(row["ranked_document_ids"]))
