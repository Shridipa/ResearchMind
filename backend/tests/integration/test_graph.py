import pytest
from app.graphs.enterprise_graph import build_enterprise_graph, EnterpriseGraphState

@pytest.mark.asyncio
async def test_enterprise_graph_execution():
    graph = build_enterprise_graph()
    
    initial_state = {
        "input": "Analyze Q2 sales",
        "subtasks": [],
        "retrieved_docs": [],
        "evidence": "",
        "analysis": "",
        "recommendations": [],
        "final_report": "",
        "error": None,
        "retries": 0
    }
    
    # Run the graph
    # LangGraph returns a dictionary or async generator depending on invocation
    result = await graph.ainvoke(initial_state)
    
    assert "subtasks" in result
    assert "retrieved_docs" in result
    assert "evidence" in result
    assert "analysis" in result
    assert "recommendations" in result
    assert "final_report" in result
    assert "Executive Summary" in result["final_report"]
