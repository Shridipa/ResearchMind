"""Match extracted claims to retrieved evidence."""

from dataclasses import dataclass
from typing import Optional

import numpy as np
from sentence_transformers import util

from app.rag.claim_extractor import Claim, ClaimExtractor
from app.rag.chunking import DocumentChunk
from app.rag.embeddings import EmbeddingModel


@dataclass
class ClaimMatch:
    """Evidence match for a claim."""
    claim: Claim
    matched_chunk: Optional[DocumentChunk]
    similarity_score: float
    is_supported: bool
    evidence_text: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "claim": self.claim.text,
            "similarity_score": float(self.similarity_score),
            "is_supported": self.is_supported,
            "evidence": self.evidence_text[:100] if self.evidence_text else None,
            "paper_id": self.matched_chunk.paper_id if self.matched_chunk else None,
        }


class EvidenceMatcher:
    """
    Match extracted claims to retrieved evidence.
    
    Computes semantic similarity between claims and evidence chunks,
    determining if claims are grounded in retrieved documents.
    """
    
    def __init__(
        self,
        embedder: EmbeddingModel,
        support_threshold: float = 0.6,
    ):
        """
        Initialize evidence matcher.
        
        Args:
            embedder: Embedding model for similarity computation
            support_threshold: Similarity score above which claim is considered supported
        """
        self.embedder = embedder
        self.support_threshold = support_threshold
        self.claim_extractor = ClaimExtractor()
    
    def match_claims(
        self,
        answer: str,
        evidence_chunks: list[tuple[DocumentChunk, float]],
        use_threshold: bool = True,
    ) -> list[ClaimMatch]:
        """
        Match all claims in answer to evidence.
        
        Args:
            answer: Generated answer text
            evidence_chunks: Retrieved evidence chunks with scores
            use_threshold: Whether to apply support threshold
        
        Returns:
            List of ClaimMatch objects
        """
        # Extract claims
        claims = self.claim_extractor.extract_claims(answer)
        if not claims or not evidence_chunks:
            return []
        
        # Extract just chunks for similarity matching
        chunks = [chunk for chunk, _ in evidence_chunks]
        
        # Encode evidence once
        evidence_embeddings = self.embedder.encode([c.text for c in chunks])
        if evidence_embeddings.size == 0:
            return []
        
        matches = []
        for claim in claims:
            match = self._match_single_claim(
                claim,
                chunks,
                evidence_embeddings,
                use_threshold,
            )
            matches.append(match)
        
        return matches
    
    def _match_single_claim(
        self,
        claim: Claim,
        chunks: list[DocumentChunk],
        evidence_embeddings: np.ndarray,
        use_threshold: bool,
    ) -> ClaimMatch:
        """Match a single claim to best evidence."""
        # Encode claim
        claim_embedding = self.embedder.encode([claim.text])[0]
        
        # Compute similarities
        similarities = util.pytorch_cos_sim(claim_embedding, evidence_embeddings)[0]
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_score = float(similarities[best_idx])
        best_chunk = chunks[best_idx]
        
        # Determine if supported
        is_supported = best_score >= self.support_threshold if use_threshold else True
        
        return ClaimMatch(
            claim=claim,
            matched_chunk=best_chunk,
            similarity_score=best_score,
            is_supported=is_supported,
            evidence_text=best_chunk.text,
        )
    
    def compute_groundedness_score(self, matches: list[ClaimMatch]) -> float:
        """
        Compute overall groundedness score for all claims.
        
        Args:
            matches: List of claim matches
        
        Returns:
            Score from 0-100 indicating groundedness percentage
        """
        if not matches:
            return 100.0  # Empty answer is vacuously grounded
        
        # Proportion of supported claims
        supported = sum(1 for m in matches if m.is_supported)
        
        # Also consider average similarity
        avg_similarity = np.mean([m.similarity_score for m in matches])
        
        # Weighted combination
        support_score = (supported / len(matches)) * 100
        similarity_score = avg_similarity * 100
        
        groundedness = 0.7 * support_score + 0.3 * similarity_score
        
        return groundedness
    
    def compute_hallucination_risk(self, matches: list[ClaimMatch]) -> float:
        """
        Compute hallucination risk as inverse of groundedness.
        
        Args:
            matches: List of claim matches
        
        Returns:
            Risk score from 0-100 (higher = more hallucination risk)
        """
        groundedness = self.compute_groundedness_score(matches)
        return 100.0 - groundedness
    
    def identify_unsupported_claims(
        self,
        matches: list[ClaimMatch],
        threshold: Optional[float] = None,
    ) -> list[ClaimMatch]:
        """
        Identify claims that lack sufficient evidence.
        
        Args:
            matches: List of claim matches
            threshold: Override support threshold
        
        Returns:
            List of unsupported claim matches
        """
        threshold = threshold or self.support_threshold
        return [m for m in matches if m.similarity_score < threshold]
    
    def create_grounding_report(self, matches: list[ClaimMatch]) -> dict:
        """
        Create comprehensive grounding report.
        
        Args:
            matches: List of claim matches
        
        Returns:
            Report dict with statistics and recommendations
        """
        total_claims = len(matches)
        supported = sum(1 for m in matches if m.is_supported)
        unsupported = total_claims - supported
        
        groundedness = self.compute_groundedness_score(matches)
        hallucination_risk = self.compute_hallucination_risk(matches)
        
        unsupported_claims = self.identify_unsupported_claims(matches)
        
        # Similarity statistics
        similarities = [m.similarity_score for m in matches]
        avg_similarity = np.mean(similarities) if similarities else 0
        min_similarity = np.min(similarities) if similarities else 0
        max_similarity = np.max(similarities) if similarities else 0
        
        # Risk level
        if hallucination_risk < 20:
            risk_level = "low"
        elif hallucination_risk < 50:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "total_claims": total_claims,
            "supported_claims": supported,
            "unsupported_claims": unsupported,
            "support_percentage": (supported / total_claims * 100) if total_claims > 0 else 100,
            "groundedness_score": groundedness,
            "hallucination_risk": hallucination_risk,
            "risk_level": risk_level,
            "avg_similarity": avg_similarity,
            "min_similarity": min_similarity,
            "max_similarity": max_similarity,
            "unsupported_claim_texts": [m.claim.text for m in unsupported_claims],
            "recommendations": self._generate_recommendations(
                total_claims,
                unsupported,
                hallucination_risk,
            ),
        }
    
    def _generate_recommendations(
        self,
        total_claims: int,
        unsupported: int,
        hallucination_risk: float,
    ) -> list[str]:
        """Generate recommendations based on grounding analysis."""
        recommendations = []
        
        if hallucination_risk > 50:
            recommendations.append(
                "High hallucination risk detected. Consider regenerating with more conservative temperature or stricter evidence requirements."
            )
        
        if unsupported > 0:
            percentage = (unsupported / total_claims * 100) if total_claims > 0 else 0
            recommendations.append(
                f"{percentage:.0f}% of claims lack direct evidence support. Verify or reformulate these claims."
            )
        
        if hallucination_risk < 20:
            recommendations.append(
                "Answer is well-grounded in evidence. No action needed."
            )
        
        return recommendations


class ResearchGroundingValidator:
    """
    Specialized grounding validation for research papers.
    
    Focuses on:
    - Factual accuracy
    - Citation alignment
    - Methodological claims
    - Numerical accuracy
    """
    
    def __init__(self, embedder: EmbeddingModel):
        self.embedder = embedder
        self.matcher = EvidenceMatcher(embedder, support_threshold=0.5)
        self.claim_extractor = ClaimExtractor()
    
    def validate_answer(
        self,
        answer: str,
        evidence_chunks: list[tuple[DocumentChunk, float]],
    ) -> dict:
        """
        Comprehensive validation of research answer.
        
        Args:
            answer: Generated answer text
            evidence_chunks: Retrieved evidence chunks
        
        Returns:
            Validation report
        """
        # Extract and match claims
        matches = self.matcher.match_claims(answer, evidence_chunks)
        
        # Generate report
        report = self.matcher.create_grounding_report(matches)
        
        # Add claim details
        report["claims"] = [m.to_dict() for m in matches]
        
        # Compute claim-level stats
        report["claims_by_type"] = self._group_claims_by_type(matches)
        
        return report
    
    def _group_claims_by_type(self, matches: list[ClaimMatch]) -> dict:
        """Group claim matches by claim type."""
        grouped = {}
        for match in matches:
            claim_type = match.claim.claim_type
            if claim_type not in grouped:
                grouped[claim_type] = {
                    "count": 0,
                    "supported": 0,
                    "avg_similarity": 0,
                }
            
            grouped[claim_type]["count"] += 1
            if match.is_supported:
                grouped[claim_type]["supported"] += 1
            grouped[claim_type]["avg_similarity"] += match.similarity_score
        
        # Finalize stats
        for claim_type in grouped:
            count = grouped[claim_type]["count"]
            grouped[claim_type]["avg_similarity"] /= count
        
        return grouped
