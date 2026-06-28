from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ProblemType(str, Enum):
    FACTUAL_LOOKUP = "factual_lookup"
    DESIGN_SYNTHESIS = "design_synthesis"
    ANALYTICAL_REASONING = "analytical_reasoning"
    RESEARCH = "research"
    DESIGN_PLANNING = "design_planning"
    CRITICAL_EVALUATION = "critical_evaluation"
    INTERPRETIVE_REASONING = "interpretive_reasoning"
    UNKNOWN = "unknown"


class ProblemSpec(BaseModel):
    query: str
    task_type: ProblemType = ProblemType.UNKNOWN
    complexity: str = "medium"
    required_tools: list[str] = Field(default_factory=list)
    uncertainty: str = "low"
    expected_output: str = "text"
    confidence: float = 1.0
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
