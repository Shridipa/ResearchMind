import pytest
from app.tools.registry import tool_registry
import app.tools.search_tool
import app.tools.calculator_tool

def test_tool_registration():
    schemas = tool_registry.get_tool_schemas()
    names = [s["name"] for s in schemas]
    assert "search_tool" in names
    assert "calculator_tool" in names

def test_tool_execution_success():
    result = tool_registry.execute(
        "calculator_tool", 
        {"expression": "15"}, 
        ["calc:execute"]
    )
    assert result == "Result: 15.0"

def test_tool_execution_permission_denied():
    with pytest.raises(PermissionError):
        tool_registry.execute(
            "calculator_tool", 
            {"expression": "15"}, 
            ["search:read"]
        )

def test_tool_execution_validation_failed():
    with pytest.raises(ValueError):
        tool_registry.execute(
            "calculator_tool", 
            {"wrong_param": "15"}, 
            ["calc:execute"]
        )
