"""
Persistent demo data store for ResearchMind 2.0.
JSON-backed so judges can use the full demo without PostgreSQL.
"""
from __future__ import annotations

import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.auth.jwt_handler import hash_password, verify_password
from app.auth.rbac import Role
from app.core.config import settings

logger = logging.getLogger(__name__)

DEMO_USER_ID = "demo-user-001"
DEMO_WORKSPACE_ID = "demo-workspace-001"
DEMO_EMAIL = "demo@researchmind.ai"
DEMO_PASSWORD = "Demo@123"

_lock = threading.Lock()
_store_path = settings.data_dir / "demo_store.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_store() -> dict[str, Any]:
    return {
        "users": [
            {
                "id": DEMO_USER_ID,
                "email": DEMO_EMAIL,
                "hashed_password": hash_password(DEMO_PASSWORD),
                "first_name": "Demo",
                "last_name": "Admin",
                "role": Role.WORKSPACE_ADMIN.value,
            }
        ],
        "workspaces": [
            {
                "id": DEMO_WORKSPACE_ID,
                "name": "ResearchMind Demo Workspace",
                "description": "Pre-loaded demo workspace for judges and evaluators",
                "created_at": _now(),
                "member_count": 4,
            }
        ],
        "workspace_members": [
            {"workspace_id": DEMO_WORKSPACE_ID, "user_id": DEMO_USER_ID, "role": Role.WORKSPACE_ADMIN.value},
        ],
        "documents": [
            {
                "id": "doc-001",
                "workspace_id": DEMO_WORKSPACE_ID,
                "title": "AI Research Trends 2026",
                "file_name": "AI Research Trends 2026.pdf",
                "file_type": "PDF",
                "size_bytes": 2457600,
                "status": "COMPLETED",
                "progress": 100,
                "uploaded_by": "Demo Admin",
                "uploaded_at": _now(),
                "versions": [
                    {"version": 1, "created_at": _now(), "author": "Demo Admin", "summary": "Initial upload"},
                ],
            },
            {
                "id": "doc-002",
                "workspace_id": DEMO_WORKSPACE_ID,
                "title": "Market Analysis Report",
                "file_name": "Market Analysis Report.docx",
                "file_type": "DOCX",
                "size_bytes": 1843200,
                "status": "COMPLETED",
                "progress": 100,
                "uploaded_by": "Alex Chen",
                "uploaded_at": _now(),
                "versions": [
                    {"version": 1, "created_at": _now(), "author": "Alex Chen", "summary": "Initial upload"},
                ],
            },
            {
                "id": "doc-003",
                "workspace_id": DEMO_WORKSPACE_ID,
                "title": "Technical Architecture",
                "file_name": "Technical Architecture.md",
                "file_type": "MD",
                "size_bytes": 524288,
                "status": "COMPLETED",
                "progress": 100,
                "uploaded_by": "Priya Singh",
                "uploaded_at": _now(),
                "versions": [
                    {"version": 1, "created_at": _now(), "author": "Priya Singh", "summary": "Initial upload"},
                ],
            },
            {
                "id": "doc-004",
                "workspace_id": DEMO_WORKSPACE_ID,
                "title": "Machine Learning Survey",
                "file_name": "Machine Learning Survey.pdf",
                "file_type": "PDF",
                "size_bytes": 3145728,
                "status": "EMBEDDING",
                "progress": 62,
                "uploaded_by": "Demo Admin",
                "uploaded_at": _now(),
                "versions": [
                    {"version": 1, "created_at": _now(), "author": "Demo Admin", "summary": "Initial upload"},
                ],
            },
        ],
        "research_projects": [
            {"id": "rp-001", "workspace_id": DEMO_WORKSPACE_ID, "name": "AI Adoption Research", "status": "active"},
            {"id": "rp-002", "workspace_id": DEMO_WORKSPACE_ID, "name": "Healthcare Analytics Study", "status": "active"},
            {"id": "rp-003", "workspace_id": DEMO_WORKSPACE_ID, "name": "FinTech Market Research", "status": "completed"},
        ],
        "ingestion_jobs": [
            {
                "id": "job-001",
                "document_id": "doc-004",
                "workspace_id": DEMO_WORKSPACE_ID,
                "document_name": "Machine Learning Survey.pdf",
                "status": "EMBEDDING",
                "progress": 62,
                "error_message": None,
                "created_at": _now(),
            }
        ],
        "research_jobs": [],
        "activity": [
            {"id": "act-001", "workspace_id": DEMO_WORKSPACE_ID, "action": "DOCUMENT_UPLOAD", "message": "AI Research Trends 2026.pdf uploaded", "user": "Demo Admin", "timestamp": _now()},
            {"id": "act-002", "workspace_id": DEMO_WORKSPACE_ID, "action": "RESEARCH_COMPLETED", "message": "FinTech Market Research analysis completed", "user": "Alex Chen", "timestamp": _now()},
            {"id": "act-003", "workspace_id": DEMO_WORKSPACE_ID, "action": "VERSION_CREATED", "message": "Version 2 created for Market Analysis Report", "user": "Priya Singh", "timestamp": _now()},
            {"id": "act-004", "workspace_id": DEMO_WORKSPACE_ID, "action": "MEMBER_ADDED", "message": "Marcus Wu joined the workspace", "user": "Demo Admin", "timestamp": _now()},
            {"id": "act-005", "workspace_id": DEMO_WORKSPACE_ID, "action": "AI_SUMMARY", "message": "AI summary generated for Technical Architecture", "user": "System", "timestamp": _now()},
        ],
        "notifications": [],
        "metrics": {
            "documents_processed_today": 42,
            "active_research_jobs": 3,
            "queue_depth": 1,
            "workspace_members": 4,
            "storage_used_gb": 2.4,
            "search_queries_today": 187,
            "avg_processing_time_sec": 144,
            "documents_total": 10000,
            "research_sessions_total": 1000,
            "reliability_pct": 99.9,
        },
    }


class DemoStore:
    def __init__(self):
        self._data: dict[str, Any] = {}

    def load(self) -> None:
        _store_path.parent.mkdir(parents=True, exist_ok=True)
        with _lock:
            if _store_path.exists():
                try:
                    self._data = json.loads(_store_path.read_text(encoding="utf-8"))
                    logger.info("Demo store loaded from %s", _store_path)
                    return
                except Exception as exc:
                    logger.warning("Demo store corrupt, re-seeding: %s", exc)
            self._data = _default_store()
            self._save_unlocked()

    def _save_unlocked(self) -> None:
        _store_path.write_text(json.dumps(self._data, indent=2, default=str), encoding="utf-8")

    def save(self) -> None:
        with _lock:
            self._save_unlocked()

    def get_user_by_email(self, email: str) -> dict | None:
        for u in self._data.get("users", []):
            if u["email"].lower() == email.lower():
                return u
        return None

    def get_user_by_id(self, user_id: str) -> dict | None:
        for u in self._data.get("users", []):
            if u["id"] == user_id:
                return u
        return None

    def authenticate(self, email: str, password: str) -> dict | None:
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user["hashed_password"]):
            return None
        return user

    def list_workspaces_for_user(self, user_id: str) -> list[dict]:
        ws_ids = {m["workspace_id"] for m in self._data.get("workspace_members", []) if m["user_id"] == user_id}
        return [w for w in self._data.get("workspaces", []) if w["id"] in ws_ids]

    def get_workspace(self, workspace_id: str) -> dict | None:
        for w in self._data.get("workspaces", []):
            if w["id"] == workspace_id:
                return w
        return None

    def list_documents(self, workspace_id: str) -> list[dict]:
        return [d for d in self._data.get("documents", []) if d["workspace_id"] == workspace_id]

    def get_document(self, workspace_id: str, document_id: str) -> dict | None:
        for d in self._data.get("documents", []):
            if d["id"] == document_id and d["workspace_id"] == workspace_id:
                return d
        return None

    def add_document(self, workspace_id: str, file_name: str, uploaded_by: str) -> dict:
        doc_id = str(uuid.uuid4())
        ext = file_name.rsplit(".", 1)[-1].upper() if "." in file_name else "FILE"
        doc = {
            "id": doc_id,
            "workspace_id": workspace_id,
            "title": file_name.rsplit(".", 1)[0],
            "file_name": file_name,
            "file_type": ext,
            "size_bytes": 0,
            "status": "PENDING",
            "progress": 0,
            "uploaded_by": uploaded_by,
            "uploaded_at": _now(),
            "versions": [{"version": 1, "created_at": _now(), "author": uploaded_by, "summary": "Initial upload"}],
        }
        with _lock:
            self._data.setdefault("documents", []).append(doc)
            self._save_unlocked()
        return doc

    def create_ingestion_job(self, job_id: str, document_id: str, workspace_id: str, document_name: str) -> dict:
        job = {
            "id": job_id,
            "document_id": document_id,
            "workspace_id": workspace_id,
            "document_name": document_name,
            "status": "PENDING",
            "progress": 0,
            "error_message": None,
            "created_at": _now(),
        }
        with _lock:
            self._data.setdefault("ingestion_jobs", []).append(job)
            self._save_unlocked()
        return job

    def update_ingestion_job(self, job_id: str, status: str, progress: int, error_message: str | None = None) -> dict | None:
        with _lock:
            for job in self._data.get("ingestion_jobs", []):
                if job["id"] == job_id:
                    job["status"] = status
                    job["progress"] = progress
                    if error_message:
                        job["error_message"] = error_message
                    for doc in self._data.get("documents", []):
                        if doc["id"] == job["document_id"]:
                            doc["status"] = status
                            doc["progress"] = progress
                    self._save_unlocked()
                    return job
        return None

    def get_ingestion_job(self, job_id: str) -> dict | None:
        for job in self._data.get("ingestion_jobs", []):
            if job["id"] == job_id:
                return job
        return None

    def list_ingestion_jobs(self, workspace_id: str | None = None) -> list[dict]:
        jobs = self._data.get("ingestion_jobs", [])
        if workspace_id:
            jobs = [j for j in jobs if j["workspace_id"] == workspace_id]
        return sorted(jobs, key=lambda j: j.get("created_at", ""), reverse=True)

    def add_activity(self, workspace_id: str, action: str, message: str, user: str) -> dict:
        entry = {
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "action": action,
            "message": message,
            "user": user,
            "timestamp": _now(),
        }
        with _lock:
            self._data.setdefault("activity", []).insert(0, entry)
            self._data["activity"] = self._data["activity"][:100]
            self._save_unlocked()
        return entry

    def list_activity(self, workspace_id: str, limit: int = 50) -> list[dict]:
        items = [a for a in self._data.get("activity", []) if a["workspace_id"] == workspace_id]
        return items[:limit]

    def get_metrics(self) -> dict:
        m = dict(self._data.get("metrics", {}))
        m["active_jobs"] = len([j for j in self._data.get("ingestion_jobs", []) if j["status"] not in ("COMPLETED", "FAILED")])
        m["completed_jobs"] = len([j for j in self._data.get("ingestion_jobs", []) if j["status"] == "COMPLETED"])
        m["failed_jobs"] = len([j for j in self._data.get("ingestion_jobs", []) if j["status"] == "FAILED"])
        m["documents_in_workspace"] = len(self._data.get("documents", []))
        return m

    def get_dashboard_activity_chart(self) -> list[dict]:
        return [
            {"time": "00:00", "docs": 2, "research": 5},
            {"time": "04:00", "docs": 1, "research": 3},
            {"time": "08:00", "docs": 8, "research": 14},
            {"time": "12:00", "docs": 15, "research": 28},
            {"time": "16:00", "docs": 12, "research": 22},
            {"time": "20:00", "docs": 6, "research": 11},
            {"time": "23:59", "docs": 4, "research": 8},
        ]

    def create_research_job(self, workspace_id: str, query: str, user: str) -> dict:
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "workspace_id": workspace_id,
            "query": query,
            "status": "INITIALIZING",
            "progress": 0,
            "created_by": user,
            "created_at": _now(),
        }
        with _lock:
            self._data.setdefault("research_jobs", []).append(job)
            self._save_unlocked()
        return job

    def get_research_job(self, job_id: str) -> dict | None:
        for j in self._data.get("research_jobs", []):
            if j["id"] == job_id:
                return j
        return None

    def update_research_job(self, job_id: str, status: str, progress: int, result: str | None = None) -> dict | None:
        with _lock:
            for j in self._data.get("research_jobs", []):
                if j["id"] == job_id:
                    j["status"] = status
                    j["progress"] = progress
                    if result:
                        j["result"] = result
                    self._save_unlocked()
                    return j
        return None

    def list_research_projects(self, workspace_id: str) -> list[dict]:
        return [p for p in self._data.get("research_projects", []) if p["workspace_id"] == workspace_id]

    def add_notification(self, user_id: str, title: str, message: str, ntype: str = "info") -> dict:
        n = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": ntype,
            "title": title,
            "message": message,
            "read": False,
            "timestamp": _now(),
        }
        with _lock:
            self._data.setdefault("notifications", []).insert(0, n)
            self._save_unlocked()
        return n

    def list_notifications(self, user_id: str) -> list[dict]:
        return [n for n in self._data.get("notifications", []) if n["user_id"] == user_id]


demo_store = DemoStore()
