from app.tools.registry import tool_registry

@tool_registry.register(
    name="search_tool",
    description="Search the web or internal database for a query.",
    input_schema={"query": "string"},
    permissions=["search:read"]
)
def search_tool(query: str) -> str:
    # Simulated search execution
    return f"Search results for '{query}': Revenue grew 15% in Q2."
