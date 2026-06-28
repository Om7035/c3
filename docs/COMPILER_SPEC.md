# Compiler Specification

## Philosophy
The C³ Compiler is responsible for translating a natural language query into a strict, deterministic RIR graph. It **does not execute logic**; it is purely a code generator.

## Phase 1: Problem Analysis (Front-End)
- **Input**: Raw natural language query string.
- **Process**: Lexical and semantic analysis. Identifies the problem category, constraints, uncertainty levels, and the requisite Primitive Types needed to solve it.
- **Output**: `ProblemSpecification` object.

## Phase 2: Reasoning Strategy (Mid-End)
- **Input**: `ProblemSpecification`.
- **Process**: Determines the macro-architecture of the computation. Decides if the problem requires a sequential pipeline, a branching DAG, or heavy verification.
- **Output**: `ReasoningStrategy` object.

## Phase 3: IR Emission (Back-End)
- **Input**: `ReasoningStrategy` + `ProblemSpecification`.
- **Process**: 
  1. Instantiates the explicit DAG structure.
  2. Allocates `Registers` for intermediate states.
  3. Assigns `Opcodes` (from the Primitive ISA) to nodes.
  4. Wires the `Edges` representing control and data flow.
  5. Assigns execution `Metadata` (cost/latency).
- **Output**: Validated `Reasoning Intermediate Representation (RIR)` document.

## Compiler Contract
- The Compiler MUST be deterministic (or semi-deterministic if relying on an LLM) in generating graphs for the same Strategy.
- The Compiler MUST output a valid RIR schema.
- The Compiler MUST NOT make network calls to fetch data or execute arbitrary code to generate the IR (except to its own LLM backend for synthesis).
