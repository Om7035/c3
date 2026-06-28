from __future__ import annotations

from models.problem import ProblemSpec, ProblemType

class ProblemAnalyzer:
    def analyze(self, query: str) -> ProblemSpec:
        q = query.lower()
        task_type = ProblemType.UNKNOWN
        req_calc = False
        req_knowledge = False
        
        if any(token in q for token in ["how many", "calculate", "math"]):
            task_type = ProblemType.ANALYTICAL_REASONING
            req_calc = True
        elif any(token in q for token in ["write", "code", "python"]):
            task_type = ProblemType.DESIGN_SYNTHESIS
            req_calc = True
        elif any(token in q for token in ["who", "what", "where", "when"]):
            task_type = ProblemType.FACTUAL_LOOKUP
            req_knowledge = True
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
