from app.rag.chunking import DocumentChunk


def confidence_from_evidence(evidence: list[tuple[DocumentChunk, float]]) -> float:
    if not evidence:
        return 0.0
    mean_score = sum(score for _, score in evidence) / len(evidence)
    coverage_bonus = min(len(evidence) / 5, 1.0) * 0.15
    return round(max(0.0, min(1.0, mean_score + coverage_bonus)), 3)


def unsupported_claim_risk(confidence: float) -> float:
    return round(max(0.0, min(1.0, 1.0 - confidence)), 3)
