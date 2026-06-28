import asyncio
import sys
import os

# Add root to pythonpath for simple script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.analyzer import ProblemAnalyzer
from planner.planner import ReasoningPlanner
from compiler.compiler import Compiler
from runtime.executor import GraphExecutor
from operators.library import get_operator_registry
from core.context import ExecutionContext
from verification.report import VerificationEngine
from visualization.exporter import GraphVisualizer

async def run_pipeline(query: str):
    print(f"--- Running C3 Pipeline for: '{query}' ---")
    
    analyzer = ProblemAnalyzer()
    spec = analyzer.analyze(query)
    print(f"[Analyzer] Task Type: {spec.task_type.value}")
    
    planner = ReasoningPlanner()
    plan = planner.plan(spec)
    print(f"[Planner] Generated plan with operators: {plan.operators}")
    
    compiler = Compiler()
    graph = compiler.compile(plan)
    print(f"[Compiler] Compiled RIR Graph with {len(graph.nodes)} nodes")
    
    executor = GraphExecutor(get_operator_registry())
    context = ExecutionContext(query=query)
    
    results = await executor.execute(graph, context)
    print(f"[Runtime] Execution completed.")
    
    verifier = VerificationEngine()
    report = verifier.generate_report(graph, results, context.trace_logs)
    print(f"[Verification] Report generated, success: {report.success}")
    
    visualizer = GraphVisualizer()
    mermaid = visualizer.to_mermaid(graph)
    print("\n--- Reasoning Graph (Mermaid) ---")
    print(mermaid)
    print("---------------------------------\n")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "How many people fit inside Wembley Stadium?"
    asyncio.run(run_pipeline(query))
