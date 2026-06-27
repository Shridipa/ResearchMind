"""Publish real-time events via Redis pub/sub."""
from __future__ import annotations

import json
import logging
import os

logger = logging.getLogger(__name__)


def publish_event(channel: str, payload: dict) -> bool:
    try:
        import redis as sync_redis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = sync_redis.from_url(redis_url, decode_responses=True)
        r.publish(channel, json.dumps(payload))
        return True
    except Exception as exc:
        logger.debug("Redis publish skipped (%s): %s", channel, exc)
        return False


def publish_ingestion_progress(
    *,
    job_id: str,
    document_id: str,
    workspace_id: str,
    document_name: str,
    status: str,
    progress: int,
    error_message: str | None = None,
) -> None:
    publish_event(
        "document_updates",
        {
            "event_type": "IngestionProgressEvent",
            "job_id": job_id,
            "document_id": document_id,
            "workspace_id": workspace_id,
            "document_name": document_name,
            "status": status,
            "progress": progress,
            "error_message": error_message,
        },
    )


def publish_activity(workspace_id: str, action: str, message: str, user: str) -> None:
    publish_event(
        "workspace_updates",
        {
            "event_type": "WorkspaceActivityEvent",
            "workspace_id": workspace_id,
            "action": action,
            "message": message,
            "user": user,
        },
    )


def publish_research_progress(
    *,
    job_id: str,
    workspace_id: str,
    status: str,
    progress: int,
    query: str,
) -> None:
    publish_event(
        "research_updates",
        {
            "event_type": "ResearchProgressEvent",
            "job_id": job_id,
            "workspace_id": workspace_id,
            "status": status,
            "progress": progress,
            "query": query,
        },
    )


def publish_notification(user_id: str, title: str, message: str, ntype: str = "info") -> None:
    publish_event(
        "notifications",
        {
            "event_type": "NotificationEvent",
            "user_id": user_id,
            "type": ntype,
            "title": title,
            "message": message,
        },
    )
