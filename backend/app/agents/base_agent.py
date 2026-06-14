from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from app.llm.provider_factory import get_llm_provider

class BaseAgent:
    """Base class for all autonomous agents in the ecosystem."""
    
    def __init__(self, name: str, system_prompt: str, tools: Optional[List[Any]] = None):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.llm = get_llm_provider()

    async def _execute_tools(self, tool_calls: List[dict]) -> List[dict]:
        # Tool execution logic will be expanded in Phase 5 (Tool Calling)
        results = []
        for call in tool_calls:
            results.append({"tool": call["name"], "result": "mock_result"})
        return results

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent logic based on the shared state.
        Must be overridden by specific agents.
        """
        raise NotImplementedError("Subclasses must implement run()")
