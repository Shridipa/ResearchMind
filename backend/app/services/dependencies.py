from functools import lru_cache

from app.core.config import settings
from app.document_processing.summarizer import LocalSummarizer
from app.rag.bm25_index import BM25Index
from app.rag.embeddings import build_embedder
from app.rag.retriever import Retriever
from app.rag.vector_store import FaissVectorStore
from app.rag.paper_comparator import PaperComparator


@lru_cache
def get_embedder():
    return build_embedder()


@lru_cache
def get_vector_store():
    embedder = get_embedder()
    return FaissVectorStore(embedder.dimension, settings.faiss_index_path, settings.metadata_path)


@lru_cache
def get_bm25_index():
    return BM25Index(
        index_path=settings.indexes_path / "bm25_index.pkl",
        corpus_path=settings.indexes_path / "bm25_corpus.json",
        metadata_path=settings.indexes_path / "bm25_metadata.json",
    )


@lru_cache
def get_retriever():
    embedder = get_embedder()
    vector_store = get_vector_store()
    bm25_index = get_bm25_index()
    return Retriever(
        embedder=embedder,
        vector_store=vector_store,
        bm25_index=bm25_index,
        use_hybrid=True,
    )


@lru_cache
def get_summarizer():
    """Get local summarization engine."""
    if settings.use_local_summarization:
        return LocalSummarizer(cache_dir=settings.summary_cache_path)
    return None


@lru_cache
def get_paper_comparator():
    """Get paper comparison engine."""
    embedder = get_embedder()
    return PaperComparator(embedder)
