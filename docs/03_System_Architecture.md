# 03 System Architecture

## Top-Level Flow

```text
Problem Specification Engine
  -> Epistemic Classifier
  -> Reasoning Compiler
  -> Execution Runtime
  -> Verification Engine
  -> Response Generator
```

## Component Responsibilities

### Problem Specification Engine

Normalizes raw user input into a structured `ProblemSpec` containing text, metadata, constraints, and optional execution hints.

### Epistemic Classifier

Estimates what kind of knowledge work is required. Example dimensions include factual lookup, multi-step reasoning, design synthesis, code execution, and verification intensity.

### Reasoning Compiler

Transforms a `ProblemSpec` into a `ReasoningGraph` IR. This is the architectural heart of C³.

### Execution Runtime

Schedules graph nodes, resolves dependencies, executes operators, and stores results in a shared execution context.

### Verification Engine

Evaluates intermediate outputs and final claims. Verification may be embedded as graph nodes and also enforced as a runtime policy.

### Response Generator

Builds the final user-facing answer from graph outputs, traces, and verification results.

## Architectural Boundaries

- the compiler chooses graph structure
- operators implement atomic capabilities
- the runtime executes graphs but does not invent them
- the verifier checks claims but does not replace compilation logic

## V1 Implementation Strategy

Start with in-process Python components, an async runtime, and a small operator registry. Treat the graph IR as the primary contract between compiler and runtime.
