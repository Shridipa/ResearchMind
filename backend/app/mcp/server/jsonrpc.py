import json
from typing import Any, Dict
import logging
from app.tools.registry import tool_registry

logger = logging.getLogger(__name__)

class MCPServer:
    """Model Context Protocol (MCP) JSON-RPC 2.0 Server."""

    def __init__(self):
        self.registry = tool_registry

    async def handle_request(self, request_payload: str, user_permissions: list[str]) -> str:
        """Handle an incoming JSON-RPC request and route to tools."""
        try:
            req = json.loads(request_payload)
            if req.get("jsonrpc") != "2.0":
                return self._error(req.get("id"), -32600, "Invalid Request")

            method = req.get("method")
            params = req.get("params", {})
            req_id = req.get("id")

            if method == "discover_tools":
                tools = self.registry.get_tool_schemas()
                return self._success(req_id, {"tools": tools})

            if method == "call_tool":
                tool_name = params.get("tool_name")
                tool_kwargs = params.get("kwargs", {})
                try:
                    result = self.registry.execute(tool_name, tool_kwargs, user_permissions)
                    return self._success(req_id, {"result": result})
                except Exception as e:
                    return self._error(req_id, -32000, str(e))
            
            return self._error(req_id, -32601, "Method not found")

        except json.JSONDecodeError:
            return self._error(None, -32700, "Parse error")
        except Exception as e:
            return self._error(None, -32603, f"Internal error: {str(e)}")

    def _success(self, req_id: Any, result: Any) -> str:
        return json.dumps({
            "jsonrpc": "2.0",
            "result": result,
            "id": req_id
        })

    def _error(self, req_id: Any, code: int, message: str) -> str:
        return json.dumps({
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": req_id
        })

mcp_server = MCPServer()
