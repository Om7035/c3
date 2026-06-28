from __future__ import annotations
from typing import Any
from rir.graph import ReasoningGraph


def compute_graph_metrics(graph: ReasoningGraph) -> dict[str, Any]:
    """
    Computes structural metrics for a compiled ReasoningGraph.
    These are used to measure graph diversity across problem classes.
    """
    nodes = graph.nodes
    edges = graph.edges
    n = len(nodes)

    if n == 0:
        return {
            "node_count": 0,
            "edge_count": 0,
            "register_count": 0,
            "graph_depth": 0,
            "graph_width": 0,
            "opcode_distribution": {},
            "verification_density": 0.0,
            "know_ratio": 0.0,
            "exec_ratio": 0.0,
            "reas_ratio": 0.0,
            "veri_ratio": 0.0,
        }

    # Opcode distribution
    opcode_distribution: dict[str, int] = {}
    for node in nodes:
        opcode_distribution[node.opcode] = opcode_distribution.get(node.opcode, 0) + 1

    # Category ratios
    know_count = sum(1 for nd in nodes if nd.opcode.startswith("KNOW"))
    exec_count = sum(1 for nd in nodes if nd.opcode.startswith("EXEC"))
    reas_count = sum(1 for nd in nodes if nd.opcode.startswith("REAS"))
    veri_count = sum(1 for nd in nodes if nd.opcode.startswith("VERI"))

    # Graph depth (longest path) — using topological sort over adjacency
    successors: dict[str, list[str]] = {nd.id: [] for nd in nodes}
    for e in edges:
        successors[e.source].append(e.target)

    predecessors: dict[str, list[str]] = {nd.id: [] for nd in nodes}
    for e in edges:
        predecessors[e.target].append(e.source)

    # Compute depth via memoized DFS
    memo: dict[str, int] = {}

    def depth(node_id: str) -> int:
        if node_id in memo:
            return memo[node_id]
        if not successors[node_id]:
            memo[node_id] = 1
        else:
            memo[node_id] = 1 + max(depth(s) for s in successors[node_id])
        return memo[node_id]

    graph_depth = max((depth(nd.id) for nd in nodes), default=0)

    # Graph width: max number of nodes at any depth level
    level: dict[str, int] = {}

    def assign_level(node_id: str, lvl: int) -> None:
        if node_id in level and level[node_id] >= lvl:
            return
        level[node_id] = lvl
        for s in successors[node_id]:
            assign_level(s, lvl + 1)

    roots = [nd.id for nd in nodes if not predecessors[nd.id]]
    for r in roots:
        assign_level(r, 0)

    if level:
        level_counts: dict[int, int] = {}
        for lvl in level.values():
            level_counts[lvl] = level_counts.get(lvl, 0) + 1
        graph_width = max(level_counts.values())
    else:
        graph_width = 1

    return {
        "node_count": n,
        "edge_count": len(edges),
        "register_count": len(graph.registers),
        "graph_depth": graph_depth,
        "graph_width": graph_width,
        "opcode_distribution": opcode_distribution,
        "verification_density": round(veri_count / n, 3),
        "know_ratio": round(know_count / n, 3),
        "exec_ratio": round(exec_count / n, 3),
        "reas_ratio": round(reas_count / n, 3),
        "veri_ratio": round(veri_count / n, 3),
    }
