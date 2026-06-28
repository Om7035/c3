# C³ Specification

## Purpose

C³ is a reasoning compiler. It accepts a problem specification, plans a reasoning strategy, compiles that strategy into a declarative reasoning graph (RIR), optimizes it, and executes it through a runtime that records evidence, intermediate state, and verification results.

The core hypothesis is that **dynamically synthesized reasoning programs outperform fixed reasoning pipelines.**

## Core Design Rules

1. The compiler emits an intermediate representation (RIR), not imperative Python code.
2. Operators are independent execution primitives behind a stable async interface.
3. The runtime owns scheduling, state flow, observability, and failure handling.
4. Verification is a first-class phase, not an afterthought.
5. Components may evolve internally as long as they preserve interface contracts.

## Architectural Flow

```
Question
  ↓
Problem Analyzer
  ↓
Strategy Builder
  ↓
Reasoning Strategy (AST)
  ↓
Compiler
  ↓
Reasoning Intermediate Representation (RIR)
  ↓
Optimizer (e.g. Graph Optimization, redundant node removal)
  ↓
Reasoning Runtime
  ↓
Primitive Library
  ↓
Verification
  ↓
Reasoning Provenance Specification (RPS) / Execution Trace
  ↓
Answer
```

## Primitive Instruction Set Architecture (ISA)

Operators in C³ are structured as primitives with specific capabilities:

1. **Knowledge Primitives**: `Retrieve`, `Search`, `Memory`
2. **Reasoning Primitives**: `Infer`, `Summarize`, `Compare`, `Critique`
3. **Execution Primitives**: `Python`, `Shell`, `API`
4. **Verification Primitives**: `Verify`, `Vote`, `Confidence`

Each primitive implements a standard async interface and returns strongly-typed results, confidence scores, and execution metadata.

## Reasoning Intermediate Representation (RIR) v1

The RIR is the heart of the project (similar to LLVM IR). It defines exactly how a problem will be executed, verified, and traced.

```yaml
version: "1.0"

problem:
  id: "uuid"
  category: "analytical_reasoning"
  objective: "Determine the exact capacity of Wembley Stadium."

strategy:
  approach: "research_then_calculate"
  verification_level: "high"
  parallel_retrieval: true
  evidence_required: "external_sources"

execution:
  parallel: true
  timeout_ms: 30000
  max_retries: 3
  fail_fast: false

nodes:
  - id: "node_1_retrieve"
    primitive_type: "Knowledge"
    operator: "Search"
    inputs:
      query: "Wembley Stadium official capacity"
    outputs: ["search_results"]
    expected_latency_ms: 2000
    expected_cost: 0.001

  - id: "node_2_verify"
    primitive_type: "Verification"
    operator: "CrossCheck"
    inputs:
      data: "$node_1_retrieve.search_results"
    outputs: ["verified_facts"]
    confidence_threshold: 0.9

edges:
  - source: "node_1_retrieve"
    target: "node_2_verify"

observability:
  trace_enabled: true
  log_level: "DEBUG"
  export_visuals: ["mermaid", "json"]
```

## Success Criteria

- Compile different problem classes into different graphs
- Execute graphs deterministically in a testable reasoning runtime
- Verify intermediate claims and final outputs
- Measure the value of adaptive compilation against fixed pipelines
