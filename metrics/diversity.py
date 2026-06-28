from __future__ import annotations
from typing import Any


def jaccard_distance(dist_a: dict[str, int], dist_b: dict[str, int]) -> float:
    """
    Computes Jaccard distance between two opcode distribution dicts.
    A score of 1.0 means completely different opcode sets; 0.0 means identical.
    """
    keys_a = set(dist_a.keys())
    keys_b = set(dist_b.keys())
    intersection = keys_a & keys_b
    union = keys_a | keys_b
    if not union:
        return 0.0
    return round(1.0 - len(intersection) / len(union), 4)


def compute_pairwise_diversity(metrics_list: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Given a list of graph metrics (one per benchmark), computes pairwise
    Jaccard distances between opcode distributions and returns a diversity report.
    """
    n = len(metrics_list)
    labels = [m.get("benchmark_id", f"G{i}") for i, m in enumerate(metrics_list)]
    distances: list[list[float]] = []

    for i in range(n):
        row = []
        for j in range(n):
            d = jaccard_distance(
                metrics_list[i]["opcode_distribution"],
                metrics_list[j]["opcode_distribution"]
            )
            row.append(d)
        distances.append(row)

    # Average pairwise distance (excluding self-comparison on diagonal)
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
    avg_diversity = round(sum(distances[i][j] for i, j in pairs) / len(pairs), 4) if pairs else 0.0

    return {
        "labels": labels,
        "distance_matrix": distances,
        "average_diversity_score": avg_diversity,
        "interpretation": (
            "HIGH diversity: C³ is generating structurally distinct graphs per problem class."
            if avg_diversity >= 0.4
            else "LOW diversity: graphs are too similar — planner may need more differentiation."
        )
    }
