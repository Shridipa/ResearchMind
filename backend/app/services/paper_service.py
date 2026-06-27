import re
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.api.v1.schemas import (
    CompareResponse,
    PaperActionResponse,
    PaperRecord,
    PaperSearchResult,
    SourceSpan,
    SummaryResponse,
    SummarizationStats,
    UploadResponse,
)
from app.core.config import settings
from app.document_processing.citations import extract_citations
from app.document_processing.pdf_parser import PdfParser
from app.document_processing.extractive import ResearchPaperExtractor
from app.rag.chunking import AdaptiveChunker
from app.rag.generator import GroundedGenerator
from app.rag.paper_comparator import PaperComparator
from app.rag.section_extractor import SectionExtractor
from app.services.dependencies import get_bm25_index, get_embedder, get_retriever, get_summarizer, get_vector_store
from app.services.paper_registry import paper_registry


class PaperService:
    def __init__(self) -> None:
        self.parser = PdfParser()
        self.generator = GroundedGenerator()

    async def ingest_upload(self, file: UploadFile) -> UploadResponse:
        paper_id = uuid4().hex
        upload_dir = settings.data_dir / "papers"
        upload_dir.mkdir(parents=True, exist_ok=True)
        path = upload_dir / f"{paper_id}.pdf"
        with path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        document = self.parser.parse(path, paper_id=paper_id)
        title = document.title
        first_page_text = document.pages[0].text
        parsed_title, authors, first_page_abstract = self.parser.extract_metadata(first_page_text)
        title = parsed_title or title

        chunks = AdaptiveChunker(settings.chunk_size, settings.chunk_overlap).chunk(document)
        embeddings = get_embedder().encode([chunk.text for chunk in chunks])
        # Add to FAISS vector store
        get_vector_store().add(chunks, embeddings)
        # Add to BM25 index for hybrid retrieval
        get_bm25_index().add_chunks(chunks)
        full_text = "\n".join(page.text for page in document.pages)
        citation_strings = sorted(set(extract_citations(full_text)))
        citation_count = len(citation_strings)

        # Extract sections and metadata
        extractor = ResearchPaperExtractor()
        section_extractor = SectionExtractor()
        abstract = section_extractor.extract_abstract(full_text) or first_page_abstract
        if not abstract:
            summarizer = get_summarizer()
            if summarizer:
                abstract = summarizer.summarize_abstract(full_text[:4000], paper_id=paper_id)
        if not abstract:
            abstract = "Abstract extraction could not be completed automatically."

        methodology = extractor.extract_methodology(full_text) or "Methodology could not be extracted automatically."
        limitations = extractor.extract_limitations(full_text)

        key_contributions: list[str] = []
        summarizer = get_summarizer()
        if summarizer:
            summary = summarizer.summarize_paper(full_text[:6000], paper_id=paper_id)
            contribution_text = summary.get("contributions", "")
            key_contributions = [item.strip() for item in re.split(r"\.\s+(?=[A-Z])", contribution_text) if item.strip()]
        if not key_contributions:
            contribution = extractor.extract_contribution(full_text)
            key_contributions = [contribution] if contribution else []

        paper_registry.register(
            paper_id,
            filename=file.filename or path.name,
            title=title,
            chunks_indexed=len(chunks),
            citations_found=citation_count,
            file_path=str(path),
            authors=authors,
            abstract=abstract,
            methodology=methodology,
            limitations=limitations,
            key_contributions=key_contributions,
            citations=citation_strings,
        )
        return UploadResponse(
            paper_id=paper_id,
            filename=file.filename or path.name,
            chunks_indexed=len(chunks),
            citations_found=citation_count,
        )

    def summarize(self, paper_id: str) -> SummaryResponse:
        """Summarize paper using local models first, fallback to LLM."""
        # Try local summarization first (no API cost!)
        summarizer = get_summarizer()
        evidence = get_retriever().retrieve("main contribution methods results limitations", 8, [paper_id])
        
        local_summary = None
        summarization_stats = None
        
        if summarizer and evidence:
            # Combine evidence text for local summarization
            combined_text = "\n".join(chunk.text for chunk, _ in evidence)
            local_summary = summarizer.summarize_paper(combined_text, paper_id=paper_id)
            
            # Create stats
            mode = summarizer.get_summary_mode()
            summarization_stats = SummarizationStats(
                mode=mode,
                tokens_saved=len(combined_text) // 4,  # Rough token estimate
                api_calls_avoided=1,
            )
        
        # Fallback to LLM-based summary if local failed
        if not local_summary:
            summary = self.generator.summarize(evidence)
            if summarization_stats:
                summarization_stats.mode = "llm"
                summarization_stats.api_calls_avoided = 0
        else:
            # Use local summary
            summary = local_summary
        
        # Cache summary in registry
        paper_registry.update(paper_id, summary=summary)
        return SummaryResponse(
            paper_id=paper_id,
            summary=summary,
            sources=[_to_source(chunk, score) for chunk, score in evidence],
            summarization_stats=summarization_stats,
        )

    def list_papers(self) -> list[PaperRecord]:
        records = paper_registry.list_all()
        sorted_records = sorted(records, key=lambda record: record.get("upload_date", ""), reverse=True)
        return [PaperRecord(**r) for r in sorted_records]

    def get_paper(self, paper_id: str) -> PaperRecord | None:
        record = paper_registry.get(paper_id)
        if record is None:
            return None
        return PaperRecord(**record)

    def delete_paper(self, paper_id: str) -> None:
        record = paper_registry.get(paper_id)
        if record is None:
            raise KeyError("Paper not found")

        get_vector_store().remove_chunks([paper_id])
        get_bm25_index().remove_chunks([paper_id])

        file_path = record.get("file_path")
        if file_path:
            try:
                Path(file_path).unlink(missing_ok=True)
            except OSError:
                pass

        paper_registry.delete(paper_id)

    def search_papers(self, query: str, top_k: int = 5) -> list[PaperSearchResult]:
        """Semantic search returning paper-level results with best chunk scores."""
        evidence = get_retriever().retrieve(query, top_k * 4)
        seen: dict[str, float] = {}
        for chunk, score in evidence:
            if chunk.paper_id not in seen or score > seen[chunk.paper_id]:
                seen[chunk.paper_id] = score
        results = []
        for paper_id, score in sorted(seen.items(), key=lambda x: -x[1])[:top_k]:
            record = paper_registry.get(paper_id)
            if record:
                results.append(PaperSearchResult(**record, similarity_score=round(score, 4)))
        return results

    def action(self, action: str, paper_id: str | None = None) -> PaperActionResponse:
        paper = self.get_paper(paper_id) if paper_id else None

        if action == "flashcards":
            cards = [
                {
                    "question": "What is the paper's central research claim?",
                    "answer": paper.summary.get("contributions") if paper and paper.summary and "contributions" in paper.summary else "Review the paper summary to identify the primary contribution.",
                },
                {
                    "question": "Which methods or techniques does the paper use?",
                    "answer": paper.methodology or "Check the paper methodology section for the main techniques used.",
                },
            ]
            result = {"cards": cards}
        elif action == "equations":
            result = {
                "equations": [
                    "Equation extraction is queued for the selected paper.",
                    "Detected equations will include symbol explanations and source locations.",
                ]
            }
        elif action == "extract-citations":
            result = {"citations": paper.citations if paper else []}
        elif action == "compare":
            result = {"message": "Compare two papers using the dedicated compare workflow or compare endpoint."}
        elif action == "literature_review":
            summary_snippet = (
                paper.summary.get("contributions")
                if paper and paper.summary and "contributions" in paper.summary
                else "A helpful next step is to compare this paper's contributions with related work."
            )
            result = {
                "outline": [
                    "Problem framing",
                    "Method families",
                    "Evidence comparison",
                    "Open gaps and future work",
                ],
                "summary": summary_snippet,
                "citations": paper.citations if paper else [],
            }
        else:
            result = {"message": "Research action accepted for grounded processing."}
        return PaperActionResponse(action=action, status="ready", result=result)

    def compare(self, paper_ids: list[str]) -> CompareResponse:
        if len(paper_ids) < 2:
            return CompareResponse(comparison={"error": "Select at least two papers for comparison."}, sources=[])
            
        p1 = paper_registry.get(paper_ids[0])
        p2 = paper_registry.get(paper_ids[1])
        
        if not p1 or not p2:
            return CompareResponse(comparison={"error": "Paper not found."}, sources=[])
            
        # Parse full text
        doc1 = self.parser.parse(Path(p1["file_path"]), p1["paper_id"])
        doc2 = self.parser.parse(Path(p2["file_path"]), p2["paper_id"])
        
        text1 = "\n".join(page.text for page in doc1.pages)
        text2 = "\n".join(page.text for page in doc2.pages)
        
        comparator = PaperComparator(get_embedder())
        result = comparator.compare(
            p1["paper_id"], p1["title"], text1,
            p2["paper_id"], p2["title"], text2
        )
        
        summary = comparator.get_comparison_summary(result)
        
        evidence = get_retriever().retrieve("contribution method dataset result limitation", 10, paper_ids)
        comparison = {
            "summary": summary,
            "overall_similarity": f"{result.overall_similarity * 100:.0f}%",
            "relationship": result.relationship_type.replace("_", " ").title(),
        }
        
        return CompareResponse(
            comparison=comparison,
            sources=[_to_source(chunk, score) for chunk, score in evidence],
        )


def _to_source(chunk, score: float) -> SourceSpan:
    return SourceSpan(
        paper_id=chunk.paper_id,
        title=chunk.title,
        page=chunk.page,
        chunk_id=chunk.chunk_id,
        score=round(score, 4),
        text=chunk.text,
    )


paper_service = PaperService()
