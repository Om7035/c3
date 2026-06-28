import asyncio
import sys
import os
import json

# Add root to pythonpath for simple script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer.analyzer import ProblemAnalyzer
from planner.planner import ReasoningPlanner
from compiler.compiler import Compiler
from optimizer.optimizer import GraphOptimizer
from runtime.executor import GraphExecutor
from operators.library import get_operator_registry
from core.context import ExecutionContext
from visualization.exporter import GraphVisualizer

async def run_pipeline(query: str):
    print(f"--- Running C3 Pipeline for: '{query}' ---")
    
    # 1. Front-End: Problem Analysis & Strategy Planning
    analyzer = ProblemAnalyzer()
    spec = analyzer.analyze(query)
    print(f"\n[Analyzer] Task Type: {spec.task_type.value}")
    
    planner = ReasoningPlanner()
    strategy = planner.plan(spec)
    print("\n--- Strategy AST ---")
    print(strategy.model_dump_json(indent=2))
    
    # 2. Middle-End: Compilation & Optimization
    compiler = Compiler()
    rir_graph = compiler.compile(strategy)
    print(f"\n[Compiler] Lowered Strategy into RIR Graph with {len(rir_graph.nodes)} nodes")
    
    optimizer = GraphOptimizer()
    optimized_graph = optimizer.optimize(rir_graph)
    
    # 3. Back-End: Execution & Provenance
    executor = GraphExecutor(get_operator_registry())
    context = ExecutionContext(objective=query)
    
    print(f"\n[Runtime] Beginning Execution...")
    rps_report = await executor.execute(optimized_graph, context)
    print(f"[Runtime] Execution completed in {rps_report['execution']['total_latency_ms']}ms.")
    
    visualizer = GraphVisualizer()
    dag_mermaid = visualizer.to_mermaid_dag(optimized_graph)
    gantt_mermaid = visualizer.to_mermaid_gantt(rps_report)
    
    print("\n--- RIR DAG (Mermaid) ---")
    print(dag_mermaid)
    
    print("\n--- Reasoning Provenance Timeline (Mermaid Gantt) ---")
    print(gantt_mermaid)
    
    print("\n--- Reasoning Provenance Specification (RPS JSON) ---")
    print(json.dumps(rps_report, indent=2))
    print("---------------------------------\n")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "How many people fit inside Wembley Stadium?"
    asyncio.run(run_pipeline(query))
