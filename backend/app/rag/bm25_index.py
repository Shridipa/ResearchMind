"""BM25 sparse retrieval index for keyword-based document search."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import numpy as np

try:
    from rank_bm25 import BM25Okapi
except ModuleNotFoundError:
    class BM25Okapi:
        """Tiny keyword-scoring fallback used when rank-bm25 is not installed."""

        def __init__(self, corpus: list[list[str]]) -> None:
            self.corpus = corpus

        def get_scores(self, query_tokens: list[str]) -> np.ndarray:
            query = set(query_tokens)
            scores = [
                sum(1 for token in document if token in query) / max(len(document), 1)
                for document in self.corpus
            ]
            return np.asarray(scores, dtype="float32")

from app.rag.chunking import DocumentChunk


class BM25Index:
    """
    BM25 sparse retrieval index.
    
    Maintains a BM25 index over document chunks for keyword-based retrieval.
    Persists corpus and tokenized documents to enable efficient reloading.
    """
    
    def __init__(self, index_path: Path, corpus_path: Path, metadata_path: Path) -> None:
        """
        Initialize BM25 index.
        
        Args:
            index_path: Path to save BM25 index state
            corpus_path: Path to save tokenized corpus
            metadata_path: Path to save chunk metadata
        """
        self.index_path = index_path
        self.corpus_path = corpus_path
        self.metadata_path = metadata_path
        
        # Create directories
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.corpus_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create index
        self.bm25: Optional[BM25Okapi] = None
        self.corpus: list[list[str]] = []  # tokenized docs
        self.metadata: list[dict] = []  # chunk metadata
        
        self._load()
    
    def _load(self) -> None:
        """Load index from disk if it exists."""
        if self.corpus_path.exists() and self.metadata_path.exists():
            with open(self.corpus_path, 'r', encoding='utf-8') as f:
                self.corpus = json.load(f)
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            if self.corpus:
                self.bm25 = BM25Okapi(self.corpus)
    
    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        """
        Add chunks to BM25 index.
        
        Args:
            chunks: List of document chunks to index
        """
        if not chunks:
            return
        
        # Tokenize and add to corpus
        for chunk in chunks:
            # Simple whitespace tokenization + lowercase
            tokens = chunk.text.lower().split()
            self.corpus.append(tokens)
            self.metadata.append(asdict(chunk))
        
        # Rebuild BM25 index
        if self.corpus:
            self.bm25 = BM25Okapi(self.corpus)
        
        self.persist()

    def remove_chunks(self, paper_ids: list[str]) -> None:
        if not paper_ids or not self.metadata:
            return

        remaining = [i for i, meta in enumerate(self.metadata) if meta.get("paper_id") not in paper_ids]
        if len(remaining) == len(self.metadata):
            return

        self.corpus = [self.corpus[i] for i in remaining]
        self.metadata = [self.metadata[i] for i in remaining]
        self.bm25 = BM25Okapi(self.corpus) if self.corpus else None
        self.persist()
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        paper_ids: Optional[list[str]] = None,
    ) -> list[tuple[DocumentChunk, float]]:
        """
        Search for top-k documents using BM25.
        
        Args:
            query: Search query
            top_k: Number of results to return
            paper_ids: Optional filter by paper IDs
        
        Returns:
            List of (DocumentChunk, BM25 score) tuples, sorted by score descending
        """
        if not self.bm25 or not self.corpus:
            return []
        
        # Tokenize query
        tokens = query.lower().split()
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k * 4]
        
        results: list[tuple[DocumentChunk, float]] = []
        allowed = set(paper_ids or [])
        
        for idx in top_indices:
            if idx < 0 or idx >= len(self.metadata):
                continue
            
            meta = self.metadata[idx]
            
            # Filter by paper_id if specified
            if allowed and meta.get("paper_id") not in allowed:
                continue
            
            score = float(scores[idx])
            chunk = DocumentChunk(**meta)
            results.append((chunk, score))
            
            if len(results) >= top_k:
                break
        
        return results
    
    def persist(self) -> None:
        """Save index to disk."""
        with open(self.corpus_path, 'w', encoding='utf-8') as f:
            json.dump(self.corpus, f)
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_corpus_size(self) -> int:
        """Get number of indexed documents."""
        return len(self.corpus)
