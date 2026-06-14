from typing import Any, Dict
import logging
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research",
            system_prompt="You are a Research Agent. Gather evidence and collect information based on retrieved documents."
        )

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Research Agent running...")
        docs = state.get("retrieved_docs", [])
        
        # Simulated research synthesis
        evidence = f"Gathered evidence from {len(docs)} sources indicating growth but highlighting supply chain risks."
        
        return {"evidence": evidence}
