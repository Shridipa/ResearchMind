import pytest
import json
from app.mcp.server.jsonrpc import mcp_server

@pytest.mark.asyncio
async def test_mcp_discover_tools():
    req = {
        "jsonrpc": "2.0",
        "method": "discover_tools",
        "id": 1
    }
    response_str = await mcp_server.handle_request(json.dumps(req), [])
    response = json.loads(response_str)
    
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "tools" in response["result"]

@pytest.mark.asyncio
async def test_mcp_call_tool_success():
    req = {
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {
            "tool_name": "calculator_tool",
            "kwargs": {"expression": "15"}
        },
        "id": 2
    }
    # Provide the necessary permission "calc:execute"
    response_str = await mcp_server.handle_request(json.dumps(req), ["calc:execute"])
    response = json.loads(response_str)
    
    assert response["jsonrpc"] == "2.0"
    assert "error" not in response
    assert response["result"]["result"] == "Result: 15.0"

@pytest.mark.asyncio
async def test_mcp_call_tool_permission_denied():
    req = {
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {
            "tool_name": "calculator_tool",
            "kwargs": {"expression": "15"}
        },
        "id": 3
    }
    # No permissions provided
    response_str = await mcp_server.handle_request(json.dumps(req), [])
    response = json.loads(response_str)
    
    assert "error" in response
    assert response["error"]["code"] == -32000
    assert "Insufficient permissions" in response["error"]["message"]
