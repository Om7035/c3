from __future__ import annotations
from typing import Any


def compute_reasoning_efficiency(
    node_count: int,
    confidence: float,
    estimated_latency_ms: int,
    estimated_token_cost: float,
    verification_density: float,
) -> dict[str, Any]:
    """
    Computes the Reasoning Efficiency (RE) metric for a compiled and executed graph.

    RE = (Accuracy * Confidence) / (Cost * Latency * Nodes)

    With mock operators, we proxy Accuracy with verification_density
    (the proportion of the graph dedicated to self-checking). This is labeled
    "projected RE" in the paper until live LLM integration provides real accuracy.

    Args:
        node_count: Total nodes in the optimized graph.
        confidence: Mean confidence across all provenance events.
        estimated_latency_ms: Projected latency from cost model (ms).
        estimated_token_cost: Projected token cost in USD from cost model.
        verification_density: Ratio of VERI nodes to total nodes.

    Returns:
        A dict containing the RE score and its component values.
    """
    # Proxy accuracy with verification density: a graph that verifies itself
    # has a higher accuracy ceiling than one that doesn't.
    # Minimum proxy accuracy of 0.5 to avoid zero-division artifacts.
    proxy_accuracy = max(0.5, verification_density)

    # Normalize cost and latency to avoid underflow
    # cost floor: 0.0001 USD (so pure-compute tasks don't get infinite RE)
    norm_cost = max(estimated_token_cost, 0.0001)
    # latency floor: 100ms
    norm_latency_s = max(estimated_latency_ms, 100) / 1000.0
    # node floor: 1
    norm_nodes = max(node_count, 1)

    numerator = proxy_accuracy * confidence
    denominator = norm_cost * norm_latency_s * norm_nodes

    re_score = round(numerator / denominator, 4) if denominator > 0 else 0.0

    return {
        "re_score": re_score,
        "components": {
            "proxy_accuracy": round(proxy_accuracy, 4),
            "confidence": round(confidence, 4),
            "norm_cost_usd": round(norm_cost, 6),
            "norm_latency_s": round(norm_latency_s, 4),
            "node_count": norm_nodes,
        },
        "label": "projected_re",
        "note": (
            "RE uses proxy accuracy (verification density) until live LLM "
            "integration provides empirical accuracy scores."
        )
    }


def compute_mean_confidence(rps_report: dict) -> float:
    """Extracts mean confidence across all provenance events."""
    events = rps_report.get("provenance_events", [])
    if not events:
        return 0.0
    return sum(e.get("confidence", 0.0) for e in events) / len(events)
