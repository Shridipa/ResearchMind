"""
Celery application — configure broker/backend and task routing.
Workers are organised into named queues for isolation and scaling.
"""
from celery import Celery

BROKER_URL = "redis://localhost:6379/1"
RESULT_BACKEND = "redis://localhost:6379/2"

celery_app = Celery(
    "researchmind",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=[
        "app.workers.document_worker",
        "app.workers.embedding_worker",
        "app.workers.research_worker",
        "app.workers.cleanup_worker",
        "app.workers.notification_worker",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,           # acknowledge only after task completes (safer retries)
    worker_prefetch_multiplier=1,  # fair dispatching for long-running tasks
    task_routes={
        "app.workers.document_worker.*": {"queue": "documents"},
        "app.workers.embedding_worker.*": {"queue": "embeddings"},
        "app.workers.research_worker.*": {"queue": "research"},
        "app.workers.cleanup_worker.*": {"queue": "cleanup"},
        "app.workers.notification_worker.*": {"queue": "notifications"},
    },
    # Dead-letter handling via task max retries
    task_max_retries=3,
    task_default_retry_delay=60,  # seconds
)
