from __future__ import annotations

import networkx as nx
from typing import Any

from rir.graph import ReasoningGraph
from core.context import ExecutionContext
from operators.interfaces import Operator


class GraphExecutor:
    def __init__(self, registry: dict[str, Operator]):
        self.registry = registry

    async def execute(self, graph: ReasoningGraph, context: ExecutionContext) -> dict[str, Any]:
        context.add_trace("Graph execution started", {"graph_id": graph.graph_id})

        dag = nx.DiGraph()
        for node in graph.nodes:
            dag.add_node(node.id, data=node)

        for edge in graph.edges:
            dag.add_edge(edge.source, edge.target)

        if not nx.is_directed_acyclic_graph(dag):
            raise ValueError("Graph is not a DAG")

        order = list(nx.topological_sort(dag))
        results: dict[str, Any] = {}

        for node_id in order:
            node = dag.nodes[node_id]["data"]
            operator = self.registry.get(node.operator)
            if not operator:
                raise ValueError(f"Operator {node.operator} not found")

            # Simple input aggregation: merge results from dependencies
            inputs = dict(node.params)
            for pred in dag.predecessors(node_id):
                if pred in results:
                    inputs.update(results[pred])

            result = await operator.execute(inputs, context)
            if not result.success:
                raise RuntimeError(f"Operator {node_id} failed: {result.error}")

            results[node_id] = result.data

        context.add_trace("Graph execution finished")
        return results
