"""
C³ Observatory API Server

Exposes a streaming SSE endpoint that runs the full compiler pipeline
and pushes each stage as a discrete event to the browser.

Run with:
    uvicorn api.server:app --reload --port 8000
"""
from __future__ import annotations

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from analyzer.analyzer import ProblemAnalyzer
from planner.planner import ReasoningPlanner
from planner.cost_model import estimate_cost
from compiler.compiler import Compiler
from compiler.validator import StrategyValidator
from optimizer.optimizer import PassManager
from runtime.executor import GraphExecutor
from operators.library import get_operator_registry
from core.context import ExecutionContext
from metrics.graph_metrics import compute_graph_metrics
from metrics.ere import compute_reasoning_efficiency, compute_mean_confidence
from visualization.exporter import GraphVisualizer

app = FastAPI(title="C³ Observatory API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_registry = get_operator_registry()
_visualizer = GraphVisualizer()


class CompileRequest(BaseModel):
    query: str


def _sse(event: str, data: dict) -> str:
    """Format a Server-Sent Event frame."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def pipeline_stream(query: str):
    """
    Runs the full C³ pipeline stage-by-stage and yields SSE frames
    so the browser can animate each step in real time.
    """
    try:
        # Stage 1: Analysis
        yield _sse("stage_start", {"stage": "analyzer", "label": "Problem Analyzer"})
        await asyncio.sleep(0.05)
        analyzer = ProblemAnalyzer()
        spec = analyzer.analyze(query)
        yield _sse("analyzer_done", {
            "problem_class": spec.task_type.value,
            "complexity": spec.complexity,
            "metadata": spec.metadata,
        })

        # Stage 2: Strategy Planning
        yield _sse("stage_start", {"stage": "planner", "label": "Strategy Builder"})
        await asyncio.sleep(0.05)
        planner = ReasoningPlanner()
        strategy = planner.plan(spec)
        cost = estimate_cost(strategy)
        strategy.cost_estimate = cost.model_dump()
        yield _sse("strategy_done", {
            "strategy": strategy.model_dump(),
            "cost_estimate": cost.model_dump(),
        })

        # Stage 3: Validation
        yield _sse("stage_start", {"stage": "validator", "label": "Strategy Validator"})
        await asyncio.sleep(0.05)
        validator = StrategyValidator()
        validation = validator.validate(strategy)
        yield _sse("validation_done", {
            "valid": validation.valid,
            "diagnostics": validation.as_dict(),
        })

        if not validation.valid:
            yield _sse("pipeline_error", {
                "stage": "validator",
                "message": "Strategy validation failed",
                "errors": [d.__dict__ for d in validation.errors],
            })
            return

        # Stage 4: Compilation
        yield _sse("stage_start", {"stage": "compiler", "label": "Compiler (RIR Synthesis)"})
        await asyncio.sleep(0.05)
        compiler = Compiler()
        rir_graph = compiler.compile(strategy)
        mermaid_dag = _visualizer.to_mermaid_dag(rir_graph)
        yield _sse("compiler_done", {
            "node_count": len(rir_graph.nodes),
            "edge_count": len(rir_graph.edges),
            "registers": rir_graph.registers,
            "nodes": [{"id": n.id, "opcode": n.opcode, "outputs": n.outputs} for n in rir_graph.nodes],
            "edges": [{"source": e.source, "target": e.target} for e in rir_graph.edges],
            "mermaid_dag": mermaid_dag,
        })

        # Stage 5: Optimization
        yield _sse("stage_start", {"stage": "optimizer", "label": "Pass Manager (Optimization)"})
        await asyncio.sleep(0.05)
        optimizer = PassManager()
        optimized_graph, opt_diagnostics = optimizer.optimize(rir_graph)
        yield _sse("optimizer_done", {
            "node_count_after": len(optimized_graph.nodes),
            "diagnostics": opt_diagnostics,
        })

        # Stage 6: Runtime Execution (node by node via SSE)
        yield _sse("stage_start", {"stage": "runtime", "label": "Reasoning Runtime"})
        await asyncio.sleep(0.05)

        # We stream node-by-node by executing through a custom callback
        context = ExecutionContext(objective=query)
        executor = GraphExecutor(_registry)

        # Run execution — yields per-node events by intercepting context
        rps_report = await executor.execute(optimized_graph, context)

        # Emit per-node provenance events
        for event in rps_report.get("provenance_events", []):
            yield _sse("node_executed", event)
            await asyncio.sleep(0.08)  # Small delay for animation effect

        yield _sse("runtime_done", {
            "total_latency_ms": rps_report["execution"]["total_latency_ms"],
            "registers_final_state": rps_report["registers_final_state"],
        })

        # Stage 7: Metrics & RPS
        yield _sse("stage_start", {"stage": "metrics", "label": "Reasoning Provenance (RPS)"})
        await asyncio.sleep(0.05)

        graph_metrics = compute_graph_metrics(optimized_graph)
        mean_conf = compute_mean_confidence(rps_report)
        re = compute_reasoning_efficiency(
            node_count=graph_metrics["node_count"],
            confidence=mean_conf,
            estimated_latency_ms=cost.estimated_latency_ms,
            estimated_token_cost=cost.estimated_token_cost,
            verification_density=graph_metrics["verification_density"],
        )
        mermaid_gantt = _visualizer.to_mermaid_gantt(rps_report)

        yield _sse("metrics_done", {
            "graph_metrics": graph_metrics,
            "reasoning_efficiency": re,
            "rps_summary": {
                "graph_id": rps_report["graph_id"],
                "provenance_event_count": len(rps_report["provenance_events"]),
                "success": rps_report["execution"]["success"],
            },
            "mermaid_gantt": mermaid_gantt,
        })

        yield _sse("pipeline_complete", {
            "message": "Compilation and execution complete.",
            "problem_class": strategy.problem_class,
            "re_score": re["re_score"],
        })

    except Exception as e:
        yield _sse("pipeline_error", {"stage": "unknown", "message": str(e)})


@app.post("/compile")
async def compile_query(req: CompileRequest):
    return StreamingResponse(
        pipeline_stream(req.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "C3 Observatory API"}
