import contextlib
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.api.websockets import router as ws_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.database import db_manager
from app.core.cache import cache_manager
from app.core.observability import configure_observability
from app.events.event_bus import EventBus, set_event_bus

logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────
    logger.info("Starting ResearchMind 2.0...")
    from app.services.demo_store import demo_store
    demo_store.load()
    db_manager.init_db(settings.database_url)
    await cache_manager.init_cache(settings.redis_url)

    # Initialize Event Bus (graceful fallback when Redis is unavailable)
    bus = EventBus(settings.redis_url)
    try:
        await bus.connect()
        set_event_bus(bus)
        logger.info("EventBus initialized")
    except Exception as exc:
        logger.warning("EventBus unavailable — real-time features disabled: %s", exc)
        set_event_bus(None)

    yield

    # ── Shutdown ─────────────────────────────────────────
    logger.info("Shutting down ResearchMind 2.0...")
    from app.events.event_bus import event_bus
    if event_bus is not None:
        await event_bus.disconnect()
    await db_manager.close_db()
    await cache_manager.close_cache()


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="ResearchMind 2.0 Enterprise",
        version="2.0.0",
        description=(
            "Enterprise AI Research Operating System — "
            "multi-tenant workspaces, distributed ingestion, event-driven architecture, "
            "RBAC security, and real-time collaboration."
        ),
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    configure_observability(app)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # REST routes
    app.include_router(api_router, prefix="/api/v1")

    # WebSocket routes
    app.include_router(ws_router)

    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    @app.get("/health", tags=["System"])
    def health() -> dict:
        return {
            "status": "ok",
            "service": "ResearchMind 2.0 Enterprise",
            "version": "2.0.0",
        }

    return app


app = create_app()

