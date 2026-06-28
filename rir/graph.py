from __future__ import annotations

from typing import Any
import uuid

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    id: str
    opcode: str
    operands: dict[str, Any] = Field(default_factory=dict)
    outputs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str


class ReasoningGraph(BaseModel):
    header: dict[str, Any] = Field(
        default_factory=lambda: {
            "version": "1.0",
            "rir_id": str(uuid.uuid4()),
            "objective": "unknown"
        }
    )
    strategy: dict[str, Any] = Field(default_factory=dict)
    registers: list[str] = Field(default_factory=list)
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    observability: dict[str, Any] = Field(
        default_factory=lambda: {
            "trace_enabled": True,
            "log_level": "DEBUG",
            "export_visuals": ["mermaid", "ets"]
        }
    )
