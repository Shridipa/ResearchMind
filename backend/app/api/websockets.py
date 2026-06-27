"""
WebSocket endpoint — bridges Redis Pub/Sub to connected browser clients.
Each authenticated client subscribes to workspace-scoped channels and receives
real-time updates (ingestion progress, research completion, team notifications).
"""
import asyncio
import json
import logging
from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Tracks active WebSocket connections per workspace."""

    def __init__(self):
        # workspace_id → set of websocket connections
        self.active: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workspace_id: str):
        await websocket.accept()
        self.active.setdefault(workspace_id, set()).add(websocket)
        logger.info("WS connected: workspace=%s total=%d", workspace_id, len(self.active[workspace_id]))

    def disconnect(self, websocket: WebSocket, workspace_id: str):
        self.active.get(workspace_id, set()).discard(websocket)

    async def broadcast(self, workspace_id: str, message: Any):
        dead = set()
        for ws in self.active.get(workspace_id, set()):
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        self.active.get(workspace_id, set()).difference_update(dead)

    async def send_personal(self, websocket: WebSocket, message: Any):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning("WS send failed: %s", e)


manager = ConnectionManager()

CHANNELS = ["document_updates", "research_updates", "workspace_updates", "notifications"]


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    workspace_id: str,
    token: str = Query(default=None),
):
    """
    WebSocket connection for a workspace.
    Client sends: { "type": "ping" }
    Server pushes: domain event payloads from Redis Pub/Sub
    """
    # TODO: validate token via auth.dependencies.decode_token(token)
    await manager.connect(websocket, workspace_id)

    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(*CHANNELS)

    async def listen_redis():
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    # Filter events relevant to this workspace
                    if data.get("workspace_id") in (workspace_id, None, ""):
                        await manager.broadcast(workspace_id, data)
                except Exception as e:
                    logger.warning("WS redis decode error: %s", e)

    redis_listener = asyncio.create_task(listen_redis())

    try:
        while True:
            msg = await websocket.receive_text()
            try:
                cmd = json.loads(msg)
                if cmd.get("type") == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        logger.info("WS disconnected: workspace=%s", workspace_id)
    finally:
        redis_listener.cancel()
        manager.disconnect(websocket, workspace_id)
        await pubsub.unsubscribe(*CHANNELS)
        await redis_client.aclose()
