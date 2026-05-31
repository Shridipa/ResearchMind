"""Test metadata extraction from research papers."""

import sys
from pathlib import Path

# Setup path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from app.document_processing.pdf_parser import PdfParser


class TestMetadataExtraction:
    """Test title, author, and abstract extraction."""

    @pytest.fixture
    def parser(self):
        return PdfParser()

    @pytest.fixture
    def sample_pdf_path(self):
        """Get path to sample PDF."""
        return Path(__file__).parent.parent.parent / "data" / "papers" / "0891d20b45eb4d0f8c8c8140254a2d95.pdf"

    def test_title_extraction(self, parser, sample_pdf_path):
        """Verify title is correctly extracted."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        doc = parser.parse(sample_pdf_path, paper_id="test")
        assert doc.title is not None
        assert len(doc.title) > 0
        assert doc.title == "The Momentum of News"

    def test_author_extraction_no_affiliation_leakage(self, parser, sample_pdf_path):
        """Verify authors extracted without affiliation keywords."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        doc = parser.parse(sample_pdf_path, paper_id="test")
        text = doc.pages[0].text
        title, authors, abstract = parser.extract_metadata(text)
        
        # Should have real authors
        assert len(authors) >= 2, f"Expected at least 2 authors, got {authors}"
        
        # Should not include affiliation keywords
        forbidden = {"finance", "economics", "university", "school", "institute"}
        author_lower = " ".join(authors).lower()
        for keyword in forbidden:
            assert keyword not in author_lower, f"Found forbidden keyword '{keyword}' in authors: {authors}"
        
        # Specific check for this sample
        assert "Ying Wang" in authors
        assert "Bohui Zhang" in authors
        assert "Xiaoneng Zhu" in authors
        assert all("*" not in author for author in authors)

    def test_abstract_extraction(self, parser, sample_pdf_path):
        """Verify abstract is extracted (or explicitly handled if not found)."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        doc = parser.parse(sample_pdf_path, paper_id="test")
        text = doc.pages[0].text
        title, authors, abstract = parser.extract_metadata(text)
        
        # Abstract may be None for some papers, that's okay
        # But if found, should have reasonable length
        if abstract is not None:
            assert len(abstract) > 20, "Abstract too short"
            assert len(abstract) < 2000, "Abstract too long"

    def test_author_count_reasonable(self, parser, sample_pdf_path):
        """Verify author count is reasonable (not >20 or <1)."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        doc = parser.parse(sample_pdf_path, paper_id="test")
        text = doc.pages[0].text
        title, authors, abstract = parser.extract_metadata(text)
        
        assert 1 <= len(authors) <= 15, f"Unreasonable author count: {len(authors)}"

    def test_author_extraction_strips_affiliation_and_symbols(self, parser):
        """Verify author extraction cleans up affiliation blocks, footnote markers, and draft metadata."""
        sample_text = "The Momentum of News\nYing Wang, Bohui Zhang, and Xiaoneng Zhu*\nThis Draft: October 2018\nFinance Department, University of Testing\nAbstract: This paper..."
        title, authors, abstract = parser.extract_metadata(sample_text)
        assert authors == ["Ying Wang", "Bohui Zhang", "Xiaoneng Zhu"]

    def test_title_not_empty(self, parser, sample_pdf_path):
        """Verify title is not empty or single word."""
        if not sample_pdf_path.exists():
            pytest.skip("Sample PDF not found")
        
        doc = parser.parse(sample_pdf_path, paper_id="test")
        assert doc.title is not None
        assert len(doc.title.split()) >= 2, f"Title too short: {doc.title}"
