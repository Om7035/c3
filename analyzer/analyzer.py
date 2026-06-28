from __future__ import annotations

from models.problem import ProblemSpec, ProblemType


class ProblemAnalyzer:
    def analyze(self, query: str) -> ProblemSpec:
        q = query.lower()
        task_type = ProblemType.UNKNOWN
        req_calc = False
        req_knowledge = False

        # --- Analytical Reasoning ---
        if any(token in q for token in ["how many", "calculate", "compute", "solve", "integral", "derivative", "math", "equation"]):
            task_type = ProblemType.ANALYTICAL_REASONING
            req_calc = True

        # --- Design Synthesis (code) ---
        elif any(token in q for token in ["write code", "write a script", "implement", "python function"]):
            task_type = ProblemType.DESIGN_SYNTHESIS
            req_calc = True

        # --- Design Planning (system/architecture design) ---
        elif any(token in q for token in ["design", "architect", "build a system", "infrastructure", "distributed", "scalable"]):
            task_type = ProblemType.DESIGN_PLANNING
            req_knowledge = True

        # --- Critical Evaluation ---
        elif any(token in q for token in ["critique", "evaluate", "review", "assess", "analyze the strengths", "analyze the weaknesses"]):
            task_type = ProblemType.CRITICAL_EVALUATION
            req_knowledge = True

        # --- Interpretive Reasoning (literature, philosophy, meaning-making) ---
        elif any(token in q for token in ["explain", "interpret", "what does", "why did", "motivation", "theme", "meaning of"]):
            task_type = ProblemType.INTERPRETIVE_REASONING
            req_knowledge = True

        # --- Factual Lookup ---
        elif any(token in q for token in ["who", "what", "where", "when", "which", "population", "capital"]):
            task_type = ProblemType.FACTUAL_LOOKUP
            req_knowledge = True

        # --- General Research fallback ---
        else:
            task_type = ProblemType.RESEARCH
            req_knowledge = True

        return ProblemSpec(
            query=query,
            task_type=task_type,
            complexity="medium",
            metadata={
                "requires_calculation": req_calc,
                "requires_external_knowledge": req_knowledge
            }
        )
