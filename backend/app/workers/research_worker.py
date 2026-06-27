"""Research worker — runs async AI research/agent workflows."""
import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="app.workers.research_worker.run_research_session",
    queue="research",
    max_retries=2,
    soft_time_limit=300,  # 5 minute soft limit
    time_limit=360,
)
def run_research_session(self, session_id: str, workspace_id: str, query: str, user_id: str) -> dict:
    """Execute a full RAG + agent research workflow asynchronously."""
    try:
        logger.info("Running research session %s for user %s", session_id, user_id)
        # TODO: wire to existing app.agents or app.rag pipeline
        return {"session_id": session_id, "status": "completed"}
    except Exception as exc:
        logger.exception("Research session %s failed: %s", session_id, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.workers.research_worker.summarize_document",
    queue="research",
)
def summarize_document(document_id: str, workspace_id: str) -> dict:
    """Generate an AI summary of a document post-ingestion."""
    logger.info("Summarizing document %s", document_id)
    # TODO: plug into existing summarization service
    return {"document_id": document_id, "status": "summarized"}
