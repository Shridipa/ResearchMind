"""
Redis-backed Event Bus.
Publishers push events to Redis channels.
Subscribers (workers/WebSocket handlers) listen to channels.
"""
import json
import logging
from typing import Callable, Any

import redis.asyncio as aioredis

from app.events.domain_events import DomainEvent

logger = logging.getLogger(__name__)

# Redis channel names
CHANNEL_DOCUMENT_UPDATES = "document_updates"
CHANNEL_RESEARCH_UPDATES = "research_updates"
CHANNEL_WORKSPACE_UPDATES = "workspace_updates"
CHANNEL_NOTIFICATIONS = "notifications"

# Map event class names to channels
EVENT_CHANNEL_MAP = {
    "DocumentUploadedEvent": CHANNEL_DOCUMENT_UPDATES,
    "DocumentProcessedEvent": CHANNEL_DOCUMENT_UPDATES,
    "EmbeddingCreatedEvent": CHANNEL_DOCUMENT_UPDATES,
    "IngestionProgressEvent": CHANNEL_DOCUMENT_UPDATES,
    "WorkspaceCreatedEvent": CHANNEL_WORKSPACE_UPDATES,
    "ResearchGeneratedEvent": CHANNEL_RESEARCH_UPDATES,
}


class EventBus:
    """
    Simple async event bus backed by Redis Pub/Sub.
    Usage:
        bus = EventBus(redis_url)
        await bus.connect()
        await bus.publish(DocumentUploadedEvent(...))
    """

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis: aioredis.Redis | None = None
        self._handlers: dict[str, list[Callable]] = {}

    async def connect(self):
        self._redis = aioredis.from_url(self._redis_url, decode_responses=True)
        await self._redis.ping()
        logger.info("EventBus connected to Redis")

    async def disconnect(self):
        if self._redis:
            await self._redis.aclose()

    async def publish(self, event: DomainEvent) -> int:
        if not self._redis:
            raise RuntimeError("EventBus not connected — call connect() first")
        channel = EVENT_CHANNEL_MAP.get(event.__class__.__name__, CHANNEL_NOTIFICATIONS)
        payload = event.to_json()
        receivers = await self._redis.publish(channel, payload)
        logger.debug("Published %s to %s (%d receivers)", event.__class__.__name__, channel, receivers)
        return receivers

    async def publish_raw(self, channel: str, data: dict) -> int:
        if not self._redis:
            raise RuntimeError("EventBus not connected")
        return await self._redis.publish(channel, json.dumps(data))

    def subscribe(self, event_name: str):
        """Decorator to register a handler for a given event class name."""
        def decorator(fn: Callable):
            self._handlers.setdefault(event_name, []).append(fn)
            return fn
        return decorator

    async def listen(self, channel: str, handler: Callable[[dict], Any]):
        """Start an async listener on a Redis Pub/Sub channel."""
        if not self._redis:
            raise RuntimeError("EventBus not connected")
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        logger.info("Listening on channel: %s", channel)
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    await handler(data)
                except Exception as exc:
                    logger.exception("Error in handler for channel %s: %s", channel, exc)


# Singleton — initialized in main.py lifespan
event_bus: EventBus | None = None


def set_event_bus(bus: EventBus | None) -> None:
    global event_bus
    event_bus = bus


def get_event_bus() -> EventBus:
    if event_bus is None:
        raise RuntimeError("EventBus not initialized")
    return event_bus
