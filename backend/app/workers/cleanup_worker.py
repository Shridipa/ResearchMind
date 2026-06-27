"""Cleanup worker — periodic tasks for storage / dead-job GC."""
import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.cleanup_worker.purge_failed_jobs", queue="cleanup")
def purge_failed_jobs() -> dict:
    """Remove ingestion jobs stuck in FAILED state older than 7 days."""
    logger.info("Purging failed ingestion jobs older than 7 days")
    # TODO: DB cleanup query
    return {"status": "ok"}


@celery_app.task(name="app.workers.cleanup_worker.purge_orphan_vectors", queue="cleanup")
def purge_orphan_vectors() -> dict:
    """Remove vector embeddings whose parent document has been deleted."""
    logger.info("Purging orphan vector embeddings")
    return {"status": "ok"}
