"""
Baseline pipelines for C³ benchmarking.

Three fixed baselines are defined. All have diversity score = 0.000 by definition
(every query produces the same graph). They differ in complexity and are designed
to be progressively fairer comparisons for the RE metric.

  B1 — Minimal:         KNOW.RETRIEVE → REAS.INFER
  B2 — Chain-of-Thought: KNOW.RETRIEVE → REAS.INFER → REAS.SUMMARIZE
  B3 — ReAct-style:     KNOW.RETRIEVE → EXEC.PYTHON → VERI.VERIFY → REAS.INFER
"""
from __future__ import annotations
import uuid
from rir.graph import ReasoningGraph, GraphNode, GraphEdge


def _build_linear_graph(query: str, opcodes: list[str], label: str) -> ReasoningGraph:
    """Helper: builds a fixed linear graph from a list of opcodes."""
    graph = ReasoningGraph()
    graph.header["objective"] = query
    graph.strategy = {"problem_class": label, "execution_profile": {}}
    graph.registers = ["reg_input_query"] + [f"reg_out_{i}" for i in range(len(opcodes))]

    nodes = []
    for i, opcode in enumerate(opcodes):
        node_id = f"node_{i}_{opcode.split('.')[-1].lower()}_{uuid.uuid4().hex[:4]}"
        operands = {"query": query} if i == 0 else {"input_data": f"$reg_out_{i-1}"}
        nodes.append(GraphNode(
            id=node_id,
            opcode=opcode,
            operands=operands,
            outputs=[f"reg_out_{i}"],
        ))

    graph.nodes = nodes
    graph.edges = [
        GraphEdge(source=nodes[i].id, target=nodes[i + 1].id)
        for i in range(len(nodes) - 1)
    ]
    return graph


def build_fixed_pipeline_graph(query: str) -> ReasoningGraph:
    """B1 — Minimal: RETRIEVE → INFER"""
    return _build_linear_graph(query, ["KNOW.RETRIEVE", "REAS.INFER"], "fixed_b1_minimal")


def build_cot_pipeline_graph(query: str) -> ReasoningGraph:
    """B2 — Chain-of-Thought: RETRIEVE → INFER → SUMMARIZE"""
    return _build_linear_graph(
        query,
        ["KNOW.RETRIEVE", "REAS.INFER", "REAS.SUMMARIZE"],
        "fixed_b2_cot"
    )


def build_react_pipeline_graph(query: str) -> ReasoningGraph:
    """B3 — ReAct-style: RETRIEVE → PYTHON → VERIFY → INFER"""
    return _build_linear_graph(
        query,
        ["KNOW.RETRIEVE", "EXEC.PYTHON", "VERI.VERIFY", "REAS.INFER"],
        "fixed_b3_react"
    )


BASELINES = {
    "B1 (Minimal)": build_fixed_pipeline_graph,
    "B2 (CoT)": build_cot_pipeline_graph,
    "B3 (ReAct)": build_react_pipeline_graph,
}
