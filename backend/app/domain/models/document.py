from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, JSON
from .base import BaseModel
from typing import List

class Document(BaseModel):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    workspace: Mapped["Workspace"] = relationship(back_populates="documents")  # noqa: F821

    versions: Mapped[List["DocumentVersion"]] = relationship(back_populates="document")
    ingestion_jobs: Mapped[List["IngestionJob"]] = relationship(back_populates="document")

class DocumentVersion(BaseModel):
    __tablename__ = "document_versions"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    s3_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    change_summary: Mapped[str] = mapped_column(String(500), nullable=True)
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)

    document: Mapped["Document"] = relationship(back_populates="versions")

class IngestionJob(BaseModel):
    __tablename__ = "ingestion_jobs"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str] = mapped_column(String(2000), nullable=True)
    metadata_extracted: Mapped[dict] = mapped_column(JSON, nullable=True)

    document: Mapped["Document"] = relationship(back_populates="ingestion_jobs")
