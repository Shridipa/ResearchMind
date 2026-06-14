from app.tools.registry import tool_registry

@tool_registry.register(
    name="document_tool",
    description="Read or parse a document from the filesystem or object storage.",
    input_schema={"document_id": "string"},
    permissions=["doc:read"]
)
def document_tool(document_id: str) -> str:
    # Simulated document read
    return f"Content of document {document_id}: Detailed analysis of supply chain vulnerabilities."
