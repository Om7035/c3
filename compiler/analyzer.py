from __future__ import annotations

from models.problem import ProblemSpec, ProblemType


class ProblemAnalyzer:
    """Heuristic problem analyzer."""

    def analyze(self, query: str) -> ProblemSpec:
        query_lower = query.lower()
        task_type = ProblemType.UNKNOWN
        
        if any(token in query_lower for token in ("how many", "what is", "when did", "where is")):
            task_type = ProblemType.FACTUAL_LOOKUP
        elif any(token in query_lower for token in ("design", "architect", "optimize", "build")):
            task_type = ProblemType.DESIGN_SYNTHESIS
        elif any(token in query_lower for token in ("why", "compare", "analyze", "explain")):
            task_type = ProblemType.ANALYTICAL_REASONING
        elif any(token in query_lower for token in ("research", "find out", "investigate")):
            task_type = ProblemType.RESEARCH
            
        return ProblemSpec(
            query=query,
            task_type=task_type,
            complexity="low",
            uncertainty="low" if task_type == ProblemType.FACTUAL_LOOKUP else "medium"
        )
