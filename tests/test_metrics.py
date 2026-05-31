from app.evaluation.metrics import recall_at_k


def test_recall_at_k():
    assert recall_at_k(["a", "b", "c"], {"b", "d"}, 2) == 0.5
