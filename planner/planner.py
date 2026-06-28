from __future__ import annotations
from pydantic import BaseModel
from models.problem import ProblemSpec, ProblemType

class ReasoningPlan(BaseModel):
    query: str
    operators: list[str]

class ReasoningPlanner:
    def plan(self, spec: ProblemSpec) -> ReasoningPlan:
        ops = []
        if spec.task_type == ProblemType.FACTUAL_LOOKUP or spec.metadata.get("requires_external_knowledge"):
            ops = ["Retrieve", "Verify", "Summarize", "LLM"]
        elif spec.task_type == ProblemType.ANALYTICAL_REASONING or spec.metadata.get("requires_calculation"):
            ops = ["Python", "Verify", "LLM"]
        else:
            ops = ["Retrieve", "LLM"]
        
        return ReasoningPlan(query=spec.query, operators=ops)
