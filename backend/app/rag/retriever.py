from typing import Optional

from app.rag.bm25_index import BM25Index
from app.rag.embeddings import EmbeddingModel
from app.rag.hybrid_retriever import HybridRetriever, RetrievalStats
from app.rag.reranker import Reranker
from app.rag.vector_store import FaissVectorStore


class Retriever:
    """
    Unified retriever interface using hybrid retrieval.
    
    Supports both legacy semantic-only retrieval and new hybrid mode.
    Returns results in backward-compatible format: list[tuple[DocumentChunk, float]]
    """
    
    def __init__(
        self,
        embedder: EmbeddingModel,
        vector_store: FaissVectorStore,
        bm25_index: Optional[BM25Index] = None,
        use_hybrid: bool = True,
    ) -> None:
        """
        Initialize retriever.
        
        Args:
            embedder: Embedding model
            vector_store: FAISS vector store
            bm25_index: Optional BM25 index for hybrid retrieval
            use_hybrid: Whether to use hybrid retrieval (default: True)
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.use_hybrid = use_hybrid
        self.last_stats: Optional[RetrievalStats] = None
        
        # Initialize hybrid retriever if BM25 index is provided
        self.hybrid_retriever: Optional[HybridRetriever] = None
        if use_hybrid and bm25_index:
            reranker = Reranker(embedder, use_cross_encoder=False)
            self.hybrid_retriever = HybridRetriever(
                embedder=embedder,
                vector_store=vector_store,
                bm25_index=bm25_index,
                reranker=reranker,
                semantic_weight=0.65,
                bm25_weight=0.35,
                use_reranking=True,
            )

    def retrieve(
        self,
        query: str,
        top_k: int,
        paper_ids: list[str] | None = None,
        retrieval_mode: str = "hybrid",
    ):
        """
        Retrieve documents.
        
        Args:
            query: Search query
            top_k: Number of results
            paper_ids: Optional paper ID filters
            retrieval_mode: "hybrid", "semantic", or "bm25"
        
        Returns:
            list[tuple[DocumentChunk, float]] - backward compatible format
        """
        # Use hybrid retriever if available
        if self.hybrid_retriever and self.use_hybrid:
            results = self.hybrid_retriever.retrieve(
                query,
                top_k=top_k,
                paper_ids=paper_ids,
                retrieval_mode=retrieval_mode,
            )
            # Extract chunk, score and store stats
            output = []
            for chunk, score, stats in results:
                self.last_stats = stats  # Store for later use
                output.append((chunk, score))
            return output
        
        # Fallback to semantic-only retrieval
        query_vector = self.embedder.encode([query])
        return self.vector_store.search(query_vector, top_k=top_k, paper_ids=paper_ids)
    
    def get_retrieval_stats(self) -> Optional[RetrievalStats]:
        """Get stats from last retrieval (if hybrid)."""
        return self.last_stats
