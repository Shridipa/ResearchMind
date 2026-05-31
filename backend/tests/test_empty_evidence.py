"""Test empty evidence path handling."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from app.rag.evidence_matcher import EvidenceMatcher
from app.services.rag_service import rag_service
from app.api.v1.schemas import ChatRequest


@pytest.fixture
def mock_embedder():
    """Create a mock embedder for tests."""
    embedder = MagicMock()
    embedder.embed.return_value = [[0.1, 0.2, 0.3]]
    return embedder


class TestEmptyEvidencePath:
    """Test safe handling of empty evidence."""

    def test_empty_evidence_no_crash(self, mock_embedder):
        """Verify grounding validator handles empty evidence gracefully."""
        matcher = EvidenceMatcher(mock_embedder)
        
        # Should not crash with empty evidence
        result = matcher.match_claims("Test answer", [])
        
        assert result == []
        assert isinstance(result, list)

    def test_empty_claims_no_crash(self, mock_embedder):
        """Verify matcher handles text with no claims."""
        matcher = EvidenceMatcher(mock_embedder)
        
        # Should handle empty text
        result = matcher.match_claims("", [])
        
        assert result == []

    def test_no_evidence_response_explicit(self):
        """Verify no evidence returns explicit message."""
        query = "This is a completely nonsensical query about purple triangles computing poetry"
        req = ChatRequest(question=query, top_k=5)
        
        answer = rag_service.answer_question(req)
        
        if len(answer.sources) == 0:
            # Explicitly verify the no-evidence message
            assert answer.answer == "I could not find supporting evidence in the indexed papers."
            assert answer.confidence == 0.0

    def test_grounding_score_with_no_evidence(self):
        """Verify grounding stats work with empty evidence."""
        query = "Extrasensory perception and remote viewing technologies"
        req = ChatRequest(question=query, top_k=5)
        
        answer = rag_service.answer_question(req)
        
        # Should have grounding stats even with no evidence
        assert answer.grounding_stats is not None
        
        if len(answer.sources) == 0:
            # With no evidence, grounding should be perfect (no false claims)
            assert answer.grounding_stats.groundedness_score == 100.0

    def test_weak_evidence_threshold_respected(self):
        """Verify weak evidence triggers no-evidence response."""
        # Query unrelated to any paper
        query = "Cooking recipes for international cuisine"
        req = ChatRequest(question=query, top_k=5)
        
        answer = rag_service.answer_question(req)
        
        # Should handle gracefully - either no sources or explicit message
        assert answer.answer is not None
        assert len(answer.answer) > 0
        
        # If very weak evidence, should say so
        if len(answer.sources) == 0:
            assert "could not find" in answer.answer.lower()

    def test_answer_consistency_with_no_sources(self):
        """Verify answer is consistent when no sources available."""
        query = "Medieval trade routes and spice commerce in 1200s"
        req = ChatRequest(question=query, top_k=5)
        
        answer = rag_service.answer_question(req)
        
        # Consistency checks
        if len(answer.sources) == 0:
            assert answer.confidence == 0.0
            assert answer.answer == "I could not find supporting evidence in the indexed papers."
        else:
            # If sources, should have positive confidence
            assert answer.confidence > 0
