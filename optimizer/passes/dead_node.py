from __future__ import annotations
from rir.graph import ReasoningGraph, GraphEdge
from optimizer.passes.base import OptimizationPass


class DeadNodeEliminationPass(OptimizationPass):
    """
    Removes any node whose output register is never consumed by a downstream node.
    Equivalent to dead-code elimination in a traditional compiler.
    """

    @property
    def name(self) -> str:
        return "DeadNodeElimination"

    def run(self, graph: ReasoningGraph) -> ReasoningGraph:
        if not graph.nodes:
            return graph

        # Collect all registers that are READ by any node
        registers_consumed: set[str] = set()
        for node in graph.nodes:
            for val in node.operands.values():
                if isinstance(val, str) and val.startswith("$"):
                    registers_consumed.add(val[1:])  # strip the "$"

        # Find nodes whose outputs are all unconsumed AND that are not the final node
        # (the final node's output is the program result — never "dead")
        final_node_ids = {e.source for e in graph.edges} ^ {n.id for n in graph.nodes}
        # final_node_ids = nodes that are not a source of any edge (i.e., sink nodes)
        sink_nodes = set(n.id for n in graph.nodes) - {e.source for e in graph.edges}

        dead_node_ids: set[str] = set()
        for node in graph.nodes:
            if node.id in sink_nodes:
                continue  # Never eliminate the final result node
            if all(reg not in registers_consumed for reg in node.outputs):
                dead_node_ids.add(node.id)

        if not dead_node_ids:
            return graph

        graph.nodes = [n for n in graph.nodes if n.id not in dead_node_ids]
        graph.edges = [e for e in graph.edges
                       if e.source not in dead_node_ids and e.target not in dead_node_ids]
        graph.registers = [r for r in graph.registers
                           if not any(r == out for nid in dead_node_ids
                                      for n in [next((x for x in graph.nodes if x.id == nid), None)]
                                      if n for out in n.outputs)]

        return graph
