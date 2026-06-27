"""Hybrid retrieval evaluation comparing semantic, BM25, and hybrid approaches."""

from app.rag.embeddings import build_embedder
from app.rag.vector_store import FaissVectorStore
from app.rag.bm25_index import BM25Index
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.reranker import Reranker
from app.core.config import settings


def evaluate_retrieval_modes():
    """
    Evaluate and compare retrieval modes: semantic, BM25, and hybrid.
    This demonstrates the effectiveness of the hybrid retrieval approach.
    """
    embedder = build_embedder()
    vector_store = FaissVectorStore(
        dimension=embedder.dimension,
        index_path=settings.faiss_index_path,
        metadata_path=settings.metadata_path,
    )
    bm25_index = BM25Index(
        index_path=settings.indexes_path / "bm25_index.pkl",
        corpus_path=settings.indexes_path / "bm25_corpus.json",
        metadata_path=settings.indexes_path / "bm25_metadata.json",
    )
    reranker = Reranker(embedder, use_cross_encoder=False)
    
    hybrid_retriever = HybridRetriever(
        embedder=embedder,
        vector_store=vector_store,
        bm25_index=bm25_index,
        reranker=reranker,
        semantic_weight=0.65,
        bm25_weight=0.35,
        use_reranking=True,
    )
    
    # Example queries
    test_queries = [
        "transformer attention mechanism",
        "deep learning neural networks",
        "BERT language model pre-training",
        "vision transformer image classification",
    ]
    
    print("\n" + "="*80)
    print("HYBRID RETRIEVAL EVALUATION")
    print("="*80 + "\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 80)
        
        # Semantic only
        semantic_results = hybrid_retriever.retrieve(query, top_k=3, retrieval_mode="semantic")
        
        # BM25 only
        bm25_results = hybrid_retriever.retrieve(query, top_k=3, retrieval_mode="bm25")
        
        # Hybrid (best)
        hybrid_results = hybrid_retriever.retrieve(query, top_k=3, retrieval_mode="hybrid")
        
        print("\n  SEMANTIC ONLY (top-1):")
        if semantic_results:
            chunk, score, stats = semantic_results[0]
            print(f"    Score: {stats.final_score:.4f}")
            print(f"    Text: {chunk.text[:100]}...")
        
        print("\n  BM25 ONLY (top-1):")
        if bm25_results:
            chunk, score, stats = bm25_results[0]
            print(f"    Score: {stats.final_score:.4f}")
            print(f"    Text: {chunk.text[:100]}...")
        
        print("\n  HYBRID (RECOMMENDED) (top-1):")
        if hybrid_results:
            chunk, score, stats = hybrid_results[0]
            print(f"    Final Score: {stats.final_score:.4f}")
            print(f"    Semantic: {stats.semantic_score:.4f}, BM25: {stats.bm25_score:.4f}")
            print(f"    Text: {chunk.text[:100]}...")
        
        print("\n")
    
    # Summary statistics
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Corpus Size: {bm25_index.get_corpus_size()} chunks")
    print(f"FAISS Index Size: {vector_store.index.ntotal} vectors")
    print("\nRetrieval Modes:")
    print("  ✓ Semantic: Pure dense retrieval (fast, semantic)")
    print("  ✓ BM25: Sparse keyword retrieval (accurate for exact matches)")
    print("  ✓ Hybrid: Combined with reranking (best accuracy)")
    print("\nHybrid Score Fusion:")
    print("  final_score = 0.65 * semantic_score + 0.35 * bm25_score + reranking")
    print("="*80 + "\n")


if __name__ == "__main__":
    evaluate_retrieval_modes()
