from src.evaluator import hit_at_k, reciprocal_rank

def test_reciprocal_rank():
    ranked = ["A", "B", "C"]
    assert reciprocal_rank(ranked, "A") == 1.0
    assert reciprocal_rank(ranked, "B") == 0.5
    assert reciprocal_rank(ranked, "Z") == 0.0

def test_hit_at_k():
    ranked = ["A", "B", "C"]
    assert hit_at_k(ranked, "B", 1) == 0.0
    assert hit_at_k(ranked, "B", 2) == 1.0
