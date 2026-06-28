"""
C³ Ablation Study Runner — Milestone Y

Runs 3 experimental conditions across the benchmark to map the Cost-Accuracy Pareto Frontier.

Conditions:
  A — Vanilla LLM:       Raw tool-enabled LLM call (Frontier Baseline)
  B — Fixed (ReAct):     RETRIEVE → PYTHON → VERIFY → INFER [Strong Baseline]
  C — Full C³:           Dynamic strategy + Optimizer [Hypothesis Condition]

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
from dotenv import load_dotenv

load_dotenv()

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
from benchmarks.fixed_pipeline import build_react_pipeline_graph
from benchmarks.data.judge import judge_exact, judge_numeric, judge_rubric
from benchmarks.vanilla_baseline import VanillaToolBaseline
from metrics.graph_metrics import compute_graph_metrics

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_suite() -> list[dict]:
    suite = []
    # For Milestone Y we use established slices, but fallback to trivia/gsm8k if not present.
    files = ["gsm8k_slice.json", "hotpot_slice.json", "bbh_slice.json"]
    for fname in files:
        fpath = os.path.join(DATA_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f:
                suite.extend(json.load(f))
    
    if not suite:
        # fallback to older data if the new slices aren't created yet
        for fname in ["triviaqa_subset.json", "gsm8k_subset.json", "planning_curated.json"]:
            fpath = os.path.join(DATA_DIR, fname)
            if os.path.exists(fpath):
                with open(fpath, encoding="utf-8") as f:
                    suite.extend(json.load(f))
    return suite


def extract_answer(rps_report: dict) -> str:
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
            result = {"score": 0.5}
        return result["score"]
    else:  # exact
        result = judge_exact(answer, question["answer"], question.get("answer_aliases", []))
        return result["score"]


async def run_vanilla(question: dict) -> dict:
    baseline = VanillaToolBaseline()
    result = await baseline.execute(question["query"])
    score = await evaluate_answer(result["answer"], question)
    return {
        "score": score,
        "latency_ms": result["latency_ms"],
        "cost": result["cost"],
        "verification_rate": result["verification_rate"],
        "nodes": result["nodes"]
    }


async def run_react(question: dict, registry: dict) -> dict:
    graph = build_react_pipeline_graph(question["query"])
    context = ExecutionContext(objective=question["query"])
    executor = GraphExecutor(registry)
    t0 = time.monotonic()
    rps = await executor.execute(graph, context)
    latency_ms = int((time.monotonic() - t0) * 1000)
    answer = extract_answer(rps)
    score = await evaluate_answer(answer, question)
    metrics = compute_graph_metrics(graph)
    
    # Rough cost estimate
    cost = 0.002 * metrics["node_count"]
    
    return {
        "score": score, 
        "latency_ms": latency_ms,
        "cost": cost,
        "verification_rate": metrics["verification_density"],
        "nodes": metrics["node_count"]
    }


async def run_c3(question: dict, registry: dict) -> dict:
    analyzer = ProblemAnalyzer()
    spec = analyzer.analyze(question["query"])
    
    planner = ReasoningPlanner()
    strategy = planner.plan(spec)
    
    cost_est = estimate_cost(strategy)
    strategy.cost_estimate = cost_est.model_dump()

    compiler = Compiler()
    rir_graph = compiler.compile(strategy)

    optimizer = PassManager()
    graph, _ = optimizer.optimize(rir_graph)

    context = ExecutionContext(objective=question["query"])
    executor = GraphExecutor(registry)
    
    t0 = time.monotonic()
    rps = await executor.execute(graph, context)
    latency_ms = int((time.monotonic() - t0) * 1000)
    
    # Add LLM Planner overhead to latency and cost
    if is_live():
        latency_ms += 800  
        actual_cost = cost_est.estimated_token_cost + 0.001
    else:
        actual_cost = cost_est.estimated_token_cost
        
    answer = extract_answer(rps)
    score = await evaluate_answer(answer, question)
    metrics = compute_graph_metrics(graph)
    
    return {
        "score": score, 
        "latency_ms": latency_ms,
        "cost": actual_cost,
        "verification_rate": metrics["verification_density"],
        "nodes": metrics["node_count"],
        "problem_class": strategy.problem_class
    }


def aggregate(results: list[dict]) -> dict:
    n = len(results)
    if n == 0:
        return {}
    return {
        "accuracy": round(sum(r["score"] for r in results) / n, 4),
        "latency_ms": round(sum(r["latency_ms"] for r in results) / n),
        "cost": round(sum(r["cost"] for r in results) / n, 4),
        "verification_rate": round(sum(r["verification_rate"] for r in results) / n, 4),
        "nodes": round(sum(r["nodes"] for r in results) / n, 2),
        "n": n,
    }


def print_table(agg: dict[str, dict]):
    keys = ["accuracy", "cost", "latency_ms", "verification_rate", "nodes"]
    labels = ["Accuracy", "Cost ($)", "Latency (ms)", "Verification Rate", "Avg Nodes"]
    cols = ["A - Vanilla LLM", "B - Fixed (ReAct)", "C - Full C3"]
    col_w = 20

    print("\n" + "=" * 80)
    print("  C3 PARETO ABLATION STUDY RESULTS")
    print("=" * 80)
    print(f"{'Metric':<22}" + "".join(f"{c:<{col_w}}" for c in cols))
    print("-" * 80)
    for k, lbl in zip(keys, labels):
        row = f"{lbl:<22}"
        for c in cols:
            val = agg[c].get(k, "N/A")
            row += f"{str(val):<{col_w}}"
        print(row)
    print("=" * 80)

    if "C - Full C3" in agg and "A - Vanilla LLM" in agg:
        c3_acc = agg["C - Full C3"]["accuracy"]
        vanilla_acc = agg["A - Vanilla LLM"]["accuracy"]
        if c3_acc > vanilla_acc:
            print("\n  VERDICT: C3 dominates the Pareto frontier on Accuracy.")
        else:
            print("\n  VERDICT: C3 does not yet dominate Vanilla on Accuracy.")


async def main():
    suite = load_suite()
    registry = get_operator_registry()
    backend = get_backend()
    print(f"Backend: {backend.upper()} | {len(suite)} questions")
    print("Running 3 conditions...\n")

    all_results: dict[str, list[dict]] = {
        "A - Vanilla LLM": [],
        "B - Fixed (ReAct)": [],
        "C - Full C3": [],
    }

    for i, q in enumerate(suite):
        print(f"  [{i+1:02d}/{len(suite)}] {q['query'][:55]}...")
        try:
            a = await run_vanilla(q)
            b = await run_react(q, registry)
            c = await run_c3(q, registry)

            all_results["A - Vanilla LLM"].append(a)
            all_results["B - Fixed (ReAct)"].append(b)
            all_results["C - Full C3"].append(c)

            print(f"         A_acc:{a['score']:.2f}  B_acc:{b['score']:.2f}  C_acc:{c['score']:.2f}  [{c.get('problem_class','?')}]")
        except Exception as e:
            print(f"         ERROR: {e}")
            continue

    agg = {cond: aggregate(results) for cond, results in all_results.items()}
    print_table(agg)

    out_path = os.path.join(os.path.dirname(__file__), "ablation_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"backend": backend, "conditions": agg}, f, indent=2)
    print(f"\nFull results saved to: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
