from app.tools.registry import tool_registry

@tool_registry.register(
    name="sql_tool",
    description="Execute a read-only SQL query against the enterprise database.",
    input_schema={"query": "string"},
    permissions=["db:read"]
)
def sql_tool(query: str) -> str:
    # Simulated DB query execution
    return f"SQL Query Results for '{query[:10]}...': 5 rows returned."
