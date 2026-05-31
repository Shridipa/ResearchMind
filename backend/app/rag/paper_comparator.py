"""High-level paper comparison service."""

from dataclasses import dataclass
from app.rag.comparison_analyzer import ComparisonAnalyzer, PaperComparisonResult
from app.rag.embeddings import EmbeddingModel
from app.rag.chunking import DocumentChunk


@dataclass
class PaperComparisonRequest:
    """Request for paper comparison."""
    paper1_id: str
    paper1_title: str
    paper1_text: str
    paper2_id: str
    paper2_title: str
    paper2_text: str
    detailed: bool = False  # Include full text snippets


class PaperComparator:
    """
    High-level interface for comparing research papers.
    
    Handles:
    - Two-paper comparisons
    - Multi-paper comparisons (future)
    - Caching comparison results
    - UI-ready output formatting
    """
    
    def __init__(self, embedder: EmbeddingModel):
        """Initialize paper comparator."""
        self.embedder = embedder
        self.analyzer = ComparisonAnalyzer(embedder)
        self.comparison_cache = {}  # Simple in-memory cache
    
    def compare(
        self,
        paper1_id: str,
        paper1_title: str,
        paper1_text: str,
        paper2_id: str,
        paper2_title: str,
        paper2_text: str,
        use_cache: bool = True,
    ) -> PaperComparisonResult:
        """
        Compare two papers.
        
        Args:
            paper1_id: ID of first paper
            paper1_title: Title of first paper
            paper1_text: Full text of first paper
            paper2_id: ID of second paper
            paper2_title: Title of second paper
            paper2_text: Full text of second paper
            use_cache: Use cached result if available
        
        Returns:
            Comparison result
        """
        # Check cache
        cache_key = f"{paper1_id}_{paper2_id}"
        if use_cache and cache_key in self.comparison_cache:
            return self.comparison_cache[cache_key]
        
        # Also check reversed order
        cache_key_rev = f"{paper2_id}_{paper1_id}"
        if use_cache and cache_key_rev in self.comparison_cache:
            return self.comparison_cache[cache_key_rev]
        
        # Perform comparison
        result = self.analyzer.compare_papers(
            paper1_id,
            paper1_title,
            paper1_text,
            paper2_id,
            paper2_title,
            paper2_text,
        )
        
        # Cache result
        self.comparison_cache[cache_key] = result
        
        return result
    
    def compare_with_chunks(
        self,
        paper1_id: str,
        paper1_title: str,
        paper1_chunks: list[DocumentChunk],
        paper2_id: str,
        paper2_title: str,
        paper2_chunks: list[DocumentChunk],
    ) -> PaperComparisonResult:
        """
        Compare papers using document chunks.
        
        Args:
            paper1_id: ID of first paper
            paper1_title: Title of first paper
            paper1_chunks: Document chunks from first paper
            paper2_id: ID of second paper
            paper2_title: Title of second paper
            paper2_chunks: Document chunks from second paper
        
        Returns:
            Comparison result
        """
        # Reconstruct text from chunks
        paper1_text = "\n".join(chunk.text for chunk in paper1_chunks)
        paper2_text = "\n".join(chunk.text for chunk in paper2_chunks)
        
        return self.compare(
            paper1_id,
            paper1_title,
            paper1_text,
            paper2_id,
            paper2_title,
            paper2_text,
        )
    
    def get_comparison_summary(
        self,
        result: PaperComparisonResult,
    ) -> str:
        """
        Get human-readable summary of comparison.
        
        Args:
            result: Comparison result
        
        Returns:
            Summary text
        """
        summary_parts = []
        
        # Title
        summary_parts.append(f"# Comparison: {result.paper1_title} vs {result.paper2_title}\n")
        
        # Overall similarity
        similarity_pct = result.overall_similarity * 100
        summary_parts.append(f"**Overall Similarity:** {similarity_pct:.0f}%\n")
        
        # Relationship
        summary_parts.append(f"**Relationship:** {result.relationship_type.replace('_', ' ').title()}\n")
        
        # Shared concepts
        if result.shared_concepts:
            summary_parts.append(f"\n**Shared Concepts:**\n")
            for concept in result.shared_concepts[:5]:
                summary_parts.append(f"- {concept}\n")
        
        # Distinctive concepts
        if result.distinctive_concepts_p1:
            summary_parts.append(f"\n**{result.paper1_title} Focuses On:**\n")
            for concept in result.distinctive_concepts_p1[:3]:
                summary_parts.append(f"- {concept}\n")
        
        if result.distinctive_concepts_p2:
            summary_parts.append(f"\n**{result.paper2_title} Focuses On:**\n")
            for concept in result.distinctive_concepts_p2[:3]:
                summary_parts.append(f"- {concept}\n")
        
        # Recommendations
        if result.recommendations:
            summary_parts.append(f"\n**Recommendations:**\n")
            for rec in result.recommendations:
                summary_parts.append(f"- {rec}\n")
        
        return "".join(summary_parts)
    
    def compare_multiple(
        self,
        papers: list[tuple[str, str, str]],  # [(id, title, text), ...]
    ) -> dict[str, PaperComparisonResult]:
        """
        Compare multiple papers pairwise.
        
        Args:
            papers: List of (id, title, text) tuples
        
        Returns:
            Dict mapping comparison keys to results
        """
        results = {}
        
        for i in range(len(papers)):
            for j in range(i + 1, len(papers)):
                p1_id, p1_title, p1_text = papers[i]
                p2_id, p2_title, p2_text = papers[j]
                
                key = f"{p1_id}_vs_{p2_id}"
                results[key] = self.compare(
                    p1_id, p1_title, p1_text,
                    p2_id, p2_title, p2_text,
                )
        
        return results
    
    def clear_cache(self):
        """Clear comparison cache."""
        self.comparison_cache.clear()
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "cached_comparisons": len(self.comparison_cache),
            "cache_keys": list(self.comparison_cache.keys()),
        }
