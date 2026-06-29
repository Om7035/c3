from __future__ import annotations
import json
import os
from typing import Any
from pydantic import BaseModel, Field
from openai import OpenAI

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
    def __init__(self):
        # We can use sync OpenAI for the planner to keep it simple, 
        # but in async environments we should ideally use AsyncOpenAI.
        # Since planner might be called from synchronous contexts in the current architecture,
        # we will use sync here, or provide a fallback.
        self._client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy"))

    def plan(self, spec: ProblemSpec) -> ReasoningStrategy:
        """
        Synthesizes a reasoning strategy by querying an LLM.
        This provides a true dynamic mapping from natural language to an AST,
        guiding the compiler without resorting to rigid heuristic templates.
        """
        # If running in mock backend, return a dummy strategy to avoid API calls
        if os.environ.get("C3_BACKEND", "mock").lower() == "mock":
            return self._mock_plan(spec)

        prompt = f"""You are the C³ Reasoning Planner. Your job is to analyze a problem and synthesize a Reasoning Strategy AST.

PROBLEM: {spec.query}
PROBLEM CLASS: {spec.task_type.value}

You must emit a JSON object matching this schema exactly:
{{
  "objective": "{spec.query}",
  "problem_class": "{spec.task_type.value}",
  "execution_profile": {{
    "confidence_target": <float between 0.0 and 1.0>,
    "parallelism_allowed": <bool>,
    "fail_fast": <bool>
  }},
  "knowledge_requirements": [<array of strings, e.g., "empirical_data", "context">],
  "reasoning_requirements": [<array of strings, e.g., "computation", "deduction", "summarization", "synthesis", "comparison">],
  "verification_requirements": <"required" | "optional" | "none">
}}

Rules:
1. If the problem requires factual lookup or math, verification_requirements should be "required".
2. If it requires subjective interpretation, verification_requirements can be "none".
3. Use reasoning_requirements to dictate which modules the compiler should emit:
   - "computation" triggers EXEC.PYTHON, a sandboxed Python interpreter. Use it ONLY when the
     answer requires executing code: arithmetic, algebra, calculus, sorting, string algorithms,
     date math, or similar deterministic operations on KNOWN values.
   - "summarization" or "synthesis" triggers REAS.SUMMARIZE, an LLM reading step. Use this for
     ANY problem that requires reading, combining, or extracting facts from retrieved text —
     including multi-hop trivia ("the capital of the country where X originates", "the singer of
     the band that released Y"). EXEC.PYTHON cannot read prose; do NOT pick "computation" for
     these even though they may look hard — they need text comprehension, not code execution.
   - Do not include "computation" unless the problem statement itself contains a calculation.
   - "context" (-> KNOW.MEMORY) is for multi-turn conversations needing memory of earlier turns.
     This is a single-shot question with no prior turns — never include "context".

Worked examples:
- "What is 15% of 240?" -> reasoning_requirements: ["computation"]  (arithmetic, no reading needed)
- "What is the capital of the country where the Amazon river originates?" ->
  reasoning_requirements: ["summarization"]  (pure multi-hop fact lookup — no arithmetic anywhere
  in the question, so "computation" must NOT appear here even though it requires multiple steps)
- "What is the name of the director of the film in which John Travolta plays a hitman?" ->
  reasoning_requirements: ["summarization"]  (identifying a named entity from retrieved text —
  there is nothing to execute or calculate, so "computation" must NOT appear)
- "Compute the definite integral of x squared from 0 to 3." -> reasoning_requirements: ["computation"]

Self-check before answering: re-read your reasoning_requirements list. If it contains
"computation", point to the exact substring in PROBLEM above that requires arithmetic or code
execution. If you cannot point to one, remove "computation" from the list.
"""
        try:
            resp = self._client.chat.completions.create(
                model=os.environ.get("C3_LLM_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a compiler front-end. Output strict JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            data = json.loads(resp.choices[0].message.content or "{}")
            
            return ReasoningStrategy(
                objective=data.get("objective", spec.query),
                problem_class=data.get("problem_class", spec.task_type.value),
                execution_profile=data.get("execution_profile", {"confidence_target": 0.95}),
                knowledge_requirements=data.get("knowledge_requirements", []),
                reasoning_requirements=data.get("reasoning_requirements", ["deduction"]),
                verification_requirements=data.get("verification_requirements", "optional")
            )
        except Exception:
            return self._mock_plan(spec)

    def _mock_plan(self, spec: ProblemSpec) -> ReasoningStrategy:
        """Fallback for mock mode or API failure."""
        strategy = ReasoningStrategy(
            objective=spec.query,
            problem_class=spec.task_type.value,
            execution_profile={"confidence_target": 0.95, "parallelism_allowed": True, "fail_fast": False}
        )
        if spec.task_type == ProblemType.FACTUAL_LOOKUP:
            strategy.knowledge_requirements = ["empirical_data"]
            strategy.reasoning_requirements = ["summarization"]
            strategy.verification_requirements = "required"
        elif spec.task_type == ProblemType.ANALYTICAL_REASONING:
            strategy.knowledge_requirements = []
            strategy.reasoning_requirements = ["computation", "deduction"]
            strategy.verification_requirements = "required"
        else:
            strategy.knowledge_requirements = ["empirical_data", "context"]
            strategy.reasoning_requirements = ["deduction", "synthesis"]
            strategy.verification_requirements = "optional"
        return strategy
