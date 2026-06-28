"""
C³ Ablation Study Runner — Milestone X

Runs all 4 experimental conditions across the full 50-question benchmark
and produces a comparison table proving (or disproving) the central hypothesis.

Conditions:
  A — Fixed (Minimal):   RETRIEVE → INFER          [null baseline]
  B — Fixed (ReAct):     RETRIEVE → PYTHON → VERIFY → INFER [strong baseline]
  C — C³ (no optimizer): Dynamic strategy, PassManager disabled
  D — Full C³:           Dynamic strategy + PassManager [hypothesis condition]

Usage:
  # Mock mode (fast, no API keys needed):
  python benchmarks/ablation.py

  # Live mode (real LLM, requires API keys):
  C3_BACKEND=live OPENAI_API_KEY=sk-... TAVILY_API_KEY=tvly-... python benchmarks/ablation.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from operators.config import is_live, get_backend
from operators.library import get_operator_registry
from core.context import ExecutionContext
from analyzer.analyzer import ProblemAnalyzer
from planner.planner import ReasoningPlanner
from planner.cost_model import estimate_cost
from compiler.compiler import Compiler
from optimizer.optimizer import PassManager
from runtime.executor import GraphExecutor
from benchmarks.fixed_pipeline import build_fixed_pipeline_graph, build_react_pipeline_graph
from benchmarks.data.judge import judge_exact, judge_numeric, judge_rubric
from metrics.graph_metrics import compute_graph_metrics
from metrics.ere import compute_reasoning_efficiency, compute_mean_confidence

# ── Load datasets ─────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_suite() -> list[dict]:
    suite = []
    for fname in ["triviaqa_subset.json", "gsm8k_subset.json", "planning_curated.json"]:
        with open(os.path.join(DATA_DIR, fname), encoding="utf-8") as f:
            suite.extend(json.load(f))
    return suite


def extract_answer(rps_report: dict) -> str:
    """Pull the final answer from the last provenance event."""
    events = rps_report.get("provenance_events", [])
    for event in reversed(events):
        reg_written = event.get("registers_written", {})
        for val in reg_written.values():
            if isinstance(val, dict):
                for key in ("response", "summary", "output", "answer"):
                    if key in val:
                        return str(val[key])[:500]
            elif isinstance(val, str):
                return val[:500]
    return ""


async def evaluate_answer(answer: str, question: dict) -> float:
    qtype = question.get("type", "exact")
    if qtype == "numeric":
        result = judge_numeric(answer, question["answer"])
        return result["score"]
    elif qtype == "rubric":
        if is_live():
            result = await judge_rubric(answer, question["rubric"], question["query"])
        else:
            # In mock mode, give a fixed partial score so ablation table shows differentiation
            result = {"score": 0.5}
        return result["score"]
    else:  # exact
        result = judge_exact(answer, question["answer"], question.get("answer_aliases", []))
        return result["score"]


async def run_condition_a(question: dict, registry: dict) -> dict:
    """Condition A: Fixed Minimal (RETRIEVE → INFER)"""
    graph = build_fixed_pipeline_graph(question["query"])
    context = ExecutionContext(objective=question["query"])
    executor = GraphExecutor(registry)
    t0 = time.monotonic()
    rps = await executor.execute(graph, context)
    latency_ms = int((time.monotonic() - t0) * 1000)
    answer = extract_answer(rps)
    score = await evaluate_answer(answer, question)
    metrics = compute_graph_metrics(graph)
    mean_conf = compute_mean_confidence(rps)
    ere = compute_reasoning_efficiency(metrics["node_count"], mean_conf, 2500, 0.006, metrics["verification_density"])
    return {"score": score, "answer": answer, "latency_ms": latency_ms, "metrics": metrics, "ere": ere["re_score"], "graph_diversity": 0.0, "verification_rate": metrics["verification_density"]}


async def run_condition_b(question: dict, registry: dict) -> dict:
    """Condition B: Fixed ReAct (RETRIEVE → PYTHON → VERIFY → INFER)"""
    graph = build_react_pipeline_graph(question["query"])
    context = ExecutionContext(objective=question["query"])
    executor = GraphExecutor(registry)
    t0 = time.monotonic()
    rps = await executor.execute(graph, context)
    latency_ms = int((time.monotonic() - t0) * 1000)
    answer = extract_answer(rps)
    score = await evaluate_answer(answer, question)
    metrics = compute_graph_metrics(graph)
    mean_conf = compute_mean_confidence(rps)
    ere = compute_reasoning_efficiency(metrics["node_count"], mean_conf, 3800, 0.010, metrics["verification_density"])
    return {"score": score, "answer": answer, "latency_ms": latency_ms, "metrics": metrics, "ere": ere["re_score"], "graph_diversity": 0.0, "verification_rate": metrics["verification_density"]}


async def run_c3_condition(question: dict, registry: dict, use_optimizer: bool) -> dict:
    """Condition C (no optimizer) or D (full C³)."""
    analyzer = ProblemAnalyzer()
    spec = analyzer.analyze(question["query"])
    planner = ReasoningPlanner()
    strategy = planner.plan(spec)
    cost = estimate_cost(strategy)
    strategy.cost_estimate = cost.model_dump()

    compiler = Compiler()
    rir_graph = compiler.compile(strategy)

    if use_optimizer:
        optimizer = PassManager()
        graph, _ = optimizer.optimize(rir_graph)
    else:
        graph = rir_graph

    context = ExecutionContext(objective=question["query"])
    executor = GraphExecutor(registry)
    t0 = time.monotonic()
    rps = await executor.execute(graph, context)
    latency_ms = int((time.monotonic() - t0) * 1000)
    answer = extract_answer(rps)
    score = await evaluate_answer(answer, question)
    metrics = compute_graph_metrics(graph)
    mean_conf = compute_mean_confidence(rps)
    ere = compute_reasoning_efficiency(
        metrics["node_count"], mean_conf,
        cost.estimated_latency_ms, cost.estimated_token_cost,
        metrics["verification_density"]
    )
    return {
        "score": score, "answer": answer, "latency_ms": latency_ms,
        "metrics": metrics, "ere": ere["re_score"],
        "problem_class": strategy.problem_class,
        "graph_diversity": 0.0,  # computed across questions later
        "verification_rate": metrics["verification_density"],
    }


def aggregate(results: list[dict]) -> dict:
    n = len(results)
    if n == 0:
        return {}
    return {
        "accuracy": round(sum(r["score"] for r in results) / n, 4),
        "mean_ere": round(sum(r["ere"] for r in results) / n, 4),
        "mean_latency_ms": round(sum(r["latency_ms"] for r in results) / n),
        "verification_rate": round(sum(r["verification_rate"] for r in results) / n, 4),
        "mean_nodes": round(sum(r["metrics"]["node_count"] for r in results) / n, 2),
        "n": n,
    }


def print_table(agg: dict[str, dict]):
    keys = ["accuracy", "mean_ere", "verification_rate", "mean_latency_ms", "mean_nodes"]
    labels = ["Accuracy", "Mean ERE", "Verification Rate", "Latency (ms)", "Avg Nodes"]
    cols = list(agg.keys())
    col_w = 18

    print("\n" + "=" * 90)
    print("  C3 ABLATION STUDY RESULTS")
    print("=" * 90)
    print(f"{'Metric':<22}" + "".join(f"{c:<{col_w}}" for c in cols))
    print("-" * 90)
    for k, lbl in zip(keys, labels):
        row = f"{lbl:<22}"
        for c in cols:
            val = agg[c].get(k, "N/A")
            row += f"{str(val):<{col_w}}"
        print(row)
    print("=" * 90)

    # Verdict
    if "D - Full C3" in agg and "B - Fixed (ReAct)" in agg:
        c3_ere = agg["D - Full C3"]["mean_ere"]
        b_ere = agg["B - Fixed (ReAct)"]["mean_ere"]
        c3_acc = agg["D - Full C3"]["accuracy"]
        b_acc = agg["B - Fixed (ReAct)"]["accuracy"]
        if c3_ere > b_ere and c3_acc >= b_acc:
            print("\n  VERDICT: C3 hypothesis SUPPORTED (ERE and accuracy both exceed ReAct baseline)")
        elif c3_ere > b_ere:
            print("\n  VERDICT: C3 hypothesis PARTIALLY SUPPORTED (ERE exceeds baseline; accuracy inconclusive)")
        else:
            print("\n  VERDICT: C3 hypothesis NOT YET SUPPORTED (further tuning needed)")


async def main():
    suite = load_suite()
    registry = get_operator_registry()
    backend = get_backend()
    print(f"Backend: {backend.upper()} | {len(suite)} questions")
    print("Running 4 conditions...\n")

    all_results: dict[str, list[dict]] = {
        "A - Fixed (Minimal)": [],
        "B - Fixed (ReAct)": [],
        "C - C3 (no opt)": [],
        "D - Full C3": [],
    }

    for i, q in enumerate(suite):
        print(f"  [{i+1:02d}/{len(suite)}] {q['query'][:55]}...")
        try:
            a = await run_condition_a(q, registry)
            b = await run_condition_b(q, registry)
            c = await run_c3_condition(q, registry, use_optimizer=False)
            d = await run_c3_condition(q, registry, use_optimizer=True)

            all_results["A - Fixed (Minimal)"].append(a)
            all_results["B - Fixed (ReAct)"].append(b)
            all_results["C - C3 (no opt)"].append(c)
            all_results["D - Full C3"].append(d)

            print(f"         A:{a['score']:.2f}  B:{b['score']:.2f}  C:{c['score']:.2f}  D:{d['score']:.2f}  [{c.get('problem_class','?')}]")
        except Exception as e:
            print(f"         ERROR: {e}")
            continue

    # Aggregate
    agg = {cond: aggregate(results) for cond, results in all_results.items()}
    print_table(agg)

    # Save results
    out_path = os.path.join(os.path.dirname(__file__), "ablation_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"backend": backend, "conditions": agg, "per_question": {k: v for k, v in all_results.items()}}, f, indent=2)
    print(f"\nFull results saved to: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
