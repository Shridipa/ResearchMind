from typing import Any, Callable, Dict, List
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Enterprise-grade Tool Registry with auditing and permissions."""
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._audit_log: List[Dict[str, Any]] = []

    def register(self, name: str, description: str, input_schema: Dict, permissions: List[str]):
        """Decorator for dynamic tool registration."""
        def decorator(func: Callable):
            self._tools[name] = {
                "name": name,
                "description": description,
                "input_schema": input_schema,
                "permissions": permissions,
                "func": func
            }
            logger.info(f"Registered tool: {name}")
            return func
        return decorator

    def execute(self, tool_name: str, kwargs: Dict[str, Any], user_permissions: List[str]) -> Any:
        """Execute a tool with validation, permission checks, and audit logging."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool {tool_name} not found in registry.")
            
        tool = self._tools[tool_name]
        
        # 1. Permission Check
        required_perms = set(tool["permissions"])
        provided_perms = set(user_permissions)
        if not required_perms.issubset(provided_perms):
            self._log_audit(tool_name, kwargs, "PERMISSION_DENIED")
            raise PermissionError(f"Insufficient permissions. Required: {required_perms}")
            
        # 2. Validation (Simple simulated schema validation for Phase 5)
        # Real implementation would use Pydantic or jsonschema
        for key in tool["input_schema"]:
            if key not in kwargs:
                self._log_audit(tool_name, kwargs, "VALIDATION_FAILED")
                raise ValueError(f"Missing required parameter: {key}")
                
        # 3. Execution
        try:
            result = tool["func"](**kwargs)
            self._log_audit(tool_name, kwargs, "SUCCESS")
            return result
        except Exception as e:
            self._log_audit(tool_name, kwargs, f"ERROR: {str(e)}")
            raise

    def _log_audit(self, tool_name: str, kwargs: Dict, status: str):
        """Internal audit log."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "inputs": kwargs,
            "status": status
        }
        self._audit_log.append(log_entry)
        logger.info(f"AUDIT: {json.dumps(log_entry)}")

    def get_tool_schemas(self) -> List[Dict]:
        """Return metadata for LLM tool binding."""
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["input_schema"],
                "permissions": t["permissions"]
            }
            for t in self._tools.values()
        ]

tool_registry = ToolRegistry()
