from typing import Any, Dict
import logging
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Summarizer",
            system_prompt="You are a Summarizer Agent. Generate a final executive summary combining analysis and recommendations."
        )

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Summarizer Agent running...")
        analysis = state.get("analysis", "")
        recommendations = state.get("recommendations", [])
        
        # Simulated final summary
        summary = f"Executive Summary:\n\n{analysis}\n\nStrategic Actions:\n"
        for rec in recommendations:
            summary += f"- {rec}\n"
            
        return {"final_report": summary}
