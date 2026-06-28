from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
from models.problem import ProblemSpec, ProblemType


class ReasoningStrategy(BaseModel):
    objective: str
    problem_class: str
    execution_profile: dict[str, Any] = Field(default_factory=dict)
    knowledge_requirements: list[str] = Field(default_factory=list)
    reasoning_requirements: list[str] = Field(default_factory=list)
    verification_requirements: str = "none"
    cost_estimate: dict[str, Any] = Field(default_factory=dict)


class ReasoningPlanner:
    def plan(self, spec: ProblemSpec) -> ReasoningStrategy:
        strategy = ReasoningStrategy(
            objective=spec.query,
            problem_class=spec.task_type.value,
            execution_profile={
                "confidence_target": 0.95,
                "parallelism_allowed": True,
                "fail_fast": False
            }
        )

        if spec.task_type == ProblemType.FACTUAL_LOOKUP:
            strategy.knowledge_requirements = ["empirical_data"]
            strategy.reasoning_requirements = ["summarization"]
            strategy.verification_requirements = "required"

        elif spec.task_type == ProblemType.ANALYTICAL_REASONING:
            strategy.knowledge_requirements = []
            strategy.reasoning_requirements = ["computation", "deduction"]
            strategy.verification_requirements = "required"

        elif spec.task_type in (ProblemType.DESIGN_SYNTHESIS, ProblemType.DESIGN_PLANNING):
            # Planning a system: needs background knowledge, deductive synthesis,
            # and verification of constraints.
            strategy.knowledge_requirements = ["empirical_data", "context"]
            strategy.reasoning_requirements = ["deduction", "synthesis"]
            strategy.verification_requirements = "required"

        elif spec.task_type == ProblemType.CRITICAL_EVALUATION:
            # Critique: retrieve background knowledge, compare, then infer judgment.
            strategy.knowledge_requirements = ["empirical_data", "context"]
            strategy.reasoning_requirements = ["comparison", "deduction"]
            strategy.verification_requirements = "optional"

        elif spec.task_type == ProblemType.INTERPRETIVE_REASONING:
            # Interpretation: retrieve text/context, then reason about meaning.
            strategy.knowledge_requirements = ["context"]
            strategy.reasoning_requirements = ["deduction", "summarization"]
            strategy.verification_requirements = "none"

        else:
            # RESEARCH / UNKNOWN fallback
            strategy.knowledge_requirements = ["empirical_data", "context"]
            strategy.reasoning_requirements = ["deduction"]
            strategy.verification_requirements = "optional"

        return strategy
