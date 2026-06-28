# Reasoning Intermediate Representation (RIR) v1

## Philosophy
The RIR is to C³ what LLVM IR is to C++. It is the intermediate representation that decouples the synthesis of a computation from its execution. The RIR is a strict, JSON-serializable, deterministic graph description.

## Schema Architecture

An RIR document consists of the following top-level blocks:

### 1. Header
Contains metadata about the specific compilation instance.
- `version`: The RIR spec version (currently "1.0").
- `rir_id`: Unique UUID for this execution graph.
- `objective`: The natural language objective this graph is designed to solve.

### 2. Strategy
Captures the compiler's intent and execution constraints.
- `optimization_target`: (e.g., "accuracy", "latency", "cost").
- `fail_fast`: Boolean determining if the entire graph fails on a single node error.
- `max_cost_usd`: Float for financial boundary.
- `max_latency_ms`: Integer for timeout boundary.

### 3. Registers
Memory allocation for the graph. Unlike implicit variable passing, nodes read from and write to explicitly declared registers. This provides determinism, cacheability, and an easy surface for the Optimizer to perform static single-assignment (SSA) analysis.
- Array of register names (e.g., `["reg_search_results", "reg_final_answer"]`).

### 4. Nodes
The actual computations. Each node represents one Primitive execution.
- `id`: Unique identifier (e.g., `node_1`).
- `opcode`: Maps directly to the Primitive ISA (e.g., `KNOW.RETRIEVE`).
- `operands`: Input data, which can be literal constants or pointers to registers (denoted by a `$` prefix, e.g., `$reg_search_results`).
- `outputs`: List of registers to write the results into.
- `metadata`: Node-specific execution expectations (`expected_latency_ms`, `required_confidence`).

### 5. Edges
Defines the explicit directed acyclic graph (DAG) execution order.
- `source`: ID of the predecessor node.
- `target`: ID of the successor node.

### 6. Observability
Directives for the runtime on how to trace and export this execution.
- `trace_enabled`: Boolean.
- `log_level`: Verbosity.
- `export_visuals`: Formats to export (e.g., `["mermaid", "json"]`).

## Example Document
See the main implementation plan or `README.md` for a complete JSON example.
