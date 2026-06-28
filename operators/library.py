from __future__ import annotations

from typing import Any
from core.context import ExecutionContext
from operators.interfaces import Operator, OperatorResult

class RetrieveOperator(Operator):
    @property
    def name(self) -> str: return "Retrieve"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context.add_trace("Retrieve executed")
        return OperatorResult(success=True, data={"documents": ["Mock Document 1", "Mock Document 2"]})

class PythonOperator(Operator):
    @property
    def name(self) -> str: return "Python"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context.add_trace("Python executed")
        return OperatorResult(success=True, data={"output": "Mock execution result"})

class SummarizeOperator(Operator):
    @property
    def name(self) -> str: return "Summarize"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context.add_trace("Summarize executed")
        return OperatorResult(success=True, data={"summary": "Mock summary"})

class VerifyOperator(Operator):
    @property
    def name(self) -> str: return "Verify"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context.add_trace("Verify executed")
        return OperatorResult(success=True, data={"verified": True, "confidence": 0.95})

class MemoryOperator(Operator):
    @property
    def name(self) -> str: return "Memory"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context.add_trace("Memory executed")
        return OperatorResult(success=True, data={"memory_stored": True})

class LLMOperator(Operator):
    @property
    def name(self) -> str: return "LLM"
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context.add_trace("LLM executed")
        return OperatorResult(success=True, data={"response": "Mock LLM reasoning response"})

def get_operator_registry() -> dict[str, Operator]:
    return {
        "Retrieve": RetrieveOperator(),
        "Python": PythonOperator(),
        "Summarize": SummarizeOperator(),
        "Verify": VerifyOperator(),
        "Memory": MemoryOperator(),
        "LLM": LLMOperator(),
    }
