"""
Domain Events — lightweight dataclasses representing things that happened.
Services publish events; handlers/subscribers react to them.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4, UUID
import json


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=_now)

    def to_dict(self) -> dict:
        d = {k: str(v) if isinstance(v, (UUID, datetime)) else v
             for k, v in self.__dict__.items()}
        d["event_type"] = self.__class__.__name__
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class DocumentUploadedEvent(DomainEvent):
    document_id: str = ""
    workspace_id: str = ""
    uploaded_by: str = ""
    file_name: str = ""


@dataclass
class DocumentProcessedEvent(DomainEvent):
    document_id: str = ""
    workspace_id: str = ""
    status: str = "COMPLETED"


@dataclass
class EmbeddingCreatedEvent(DomainEvent):
    document_id: str = ""
    chunk_count: int = 0


@dataclass
class WorkspaceCreatedEvent(DomainEvent):
    workspace_id: str = ""
    org_id: str = ""
    created_by: str = ""


@dataclass
class ResearchGeneratedEvent(DomainEvent):
    session_id: str = ""
    workspace_id: str = ""
    user_id: str = ""
    query: str = ""


@dataclass
class IngestionProgressEvent(DomainEvent):
    job_id: str = ""
    document_id: str = ""
    status: str = ""
    progress: int = 0
    error_message: str = ""
