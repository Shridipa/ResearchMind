"""Test paper deletion and index removal."""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from app.services.paper_service import paper_service
from app.services.dependencies import get_retriever
from app.api.v1.schemas import ChatRequest


class TestDeletePaper:
    """Test paper deletion flow."""

    def test_delete_nonexistent_paper_raises(self):
        """Verify deleting nonexistent paper raises error."""
        with pytest.raises(KeyError):
            paper_service.delete_paper("nonexistent_paper_id_12345")

    def test_delete_removes_from_registry(self):
        """Verify delete removes paper from registry."""
        # Get list of papers before
        papers_before = paper_service.list_papers()
        
        if papers_before:
            # Delete first paper
            paper_id = papers_before[0].paper_id
            paper_service.delete_paper(paper_id)
            
            # Verify it's removed from list
            papers_after = paper_service.list_papers()
            paper_ids_after = [p.paper_id for p in papers_after]
            
            assert paper_id not in paper_ids_after

    def test_delete_removes_from_retrieval(self):
        """Verify delete removes chunks from retrieval index."""
        # Get current papers
        papers_before = paper_service.list_papers()
        
        if papers_before:
            paper_id = papers_before[0].paper_id
            
            # Retrieve with the paper before delete
            retriever = get_retriever()
            evidence_before = retriever.retrieve("test query", 5, [paper_id])
            
            # Delete paper
            paper_service.delete_paper(paper_id)
            
            # Retrieve after delete - should be empty
            evidence_after = retriever.retrieve("test query", 5, [paper_id])
            assert len(evidence_after) == 0

    def test_delete_prevents_queries(self):
        """Verify deleted paper doesn't appear in Q&A."""
        papers = paper_service.list_papers()
        
        if papers:
            paper_id = papers[0].paper_id
            
            # Query before delete
            req_before = ChatRequest(question="test query", top_k=5, paper_ids=[paper_id])
            from app.services.rag_service import rag_service
            answer_before = rag_service.answer_question(req_before)
            
            # Delete
            paper_service.delete_paper(paper_id)
            
            # Query after delete
            req_after = ChatRequest(question="test query", top_k=5, paper_ids=[paper_id])
            answer_after = rag_service.answer_question(req_after)
            
            # After delete, should have no sources from that paper
            assert all(s.paper_id != paper_id for s in answer_after.sources)

    def test_delete_one_paper_preserves_others(self):
        """Verify deleting one paper doesn't affect others."""
        papers = paper_service.list_papers()
        
        if len(papers) >= 2:
            # Delete first paper
            paper_id_1 = papers[0].paper_id
            paper_id_2 = papers[1].paper_id
            
            paper_service.delete_paper(paper_id_1)
            
            # Second paper should still be retrievable
            record = paper_service.get_paper(paper_id_2)
            assert record is not None

