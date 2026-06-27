"""Unified grounding validation system for research answers."""

from dataclasses import dataclass

from app.rag.chunking import DocumentChunk
from app.rag.embeddings import EmbeddingModel
from app.rag.evidence_matcher import EvidenceMatcher, ResearchGroundingValidator


@dataclass
class GroundingValidationResult:
    """Result of grounding validation."""
    answer: str
    groundedness_score: float  # 0-100
    hallucination_risk: float  # 0-100
    risk_level: str  # low, medium, high
    total_claims: int
    supported_claims: int
    unsupported_claims: int
    support_percentage: float  # 0-100
    claim_details: list[dict]
    recommendations: list[str]
    
    def to_dict(self) -> dict:
        return {
            "groundedness_score": self.groundedness_score,
            "hallucination_risk": self.hallucination_risk,
            "risk_level": self.risk_level,
            "total_claims": self.total_claims,
            "supported_claims": self.supported_claims,
            "unsupported_claims": self.unsupported_claims,
            "support_percentage": self.support_percentage,
            "claim_details": self.claim_details,
            "recommendations": self.recommendations,
        }


class GroundingValidator:
    """
    Main grounding validation orchestrator.
    
    Validates whether generated answers are grounded in retrieved evidence.
    """
    
    def __init__(self, embedder: EmbeddingModel):
        """
        Initialize grounding validator.
        
        Args:
            embedder: Embedding model for similarity computation
        """
        self.embedder = embedder
        self.matcher = EvidenceMatcher(embedder, support_threshold=0.6)
        self.research_validator = ResearchGroundingValidator(embedder)
    
    def validate_answer(
        self,
        answer: str,
        evidence_chunks: list[tuple[DocumentChunk, float]],
        answer_type: str = "general",
    ) -> GroundingValidationResult:
        """
        Validate answer grounding in evidence.
        
        Args:
            answer: Generated answer text
            evidence_chunks: Retrieved evidence chunks with scores
            answer_type: Type of answer (general, research, technical)
        
        Returns:
            GroundingValidationResult
        """
        # Use appropriate validator
        if answer_type == "research":
            report = self.research_validator.validate_answer(answer, evidence_chunks)
        else:
            # General validation
            matches = self.matcher.match_claims(answer, evidence_chunks)
            report = self.matcher.create_grounding_report(matches)
            report["claims"] = [m.to_dict() for m in matches]
        
        # Extract key metrics
        groundedness = report.get("groundedness_score", 0)
        hallucination_risk = report.get("hallucination_risk", 0)
        risk_level = report.get("risk_level", "unknown")
        
        return GroundingValidationResult(
            answer=answer,
            groundedness_score=groundedness,
            hallucination_risk=hallucination_risk,
            risk_level=risk_level,
            total_claims=report.get("total_claims", 0),
            supported_claims=report.get("supported_claims", 0),
            unsupported_claims=report.get("unsupported_claims", 0),
            support_percentage=report.get("support_percentage", 0),
            claim_details=report.get("claims", []),
            recommendations=report.get("recommendations", []),
        )
    
    def highlight_unsupported_sentences(
        self,
        answer: str,
        evidence_chunks: list[tuple[DocumentChunk, float]],
        threshold: float = 0.5,
    ) -> dict[str, list[dict]]:
        """
        Identify and highlight unsupported sentences in answer.
        
        Args:
            answer: Generated answer text
            evidence_chunks: Retrieved evidence chunks
            threshold: Support threshold
        
        Returns:
            Dict with supported and unsupported sentences
        """
        matches = self.matcher.match_claims(answer, evidence_chunks, use_threshold=False)
        
        supported = []
        unsupported = []
        neutral = []
        
        for match in matches:
            claim_info = {
                "text": match.claim.text,
                "similarity": match.similarity_score,
                "evidence": match.evidence_text[:150] if match.evidence_text else None,
            }
            
            if match.similarity_score >= threshold:
                supported.append(claim_info)
            elif match.similarity_score >= threshold * 0.7:  # Gray zone
                neutral.append(claim_info)
            else:
                unsupported.append(claim_info)
        
        return {
            "supported": supported,
            "unsupported": unsupported,
            "neutral": neutral,
            "total": len(matches),
        }
    
    def compare_answer_versions(
        self,
        answer1: str,
        answer2: str,
        evidence_chunks: list[tuple[DocumentChunk, float]],
    ) -> dict:
        """
        Compare grounding quality of two answer versions.
        
        Args:
            answer1: First answer version
            answer2: Second answer version
            evidence_chunks: Evidence for comparison
        
        Returns:
            Comparison report
        """
        result1 = self.validate_answer(answer1, evidence_chunks)
        result2 = self.validate_answer(answer2, evidence_chunks)
        
        better = "answer2" if result2.groundedness_score > result1.groundedness_score else "answer1"
        
        return {
            "answer1_groundedness": result1.groundedness_score,
            "answer2_groundedness": result2.groundedness_score,
            "answer1_hallucination_risk": result1.hallucination_risk,
            "answer2_hallucination_risk": result2.hallucination_risk,
            "better_answer": better,
            "difference": abs(result2.groundedness_score - result1.groundedness_score),
        }


class GroundingIndicator:
    """Visual/text indicators for grounding quality."""
    
    @staticmethod
    def get_groundedness_badge(score: float) -> str:
        """Get text badge for groundedness score."""
        if score >= 80:
            return "✓ Well Grounded"
        elif score >= 60:
            return "◐ Partially Grounded"
        else:
            return "✗ Poorly Grounded"
    
    @staticmethod
    def get_risk_indicator(risk: float) -> str:
        """Get text indicator for hallucination risk."""
        if risk < 20:
            return "🟢 Low Risk"
        elif risk < 50:
            return "🟡 Medium Risk"
        else:
            return "🔴 High Risk"
    
    @staticmethod
    def get_color_code(score: float) -> str:
        """Get color code for UI display."""
        if score >= 80:
            return "#10b981"  # Green
        elif score >= 60:
            return "#f59e0b"  # Amber
        else:
            return "#ef4444"  # Red
    
    @staticmethod
    def format_grounding_summary(result: GroundingValidationResult) -> str:
        """Format grounding result as summary text."""
        badge = GroundingIndicator.get_groundedness_badge(result.groundedness_score)
        
        return (
            f"{badge}\n"
            f"Groundedness: {result.groundedness_score:.0f}%\n"
            f"Claims Supported: {result.supported_claims}/{result.total_claims}\n"
            f"Risk Level: {result.risk_level.upper()}"
        )


# Utility functions for integration

def validate_rag_answer(
    answer: str,
    evidence_chunks: list[tuple[DocumentChunk, float]],
    embedder: EmbeddingModel,
) -> GroundingValidationResult:
    """
    Quick validation of RAG answer.
    
    Args:
        answer: Generated answer
        evidence_chunks: Retrieved evidence
        embedder: Embedding model
    
    Returns:
        Validation result
    """
    validator = GroundingValidator(embedder)
    return validator.validate_answer(answer, evidence_chunks, answer_type="research")


def get_grounding_stats(
    result: GroundingValidationResult,
) -> dict[str, float | str]:
    """
    Extract key statistics from validation result.
    
    Args:
        result: Validation result
    
    Returns:
        Stats dict
    """
    return {
        "groundedness": result.groundedness_score,
        "hallucination_risk": result.hallucination_risk,
        "risk_level": result.risk_level,
        "support_percentage": result.support_percentage,
        "status": GroundingIndicator.get_groundedness_badge(result.groundedness_score),
    }
