import logging
from typing import TypedDict

from langgraph.graph import StateGraph, END
from app.agents.planner_agent import PlannerAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.research_agent import ResearchAgent
from app.agents.reasoning_agent import ReasoningAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.summarizer_agent import SummarizerAgent

logger = logging.getLogger(__name__)

# 1. Define Graph State Model
class EnterpriseGraphState(TypedDict):
    input: str
    subtasks: list[str]
    retrieved_docs: list[str]
    evidence: str
    analysis: str
    recommendations: list[str]
    final_report: str
    error: str | None
    retries: int

# 2. Node Functions
async def planner_node(state: EnterpriseGraphState):
    agent = PlannerAgent()
    try:
        result = await agent.run(state)
        return {"subtasks": result.get("subtasks", []), "error": None}
    except Exception as e:
        return {"error": f"Planner failed: {str(e)}"}

async def retrieval_node(state: EnterpriseGraphState):
    agent = RetrievalAgent()
    result = await agent.run(state)
    return {"retrieved_docs": result.get("retrieved_docs", [])}

async def research_node(state: EnterpriseGraphState):
    agent = ResearchAgent()
    result = await agent.run(state)
    return {"evidence": result.get("evidence", "")}

async def reasoning_node(state: EnterpriseGraphState):
    agent = ReasoningAgent()
    result = await agent.run(state)
    return {"analysis": result.get("analysis", "")}

async def decision_node(state: EnterpriseGraphState):
    agent = DecisionAgent()
    result = await agent.run(state)
    return {"recommendations": result.get("recommendations", [])}

async def summarizer_node(state: EnterpriseGraphState):
    agent = SummarizerAgent()
    result = await agent.run(state)
    return {"final_report": result.get("final_report", "")}

# 3. Conditional Routing
def route_after_planner(state: EnterpriseGraphState) -> str:
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "retry"
        return "end"
    return "continue"

# 4. Build Graph
def build_enterprise_graph() -> StateGraph:
    workflow = StateGraph(EnterpriseGraphState)
    
    workflow.add_node("planner", planner_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("research", research_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("summarizer", summarizer_node)
    
    # Define edges
    workflow.set_entry_point("planner")
    
    workflow.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "continue": "retrieval",
            "retry": "planner",
            "end": END
        }
    )
    
    workflow.add_edge("retrieval", "research")
    workflow.add_edge("research", "reasoning")
    workflow.add_edge("reasoning", "decision")
    workflow.add_edge("decision", "summarizer")
    workflow.add_edge("summarizer", END)
    
    return workflow.compile()

enterprise_graph = build_enterprise_graph()
