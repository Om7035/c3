from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from rir.graph import ReasoningGraph
from core.context import ExecutionContext

class Runtime(ABC):
    """Execution runtime that executes the reasoning graph deterministically."""
    
    @abstractmethod
    async def execute(self, graph: ReasoningGraph, context: ExecutionContext) -> dict[str, Any]:
        """Execute a reasoning graph deterministically and return the final state/answer."""
