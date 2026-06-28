from __future__ import annotations
import uuid
from planner.planner import ReasoningStrategy
from rir.graph import ReasoningGraph, GraphNode, GraphEdge
from compiler.validator import StrategyValidator

# Maps strategy requirement tokens to ISA opcodes.
KNOWLEDGE_OPCODE_MAP = {
    "empirical_data": "KNOW.RETRIEVE",
    "context": "KNOW.MEMORY",
}

REASONING_OPCODE_MAP = {
    "computation": "EXEC.PYTHON",
    "deduction": "REAS.INFER",
    "summarization": "REAS.SUMMARIZE",
    "synthesis": "REAS.INFER",    # synthesis is a form of inference
    "comparison": "REAS.INFER",   # comparison is a form of inference
}


class Compiler:
    def __init__(self):
        self._validator = StrategyValidator()

    def compile(self, strategy: ReasoningStrategy) -> ReasoningGraph:
        # Type-check the strategy AST before emitting any RIR
        report = self._validator.validate(strategy)
        if not report.valid:
            errors = "; ".join(f"[{d.code}] {d.message}" for d in report.errors)
            raise ValueError(f"Strategy validation failed: {errors}")

        graph = ReasoningGraph()
        graph.header["objective"] = strategy.objective
        graph.strategy = {
            "problem_class": strategy.problem_class,
            "execution_profile": strategy.execution_profile,
            "validation": report.as_dict(),
        }

        prev_node = None
        prev_register = None
        graph.registers.append("reg_input_query")

        opcodes_to_emit: list[str] = []

        # 1. KNOW phase — emit knowledge-gathering primitives (deduplicated)
        emitted_know = set()
        for req in strategy.knowledge_requirements:
            opcode = KNOWLEDGE_OPCODE_MAP.get(req)
            if opcode and opcode not in emitted_know:
                opcodes_to_emit.append(opcode)
                emitted_know.add(opcode)

        # 2. EXEC phase — computation primitives come before reasoning
        if "computation" in strategy.reasoning_requirements:
            opcodes_to_emit.append(REASONING_OPCODE_MAP["computation"])

        # 3. VERI phase — verify intermediate results before final inference
        if strategy.verification_requirements == "required":
            opcodes_to_emit.append("VERI.VERIFY")

        # 4. REAS phase — emit highest-order reasoning primitive last
        #    Priority: summarization > deduction/synthesis/comparison
        if "summarization" in strategy.reasoning_requirements:
            opcodes_to_emit.append(REASONING_OPCODE_MAP["summarization"])
        elif any(r in strategy.reasoning_requirements for r in ("deduction", "synthesis", "comparison")):
            opcodes_to_emit.append(REASONING_OPCODE_MAP["deduction"])

        # 5. Optional final verification
        if strategy.verification_requirements == "optional":
            opcodes_to_emit.append("VERI.VERIFY")

        # Emit RIR nodes
        for i, opcode in enumerate(opcodes_to_emit):
            node_id = f"node_{i}_{opcode.split('.')[-1].lower()}_{uuid.uuid4().hex[:4]}"
            out_reg = f"reg_out_{i}_{opcode.split('.')[-1].lower()}"
            graph.registers.append(out_reg)

            operands: dict = {}
            if prev_node is None:
                operands["query"] = strategy.objective
            else:
                operands["input_data"] = f"${prev_register}"

            node = GraphNode(
                id=node_id,
                opcode=opcode,
                operands=operands,
                outputs=[out_reg],
                metadata={
                    "confidence_target": strategy.execution_profile.get("confidence_target", 1.0)
                }
            )
            graph.nodes.append(node)

            if prev_node:
                graph.edges.append(GraphEdge(source=prev_node.id, target=node.id))

            prev_node = node
            prev_register = out_reg

        return graph
