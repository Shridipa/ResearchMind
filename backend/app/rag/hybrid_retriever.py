"""Hybrid retrieval combining dense semantic and sparse keyword retrieval."""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from app.rag.bm25_index import BM25Index
from app.rag.chunking import DocumentChunk
from app.rag.embeddings import EmbeddingModel
from app.rag.reranker import Reranker
from app.rag.vector_store import FaissVectorStore


@dataclass
class RetrievalStats:
    """Statistics about a hybrid retrieval."""
    semantic_score: float
    bm25_score: float
    final_score: float
    retrieval_mode: str = "hybrid"


class HybridRetriever:
    """
    Hybrid retriever combining dense semantic and sparse keyword retrieval.
    
    Pipeline:
    1. Run semantic retrieval (FAISS)
    2. Run BM25 keyword retrieval
    3. Normalize and fuse scores
    4. Optional reranking
    
    Example:
        final_score = 0.65 * semantic_score + 0.35 * bm25_score
    """
    
    def __init__(
        self,
        embedder: EmbeddingModel,
        vector_store: FaissVectorStore,
        bm25_index: BM25Index,
        reranker: Optional[Reranker] = None,
        semantic_weight: float = 0.65,
        bm25_weight: float = 0.35,
        use_reranking: bool = True,
    ) -> None:
        """
        Initialize hybrid retriever.
        
        Args:
            embedder: Embedding model for semantic retrieval
            vector_store: FAISS vector store
            bm25_index: BM25 index for keyword retrieval
            reranker: Optional reranker for post-processing
            semantic_weight: Weight for semantic scores (0-1)
            bm25_weight: Weight for BM25 scores (0-1)
            use_reranking: Whether to apply reranking
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.reranker = reranker
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight
        self.use_reranking = use_reranking
        
        # Validate weights
        assert abs(semantic_weight + bm25_weight - 1.0) < 1e-6, "Weights must sum to 1.0"
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        paper_ids: Optional[list[str]] = None,
        retrieval_mode: str = "hybrid",
    ) -> list[tuple[DocumentChunk, float, RetrievalStats]]:
        """
        Retrieve documents using hybrid retrieval.
        
        Args:
            query: Search query
            top_k: Number of results to return
            paper_ids: Optional filter by paper IDs
            retrieval_mode: "hybrid", "semantic", or "bm25"
        
        Returns:
            List of (DocumentChunk, final_score, RetrievalStats) tuples
        """
        if retrieval_mode == "semantic":
            return self._retrieve_semantic(query, top_k, paper_ids)
        elif retrieval_mode == "bm25":
            return self._retrieve_bm25(query, top_k, paper_ids)
        else:  # hybrid
            return self._retrieve_hybrid(query, top_k, paper_ids)
    
    def _retrieve_semantic(
        self,
        query: str,
        top_k: int,
        paper_ids: Optional[list[str]],
    ) -> list[tuple[DocumentChunk, float, RetrievalStats]]:
        """Retrieve using semantic search only."""
        query_vector = self.embedder.encode([query])
        results = self.vector_store.search(query_vector, top_k=top_k, paper_ids=paper_ids)
        
        output = []
        for chunk, score in results:
            stats = RetrievalStats(
                semantic_score=score,
                bm25_score=0.0,
                final_score=score,
                retrieval_mode="semantic",
            )
            output.append((chunk, score, stats))
        
        return output
    
    def _retrieve_bm25(
        self,
        query: str,
        top_k: int,
        paper_ids: Optional[list[str]],
    ) -> list[tuple[DocumentChunk, float, RetrievalStats]]:
        """Retrieve using BM25 only."""
        results = self.bm25_index.search(query, top_k=top_k, paper_ids=paper_ids)
        
        output = []
        for chunk, score in results:
            # Normalize BM25 score (typically 0-10, normalize to 0-1)
            norm_score = min(score / 10.0, 1.0)
            stats = RetrievalStats(
                semantic_score=0.0,
                bm25_score=norm_score,
                final_score=norm_score,
                retrieval_mode="bm25",
            )
            output.append((chunk, norm_score, stats))
        
        return output
    
    def _retrieve_hybrid(
        self,
        query: str,
        top_k: int,
        paper_ids: Optional[list[str]],
    ) -> list[tuple[DocumentChunk, float, RetrievalStats]]:
        """Retrieve using hybrid semantic + BM25 retrieval."""
        
        # Retrieve from both indexes (get more candidates for fusion)
        semantic_results = self.vector_store.search(
            self.embedder.encode([query]),
            top_k=top_k * 2,
            paper_ids=paper_ids,
        )
        bm25_results = self.bm25_index.search(
            query,
            top_k=top_k * 2,
            paper_ids=paper_ids,
        )
        
        # Create a dictionary to merge results
        merged: dict[str, dict] = {}  # chunk_id -> {chunk, semantic_score, bm25_score}
        
        # Add semantic results
        for chunk, score in semantic_results:
            merged[chunk.chunk_id] = {
                "chunk": chunk,
                "semantic": float(score),
                "bm25": 0.0,
            }
        
        # Add BM25 results (normalize BM25 scores)
        for chunk, score in bm25_results:
            norm_bm25 = min(float(score) / 10.0, 1.0)  # Normalize to ~0-1
            if chunk.chunk_id in merged:
                merged[chunk.chunk_id]["bm25"] = norm_bm25
            else:
                merged[chunk.chunk_id] = {
                    "chunk": chunk,
                    "semantic": 0.0,
                    "bm25": norm_bm25,
                }
        
        # Compute final scores using weighted fusion
        candidates = []
        for item in merged.values():
            semantic_score = item["semantic"]
            bm25_score = item["bm25"]
            
            # Weighted score fusion
            final_score = (
                self.semantic_weight * semantic_score +
                self.bm25_weight * bm25_score
            )
            
            candidates.append((
                item["chunk"],
                final_score,
                semantic_score,
                bm25_score,
            ))
        
        # Sort by final score
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Apply reranking if enabled
        if self.use_reranking and self.reranker:
            candidates_for_rerank = [(c[0], c[1]) for c in candidates[:top_k * 2]]
            reranked = self.reranker.rerank(query, candidates_for_rerank, top_k)
            output = []
            for chunk, rerank_score in reranked:
                # Find original scores
                orig = next(c for c in candidates if c[0].chunk_id == chunk.chunk_id)
                stats = RetrievalStats(
                    semantic_score=orig[2],
                    bm25_score=orig[3],
                    final_score=rerank_score,
                    retrieval_mode="hybrid_reranked",
                )
                output.append((chunk, rerank_score, stats))
            return output
        
        # Return top-k without reranking
        output = []
        for chunk, final_score, semantic_score, bm25_score in candidates[:top_k]:
            stats = RetrievalStats(
                semantic_score=semantic_score,
                bm25_score=bm25_score,
                final_score=final_score,
                retrieval_mode="hybrid",
            )
            output.append((chunk, final_score, stats))
        
        return output
