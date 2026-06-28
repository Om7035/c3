from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    query: str
    shared_memory: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    trace_logs: list[dict[str, Any]] = Field(default_factory=list)

    def add_trace(self, event: str, details: Any = None) -> None:
        self.trace_logs.append({"event": event, "details": details})
