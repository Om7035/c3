"""
C³ Benchmark Runner

Runs all 5 canonical benchmark queries through the full C³ compiler pipeline
AND the fixed-pipeline baseline, then prints the diversity report.

Usage:
    python benchmarks/runner.py
"""
from __future__ import annotations
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.analyzer import ProblemAnalyzer
from planner.planner import ReasoningPlanner
from planner.cost_model import estimate_cost
from compiler.compiler import Compiler
from optimizer.optimizer import PassManager
from runtime.executor import GraphExecutor
from operators.library import get_operator_registry
from core.context import ExecutionContext
from benchmarks.fixed_pipeline import build_fixed_pipeline_graph
from benchmarks.collector import collect
from metrics.graph_metrics import compute_graph_metrics
from metrics.diversity import compute_pairwise_diversity
from metrics.report import format_report


SUITE_PATH = os.path.join(os.path.dirname(__file__), "suite.json")


async def run_single(entry: dict, registry: dict) -> dict:
    query = entry["query"]
    bm_id = entry["id"]
    expected_class = entry["expected_problem_class"]

    analyzer = ProblemAnalyzer()
    spec = analyzer.analyze(query)

    planner = ReasoningPlanner()
    strategy = planner.plan(spec)

    # Attach cost estimate
    cost = estimate_cost(strategy)
    strategy.cost_estimate = cost.model_dump()

    compiler = Compiler()
    rir_graph = compiler.compile(strategy)

    optimizer = PassManager()
    optimized_graph, opt_diagnostics = optimizer.optimize(rir_graph)

    context = ExecutionContext(objective=query)
    executor = GraphExecutor(registry)
    rps_report = await executor.execute(optimized_graph, context)

    metrics = compute_graph_metrics(optimized_graph)
    metrics["benchmark_id"] = bm_id

    # Save to RPS dataset
    collect(
        benchmark_id=bm_id,
        query=query,
        problem_class=strategy.problem_class,
        strategy=strategy.model_dump(),
        rps_report=rps_report,
    )

    return {
        "id": bm_id,
        "query": query,
        "expected_class": expected_class,
        "actual_class": strategy.problem_class,
        "class_match": expected_class == strategy.problem_class,
        "strategy": strategy.model_dump(),
        "cost_estimate": cost.model_dump(),
        "optimizer_diagnostics": opt_diagnostics,
        "node_count_after_optimization": len(optimized_graph.nodes),
        "metrics": metrics,
        "rps": rps_report,
        "problem_class": strategy.problem_class,
    }


async def main():
    with open(SUITE_PATH, encoding="utf-8") as f:
        suite = json.load(f)

    registry = get_operator_registry()
    print(f"Running {len(suite)} benchmarks...\n")

    results = []
    for entry in suite:
        print(f"  [{entry['id']}] {entry['query'][:60]}...")
        result = await run_single(entry, registry)
        results.append(result)
        status = "OK" if result["class_match"] else "XX"
        print(f"         {status} Detected: {result['actual_class']}  |  "
              f"Nodes: {result['metrics']['node_count']}  |  "
              f"Cost: ${result['cost_estimate']['estimated_token_cost']:.5f}  |  "
              f"Est. latency: {result['cost_estimate']['estimated_latency_ms']}ms")

    print()

    # Diversity analysis
    diversity = compute_pairwise_diversity([r["metrics"] for r in results])
    report = format_report(results, diversity)
    print(report)

    # Save full results to JSON
    out_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "diversity": diversity}, f, indent=2)
    print(f"\nFull results saved to: {out_path}")
    print(f"RPS dataset appended:  benchmarks/rps_dataset.jsonl")


if __name__ == "__main__":
    asyncio.run(main())
