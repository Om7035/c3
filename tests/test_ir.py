from rir.graph import ReasoningGraph, GraphNode, GraphEdge
from models.problem import ProblemType

def test_reasoning_graph_validation():
    node = GraphNode(id="n1", operator="Retrieve", inputs=[], outputs=["docs"], params={"q": "test"})
    edge = GraphEdge(source="n1", target="n2")
    graph = ReasoningGraph(
        problem_type=ProblemType.FACTUAL_LOOKUP.value,
        nodes=[node],
        edges=[edge]
    )
    assert len(graph.nodes) == 1
    assert graph.problem_type == "factual_lookup"
    # test JSON serialization
    json_data = graph.model_dump_json()
    assert "factual_lookup" in json_data
