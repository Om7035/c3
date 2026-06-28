from __future__ import annotations
from rir.graph import ReasoningGraph, GraphEdge
from optimizer.passes.base import OptimizationPass


class VerificationFusionPass(OptimizationPass):
    """
    Fuses two consecutive VERI.VERIFY nodes that read from the same register
    into a single node. Equivalent to instruction fusion in a traditional compiler.
    """

    @property
    def name(self) -> str:
        return "VerificationFusion"

    def run(self, graph: ReasoningGraph) -> ReasoningGraph:
        if len(graph.nodes) < 2:
            return graph

        # Build an id->node lookup
        node_map = {n.id: n for n in graph.nodes}
        # Build successor map
        successors: dict[str, str] = {e.source: e.target for e in graph.edges}

        fused_ids: set[str] = set()

        for node in graph.nodes:
            if node.id in fused_ids:
                continue
            if node.opcode != "VERI.VERIFY":
                continue
            succ_id = successors.get(node.id)
            if not succ_id:
                continue
            succ = node_map.get(succ_id)
            if not succ or succ.opcode != "VERI.VERIFY":
                continue

            # Both read the same input register?
            node_input = node.operands.get("input_data")
            succ_input = succ.operands.get("input_data")
            if node_input != succ_input:
                continue

            # Fuse: keep `node`, redirect all edges from succ to node,
            # and mark succ as fused (to be removed).
            # Successor's successor should now point to node.
            succ_succ_id = successors.get(succ_id)
            if succ_succ_id:
                graph.edges = [
                    GraphEdge(source=node.id, target=succ_succ_id)
                    if e.source == succ_id and e.target == succ_succ_id
                    else e
                    for e in graph.edges
                ]
            fused_ids.add(succ_id)

        graph.nodes = [n for n in graph.nodes if n.id not in fused_ids]
        graph.edges = [e for e in graph.edges
                       if e.source not in fused_ids and e.target not in fused_ids]
        graph.registers = [r for r in graph.registers
                           if r not in {out for n in graph.nodes
                                        if n.id in fused_ids for out in n.outputs}]

        return graph
