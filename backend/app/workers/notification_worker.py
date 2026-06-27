"""Notification worker — send emails, Slack, webhook notifications."""
import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.notification_worker.send_email", queue="notifications")
def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email notification (SMTP / SES)."""
    logger.info("Sending email to %s: %s", to, subject)
    # TODO: integrate SMTP or AWS SES
    return {"status": "sent", "to": to}


@celery_app.task(name="app.workers.notification_worker.notify_document_ready", queue="notifications")
def notify_document_ready(user_id: str, document_id: str, document_name: str) -> dict:
    """Notify the user that their document has finished processing."""
    logger.info("Notifying user %s: document %s ready", user_id, document_id)
    # TODO: persist notification to DB + push via WebSocket
    return {"status": "notified", "user_id": user_id, "document_id": document_id}
