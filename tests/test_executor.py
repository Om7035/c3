import pytest
from rir.graph import ReasoningGraph, GraphNode, GraphEdge
from core.context import ExecutionContext
from operators.placeholder import RetrieveOperator, VerifyOperator
from runtime.executor import GraphExecutor

@pytest.mark.asyncio
async def test_graph_executor_success():
    n1 = GraphNode(id="n1", operator="Retrieve")
    n2 = GraphNode(id="n2", operator="Verify")
    e1 = GraphEdge(source="n1", target="n2")
    graph = ReasoningGraph(nodes=[n1, n2], edges=[e1])
    
    registry = {
        "Retrieve": RetrieveOperator(),
        "Verify": VerifyOperator()
    }
    executor = GraphExecutor(registry)
    context = ExecutionContext(query="test query")
    
    results = await executor.execute(graph, context)
    
    assert "n1" in results
    assert "n2" in results
    assert results["n1"]["documents"] == ["doc1", "doc2"]
    assert results["n2"]["verified_documents"] == ["doc1", "doc2"]
    assert len(context.trace_logs) > 0
