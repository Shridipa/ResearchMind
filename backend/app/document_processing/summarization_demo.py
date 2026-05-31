"""Test and demonstration of local summarization capabilities."""

import sys
from pathlib import Path

# Sample research paper text (section about transformers)
SAMPLE_TEXT = """
The Transformer architecture has become a foundational model in deep learning, particularly for natural language processing tasks. 
We propose a novel approach to improve the efficiency of transformer models by optimizing the attention mechanism. 
Our method combines both semantic understanding and keyword precision through a hybrid scoring approach.

The main contribution of this work is demonstrating that attention mechanisms can be significantly accelerated through 
a combination of sparse and dense retrieval patterns. We evaluate our approach on multiple datasets including CIFAR-100, ImageNet, and academic benchmarks.

Our methodology involves three key steps: first, we implement a hybrid attention mechanism that combines self-attention with cross-attention; 
second, we optimize through gradient descent with adaptive learning rates; third, we evaluate using standard metrics.

The results show that our approach achieves state-of-the-art performance with 25% improvement in inference speed and 15% reduction in memory usage. 
We test on BERT, GPT, and ViT architectures. The evaluation metrics include accuracy, latency, and throughput.

Limitations of this work include scalability to very large models (>1 billion parameters) and applicability to domain-specific tasks. 
Future work should explore quantum-accelerated attention mechanisms and multi-modal fusion strategies.
"""


def test_extractive_summarization():
    """Test extractive summarization."""
    from app.document_processing.extractive import ResearchPaperExtractor
    
    print("\n" + "="*80)
    print("EXTRACTIVE SUMMARIZATION TEST")
    print("="*80 + "\n")
    
    extractor = ResearchPaperExtractor()
    
    # Test overall summary
    summary = extractor.text_summarizer.summarize(SAMPLE_TEXT, num_sentences=3)
    print("Overall Summary (3 sentences):")
    print(f"  {summary}\n")
    
    # Test section extraction
    print("Extracted Sections:")
    print(f"  Contribution: {extractor.extract_contribution(SAMPLE_TEXT, num_sentences=2)}\n")
    print(f"  Methodology: {extractor.extract_methodology(SAMPLE_TEXT, num_sentences=2)}\n")
    print(f"  Results: {extractor.extract_results(SAMPLE_TEXT, num_sentences=2)}\n")
    print(f"  Limitations: {extractor.extract_limitations(SAMPLE_TEXT, num_sentences=2)}\n")


def test_transformer_summarization():
    """Test transformer-based summarization."""
    from app.document_processing.transformer_summary import AcademicPaperSummarizer
    
    print("\n" + "="*80)
    print("TRANSFORMER SUMMARIZATION TEST")
    print("="*80 + "\n")
    
    summarizer = AcademicPaperSummarizer(device=-1)
    
    if not summarizer.primary.available:
        print("⚠️  Transformer models not available (requires transformers + torch)")
        print("  Install with: pip install transformers torch\n")
        return
    
    # Test summarization
    summary = summarizer.summarize(SAMPLE_TEXT, "general")
    if summary:
        print("Generated Abstract (transformer):")
        print(f"  {summary}\n")
    else:
        print("Summarization failed or returned empty result.\n")


def test_local_summarizer():
    """Test unified local summarizer."""
    from app.document_processing.summarizer import LocalSummarizer, estimate_api_cost_saved
    
    print("\n" + "="*80)
    print("LOCAL SUMMARIZER (UNIFIED) TEST")
    print("="*80 + "\n")
    
    summarizer = LocalSummarizer(cache_dir=Path("/tmp/test_summaries"))
    
    # Get stats
    stats = summarizer.get_summary_stats()
    print(f"Summarizer Mode: {stats['mode']}")
    print(f"Transformer Available: {stats['transformer_available']}")
    print(f"Caching Enabled: {stats['cached']}\n")
    
    # Generate abstract
    abstract = summarizer.summarize_abstract(SAMPLE_TEXT, paper_id="test_paper_001")
    print("Generated Abstract:")
    print(f"  {abstract}\n")
    
    # Generate full summary
    full_summary = summarizer.summarize_paper(SAMPLE_TEXT, paper_id="test_paper_001")
    print("Full Paper Summary:")
    for section, text in full_summary.items():
        print(f"\n  {section.upper()}:")
        print(f"    {text[:100]}...")
    
    # Estimate cost savings
    savings = estimate_api_cost_saved(len(SAMPLE_TEXT), num_summaries=1)
    print(f"\n\nEstimated API Cost Savings:")
    print(f"  Tokens Avoided: {savings['estimated_tokens']:.0f}")
    print(f"  Cost Saved: ${savings['estimated_cost_usd']:.4f}")
    print(f"  API Calls Avoided: {savings['api_calls_avoided']}\n")


if __name__ == "__main__":
    print("\n" + "🚀 LOCAL SUMMARIZATION ENGINE DEMO")
    print("=" * 80)
    
    test_extractive_summarization()
    test_transformer_summarization()
    test_local_summarizer()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n✓ Extractive summarization (always available)")
    print("✓ Transformer summarization (if models installed)")
    print("✓ Smart fallback pipeline")
    print("✓ Summary caching for reuse")
    print("✓ Significant API cost reduction\n")
