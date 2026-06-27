import logging

from fastapi import APIRouter

from app.api.v1.enterprise_routes import router as enterprise_router

logger = logging.getLogger(__name__)
api_router = APIRouter()

# ── Existing RAG routes (optional — require ML stack) ─────
try:
    from app.api.v1.routes import benchmarks, chat, compare, flashcards, papers, literature

    api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
    api_router.include_router(benchmarks.router, prefix="/benchmarks", tags=["benchmarks"])
    api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
    api_router.include_router(flashcards.router, prefix="/flashcards", tags=["flashcards"])
    api_router.include_router(compare.router, prefix="/compare", tags=["compare"])
    api_router.include_router(literature.router, prefix="/literature-review", tags=["literature"])
except ImportError as exc:
    logger.warning("Legacy RAG routes disabled (ML dependencies unavailable): %s", exc)

# ── Enterprise 2.0 routes ─────────────────────────────────
api_router.include_router(enterprise_router, tags=["Enterprise"])
