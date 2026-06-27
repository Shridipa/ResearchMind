"""Test and demonstration of citation-grounded answer validation."""


from app.rag.chunking import DocumentChunk
from app.rag.claim_extractor import ClaimExtractor, FactualClaimExtractor
from app.rag.embeddings import build_embedder
from app.rag.grounding_validator import (
    GroundingValidator,
    GroundingIndicator,
)


# Sample answer and evidence
SAMPLE_ANSWER = """
The Transformer architecture introduces self-attention mechanisms that significantly improve 
performance on NLP tasks. The model achieves 95% accuracy on BERT benchmarks and 
outperforms previous methods by 15%. The approach uses multi-head attention with 8 heads 
and has been successfully applied to over 100 different research projects. 
The training process requires 2 weeks on 16 GPUs.
"""

SAMPLE_EVIDENCE = [
    DocumentChunk(
        chunk_id="chunk1",
        paper_id="paper1",
        title="Attention is All You Need",
        page=1,
        text="The Transformer model introduces self-attention mechanisms for sequence processing.",
    ),
    DocumentChunk(
        chunk_id="chunk2",
        paper_id="paper1",
        title="Attention is All You Need",
        page=2,
        text="We demonstrate strong improvements on machine translation tasks with state-of-the-art BLEU scores.",
    ),
    DocumentChunk(
        chunk_id="chunk3",
        paper_id="paper2",
        title="BERT: Pre-training of Deep Bidirectional Transformers",
        page=1,
        text="BERT achieves state-of-the-art results on multiple NLP benchmarks with improved performance metrics.",
    ),
    DocumentChunk(
        chunk_id="chunk4",
        paper_id="paper2",
        title="BERT: Pre-training of Deep Bidirectional Transformers",
        page=3,
        text="The model uses multi-head attention mechanism with different attention heads.",
    ),
]


def test_claim_extraction():
    """Test claim extraction from answers."""
    print("\n" + "="*80)
    print("CLAIM EXTRACTION TEST")
    print("="*80 + "\n")
    
    extractor = ClaimExtractor()
    
    claims = extractor.extract_claims(SAMPLE_ANSWER)
    
    print(f"Extracted {len(claims)} claims:\n")
    for i, claim in enumerate(claims, 1):
        print(f"{i}. [{claim.claim_type.upper()}] {claim.text}")
        print(f"   Position: {claim.start_pos}-{claim.end_pos}, Confidence: {claim.confidence:.2f}\n")


def test_factual_claim_extraction():
    """Test factual claim extraction."""
    print("\n" + "="*80)
    print("FACTUAL CLAIM EXTRACTION TEST")
    print("="*80 + "\n")
    
    extractor = FactualClaimExtractor()
    
    factual_claims = extractor.extract_claims(SAMPLE_ANSWER)
    quantitative = extractor.extract_quantitative_claims(SAMPLE_ANSWER)
    
    print(f"Factual Claims ({len(factual_claims)}):")
    for claim in factual_claims[:3]:
        print(f"  - {claim.text}")
    
    print(f"\nQuantitative Claims ({len(quantitative)}):")
    for claim in quantitative:
        print(f"  - {claim.text}")


def test_grounding_validation():
    """Test grounding validation."""
    print("\n" + "="*80)
    print("GROUNDING VALIDATION TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    validator = GroundingValidator(embedder)
    
    # Prepare evidence with scores
    evidence_with_scores = [(chunk, 0.8) for chunk in SAMPLE_EVIDENCE]
    
    # Validate
    result = validator.validate_answer(
        SAMPLE_ANSWER,
        evidence_with_scores,
        answer_type="research",
    )
    
    print(f"Groundedness Score: {result.groundedness_score:.1f}%")
    print(f"Hallucination Risk: {result.hallucination_risk:.1f}%")
    print(f"Risk Level: {result.risk_level.upper()}")
    print("\nClaim Analysis:")
    print(f"  Total Claims: {result.total_claims}")
    print(f"  Supported: {result.supported_claims}")
    print(f"  Unsupported: {result.unsupported_claims}")
    print(f"  Support Rate: {result.support_percentage:.1f}%")
    
    print("\nRecommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec}")


def test_highlight_unsupported():
    """Test highlighting unsupported sentences."""
    print("\n" + "="*80)
    print("UNSUPPORTED SENTENCE HIGHLIGHTING TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    validator = GroundingValidator(embedder)
    
    evidence_with_scores = [(chunk, 0.8) for chunk in SAMPLE_EVIDENCE]
    
    highlighting = validator.highlight_unsupported_sentences(
        SAMPLE_ANSWER,
        evidence_with_scores,
        threshold=0.6,
    )
    
    print(f"Supported Claims ({len(highlighting['supported'])}):")
    for claim in highlighting['supported'][:2]:
        print(f"  ✓ {claim['text'][:80]}...")
        print(f"    Similarity: {claim['similarity']:.3f}\n")
    
    print(f"Neutral Claims ({len(highlighting['neutral'])}):")
    for claim in highlighting['neutral'][:2]:
        print(f"  ◐ {claim['text'][:80]}...")
        print(f"    Similarity: {claim['similarity']:.3f}\n")
    
    print(f"Unsupported Claims ({len(highlighting['unsupported'])}):")
    for claim in highlighting['unsupported'][:2]:
        print(f"  ✗ {claim['text'][:80]}...")
        print(f"    Similarity: {claim['similarity']:.3f}\n")


def test_grounding_indicators():
    """Test grounding indicators and formatting."""
    print("\n" + "="*80)
    print("GROUNDING INDICATORS TEST")
    print("="*80 + "\n")
    
    scores = [85, 65, 35]
    labels = ["Well Grounded", "Partially Grounded", "Poorly Grounded"]
    
    for score, label in zip(scores, labels):
        badge = GroundingIndicator.get_groundedness_badge(score)
        risk = 100 - score
        indicator = GroundingIndicator.get_risk_indicator(risk)
        color = GroundingIndicator.get_color_code(score)
        
        print(f"{label}:")
        print(f"  Badge: {badge}")
        print(f"  Risk: {indicator}")
        print(f"  Color: {color}\n")


def test_answer_comparison():
    """Test comparing two answer versions."""
    print("\n" + "="*80)
    print("ANSWER COMPARISON TEST")
    print("="*80 + "\n")
    
    answer1 = (
        "The Transformer uses self-attention and multi-head attention mechanisms. "
        "It performs well on NLP tasks."
    )
    
    answer2 = (
        "The Transformer architecture introduces self-attention mechanisms that significantly improve "
        "performance on NLP tasks. The model achieves state-of-the-art results and has been successfully "
        "applied to many research projects."
    )
    
    embedder = build_embedder()
    validator = GroundingValidator(embedder)
    
    evidence_with_scores = [(chunk, 0.8) for chunk in SAMPLE_EVIDENCE]
    
    comparison = validator.compare_answer_versions(
        answer1,
        answer2,
        evidence_with_scores,
    )
    
    print(f"Answer 1 Groundedness: {comparison['answer1_groundedness']:.1f}%")
    print(f"Answer 2 Groundedness: {comparison['answer2_groundedness']:.1f}%")
    print(f"\nBetter Answer: {comparison['better_answer'].upper()}")
    print(f"Improvement: +{comparison['difference']:.1f}%")


if __name__ == "__main__":
    print("\n" + "🎯 CITATION-GROUNDED ANSWER VALIDATION DEMO")
    print("=" * 80)
    
    test_claim_extraction()
    test_factual_claim_extraction()
    test_grounding_validation()
    test_highlight_unsupported()
    test_grounding_indicators()
    test_answer_comparison()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n✓ Claim extraction from answers")
    print("✓ Semantic matching to evidence")
    print("✓ Hallucination detection")
    print("✓ Grounding quality scoring (0-100%)")
    print("✓ Supported vs unsupported claim identification")
    print("✓ Visual indicators for UI display\n")
