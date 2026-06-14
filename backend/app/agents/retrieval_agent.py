from typing import Any, Dict
import logging
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RetrievalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Retrieval",
            system_prompt="You are a Retrieval Agent. Query the vector store to find relevant data."
        )

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Retrieval Agent running...")
        
        # Simulated vector store lookup
        retrieved_docs = [
            "Doc 1: Q2 Sales were up 15%.",
            "Doc 2: Key risks include supply chain delays."
        ]
        
        return {"retrieved_docs": retrieved_docs}
