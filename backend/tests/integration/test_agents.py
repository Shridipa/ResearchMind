import pytest
from app.agents.planner_agent import PlannerAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.research_agent import ResearchAgent
from app.agents.reasoning_agent import ReasoningAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.summarizer_agent import SummarizerAgent

@pytest.mark.asyncio
async def test_planner_agent():
    agent = PlannerAgent()
    state = {"input": "Analyze Q2 sales"}
    new_state = await agent.run(state)
    assert "subtasks" in new_state
    assert len(new_state["subtasks"]) > 0

@pytest.mark.asyncio
async def test_agent_pipeline():
    # Simulate the pipeline sequentially passing state
    state = {"input": "Analyze Q2 sales"}
    
    planner = PlannerAgent()
    state.update(await planner.run(state))
    
    retrieval = RetrievalAgent()
    state.update(await retrieval.run(state))
    
    research = ResearchAgent()
    state.update(await research.run(state))
    
    reasoning = ReasoningAgent()
    state.update(await reasoning.run(state))
    
    decision = DecisionAgent()
    state.update(await decision.run(state))
    
    summarizer = SummarizerAgent()
    state.update(await summarizer.run(state))
    
    assert "retrieved_docs" in state
    assert "evidence" in state
    assert "analysis" in state
    assert "recommendations" in state
    assert "final_report" in state
    assert "Executive Summary:" in state["final_report"]
