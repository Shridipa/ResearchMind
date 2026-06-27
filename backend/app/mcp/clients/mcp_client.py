import logging
import httpx
from typing import Any, Dict

logger = logging.getLogger(__name__)

class MCPClient:
    """Async Client for connecting to external MCP Servers."""

    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self._id_counter = 0

    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        self._id_counter += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._id_counter
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.endpoint_url, json=payload, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"MCP Client HTTP Error: {e}")
                raise

    async def discover_tools(self) -> list[Dict[str, Any]]:
        """Query the remote server for available tools."""
        res = await self._send_request("discover_tools")
        if "error" in res:
            raise RuntimeError(res["error"])
        return res.get("result", {}).get("tools", [])

    async def call_tool(self, tool_name: str, kwargs: Dict[str, Any]) -> Any:
        """Execute a tool on the remote MCP server."""
        res = await self._send_request("call_tool", {"tool_name": tool_name, "kwargs": kwargs})
        if "error" in res:
            raise RuntimeError(res["error"])
        return res.get("result", {}).get("result")
