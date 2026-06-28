# C3 Specification

## Purpose

C³ is a reasoning compiler. It accepts a problem specification, compiles that problem into a declarative reasoning graph, and executes the graph through a runtime that records evidence, intermediate state, and verification results.

## Core Design Rules

1. The compiler emits an intermediate representation, not imperative Python code.
2. Operators are independent execution units behind a stable async interface.
3. The runtime owns scheduling, state flow, observability, and failure handling.
4. Verification is a first-class phase, not an afterthought.
5. Components may evolve internally as long as they preserve interface contracts.

## Architectural Components

- Problem Specification Engine
- Epistemic Classifier
- Reasoning Compiler
- Execution Runtime
- Verification Engine
- Response Generator

## Intermediate Representation

The core IR is a reasoning graph.

```yaml
problem_type: factual_lookup
operators:
  - id: retrieve_1
    kind: retrieve
  - id: verify_1
    kind: verify
  - id: answer_1
    kind: reason
edges:
  - from: retrieve_1
    to: verify_1
  - from: verify_1
    to: answer_1
```

## Interface Contracts

### Operator

Each operator must implement:

- a stable `kind`
- an async `execute(context)` method
- explicit structured output

### Compiler

Each compiler must implement:

- `compile(problem)` returning a reasoning graph

### Runtime

Each runtime must implement:

- `execute(graph, context)` returning a structured execution result

## Non-Goals for V1

- a general-purpose agent framework
- complex autonomous planning without observability
- large operator libraries before strong operator quality

## Success Criteria

- compile different problem classes into different graphs
- execute graphs deterministically in a testable runtime
- verify intermediate claims and final outputs
- measure the value of adaptive compilation against fixed pipelines
