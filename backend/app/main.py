import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.database import db_manager
from app.core.cache import cache_manager
from app.core.observability import configure_observability

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db_manager.init_db(settings.database_url)
    await cache_manager.init_cache(settings.redis_url)
    yield
    # Shutdown
    await db_manager.close_db()
    await cache_manager.close_cache()

def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Research-grade AI copilot for citation-grounded paper analysis.",
        lifespan=lifespan,
    )
    configure_observability(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return app

app = create_app()
