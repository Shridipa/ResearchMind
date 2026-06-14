from app.tools.registry import tool_registry

@tool_registry.register(
    name="api_tool",
    description="Make an HTTP request to an external API.",
    input_schema={"method": "string", "url": "string"},
    permissions=["api:call"]
)
def api_tool(method: str, url: str) -> str:
    # Simulated API call
    return f"API Response from {method} {url}: Status 200 OK"
