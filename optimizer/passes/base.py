from __future__ import annotations
from abc import ABC, abstractmethod
from rir.graph import ReasoningGraph


class OptimizationPass(ABC):
    """Abstract base for all RIR optimization passes."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def run(self, graph: ReasoningGraph) -> ReasoningGraph:
        """Apply this pass to the graph and return the (possibly modified) graph."""
        ...
