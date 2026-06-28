from __future__ import annotations
from typing import Any


def format_report(benchmark_results: list[dict[str, Any]], diversity_report: dict[str, Any]) -> str:
    """
    Formats a human-readable summary table of benchmark results.
    """
    lines = []
    lines.append("=" * 80)
    lines.append("  C³ BENCHMARK RESULTS — Graph Diversity Report")
    lines.append("=" * 80)
    lines.append("")

    # Per-benchmark table
    header = f"{'ID':<8} {'Problem Class':<25} {'Nodes':<7} {'Depth':<7} {'Width':<7} {'KNOW%':<8} {'EXEC%':<8} {'REAS%':<8} {'VERI%':<8}"
    lines.append(header)
    lines.append("-" * 80)

    for r in benchmark_results:
        m = r["metrics"]
        lines.append(
            f"{r['id']:<8} {r['problem_class']:<25} {m['node_count']:<7} "
            f"{m['graph_depth']:<7} {m['graph_width']:<7} "
            f"{m['know_ratio']*100:<8.1f} {m['exec_ratio']*100:<8.1f} "
            f"{m['reas_ratio']*100:<8.1f} {m['veri_ratio']*100:<8.1f}"
        )

    lines.append("")
    lines.append("=" * 80)
    lines.append("  DIVERSITY ANALYSIS (Jaccard Distance between Opcode Distributions)")
    lines.append("=" * 80)

    labels = diversity_report["labels"]
    matrix = diversity_report["distance_matrix"]
    col_width = 10

    # Header row
    header_row = " " * 8 + "".join(f"{lbl:<{col_width}}" for lbl in labels)
    lines.append(header_row)
    lines.append("-" * (8 + col_width * len(labels)))

    for i, row in enumerate(matrix):
        row_str = f"{labels[i]:<8}" + "".join(f"{v:<{col_width}.3f}" for v in row)
        lines.append(row_str)

    lines.append("")
    lines.append(f"  Average Pairwise Diversity Score: {diversity_report['average_diversity_score']:.4f}")
    lines.append(f"  -> {diversity_report['interpretation']}")
    lines.append("")

    # Fixed pipeline baseline note
    lines.append("  BASELINE (Fixed Pipeline): Diversity Score = 0.000")
    lines.append("  (Fixed pipeline always generates the same graph regardless of input)")
    lines.append("=" * 80)

    return "\n".join(lines)
