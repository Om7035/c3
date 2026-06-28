from __future__ import annotations

from abc import ABC, abstractmethod

from ir.graph import ReasoningGraph
from models.problem import ProblemSpec

class Compiler(ABC):
    @abstractmethod
    async def compile(self, problem: ProblemSpec) -> ReasoningGraph:
        """Compile a problem specification into a reasoning graph."""
