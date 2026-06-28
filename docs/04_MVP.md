# 04 MVP

## Objective

Deliver a minimal but real system that compiles different classes of problems into different reasoning graphs and executes them end to end.

## MVP Scope

- formal `ProblemSpec`
- formal `ReasoningGraph` IR
- classifier with simple heuristic labeling
- compiler with rule-based graph generation
- runtime with dependency-aware execution
- verification operator and verification result model
- initial operator set: retrieve, python, search, reason, verify, memory
- FastAPI endpoint to compile and execute problems

## Acceptance Criteria

- a factual question compiles into a retrieval-oriented graph
- a design-oriented request compiles into a synthesis-oriented graph
- graphs can be serialized to and from JSON
- runtime execution is testable without external services
- examples and benchmarks show baseline behavior

## Explicit Deferrals

- learned compilation
- distributed execution
- external vector stores
- production-grade sandboxing
- large-scale operator marketplace
