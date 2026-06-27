"""Lightweight reranking for hybrid retrieval results."""

from typing import Optional

from sentence_transformers import CrossEncoder, util

from app.rag.chunking import DocumentChunk
from app.rag.embeddings import EmbeddingModel


class Reranker:
    """
    Rerank retrieved documents using semantic similarity or cross-encoders.
    
    Can use either:
    1. Embedding-based reranking (lightweight, always available)
    2. Cross-encoder reranking (more accurate, optional)
    """
    
    def __init__(
        self,
        embedder: EmbeddingModel,
        use_cross_encoder: bool = False,
        cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ) -> None:
        """
        Initialize reranker.
        
        Args:
            embedder: Embedding model for semantic reranking
            use_cross_encoder: Whether to use cross-encoder (heavier but more accurate)
            cross_encoder_model: Cross-encoder model name
        """
        self.embedder = embedder
        self.use_cross_encoder = use_cross_encoder
        self.cross_encoder: Optional[CrossEncoder] = None
        
        if use_cross_encoder:
            try:
                self.cross_encoder = CrossEncoder(cross_encoder_model)
            except Exception as e:
                print(f"Warning: Failed to load cross-encoder: {e}. Falling back to embedding-based reranking.")
                self.use_cross_encoder = False
    
    def rerank(
        self,
        query: str,
        candidates: list[tuple[DocumentChunk, float]],
        top_k: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        """
        Rerank retrieved candidates.
        
        Args:
            query: Original search query
            candidates: List of (DocumentChunk, score) tuples to rerank
            top_k: Number of results to return
        
        Returns:
            Reranked list of (DocumentChunk, rerank_score) tuples
        """
        if not candidates:
            return []
        
        if self.use_cross_encoder and self.cross_encoder:
            return self._rerank_with_cross_encoder(query, candidates, top_k)
        else:
            return self._rerank_with_embeddings(query, candidates, top_k)
    
    def _rerank_with_embeddings(
        self,
        query: str,
        candidates: list[tuple[DocumentChunk, float]],
        top_k: int,
    ) -> list[tuple[DocumentChunk, float]]:
        """Rerank using embedding-based similarity (lightweight)."""
        # Encode query
        query_embedding = self.embedder.encode([query])[0]
        
        # Encode candidate texts
        texts = [chunk.text for chunk, _ in candidates]
        candidate_embeddings = self.embedder.encode(texts)
        
        # Compute similarity scores
        scores = util.pytorch_cos_sim(query_embedding, candidate_embeddings)[0]
        
        # Combine with original scores (weight: 0.7 embedding, 0.3 original)
        reranked = []
        for (chunk, original_score), similarity_score in zip(candidates, scores):
            # Normalize to [0, 1]
            norm_similarity = float((similarity_score + 1) / 2)  # cosine is [-1, 1]
            norm_original = float(original_score)
            
            # Weighted combination
            final_score = 0.7 * norm_similarity + 0.3 * norm_original
            reranked.append((chunk, final_score))
        
        # Sort by score descending
        reranked.sort(key=lambda x: x[1], reverse=True)
        
        return reranked[:top_k]
    
    def _rerank_with_cross_encoder(
        self,
        query: str,
        candidates: list[tuple[DocumentChunk, float]],
        top_k: int,
    ) -> list[tuple[DocumentChunk, float]]:
        """Rerank using cross-encoder (more accurate)."""
        # Prepare query-document pairs
        pairs = [[query, chunk.text] for chunk, _ in candidates]
        
        # Get cross-encoder scores
        cross_scores = self.cross_encoder.predict(pairs)
        
        # Combine with original scores (weight: 0.8 cross-encoder, 0.2 original)
        reranked = []
        for (chunk, original_score), cross_score in zip(candidates, cross_scores):
            # Normalize cross-encoder scores (typically 0-1 range)
            norm_cross = float(cross_score)
            norm_original = float(original_score)
            
            # Weighted combination
            final_score = 0.8 * norm_cross + 0.2 * norm_original
            reranked.append((chunk, final_score))
        
        # Sort by score descending
        reranked.sort(key=lambda x: x[1], reverse=True)
        
        return reranked[:top_k]
