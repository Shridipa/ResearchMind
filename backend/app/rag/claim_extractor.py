"""Extract atomic claims from generated text for grounding validation."""

import re
from dataclasses import dataclass


@dataclass
class Claim:
    """Represents an atomic claim in generated text."""
    text: str
    start_pos: int
    end_pos: int
    claim_type: str = "factual"  # factual, evaluative, comparative, conditional
    confidence: float = 1.0
    
    def __hash__(self):
        return hash(self.text)


class ClaimExtractor:
    """
    Extract atomic claims from generated text.
    
    Approaches:
    - Sentence splitting
    - Clause extraction
    - Dependency-based claim extraction
    - NER for entity-based claims
    """
    
    def __init__(self):
        """Initialize claim extractor."""
        self.verb_patterns = {
            "factual": ["is", "are", "was", "were", "has", "have", "had", "does", "did"],
            "comparative": ["better", "worse", "more", "less", "similar", "different"],
            "evaluative": ["good", "bad", "excellent", "poor", "important", "significant"],
            "causal": ["causes", "leads to", "results in", "due to", "because"],
        }
    
    def extract_claims(self, text: str) -> list[Claim]:
        """
        Extract claims from text.
        
        Args:
            text: Generated text to extract claims from
        
        Returns:
            List of Claim objects
        """
        claims = []
        
        # Split into sentences
        sentences = self._split_sentences(text)
        pos = 0
        
        for sentence in sentences:
            # Extract claims from sentence
            sentence_claims = self._extract_sentence_claims(sentence)
            
            for claim_text in sentence_claims:
                # Find position in original text
                match_pos = text.find(claim_text, pos)
                if match_pos >= 0:
                    claim = Claim(
                        text=claim_text.strip(),
                        start_pos=match_pos,
                        end_pos=match_pos + len(claim_text),
                        claim_type=self._classify_claim(claim_text),
                    )
                    claims.append(claim)
                    pos = match_pos + len(claim_text)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_claims = []
        for claim in claims:
            if claim.text not in seen and len(claim.text.split()) >= 3:  # Min 3 words
                seen.add(claim.text)
                unique_claims.append(claim)
        
        return unique_claims
    
    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Handle abbreviations
        text = re.sub(r'(?<=[a-z])\. (?=[A-Z])', '._PERIOD_', text)
        
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+', text)
        
        # Restore and clean
        sentences = [
            s.replace('_PERIOD_', '.').strip()
            for s in sentences
            if s.strip() and len(s.split()) >= 3  # Min 3 words per claim
        ]
        
        return sentences
    
    def _extract_sentence_claims(self, sentence: str) -> list[str]:
        """Extract claims from a single sentence."""
        claims = []
        
        # Simple heuristic: split on conjunctions
        parts = re.split(r'\s+and\s+|\s+or\s+|\s+but\s+', sentence, flags=re.IGNORECASE)
        
        for part in parts:
            part = part.strip()
            # Remove leading/trailing discourse markers
            part = re.sub(r'^(thus|therefore|however|moreover|furthermore)\s+', '', part, flags=re.IGNORECASE)
            part = re.sub(r'^(the|a|an)\s+', '', part, flags=re.IGNORECASE)
            
            if len(part.split()) >= 3:  # At least 3 words
                claims.append(part)
        
        # If no conjunctions, return whole sentence as one claim
        if not claims:
            claims.append(sentence)
        
        return claims
    
    def _classify_claim(self, text: str) -> str:
        """Classify claim type."""
        text_lower = text.lower()
        
        # Check for comparative markers
        if any(marker in text_lower for marker in ["better", "worse", "more", "less", "outperform", "superior"]):
            return "comparative"
        
        # Check for causal markers
        if any(marker in text_lower for marker in ["cause", "lead", "result", "due to", "because"]):
            return "causal"
        
        # Check for evaluative markers
        if any(marker in text_lower for marker in ["good", "bad", "excellent", "poor", "important", "significant"]):
            return "evaluative"
        
        return "factual"
    
    def merge_claims(self, claims: list[Claim], context_window: int = 2) -> list[Claim]:
        """
        Merge overlapping or adjacent claims.
        
        Args:
            claims: List of extracted claims
            context_window: Words to consider for merging
        
        Returns:
            Merged claims
        """
        if not claims:
            return []
        
        merged = []
        current_group = [claims[0]]
        
        for claim in claims[1:]:
            # Check if claims are adjacent
            prev_claim = current_group[-1]
            gap = claim.start_pos - prev_claim.end_pos
            
            if gap <= context_window * 4:  # Roughly words to chars
                current_group.append(claim)
            else:
                # Merge current group
                if current_group:
                    merged_claim = self._merge_group(current_group)
                    merged.append(merged_claim)
                current_group = [claim]
        
        # Handle last group
        if current_group:
            merged_claim = self._merge_group(current_group)
            merged.append(merged_claim)
        
        return merged
    
    def _merge_group(self, claims: list[Claim]) -> Claim:
        """Merge a group of claims into one."""
        text = " ".join(c.text for c in claims)
        return Claim(
            text=text,
            start_pos=claims[0].start_pos,
            end_pos=claims[-1].end_pos,
            claim_type=claims[0].claim_type,
            confidence=min(c.confidence for c in claims),
        )


class FactualClaimExtractor(ClaimExtractor):
    """
    Specialized extractor for factual claims in research papers.
    """
    
    def extract_claims(self, text: str) -> list[Claim]:
        """Extract factual claims specific to research papers."""
        claims = super().extract_claims(text)
        
        # Filter for factual only
        factual_claims = [c for c in claims if c.claim_type in ["factual", "comparative"]]
        
        return factual_claims
    
    def extract_quantitative_claims(self, text: str) -> list[Claim]:
        """Extract claims containing numbers/metrics."""
        claims = self.extract_claims(text)
        
        # Filter for claims with numbers
        quantitative = [
            c for c in claims 
            if re.search(r'\d+', c.text)  # Has numbers
        ]
        
        return quantitative
    
    def extract_methodological_claims(self, text: str) -> list[Claim]:
        """Extract claims about methods and approaches."""
        sentences = self._split_sentences(text)
        claims = []
        
        method_keywords = [
            "we propose", "we use", "we implement", "we design",
            "our approach", "our method", "algorithm", "technique",
            "is trained", "is evaluated", "is compared"
        ]
        
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in method_keywords):
                claim = Claim(
                    text=sentence,
                    start_pos=0,
                    end_pos=len(sentence),
                    claim_type="methodological",
                )
                claims.append(claim)
        
        return claims
