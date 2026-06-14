from app.tools.registry import tool_registry

@tool_registry.register(
    name="calculator_tool",
    description="Perform basic arithmetic.",
    input_schema={"expression": "string"},
    permissions=["calc:execute"]
)
def calculator_tool(expression: str) -> str:
    # Simulated calculator execution (WARNING: eval is unsafe in production. 
    # Use ast.literal_eval or specialized math parsers in a real enterprise app)
    try:
        # safe mock execution
        if "15" in expression:
            return "Result: 15.0"
        return "Result: 0.0"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"
