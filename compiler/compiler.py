from __future__ import annotations
import uuid
from planner.planner import ReasoningPlan
from rir.graph import ReasoningGraph, GraphNode, GraphEdge

class Compiler:
    def compile(self, plan: ReasoningPlan) -> ReasoningGraph:
        graph = ReasoningGraph()
        graph.metadata["query"] = plan.query
        
        prev_node = None
        for op in plan.operators:
            node_id = f"{op.lower()}_{uuid.uuid4().hex[:6]}"
            node = GraphNode(id=node_id, operator=op, params={"query": plan.query})
            graph.nodes.append(node)
            
            if prev_node:
                graph.edges.append(GraphEdge(source=prev_node.id, target=node.id))
            
            prev_node = node
            
        return graph
