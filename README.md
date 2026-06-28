# C3

C3, the Cognitive Computation Compiler, is a research prototype for compiling problems into reasoning graphs instead of forcing all tasks through one fixed pipeline.

## Vision

Instead of hard-coding one agent loop for every problem, C3 compiles a problem specification into a declarative reasoning graph, then executes that graph through a runtime and verification layer.

## Repository Layout

```text
C3/
|-- benchmarks/
|-- compiler/
|-- docs/
|-- examples/
|-- operators/
|-- planner/
|-- runtime/
|-- tests/
|-- CONTRIBUTING.md
|-- C3_SPEC.md
|-- Dockerfile
|-- LICENSE
|-- ROADMAP.md
`-- README.md
```

## Current Scope

This repository currently provides:

- repository structure and engineering documentation
- an initial intermediate representation specification
- interface contracts for compiler, runtime, operators, and verification
- development tooling for formatting, linting, typing, testing, and CI

## Phase Plan

- Phase 1: repository, docs, interfaces, IR, roadmap
- Phase 2: compiler skeleton
- Phase 3: runtime skeleton
- Phase 4: operator implementations
- Phase 5: evaluation framework

## Milestones

See [ROADMAP.md](E:\C³\ROADMAP.md) and [C3_SPEC.md](E:\C³\C3_SPEC.md) for the guiding plan and system contract.
