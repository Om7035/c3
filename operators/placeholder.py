from __future__ import annotations

from typing import Any

from core.context import ExecutionContext
from operators.interfaces import Operator, OperatorResult


class RetrieveOperator(Operator):
    @property
    def name(self) -> str:
        return "Retrieve"

    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context.add_trace(f"Executed {self.name}", inputs)
        return OperatorResult(data={"documents": ["doc1", "doc2"]}, success=True)


class VerifyOperator(Operator):
    @property
    def name(self) -> str:
        return "Verify"

    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context.add_trace(f"Executed {self.name}", inputs)
        return OperatorResult(data={"verified_documents": inputs.get("documents", [])}, success=True)
