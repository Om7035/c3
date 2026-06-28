from __future__ import annotations
from dataclasses import dataclass, field
from planner.planner import ReasoningStrategy


@dataclass
class ValidationDiagnostic:
    level: str   # "error" | "warning"
    code: str
    message: str


@dataclass
class ValidationReport:
    valid: bool
    diagnostics: list[ValidationDiagnostic] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationDiagnostic]:
        return [d for d in self.diagnostics if d.level == "error"]

    @property
    def warnings(self) -> list[ValidationDiagnostic]:
        return [d for d in self.diagnostics if d.level == "warning"]

    def as_dict(self) -> dict:
        return {
            "valid": self.valid,
            "errors": [{"code": d.code, "message": d.message} for d in self.errors],
            "warnings": [{"code": d.code, "message": d.message} for d in self.warnings],
        }


class StrategyValidator:
    """
    Type-checks a ReasoningStrategy AST before it is lowered to RIR.
    Analogous to the semantic analysis / type-checking phase in a traditional compiler.
    Emits errors (which block compilation) and warnings (which are advisory).
    """

    def validate(self, strategy: ReasoningStrategy) -> ValidationReport:
        diagnostics: list[ValidationDiagnostic] = []

        # E001: Empty program — no knowledge AND no reasoning
        if not strategy.knowledge_requirements and not strategy.reasoning_requirements:
            diagnostics.append(ValidationDiagnostic(
                level="error",
                code="E001",
                message=(
                    "Strategy produces an empty program: both 'knowledge_requirements' "
                    "and 'reasoning_requirements' are empty. "
                    "At least one must be specified."
                )
            ))

        # E002: Logical contradiction — fail_fast with no verification
        if (strategy.execution_profile.get("fail_fast") is True
                and strategy.verification_requirements == "none"):
            diagnostics.append(ValidationDiagnostic(
                level="error",
                code="E002",
                message=(
                    "Contradiction: 'fail_fast' is True but 'verification_requirements' "
                    "is 'none'. A fast-failing strategy must include verification to "
                    "determine failure conditions."
                )
            ))

        # W001: Unreachable confidence target — high target with no verification
        confidence_target = strategy.execution_profile.get("confidence_target", 0.95)
        if confidence_target > 0.98 and strategy.verification_requirements == "none":
            diagnostics.append(ValidationDiagnostic(
                level="warning",
                code="W001",
                message=(
                    f"Confidence target {confidence_target} is very high but "
                    "'verification_requirements' is 'none'. "
                    "The confidence target may be unreachable without a VERI pass."
                )
            ))

        # W002: Computation without EXEC primitive availability check
        if "computation" in strategy.reasoning_requirements:
            diagnostics.append(ValidationDiagnostic(
                level="warning",
                code="W002",
                message=(
                    "Strategy requires 'computation' (EXEC.PYTHON). "
                    "Ensure the runtime environment has a Python execution sandbox available."
                )
            ))

        # W003: Cost budget likely exceeded
        cost_budget = strategy.execution_profile.get("cost_budget_usd", None)
        if cost_budget is not None:
            from planner.cost_model import estimate_cost
            estimate = estimate_cost(strategy)
            if estimate.feasibility == "over_cost":
                diagnostics.append(ValidationDiagnostic(
                    level="warning",
                    code="W003",
                    message=(
                        f"Projected cost ${estimate.estimated_token_cost:.5f} exceeds "
                        f"budget ${cost_budget:.5f}. Consider reducing knowledge "
                        "requirements or relaxing verification."
                    )
                ))
            elif estimate.feasibility == "over_latency":
                diagnostics.append(ValidationDiagnostic(
                    level="warning",
                    code="W004",
                    message=(
                        f"Projected latency {estimate.estimated_latency_ms}ms exceeds "
                        f"budget {strategy.execution_profile.get('latency_budget_ms')}ms."
                    )
                ))

        has_errors = any(d.level == "error" for d in diagnostics)
        return ValidationReport(valid=not has_errors, diagnostics=diagnostics)
