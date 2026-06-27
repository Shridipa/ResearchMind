"""Test and demonstration of paper comparison engine."""

from app.rag.embeddings import build_embedder
from app.rag.paper_comparator import PaperComparator


# Sample research papers
BERT_ABSTRACT = """
BERT (Bidirectional Encoder Representations from Transformers) introduces a new approach to 
pre-training language models. Unlike previous methods that use unidirectional representations, 
BERT uses bidirectional context. We pre-train using masked language modeling and next sentence 
prediction. BERT achieves state-of-the-art results on eleven GLUE tasks with minimal 
task-specific fine-tuning. The model uses the Transformer architecture with multi-head attention.
"""

BERT_METHODOLOGY = """
We use the Transformer architecture as described in Vaswani et al. (2017). The model contains 
12 layers of Transformer blocks with 12 attention heads. Training is performed on 16 TPUs using 
masked language modeling as the pre-training objective. We mask 15% of input tokens and train 
the model to predict them. We also use next sentence prediction as an auxiliary task.
"""

BERT_RESULTS = """
BERT achieves 80.5% accuracy on MRPC, 88.3% on CoLA, and 92.7% on RTE from the GLUE benchmark. 
Compared to ELMo baseline methods showing 76.4%, 63.6%, and 85.2% respectively, BERT provides 
significant improvements. We also achieve 86.3% on QNLI task and 88.6% on QQP. These results 
represent state-of-the-art performance at the time of publication.
"""

ALBERT_ABSTRACT = """
ALBERT (A Lite BERT) addresses the parameter inefficiency of BERT by introducing parameter 
reduction techniques. We reduce model size through factorized embeddings and cross-layer parameter 
sharing. ALBERT achieves comparable or better performance than BERT with significantly fewer 
parameters. Using fewer parameters improves training and inference efficiency.
"""

ALBERT_METHODOLOGY = """
Similar to BERT, we use the Transformer architecture. However, we introduce factorization of the 
embedding parameters into two matrices of lower dimension. We also share parameters across layers 
to reduce total parameter count. Training uses masked language modeling similar to BERT. We 
experiment with different model sizes: ALBERT-base, ALBERT-large, and ALBERT-xlarge.
"""

ALBERT_RESULTS = """
ALBERT-base achieves 78.6% on MRPC, 86.1% on CoLA, and 89.2% on RTE, with 70% fewer parameters 
than BERT-base. ALBERT-large achieves 88.4% on MRPC and 90.5% on RTE, matching or exceeding 
BERT-large while using 30% fewer parameters. On QNLI, ALBERT achieves 87.1%, slightly lower 
than BERT's 86.3% but with much better efficiency. We also show that pre-training time is 
reduced due to parameter sharing.
"""


def test_basic_comparison():
    """Test basic paper comparison."""
    print("\n" + "="*80)
    print("BASIC PAPER COMPARISON TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    comparator = PaperComparator(embedder)
    
    # Build full papers
    bert_paper = BERT_ABSTRACT + "\n\n" + BERT_METHODOLOGY + "\n\n" + BERT_RESULTS
    albert_paper = ALBERT_ABSTRACT + "\n\n" + ALBERT_METHODOLOGY + "\n\n" + ALBERT_RESULTS
    
    # Compare
    result = comparator.compare(
        "bert_2019",
        "BERT: Pre-training of Deep Bidirectional Transformers",
        bert_paper,
        "albert_2020",
        "ALBERT: A Lite BERT for Self-supervised Learning",
        albert_paper,
    )
    
    print(f"Paper 1: {result.paper1_title}")
    print(f"Paper 2: {result.paper2_title}\n")
    print(f"Overall Similarity: {result.overall_similarity*100:.1f}%")
    print(f"Relationship: {result.relationship_type}")
    print(f"Confidence: {result.confidence*100:.0f}%\n")
    
    print(f"Shared Concepts: {', '.join(result.shared_concepts[:5])}\n")
    print(f"BERT Distinctive: {', '.join(result.distinctive_concepts_p1[:3])}")
    print(f"ALBERT Distinctive: {', '.join(result.distinctive_concepts_p2[:3])}\n")
    
    print("Section Comparisons:")
    for section_name, comp in result.section_comparisons.items():
        print(f"  {section_name}: {comp.similarity_score*100:.1f}% similarity")
    
    print("\nRecommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec}")


def test_summary_generation():
    """Test comparison summary generation."""
    print("\n" + "="*80)
    print("COMPARISON SUMMARY TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    comparator = PaperComparator(embedder)
    
    bert_paper = BERT_ABSTRACT + "\n\n" + BERT_METHODOLOGY + "\n\n" + BERT_RESULTS
    albert_paper = ALBERT_ABSTRACT + "\n\n" + ALBERT_METHODOLOGY + "\n\n" + ALBERT_RESULTS
    
    result = comparator.compare(
        "bert_2019",
        "BERT: Pre-training of Deep Bidirectional Transformers",
        bert_paper,
        "albert_2020",
        "ALBERT: A Lite BERT for Self-supervised Learning",
        albert_paper,
    )
    
    summary = comparator.get_comparison_summary(result)
    print(summary)


def test_section_comparison():
    """Test section-level comparison."""
    print("\n" + "="*80)
    print("SECTION COMPARISON TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    comparator = PaperComparator(embedder)
    
    bert_paper = BERT_ABSTRACT + "\n\n" + BERT_METHODOLOGY + "\n\n" + BERT_RESULTS
    albert_paper = ALBERT_ABSTRACT + "\n\n" + ALBERT_METHODOLOGY + "\n\n" + ALBERT_RESULTS
    
    result = comparator.compare(
        "bert_2019",
        "BERT",
        bert_paper,
        "albert_2020",
        "ALBERT",
        albert_paper,
    )
    
    print("Section-by-Section Comparison:\n")
    for section_name, comparison in result.section_comparisons.items():
        print(f"Section: {section_name.upper()}")
        print(f"  Similarity: {comparison.similarity_score*100:.1f}%")
        print(f"  BERT Length: {comparison.paper1_length} words")
        print(f"  ALBERT Length: {comparison.paper2_length} words")
        print(f"  Similarities: {', '.join(comparison.key_similarities[:3]) if comparison.key_similarities else 'None'}")
        print(f"  Differences: {', '.join(comparison.key_differences[:3]) if comparison.key_differences else 'None'}\n")


def test_caching():
    """Test comparison caching."""
    print("\n" + "="*80)
    print("CACHING TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    comparator = PaperComparator(embedder)
    
    bert_paper = BERT_ABSTRACT + "\n\n" + BERT_METHODOLOGY
    albert_paper = ALBERT_ABSTRACT + "\n\n" + ALBERT_METHODOLOGY
    
    # First comparison
    print("First comparison (uncached)...")
    result1 = comparator.compare(
        "bert", "BERT", bert_paper,
        "albert", "ALBERT", albert_paper,
    )
    
    # Check cache
    stats = comparator.get_cache_stats()
    print(f"\nCache Stats: {stats['cached_comparisons']} comparisons cached")
    
    # Second comparison (should be cached)
    print("\nSecond comparison (should use cache)...")
    result2 = comparator.compare(
        "bert", "BERT", bert_paper,
        "albert", "ALBERT", albert_paper,
    )
    
    print(f"Results match: {result1.overall_similarity == result2.overall_similarity}")


def test_relationship_classification():
    """Test relationship classification."""
    print("\n" + "="*80)
    print("RELATIONSHIP CLASSIFICATION TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    comparator = PaperComparator(embedder)
    
    bert_paper = BERT_ABSTRACT + "\n\n" + BERT_METHODOLOGY + "\n\n" + BERT_RESULTS
    albert_paper = ALBERT_ABSTRACT + "\n\n" + ALBERT_METHODOLOGY + "\n\n" + ALBERT_RESULTS
    
    result = comparator.compare(
        "bert", "BERT", bert_paper,
        "albert", "ALBERT", albert_paper,
    )
    
    print(f"Papers: {result.paper1_title} <-> {result.paper2_title}")
    print(f"\nRelationship Type: {result.relationship_type.upper()}")
    print(f"Classification Confidence: {result.confidence*100:.0f}%\n")
    
    relationships = {
        "building_on": "ALBERT builds on/improves BERT's approach",
        "alternative": "These are alternative approaches to the same problem",
        "complementary": "These papers address complementary aspects",
        "unrelated": "These papers cover unrelated topics",
    }
    
    print(f"Interpretation: {relationships.get(result.relationship_type, 'Unknown')}")


if __name__ == "__main__":
    print("\n" + "🎯 PAPER COMPARISON ENGINE DEMO")
    print("=" * 80)
    
    test_basic_comparison()
    test_summary_generation()
    test_section_comparison()
    test_caching()
    test_relationship_classification()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n✓ Section-aware paper comparison")
    print("✓ Semantic similarity analysis")
    print("✓ Concept extraction and matching")
    print("✓ Relationship classification")
    print("✓ Comparison caching")
    print("✓ Human-readable summaries\n")
