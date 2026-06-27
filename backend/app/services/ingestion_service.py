"""
Ingestion Service — orchestrates document upload → job creation → async processing.
"""
import asyncio
import logging
import uuid

from app.services.demo_store import demo_store
from app.services.realtime_service import publish_ingestion_progress, publish_activity

logger = logging.getLogger(__name__)

INLINE_FALLBACK_STAGES = [
    ("UPLOADING", 10),
    ("PROCESSING", 55),
    ("SEARCH_READY", 100),
]


class IngestionService:
    async def start_ingestion(
        self,
        document_id: str,
        workspace_id: str,
        s3_key: str,
        document_name: str = "Document",
        uploaded_by: str = "User",
        job_id: str | None = None,
        db=None,
    ) -> dict:
        job_id = job_id or str(uuid.uuid4())
        demo_store.create_ingestion_job(job_id, document_id, workspace_id, document_name)

        try:
            from app.workers.document_worker import ingest_document
            result = ingest_document.apply_async(
                kwargs={
                    "job_id": job_id,
                    "document_id": document_id,
                    "workspace_id": workspace_id,
                    "s3_key": s3_key,
                    "document_name": document_name,
                },
                queue="documents",
            )
            if getattr(result, "id", None):
                logger.info("Dispatched Celery ingestion job=%s", job_id)
            else:
                raise RuntimeError("Celery did not accept the ingestion job")
        except Exception as exc:
            logger.warning("Celery unavailable, running inline ingestion: %s", exc)
            asyncio.create_task(
                self._run_inline_ingestion(job_id, document_id, workspace_id, document_name, uploaded_by)
            )

        return {"job_id": job_id, "status": "PENDING"}

    async def _run_inline_ingestion(
        self, job_id: str, document_id: str, workspace_id: str, document_name: str, uploaded_by: str
    ):
        """Process ingestion in-process when Celery/Redis workers are unavailable."""
        for stage, progress in INLINE_FALLBACK_STAGES:
            await asyncio.sleep(0.25)
            demo_store.update_ingestion_job(job_id, stage, progress)
            publish_ingestion_progress(
                job_id=job_id,
                document_id=document_id,
                workspace_id=workspace_id,
                document_name=document_name,
                status=stage,
                progress=progress,
            )
        demo_store.update_ingestion_job(job_id, "COMPLETED", 100)
        publish_ingestion_progress(
            job_id=job_id,
            document_id=document_id,
            workspace_id=workspace_id,
            document_name=document_name,
            status="COMPLETED",
            progress=100,
        )
        publish_activity(workspace_id, "DOCUMENT_INDEXED", f"{document_name} is now searchable", uploaded_by)
        logger.info("Inline ingestion completed job=%s", job_id)

    async def get_job_status(self, job_id: str, db=None) -> dict | None:
        job = demo_store.get_ingestion_job(job_id)
        if not job:
            return None
        return {
            "job_id": job["id"],
            "status": job["status"],
            "progress": job["progress"],
            "error_message": job.get("error_message"),
        }
