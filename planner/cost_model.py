from __future__ import annotations
from pydantic import BaseModel
from planner.planner import ReasoningStrategy

# Cost estimates per opcode (in mock units: latency ms and token cost)
OPCODE_COST_TABLE: dict[str, dict] = {
    "KNOW.RETRIEVE":  {"latency_ms": 800,  "token_cost": 0.001},
    "KNOW.MEMORY":    {"latency_ms": 100,  "token_cost": 0.0001},
    "EXEC.PYTHON":    {"latency_ms": 300,  "token_cost": 0.0},
    "VERI.VERIFY":    {"latency_ms": 500,  "token_cost": 0.0005},
    "REAS.INFER":     {"latency_ms": 1500, "token_cost": 0.005},
    "REAS.SUMMARIZE": {"latency_ms": 1200, "token_cost": 0.004},
}

KNOWLEDGE_OPCODE_MAP = {
    "empirical_data": "KNOW.RETRIEVE",
    "context":        "KNOW.MEMORY",
}

REASONING_OPCODE_MAP = {
    "computation":  "EXEC.PYTHON",
    "deduction":    "REAS.INFER",
    "summarization":"REAS.SUMMARIZE",
    "synthesis":    "REAS.INFER",
    "comparison":   "REAS.INFER",
}


class CostEstimate(BaseModel):
    estimated_latency_ms: int
    estimated_token_cost: float
    estimated_node_count: int
    confidence_projection: float
    feasibility: str   # "within_budget" | "over_latency" | "over_cost"


def estimate_cost(strategy: ReasoningStrategy) -> CostEstimate:
    """
    Computes a cost estimate for the strategy before compilation.
    Mirrors the Compiler's opcode emission logic to predict what will be emitted.
    """
    predicted_opcodes: list[str] = []

    emitted_know: set[str] = set()
    for req in strategy.knowledge_requirements:
        opcode = KNOWLEDGE_OPCODE_MAP.get(req)
        if opcode and opcode not in emitted_know:
            predicted_opcodes.append(opcode)
            emitted_know.add(opcode)

    if "computation" in strategy.reasoning_requirements:
        predicted_opcodes.append(REASONING_OPCODE_MAP["computation"])

    if strategy.verification_requirements == "required":
        predicted_opcodes.append("VERI.VERIFY")

    if "summarization" in strategy.reasoning_requirements:
        predicted_opcodes.append(REASONING_OPCODE_MAP["summarization"])
    elif any(r in strategy.reasoning_requirements for r in ("deduction", "synthesis", "comparison")):
        predicted_opcodes.append(REASONING_OPCODE_MAP["deduction"])

    if strategy.verification_requirements == "optional":
        predicted_opcodes.append("VERI.VERIFY")

    total_latency = sum(OPCODE_COST_TABLE.get(op, {}).get("latency_ms", 500)
                        for op in predicted_opcodes)
    total_cost = sum(OPCODE_COST_TABLE.get(op, {}).get("token_cost", 0.001)
                     for op in predicted_opcodes)

    # Simple confidence projection: starts at target, reduced by verification gaps
    confidence_projection = strategy.execution_profile.get("confidence_target", 0.95)
    if strategy.verification_requirements == "none":
        confidence_projection *= 0.85  # no verification reduces confidence projection

    feasibility = "within_budget"
    latency_budget = strategy.execution_profile.get("latency_budget_ms", 10000)
    cost_budget = strategy.execution_profile.get("cost_budget_usd", 0.10)
    if total_latency > latency_budget:
        feasibility = "over_latency"
    elif total_cost > cost_budget:
        feasibility = "over_cost"

    return CostEstimate(
        estimated_latency_ms=total_latency,
        estimated_token_cost=round(total_cost, 6),
        estimated_node_count=len(predicted_opcodes),
        confidence_projection=round(confidence_projection, 3),
        feasibility=feasibility,
    )
