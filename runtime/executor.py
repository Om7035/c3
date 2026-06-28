from __future__ import annotations

import time
import datetime
import networkx as nx
from typing import Any

from rir.graph import ReasoningGraph
from core.context import ExecutionContext
from operators.interfaces import Operator


class GraphExecutor:
    def __init__(self, registry: dict[str, Operator]):
        self.registry = registry

    def _resolve_operand(self, val: Any, context: ExecutionContext) -> Any:
        if isinstance(val, str) and val.startswith("$"):
            reg_name = val[1:]
            return context.register_bank.get(reg_name)
        return val

    def _resolve_operands(self, operands: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        resolved = {}
        for k, v in operands.items():
            if isinstance(v, dict):
                resolved[k] = self._resolve_operands(v, context)
            elif isinstance(v, list):
                resolved[k] = [self._resolve_operand(item, context) for item in v]
            else:
                resolved[k] = self._resolve_operand(v, context)
        return resolved

    async def execute(self, graph: ReasoningGraph, context: ExecutionContext) -> dict[str, Any]:
        global_start_time = time.time()
        global_start_dt = datetime.datetime.now(datetime.timezone.utc).isoformat()

        dag = nx.DiGraph()
        for node in graph.nodes:
            dag.add_node(node.id, data=node)

        for edge in graph.edges:
            dag.add_edge(edge.source, edge.target)

        if not nx.is_directed_acyclic_graph(dag):
            raise ValueError("Graph is not a DAG")

        order = list(nx.topological_sort(dag))

        for node_id in order:
            node = dag.nodes[node_id]["data"]
            operator = self.registry.get(node.opcode)
            if not operator:
                raise ValueError(f"Operator {node.opcode} not found in registry")

            # Resolve operands from registers
            inputs = self._resolve_operands(node.operands, context)
            
            node_start_time = time.time()
            node_start_dt = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            # Execute primitive
            result = await operator.execute(inputs, context)
            
            node_end_time = time.time()
            node_end_dt = datetime.datetime.now(datetime.timezone.utc).isoformat()

            if not result.success:
                context.add_provenance_event({
                    "node_id": node.id,
                    "opcode": node.opcode,
                    "start_time": node_start_dt,
                    "end_time": node_end_dt,
                    "latency_ms": int((node_end_time - node_start_time) * 1000),
                    "registers_read": {k: v for k, v in inputs.items()},
                    "registers_written": {},
                    "confidence": 0.0,
                    "error": result.error
                })
                raise RuntimeError(f"Operator {node_id} failed: {result.error}")

            # Write outputs to registers
            written_regs = {}
            if node.outputs:
                primary_out_reg = node.outputs[0]
                context.register_bank.set(primary_out_reg, result.data)
                written_regs[primary_out_reg] = result.data

            # Emit RPS Provenance Event
            context.add_provenance_event({
                "node_id": node.id,
                "opcode": node.opcode,
                "start_time": node_start_dt,
                "end_time": node_end_dt,
                "latency_ms": int((node_end_time - node_start_time) * 1000),
                "registers_read": {k: v for k, v in inputs.items()},
                "registers_written": written_regs,
                "confidence": getattr(result, "confidence", 1.0),
                "error": None
            })

        global_end_time = time.time()
        global_end_dt = datetime.datetime.now(datetime.timezone.utc).isoformat()

        rps_report = {
            "version": "1.0",
            "graph_id": graph.header.get("rir_id"),
            "execution": {
                "start_time": global_start_dt,
                "end_time": global_end_dt,
                "total_latency_ms": int((global_end_time - global_start_time) * 1000),
                "success": True
            },
            "registers_final_state": context.register_bank.registers,
            "provenance_events": context.provenance_events
        }

        return rps_report
