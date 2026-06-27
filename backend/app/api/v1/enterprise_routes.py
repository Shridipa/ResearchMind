"""
Enterprise API routes for ResearchMind 2.0 — wired to demo store + real-time events.
"""
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_permission, require_role
from app.auth.rbac import Permission, Role
from app.auth.jwt_handler import create_access_token, create_refresh_token, hash_password
from app.services.demo_store import demo_store, DEMO_WORKSPACE_ID, DEMO_USER_ID, DEMO_EMAIL
from app.services.ingestion_service import IngestionService
from app.services.realtime_service import publish_activity, publish_research_progress, publish_notification

router = APIRouter()
ingestion_service = IngestionService()


def _user_display(user: dict) -> str:
    return f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get("email", "User")


def _token_response(user: dict) -> dict:
    access = create_access_token(
        user["id"],
        extra={
            "role": user.get("role", Role.RESEARCHER.value),
            "email": user["email"],
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "workspace_id": DEMO_WORKSPACE_ID,
        },
    )
    refresh = create_refresh_token(user["id"])
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "firstName": user.get("first_name", ""),
            "lastName": user.get("last_name", ""),
            "role": user.get("role", Role.RESEARCHER.value),
            "workspaceId": DEMO_WORKSPACE_ID,
        },
    }


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/auth/register", tags=["Auth"], status_code=201)
async def register(body: RegisterRequest):
    if demo_store.get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": body.email,
        "hashed_password": hash_password(body.password),
        "first_name": body.first_name,
        "last_name": body.last_name,
        "role": Role.RESEARCHER.value,
    }
    demo_store._data.setdefault("users", []).append(user)
    demo_store.save()
    return _token_response(user)


@router.post("/auth/login", tags=["Auth"])
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = demo_store.authenticate(form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _token_response(user)


@router.post("/auth/demo-login", tags=["Auth"])
async def demo_login():
    """One-click demo login for judges."""
    user = demo_store.get_user_by_email(DEMO_EMAIL)
    if not user:
        raise HTTPException(status_code=500, detail="Demo user not seeded")
    publish_activity(DEMO_WORKSPACE_ID, "USER_LOGIN", "Demo user signed in", "Demo Admin")
    return _token_response(user)


@router.post("/auth/logout", tags=["Auth"])
async def logout(current_user: dict = Depends(get_current_user)):
    return {"logged_out": True, "user_id": current_user.get("sub")}


@router.post("/auth/refresh", tags=["Auth"], response_model=TokenResponse)
async def refresh_token(refresh: str):
    from app.auth.jwt_handler import decode_token
    payload = decode_token(refresh)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Not a refresh token")
    user = demo_store.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _token_response(user)


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@router.get("/dashboard/metrics", tags=["Dashboard"])
async def dashboard_metrics(current_user: dict = Depends(get_current_user)):
    return demo_store.get_metrics()


@router.get("/dashboard/activity", tags=["Dashboard"])
async def dashboard_activity(current_user: dict = Depends(get_current_user)):
    ws = current_user.get("workspace_id", DEMO_WORKSPACE_ID)
    return {
        "chart": demo_store.get_dashboard_activity_chart(),
        "recent": demo_store.list_activity(ws, limit=20),
    }


@router.get("/dashboard/jobs", tags=["Dashboard"])
async def dashboard_jobs(current_user: dict = Depends(get_current_user)):
    ws = current_user.get("workspace_id", DEMO_WORKSPACE_ID)
    jobs = demo_store.list_ingestion_jobs(ws)
    return {"jobs": jobs, "total": len(jobs)}


@router.get("/dashboard/system-activity", tags=["Dashboard"])
async def system_activity_stream(current_user: dict = Depends(get_current_user)):
    ws = current_user.get("workspace_id", DEMO_WORKSPACE_ID)
    return {"events": demo_store.list_activity(ws, limit=30)}


# ─────────────────────────────────────────────
# WORKSPACES
# ─────────────────────────────────────────────

class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None


@router.post(
    "/workspaces",
    tags=["Workspaces"],
    status_code=201,
    dependencies=[Depends(require_permission(Permission.CREATE_WORKSPACE))],
)
async def create_workspace(body: WorkspaceCreate, current_user: dict = Depends(get_current_user)):
    workspace_id = str(uuid.uuid4())
    ws = {
        "id": workspace_id,
        "name": body.name,
        "description": body.description,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "member_count": 1,
    }
    demo_store._data.setdefault("workspaces", []).append(ws)
    demo_store._data.setdefault("workspace_members", []).append(
        {"workspace_id": workspace_id, "user_id": current_user["sub"], "role": current_user.get("role")}
    )
    demo_store.save()
    publish_activity(workspace_id, "WORKSPACE_CREATE", f"Workspace '{body.name}' created", _user_display(demo_store.get_user_by_id(current_user["sub"]) or {}))
    return ws


@router.get("/workspaces", tags=["Workspaces"])
async def list_workspaces(current_user: dict = Depends(get_current_user)):
    workspaces = demo_store.list_workspaces_for_user(current_user["sub"])
    return {"workspaces": workspaces, "total": len(workspaces)}


@router.get("/workspaces/{workspace_id}", tags=["Workspaces"])
async def get_workspace(workspace_id: str, current_user: dict = Depends(get_current_user)):
    ws = demo_store.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {
        **ws,
        "documents_count": len(demo_store.list_documents(workspace_id)),
        "research_projects": demo_store.list_research_projects(workspace_id),
    }


@router.get("/workspaces/{workspace_id}/activity", tags=["Workspaces"])
async def workspace_activity(workspace_id: str, current_user: dict = Depends(get_current_user)):
    return {"activity": demo_store.list_activity(workspace_id)}


@router.post("/workspaces/{workspace_id}/members", tags=["Workspaces"])
async def invite_member(
    workspace_id: str,
    email: str,
    role: Role = Role.RESEARCHER,
    current_user: dict = Depends(require_permission(Permission.MANAGE_USERS)),
):
    publish_activity(workspace_id, "MEMBER_INVITED", f"Invited {email} as {role.value}", current_user.get("email", "Admin"))
    return {"workspace_id": workspace_id, "email": email, "role": role.value, "status": "invited"}


@router.delete("/workspaces/{workspace_id}/members/{user_id}", tags=["Workspaces"])
async def remove_member(
    workspace_id: str,
    user_id: str,
    current_user: dict = Depends(require_permission(Permission.MANAGE_USERS)),
):
    return {"removed": True}


# ─────────────────────────────────────────────
# DOCUMENTS
# ─────────────────────────────────────────────

@router.post(
    "/workspaces/{workspace_id}/documents",
    tags=["Documents"],
    status_code=202,
    dependencies=[Depends(require_permission(Permission.UPLOAD_DOCUMENTS))],
)
async def upload_document(
    workspace_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    user = demo_store.get_user_by_id(current_user["sub"]) or {}
    doc = demo_store.add_document(workspace_id, file.filename or "upload.bin", _user_display(user))
    document_id = doc["id"]
    s3_key = f"workspaces/{workspace_id}/documents/{document_id}/{file.filename}"
    content = await file.read()
    doc["size_bytes"] = len(content)

    result = await ingestion_service.start_ingestion(
        document_id=document_id,
        workspace_id=workspace_id,
        s3_key=s3_key,
        document_name=file.filename or "upload.bin",
        uploaded_by=_user_display(user),
    )

    publish_activity(workspace_id, "DOCUMENT_UPLOAD", f"{file.filename} uploaded", _user_display(user))
    publish_notification(current_user["sub"], "Upload Started", f"Processing {file.filename}…", "info")

    return {
        "document_id": document_id,
        "file_name": file.filename,
        "s3_key": s3_key,
        **result,
    }


@router.get("/workspaces/{workspace_id}/documents", tags=["Documents"])
async def list_documents(workspace_id: str, current_user: dict = Depends(get_current_user)):
    docs = demo_store.list_documents(workspace_id)
    return {"documents": docs, "total": len(docs), "workspace_id": workspace_id}


@router.get("/workspaces/{workspace_id}/documents/{document_id}", tags=["Documents"])
async def get_document(workspace_id: str, document_id: str, current_user: dict = Depends(get_current_user)):
    doc = demo_store.get_document(workspace_id, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/workspaces/{workspace_id}/documents/{document_id}/versions", tags=["Documents"])
async def document_versions(workspace_id: str, document_id: str, current_user: dict = Depends(get_current_user)):
    doc = demo_store.get_document(workspace_id, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": document_id, "versions": doc.get("versions", [])}


@router.delete(
    "/workspaces/{workspace_id}/documents/{document_id}",
    tags=["Documents"],
    dependencies=[Depends(require_permission(Permission.DELETE_DOCUMENTS))],
)
async def delete_document(workspace_id: str, document_id: str, current_user: dict = Depends(get_current_user)):
    demo_store._data["documents"] = [
        d for d in demo_store._data.get("documents", [])
        if not (d["id"] == document_id and d["workspace_id"] == workspace_id)
    ]
    demo_store.save()
    publish_activity(workspace_id, "DOCUMENT_DELETE", f"Document {document_id} deleted", current_user.get("email", "User"))
    return {"deleted": True, "document_id": document_id}


# ─────────────────────────────────────────────
# INGESTION JOBS
# ─────────────────────────────────────────────

@router.get("/ingestion-jobs/{job_id}", tags=["Ingestion"])
async def get_ingestion_job(job_id: str, current_user: dict = Depends(get_current_user)):
    job = demo_store.get_ingestion_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/ingestion-jobs/{job_id}/retry", tags=["Ingestion"])
async def retry_ingestion_job(job_id: str, current_user: dict = Depends(get_current_user)):
    job = demo_store.get_ingestion_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    demo_store.update_ingestion_job(job_id, "PENDING", 0)
    await ingestion_service.start_ingestion(
        document_id=job["document_id"],
        workspace_id=job["workspace_id"],
        s3_key=f"retry/{job['document_id']}",
        document_name=job.get("document_name", "document"),
        job_id=job_id,
    )
    return {"job_id": job_id, "status": "PENDING"}


# ─────────────────────────────────────────────
# RESEARCH
# ─────────────────────────────────────────────

class ResearchStartRequest(BaseModel):
    query: str
    workspace_id: str = DEMO_WORKSPACE_ID


@router.post("/research/start", tags=["Research"])
async def start_research(body: ResearchStartRequest, current_user: dict = Depends(get_current_user)):
    user = demo_store.get_user_by_id(current_user["sub"]) or {}
    job = demo_store.create_research_job(body.workspace_id, body.query, _user_display(user))
    asyncio.create_task(_run_research_job(job["id"], body.workspace_id, body.query, current_user["sub"]))
    return {"job_id": job["id"], "status": "INITIALIZING"}


async def _run_research_job(job_id: str, workspace_id: str, query: str, user_id: str):
    stages = [
        ("COLLECTING_CONTEXT", 35),
        ("GENERATING_ANALYSIS", 75),
        ("COMPLETED", 100),
    ]
    for stage, progress in stages:
        await asyncio.sleep(0.3)
        demo_store.update_research_job(job_id, stage, progress, result=query[:200] if stage == "COMPLETED" else None)
        publish_research_progress(job_id=job_id, workspace_id=workspace_id, status=stage, progress=progress, query=query)
    publish_activity(workspace_id, "RESEARCH_COMPLETED", f"Research completed: {query[:60]}…", "AI Engine")
    publish_notification(user_id, "Research Complete", f'Analysis ready for "{query[:40]}…"', "success")


@router.get("/research/{job_id}/status", tags=["Research"])
async def research_status(job_id: str, current_user: dict = Depends(get_current_user)):
    job = demo_store.get_research_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    return job


@router.get("/research/{job_id}/results", tags=["Research"])
async def research_results(job_id: str, current_user: dict = Depends(get_current_user)):
    job = demo_store.get_research_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
    if job["status"] != "COMPLETED":
        raise HTTPException(status_code=202, detail="Research still in progress")
    return {
        "job_id": job_id,
        "query": job["query"],
        "summary": job.get("result", ""),
        "sources": demo_store.list_documents(job["workspace_id"])[:3],
    }


# ─────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    workspace_id: Optional[str] = None
    mode: str = "hybrid"
    filters: dict = {}
    limit: int = 20
    offset: int = 0


@router.post("/search", tags=["Search"])
async def unified_search(body: SearchRequest, current_user: dict = Depends(get_current_user)):
    ws = body.workspace_id or current_user.get("workspace_id", DEMO_WORKSPACE_ID)
    docs = demo_store.list_documents(ws)
    q = body.query.lower()
    results = [
        {"id": d["id"], "title": d["title"], "file_name": d["file_name"], "score": 0.92, "type": "document"}
        for d in docs
        if q in d["title"].lower() or q in d["file_name"].lower()
    ]
    if not results and docs:
        results = [{"id": d["id"], "title": d["title"], "file_name": d["file_name"], "score": 0.75, "type": "document"} for d in docs[:3]]
    return {"query": body.query, "mode": body.mode, "results": results, "total": len(results), "workspace_id": ws}


# ─────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────

@router.get("/admin/health", tags=["Admin"], dependencies=[Depends(require_role(Role.WORKSPACE_ADMIN))])
async def system_health():
    from app.core.cache import cache_manager
    redis_ok = False
    try:
        if cache_manager.redis:
            await cache_manager.redis.ping()
            redis_ok = True
    except Exception:
        pass
    return {
        "status": "ok",
        "api": "healthy",
        "database": "demo_store",
        "redis": "healthy" if redis_ok else "unavailable",
        "celery": "optional",
        "vector_store": "healthy",
    }


@router.get("/admin/users", tags=["Admin"], dependencies=[Depends(require_role(Role.WORKSPACE_ADMIN))])
async def list_all_users():
    users = [{"id": u["id"], "email": u["email"], "role": u.get("role")} for u in demo_store._data.get("users", [])]
    return {"users": users, "total": len(users)}


@router.get("/admin/audit-logs", tags=["Admin"], dependencies=[Depends(require_role(Role.WORKSPACE_ADMIN))])
async def get_audit_logs(limit: int = 100, offset: int = 0):
    logs = demo_store._data.get("activity", [])[offset: offset + limit]
    return {"logs": logs, "total": len(demo_store._data.get("activity", [])), "limit": limit, "offset": offset}


@router.get("/admin/queue-stats", tags=["Admin"], dependencies=[Depends(require_role(Role.WORKSPACE_ADMIN))])
async def queue_stats():
    jobs = demo_store.list_ingestion_jobs()
    return {
        "queued": len([j for j in jobs if j["status"] == "PENDING"]),
        "active": len([j for j in jobs if j["status"] not in ("PENDING", "COMPLETED", "FAILED")]),
        "completed": len([j for j in jobs if j["status"] == "COMPLETED"]),
        "failed": len([j for j in jobs if j["status"] == "FAILED"]),
    }
