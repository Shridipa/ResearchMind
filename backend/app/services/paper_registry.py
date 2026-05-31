"""Persistent paper registry backed by a JSON file.

Stores paper-level metadata separately from FAISS chunk-level metadata,
enabling list/detail/search operations without scanning the vector store.
"""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PaperRegistry:
    """Thread-safe JSON-backed store of paper records."""

    def __init__(self, registry_path: Path) -> None:
        self._path = registry_path
        self._lock = threading.Lock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, dict[str, Any]] = self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load(self) -> dict[str, dict[str, Any]]:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self._records, indent=2, default=str),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def register(
        self,
        paper_id: str,
        *,
        filename: str,
        title: str,
        chunks_indexed: int,
        citations_found: int,
        file_path: str = "",
        authors: list[str] | None = None,
        abstract: str | None = None,
        methodology: str | None = None,
        limitations: list[str] | None = None,
        key_contributions: list[str] | None = None,
        citations: list[str] | None = None,
    ) -> dict[str, Any]:
        record: dict[str, Any] = {
            "paper_id": paper_id,
            "filename": filename,
            "title": title,
            "chunks_indexed": chunks_indexed,
            "citations_found": citations_found,
            "file_path": file_path,
            "status": "indexed",
            "processing_state": "ready",
            "embedding_status": "indexed",
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "authors": authors or [],
            "abstract": abstract or "Abstract extraction will be populated from the parsed first-page evidence.",
            "sections": ["Abstract", "Introduction", "Methodology", "Results", "Limitations"],
            "methodology": methodology or "Run Summarize to generate a grounded methodology view from retrieved source chunks.",
            "limitations": limitations if limitations is not None else [],
            "key_contributions": key_contributions or [],
            "citations": citations or [],
            "summary": None,
        }
        with self._lock:
            self._records[paper_id] = record
            self._save()
        return record

    def get(self, paper_id: str) -> dict[str, Any] | None:
        return self._records.get(paper_id)

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._records.values())

    def update(self, paper_id: str, **fields: Any) -> None:
        with self._lock:
            if paper_id in self._records:
                self._records[paper_id].update(fields)
                self._save()

    def delete(self, paper_id: str) -> None:
        with self._lock:
            if paper_id in self._records:
                self._records.pop(paper_id)
                self._save()

    def count(self) -> int:
        return len(self._records)


# Singleton — re-uses path from settings
def _build_registry() -> PaperRegistry:
    from app.core.config import settings  # lazy import to avoid circular dep

    return PaperRegistry(settings.data_dir / "paper_registry.json")


paper_registry: PaperRegistry = _build_registry()
