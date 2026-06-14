from typing import Any, Dict
import logging
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ReasoningAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Reasoning",
            system_prompt="You are a Reasoning Agent. Analyze findings and draw conclusions."
        )

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Reasoning Agent running...")
        evidence = state.get("evidence", "")
        
        # Simulated analysis
        analysis = f"Analysis of evidence: {evidence}. Conclusion: Q2 performance is strong but vulnerable to external shocks."
        
        return {"analysis": analysis}
