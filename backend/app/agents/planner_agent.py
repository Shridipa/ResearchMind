from typing import Any, Dict
import logging
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Planner",
            system_prompt="""You are a master Planner Agent.
Your job is to break down complex user requests into smaller, actionable subtasks.
Output a JSON list of subtasks."""
        )

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Planner Agent running...")
        user_input = state.get("input", "")
        
        prompt = f"Decompose this task: {user_input}"
        
        # We would normally invoke the LLM here to get the JSON array of subtasks
        # response = await self.llm.generate(self.system_prompt, prompt)
        # For Phase 3, we simulate the LLM's structured output based on the prompt's example:
        subtasks = [
            "Search for relevant data",
            "Research specific details",
            "Analyze findings",
            "Generate recommendations",
            "Write summary"
        ]
        
        return {"subtasks": subtasks}
