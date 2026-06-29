"""
Adaptive Compilation Gate.

Decides whether a query is "hard" enough to justify the full C³ compiler
pipeline (retrieval + codegen + verification, multiple LLM calls, more
failure surface) or whether a single direct LLM call ("Vanilla") will
already get the right answer for less cost and latency.

Heuristic, not a model call: keeps the gate itself free and deterministic,
which matters for reproducible ablation runs. The signal is structural —
genuine multi-hop questions (the answer requires chaining facts through an
intermediate entity) and analytically heavy computation (calculus, etc.)
are routed to the compiler; everything else (single-formula arithmetic,
single-hop trivia, direct logic/string puzzles) is routed to Vanilla.
"""
from __future__ import annotations

from models.problem import ProblemSpec, ProblemType

# Phrases that indicate the answer requires resolving an intermediate entity
# before answering (classic multi-hop structure: "X of the Y that Z").
_MULTIHOP_MARKERS = [
    " in which", " that released", " that directed", " who directed",
    " where the", " country where", " band that", " film in which",
    " album that", " director of the film", " born in the",
]

# Computation that a single LLM forward pass tends to get wrong without
# actually executing code (multi-step symbolic/numeric work).
_COMPLEX_CALC_MARKERS = [
    "integral", "derivative", "matrix", "eigenvalue", "geometric series",
    "standard deviation", "probability distribution",
]


class AdaptiveGate:
    def evaluate(self, query: str, spec: ProblemSpec) -> dict:
        q = query.lower()

        is_multihop = any(marker in q for marker in _MULTIHOP_MARKERS)
        is_complex_calc = any(marker in q for marker in _COMPLEX_CALC_MARKERS)

        needs_retrieval_chain = is_multihop and spec.task_type in (
            ProblemType.FACTUAL_LOOKUP,
            ProblemType.RESEARCH,
        )

        hard = needs_retrieval_chain or is_complex_calc
        diff_score = 0.85 if hard else 0.25

        return {
            "compile": hard,
            "diff_score": diff_score,
            "reason": "multi_hop_retrieval" if needs_retrieval_chain else (
                "complex_calculation" if is_complex_calc else "single_step"
            ),
        }
