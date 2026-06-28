from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from core.context import ExecutionContext


class OperatorResult(BaseModel):
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    confidence: float = 1.0


class Operator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the operator."""

    @abstractmethod
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        """Execute the operator with the given parameters and runtime context."""

    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        """Validate inputs before execution."""
        return True
