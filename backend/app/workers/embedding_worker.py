"""Embedding worker — dedicated queue for GPU-bound embedding tasks."""
import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="app.workers.embedding_worker.generate_embeddings",
    queue="embeddings",
    max_retries=3,
)
def generate_embeddings(self, document_id: str, chunks: list[str]) -> dict:
    """Generate sentence-transformer embeddings for a list of text chunks."""
    try:
        logger.info("Generating embeddings for document %s (%d chunks)", document_id, len(chunks))
        # TODO: plug in sentence-transformers / existing embedding layer
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer("all-MiniLM-L6-v2")
        # embeddings = model.encode(chunks).tolist()
        return {"document_id": document_id, "chunk_count": len(chunks), "status": "ok"}
    except Exception as exc:
        logger.exception("Embedding task failed: %s", exc)
        raise self.retry(exc=exc)
