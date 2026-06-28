from __future__ import annotations
from rir.graph import ReasoningGraph
from optimizer.passes.base import OptimizationPass
from optimizer.passes.dead_node import DeadNodeEliminationPass
from optimizer.passes.verify_fusion import VerificationFusionPass


class PassManager:
    """Applies a sequence of optimization passes over a ReasoningGraph (RIR)."""

    def __init__(self, passes: list[OptimizationPass] | None = None):
        if passes is None:
            # Default pass pipeline
            self._passes: list[OptimizationPass] = [
                VerificationFusionPass(),
                DeadNodeEliminationPass(),
            ]
        else:
            self._passes = passes

    def optimize(self, graph: ReasoningGraph) -> tuple[ReasoningGraph, list[str]]:
        """
        Run all passes in sequence.
        Returns the optimized graph and a diagnostic log of which passes fired.
        """
        diagnostics: list[str] = []
        before_nodes = len(graph.nodes)

        for pass_ in self._passes:
            graph = pass_.run(graph)
            after_nodes = len(graph.nodes)
            if after_nodes != before_nodes:
                diagnostics.append(
                    f"[{pass_.name}] {before_nodes} nodes -> {after_nodes} nodes"
                )
                before_nodes = after_nodes
            else:
                diagnostics.append(f"[{pass_.name}] no change")

        return graph, diagnostics


# Convenience alias used by existing code
GraphOptimizer = PassManager
