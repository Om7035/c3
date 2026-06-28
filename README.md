# C³ (Cognitive Computation Compiler)

Current AI systems execute essentially one reasoning pipeline for every problem.

C³ introduces a different hypothesis:

> **Every problem deserves its own synthesized computation.**

Instead of forcing every task through one fixed reasoning workflow, C³ compiles each problem into a custom reasoning graph, executes that graph, verifies intermediate results, and produces an explainable answer.

The research question is simple:

> **Can dynamically synthesized reasoning programs outperform fixed reasoning pipelines?**

## Repository Layout

```text
C3/
|-- analyzer/       # Problem Analyzer
|-- planner/        # Reasoning Planner
|-- compiler/       # Reasoning Compiler
|-- rir/            # Reasoning Intermediate Representation (RIR)
|-- runtime/        # Reasoning Runtime
|-- operators/      # Primitive Operator Library (Knowledge, Reasoning, Execution, Verification)
|-- verification/   # Verification Layer
|-- visualization/  # Graph Visualization (Mermaid/JSON)
|-- benchmarks/     # Benchmark runner
|-- cli/            # Command Line Interface
|-- tests/          # Test suite
|-- CONTRIBUTING.md
|-- C3_SPEC.md      # Core Specification and RIR v1 Design
|-- ROADMAP.md
|-- LICENSE
`-- README.md
```

## Architecture Flow

C³ operates on a strict pipeline analogous to LLVM for reasoning:

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
Optimizer
  ↓
Reasoning Runtime
  ↓
Primitive Library
  ↓
Verification
  ↓
Reasoning Provenance Specification (RPS)
  ↓
Answer
```

## Milestones

See [ROADMAP.md](ROADMAP.md) and [C3_SPEC.md](C3_SPEC.md) for the guiding plan and system contract.
