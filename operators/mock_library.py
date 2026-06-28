"""
Mock operator implementations — used when C3_BACKEND=mock (default).
These return deterministic stub data and are used for unit tests, CI,
and development without API keys.
"""
from __future__ import annotations
from typing import Any
from core.context import ExecutionContext
from operators.interfaces import Operator, OperatorResult


class RetrieveOperator(Operator):
    @property
    def name(self) -> str: return "KNOW.RETRIEVE"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        return OperatorResult(success=True, data={"documents": ["Mock Document 1", "Mock Document 2"], "answer": "Mock retrieved answer", "source": "mock"}, confidence=0.8)


class PythonOperator(Operator):
    @property
    def name(self) -> str: return "EXEC.PYTHON"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        return OperatorResult(success=True, data={"output": "Mock execution result based on: " + str(inputs), "code": "# mock"}, confidence=1.0)


class SummarizeOperator(Operator):
    @property
    def name(self) -> str: return "REAS.SUMMARIZE"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        return OperatorResult(success=True, data={"summary": "Mock summary of: " + str(inputs)[:80]}, confidence=0.8)


class VerifyOperator(Operator):
    @property
    def name(self) -> str: return "VERI.VERIFY"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        return OperatorResult(success=True, data={"verified": True, "confidence": 0.95, "reason": "Mock verification passed"}, confidence=0.95)


class MemoryOperator(Operator):
    @property
    def name(self) -> str: return "KNOW.MEMORY"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        return OperatorResult(success=True, data={"memory_stored": True, "context": str(inputs)[:80]}, confidence=0.9)


class InferOperator(Operator):
    @property
    def name(self) -> str: return "REAS.INFER"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        return OperatorResult(success=True, data={"response": "Mock LLM reasoning response for: " + str(inputs)[:80]}, confidence=0.75)


def get_operator_registry() -> dict[str, Operator]:
    """
    Returns the operator registry.
    Delegates to operators.library which checks C3_BACKEND.
    This function is kept for backwards compatibility.
    """
    from operators import library
    return library.get_operator_registry()
