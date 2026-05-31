from fastapi import APIRouter

from app.api.v1.routes import benchmarks, chat, compare, flashcards, papers, literature

api_router = APIRouter()
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(benchmarks.router, prefix="/benchmarks", tags=["benchmarks"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["flashcards"])
api_router.include_router(compare.router, prefix="/compare", tags=["compare"])
api_router.include_router(literature.router, prefix="/literature-review", tags=["literature"])
