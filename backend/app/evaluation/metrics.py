import time
from collections.abc import Callable


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    if not relevant_ids:
        return 0.0
    return len(set(retrieved_ids[:k]) & relevant_ids) / len(relevant_ids)


def semantic_similarity(a, b) -> float:
    from sklearn.metrics.pairwise import cosine_similarity

    return float(cosine_similarity([a], [b])[0][0])


def measure_latency(fn: Callable, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, time.perf_counter() - start
