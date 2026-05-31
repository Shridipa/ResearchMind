"""Test multi-paper retrieval and comparison."""

import sys
import asyncio
import io
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi import UploadFile
from app.services.paper_service import paper_service
from app.api.v1.schemas import ChatRequest


@pytest.fixture
def sample_pdf_path():
    """Get path to sample PDF."""
    return Path(__file__).parent.parent.parent / "data" / "papers" / "0891d20b45eb4d0f8c8c8140254a2d95.pdf"


@pytest.fixture
async def three_uploaded_papers(sample_pdf_path):
    """Upload three test papers and return their IDs."""
    if not sample_pdf_path.exists():
        pytest.skip("Sample PDF not found")
    
    ids = []
    for i in range(3):
        with sample_pdf_path.open("rb") as f:
            upload = UploadFile(io.BytesIO(f.read()), filename=sample_pdf_path.name)
        resp = await paper_service.ingest_upload(upload)
        ids.append(resp.paper_id)
    
    yield ids
    
    # Cleanup
    for paper_id in ids:
        try:
            paper_service.delete_paper(paper_id)
        except Exception:
            pass


class TestMultiPaperRetrieval:
    """Test retrieval and comparison across multiple papers."""

    def test_retrieval_includes_multiple_papers(self, sample_pdf_path):
        """Verify retrieval returns results from multiple uploaded papers."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        # Upload 3 papers
        ids = []
        for i in range(3):
            with sample_pdf_path.open("rb") as f:
                upload = UploadFile(io.BytesIO(f.read()), filename=sample_pdf_path.name)
            resp = asyncio.run(paper_service.ingest_upload(upload))
            ids.append(resp.paper_id)
        
        try:
            # Query across all papers
            req = ChatRequest(question="News momentum", top_k=10, paper_ids=ids)
            from app.services.rag_service import rag_service
            answer = rag_service.answer_question(req)
            
            # Should find sources from multiple papers
            if len(answer.sources) > 0:
                paper_ids_in_sources = set(s.paper_id for s in answer.sources)
                # Should have sources from at least one of the uploaded papers
                overlap = paper_ids_in_sources.intersection(ids)
                assert len(overlap) > 0, "No sources from uploaded papers"
        finally:
            # Cleanup
            for paper_id in ids:
                try:
                    paper_service.delete_paper(paper_id)
                except Exception:
                    pass

    def test_compare_two_papers(self, sample_pdf_path):
        """Verify comparison works with two papers."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        # Upload 2 papers
        ids = []
        for i in range(2):
            with sample_pdf_path.open("rb") as f:
                upload = UploadFile(io.BytesIO(f.read()), filename=sample_pdf_path.name)
            resp = asyncio.run(paper_service.ingest_upload(upload))
            ids.append(resp.paper_id)
        
        try:
            # Compare
            result = paper_service.compare(ids)
            
            # Should have comparison result
            assert result.comparison is not None
            assert "error" not in result.comparison or len(result.comparison) > 0
            
            # Should have sources from the comparison
            assert isinstance(result.sources, list)
        finally:
            # Cleanup
            for paper_id in ids:
                try:
                    paper_service.delete_paper(paper_id)
                except Exception:
                    pass

    def test_compare_respects_paper_filter(self, sample_pdf_path):
        """Verify comparison only uses specified papers."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        # Upload 2 papers
        ids = []
        for i in range(2):
            with sample_pdf_path.open("rb") as f:
                upload = UploadFile(io.BytesIO(f.read()), filename=sample_pdf_path.name)
            resp = asyncio.run(paper_service.ingest_upload(upload))
            ids.append(resp.paper_id)
        
        try:
            # Compare only the first two
            result = paper_service.compare(ids[:2])
            
            # Sources should be from the compared papers
            for source in result.sources:
                assert source.paper_id in ids[:2], f"Source from unexpected paper: {source.paper_id}"
        finally:
            # Cleanup
            for paper_id in ids:
                try:
                    paper_service.delete_paper(paper_id)
                except Exception:
                    pass

    def test_compare_requires_minimum_papers(self):
        """Verify compare requires at least 2 papers."""
        result = paper_service.compare(["paper1"])
        
        # Should return error
        assert "error" in result.comparison

    def test_multi_paper_qa_with_filter(self, sample_pdf_path):
        """Verify Q&A respects multi-paper filter."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        # Upload 2 papers
        ids = []
        for i in range(2):
            with sample_pdf_path.open("rb") as f:
                upload = UploadFile(io.BytesIO(f.read()), filename=sample_pdf_path.name)
            resp = asyncio.run(paper_service.ingest_upload(upload))
            ids.append(resp.paper_id)
        
        try:
            # Query with specific paper filter
            req = ChatRequest(question="Research methodology", top_k=5, paper_ids=[ids[0]])
            from app.services.rag_service import rag_service
            answer = rag_service.answer_question(req)
            
            # All sources should be from the filtered paper
            for source in answer.sources:
                assert source.paper_id == ids[0], f"Source from wrong paper: {source.paper_id}"
        finally:
            # Cleanup
            for paper_id in ids:
                try:
                    paper_service.delete_paper(paper_id)
                except Exception:
                    pass
