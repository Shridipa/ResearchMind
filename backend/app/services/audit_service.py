"""
Audit Service — logs all user actions to the audit_logs table.
Every sensitive operation (login, upload, delete, permission change) calls this service.
"""
import uuid
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AuditService:
    """
    Append-only audit log writer.
    Each record captures: who, when, what, where.
    """

    async def log(
        self,
        db,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        workspace_id: str | None = None,
        metadata: dict | None = None,
        ip_address: str | None = None,
    ) -> str:
        """Write one audit log entry and return its id."""
        entry_id = str(uuid.uuid4())
        from sqlalchemy import text
        try:
            await db.execute(
                text(
                    """INSERT INTO audit_logs
                       (id, user_id, action, resource_type, resource_id,
                        workspace_id, metadata, ip_address, created_at)
                       VALUES (:id, :user_id, :action, :resource_type, :resource_id,
                               :workspace_id, :metadata::jsonb, :ip_address, :now)"""
                ),
                {
                    "id": entry_id,
                    "user_id": user_id,
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "workspace_id": workspace_id,
                    "metadata": str(metadata or {}),
                    "ip_address": ip_address,
                    "now": datetime.now(timezone.utc),
                },
            )
            await db.commit()
        except Exception as e:
            logger.exception("Failed to write audit log: %s", e)
        return entry_id


audit_service = AuditService()
