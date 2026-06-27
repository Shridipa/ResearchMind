"""Core paper comparison analysis."""

from dataclasses import dataclass, field
from enum import Enum

from app.rag.embeddings import EmbeddingModel
from app.rag.section_extractor import SectionExtractor, ResearchPaperExtractor


class SimilarityMetric(str, Enum):
    """Types of similarity metrics."""
    SEMANTIC = "semantic"  # Embedding-based
    STRUCTURAL = "structural"  # Section-level
    LEXICAL = "lexical"  # Word overlap
    COMBINED = "combined"  # Weighted combination


@dataclass
class SectionComparison:
    """Comparison of two paper sections."""
    section_name: str
    paper1_title: str
    paper2_title: str
    paper1_text: str
    paper2_text: str
    similarity_score: float  # 0-1
    similarity_type: str
    key_differences: list[str] = field(default_factory=list)
    key_similarities: list[str] = field(default_factory=list)
    paper1_length: int = 0
    paper2_length: int = 0
    
    def __post_init__(self):
        self.paper1_length = len(self.paper1_text.split())
        self.paper2_length = len(self.paper2_text.split())


@dataclass
class PaperComparisonResult:
    """Complete comparison between two papers."""
    paper1_id: str
    paper1_title: str
    paper2_id: str
    paper2_title: str
    
    # Section comparisons
    section_comparisons: dict[str, SectionComparison]
    
    # Overall metrics
    overall_similarity: float  # 0-1
    shared_concepts: list[str]
    distinctive_concepts_p1: list[str]
    distinctive_concepts_p2: list[str]
    
    # Relationships
    relationship_type: str  # "building_on", "alternative", "complementary", "unrelated"
    confidence: float  # 0-1
    
    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "paper1_id": self.paper1_id,
            "paper1_title": self.paper1_title,
            "paper2_id": self.paper2_id,
            "paper2_title": self.paper2_title,
            "section_comparisons": {
                name: {
                    "section_name": comp.section_name,
                    "similarity_score": comp.similarity_score,
                    "key_differences": comp.key_differences,
                    "key_similarities": comp.key_similarities,
                    "paper1_length": comp.paper1_length,
                    "paper2_length": comp.paper2_length,
                }
                for name, comp in self.section_comparisons.items()
            },
            "overall_similarity": self.overall_similarity,
            "shared_concepts": self.shared_concepts,
            "distinctive_concepts_p1": self.distinctive_concepts_p1,
            "distinctive_concepts_p2": self.distinctive_concepts_p2,
            "relationship_type": self.relationship_type,
            "confidence": self.confidence,
            "recommendations": self.recommendations,
        }


class ComparisonAnalyzer:
    """
    Analyze and compare research papers.
    
    Provides:
    - Section-level comparisons
    - Semantic similarity analysis
    - Concept extraction and comparison
    - Relationship classification
    """
    
    def __init__(self, embedder: EmbeddingModel):
        """
        Initialize comparison analyzer.
        
        Args:
            embedder: Embedding model for semantic similarity
        """
        self.embedder = embedder
        self.section_extractor = SectionExtractor()
        self.paper_extractor = ResearchPaperExtractor()
    
    def compare_papers(
        self,
        paper1_id: str,
        paper1_title: str,
        paper1_text: str,
        paper2_id: str,
        paper2_title: str,
        paper2_text: str,
        use_sections: bool = True,
    ) -> PaperComparisonResult:
        """
        Compare two research papers.
        
        Args:
            paper1_id: ID of first paper
            paper1_title: Title of first paper
            paper1_text: Full text of first paper
            paper2_id: ID of second paper
            paper2_title: Title of second paper
            paper2_text: Full text of second paper
            use_sections: If True, compare sections; else compare full texts
        
        Returns:
            PaperComparisonResult with detailed comparison
        """
        # Extract sections
        sections1 = self.section_extractor.extract_sections(paper1_text)
        sections2 = self.section_extractor.extract_sections(paper2_text)
        
        # Compare sections
        section_comparisons = {}
        if use_sections:
            common_sections = set(sections1.keys()) & set(sections2.keys())
            for section_name in common_sections:
                section_comparisons[section_name] = self._compare_sections(
                    section_name,
                    paper1_title,
                    sections1[section_name].content,
                    paper2_title,
                    sections2[section_name].content,
                )
        else:
            # Compare full texts as single section
            section_comparisons["full_text"] = self._compare_sections(
                "full_text",
                paper1_title,
                paper1_text,
                paper2_title,
                paper2_text,
            )
        
        # Extract concepts
        concepts1 = self._extract_concepts(paper1_text)
        concepts2 = self._extract_concepts(paper2_text)
        
        shared_concepts = list(set(concepts1) & set(concepts2))[:10]  # Top 10
        distinctive_p1 = list(set(concepts1) - set(concepts2))[:10]
        distinctive_p2 = list(set(concepts2) - set(concepts1))[:10]
        
        # Calculate overall similarity
        overall_similarity = self._calculate_overall_similarity(section_comparisons)
        
        # Classify relationship
        relationship_type, confidence = self._classify_relationship(
            paper1_text,
            paper2_text,
            shared_concepts,
            overall_similarity,
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall_similarity,
            relationship_type,
            distinctive_p1,
            distinctive_p2,
        )
        
        return PaperComparisonResult(
            paper1_id=paper1_id,
            paper1_title=paper1_title,
            paper2_id=paper2_id,
            paper2_title=paper2_title,
            section_comparisons=section_comparisons,
            overall_similarity=overall_similarity,
            shared_concepts=shared_concepts,
            distinctive_concepts_p1=distinctive_p1,
            distinctive_concepts_p2=distinctive_p2,
            relationship_type=relationship_type,
            confidence=confidence,
            recommendations=recommendations,
        )
    
    def _compare_sections(
        self,
        section_name: str,
        title1: str,
        text1: str,
        title2: str,
        text2: str,
    ) -> SectionComparison:
        """Compare two sections using semantic similarity."""
        # Compute similarity
        similarity = self._compute_semantic_similarity(text1, text2)
        
        # Extract key points
        key_points1 = self._extract_key_phrases(text1)[:5]
        key_points2 = self._extract_key_phrases(text2)[:5]
        
        # Find similarities and differences
        similarities = list(set(key_points1) & set(key_points2))
        differences = {
            "unique_to_p1": [p for p in key_points1 if p not in key_points2][:3],
            "unique_to_p2": [p for p in key_points2 if p not in key_points1][:3],
        }
        
        return SectionComparison(
            section_name=section_name,
            paper1_title=title1,
            paper2_title=title2,
            paper1_text=text1[:500],  # Truncate for storage
            paper2_text=text2[:500],
            similarity_score=similarity,
            similarity_type=SimilarityMetric.SEMANTIC.value,
            key_similarities=similarities,
            key_differences=differences.get("unique_to_p1", []) + differences.get("unique_to_p2", []),
        )
    
    def _compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts."""
        try:
            # Truncate very long texts
            text1_trunc = text1[:1000]
            text2_trunc = text2[:1000]
            
            # Embed texts
            emb1 = self.embedder.embed(text1_trunc)
            emb2 = self.embedder.embed(text2_trunc)
            
            # Compute cosine similarity
            import numpy as np
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return max(0.0, min(1.0, float(similarity)))
        except Exception:
            return 0.5  # Default if embedding fails
    
    def _extract_concepts(self, text: str, top_k: int = 20) -> list[str]:
        """Extract key concepts/terms from text."""
        # Simple approach: extract capitalized terms and common keywords
        import re
        
        concepts = []
        
        # Extract capitalized phrases (likely proper nouns/concepts)
        proper_nouns = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
        concepts.extend(proper_nouns[:10])
        
        # Extract common research terms
        research_terms = [
            term for term in re.findall(r"\b[a-z]+(?:\s+[a-z]+)?\b", text.lower())
            if term in {
                "algorithm", "neural", "network", "deep learning", "model",
                "architecture", "framework", "evaluation", "benchmark",
                "optimization", "training", "inference", "dataset",
            }
        ]
        concepts.extend(research_terms[:5])
        
        return list(set(concepts))[:top_k]
    
    def _extract_key_phrases(self, text: str, top_k: int = 10) -> list[str]:
        """Extract key phrases from text."""
        # Simple: extract 2-3 word phrases
        import re
        
        phrases = re.findall(r"\b[A-Za-z]+(?:\s+[A-Za-z]+){1,2}\b", text)
        
        # Filter for meaningful phrases
        filtered = [
            p for p in phrases
            if len(p.split()) <= 3 and len(p) > 5
        ]
        
        return list(set(filtered))[:top_k]
    
    def _calculate_overall_similarity(
        self,
        section_comparisons: dict[str, SectionComparison],
    ) -> float:
        """Calculate overall similarity score across sections."""
        if not section_comparisons:
            return 0.0
        
        scores = [comp.similarity_score for comp in section_comparisons.values()]
        return sum(scores) / len(scores)
    
    def _classify_relationship(
        self,
        text1: str,
        text2: str,
        shared_concepts: list[str],
        similarity: float,
    ) -> tuple[str, float]:
        """
        Classify relationship between papers.
        
        Returns:
            (relationship_type, confidence)
        """
        # Heuristics for relationship classification
        if similarity > 0.75 and len(shared_concepts) > 8:
            return "building_on", 0.9  # Likely extensions/improvements
        elif similarity > 0.6 and len(shared_concepts) > 5:
            return "complementary", 0.8  # Different but related
        elif similarity > 0.4 and len(shared_concepts) > 2:
            return "alternative", 0.7  # Alternative approaches
        else:
            return "unrelated", 0.6  # Different topics
    
    def _generate_recommendations(
        self,
        similarity: float,
        relationship: str,
        distinctive_p1: list[str],
        distinctive_p2: list[str],
    ) -> list[str]:
        """Generate recommendations based on comparison."""
        recs = []
        
        if similarity > 0.75:
            recs.append("These papers are very similar. Check if paper 2 builds on paper 1.")
        elif similarity > 0.6:
            recs.append("These papers share significant methodology. Consider citing both.")
        elif similarity < 0.3:
            recs.append("These papers approach different problems. Use them for complementary context.")
        
        if relationship == "building_on":
            recs.append("Paper 2 likely improves upon paper 1's approach.")
            if distinctive_p2:
                recs.append(f"Key differences: {', '.join(distinctive_p2[:3])}")
        
        elif relationship == "complementary":
            recs.append(f"Paper 1 excels in: {', '.join(distinctive_p1[:2])}")
            recs.append(f"Paper 2 excels in: {', '.join(distinctive_p2[:2])}")
        
        return recs
