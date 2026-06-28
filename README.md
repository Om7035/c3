<div align="center">
  <img src="docs/assets/c3_architecture.png" alt="C3 Architecture" width="800"/>
</div>

# C³: Cognitive Computation Compiler

<div align="center">
  <em>Typed, Verifiable, Per-Query Reasoning Programs with Full Provenance.</em>
</div>

<br/>

[![Status](https://img.shields.io/badge/Status-Research_Prototype-blue.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Model](https://img.shields.io/badge/Supported_Models-Groq_%7C_OpenAI_%7C_Gemini-purple.svg)]()

## 🧠 The Problem: Fixed Workflows Don't Generalize

Current AI systems execute essentially one static reasoning pipeline for every problem. Whether you use a prompt-and-generate loop, a Retrieval-Augmented Generation (RAG) system, or a fixed ReAct agent workflow, the structure of the computation remains identical regardless of the task's actual requirements.

Recent approaches (ADAS, AFlow) try to optimize this by searching for better workflows offline—but they still deploy a **frozen** pipeline per task. 

C³ operates on a different hypothesis: **Every problem deserves its own synthesized computation.** 

Instead of routing every query through a fixed inference pipeline, C³ acts as a compiler for Large Language Models. It dynamically synthesizes a strictly typed **Reasoning Intermediate Representation (RIR)** tailored to the specific query, ensuring that every reasoning trace is verifiable and auditable.

## 🚀 Key Differentiators

Why use C³ instead of just writing a Python script with an LLM call?

1. **Per-Query Synthesis:** We don't use fixed workflows. The LLM Planner synthesizes a custom Abstract Syntax Tree (AST) for *each individual query*.
2. **Typed & Verifiable (RIR):** The AST is lowered into a register-based Directed Acyclic Graph (DAG). Types are enforced. Execution is deterministic.
3. **First-Class Verification:** Claims are gated by a `VERI.VERIFY` primitive. We don't trust self-reported confidence from a generation node; we mathematically prove trust through retrieved evidence.
4. **Full Provenance (RPS):** The primary output isn't just an "answer"—it's a Reasoning Provenance Specification (RPS). You get a complete, auditable trace of the knowledge flow, intermediate states, and calibrated confidence at every node.

## 🏗️ Architecture

C³ follows a strict pipeline analogous to LLVM, designed for natural language reasoning:

1. **LLM Planner (Front-End):** A constrained LLM strictly outputs a JSON-schema `ReasoningStrategy` AST.
2. **Compiler (Middle-End):** Lowers the AST into the **Reasoning Intermediate Representation (RIR)**.
3. **Pass Manager (Optimization):** Fuses redundant steps, prunes dead execution paths, and optimizes the graph before execution.
4. **Reasoning Runtime (Back-End):** A virtual machine that executes the RIR graph, handling dependencies, timeouts, and register state across our **Primitive ISA** (`KNOW.RETRIEVE`, `EXEC.PYTHON`, `VERI.VERIFY`, `REAS.INFER`).

## ⚡ Quick Start (Live API & Web Observatory)

C³ comes with a live Web Observatory UI to visualize the dynamic compilation and execution of reasoning programs in real-time.

```bash
# 1. Install dependencies
pip install fastapi uvicorn httpx pydantic networkx openai python-dotenv tenacity

# 2. Configure your environment (.env)
# We highly recommend Groq for fast, free inference
OPENAI_API_KEY="gsk_your_groq_key"
OPENAI_BASE_URL="https://api.groq.com/openai/v1"
C3_LLM_MODEL="llama-3.1-70b-versatile"
TAVILY_API_KEY="tvly-your_tavily_key" # Optional for search
C3_BACKEND="live"

# 3. Start the API server
uvicorn api.server:app --port 8000

# 4. Open the UI in your browser
start ui/index.html
```

## 📊 Scientific Validation & Benchmarks

C³ is built for rigorous evaluation on the **Cost-Accuracy Pareto Frontier**. We provide an ablation harness that pits C³ against a Vanilla Tool-Enabled LLM and a Fixed ReAct loop. 

To run the ablation suite over our diverse benchmark dataset (GSM8K, HotpotQA, BBH):

```bash
python benchmarks/ablation.py
```

*This script produces a Pareto metrics table analyzing Empirical Accuracy, Token Cost ($), Latency (ms), and Verification Rate.*

## 🔮 The Future: Learning Compiler

The complete Reasoning Provenance Specification (RPS) generated from every run serves as training data. The next stage of C³ is the **Learning Compiler**, an LLM-guided planner that uses historical RPS execution logs to empirically improve its own synthesis logic.

---

### 📖 Documentation
- **[Formal Semantics & Research Paper](paper/paper.md)**
- **[C³ Specification & RIR Design](docs/C3_SPEC.md)**
- **[Primitive Instruction Set Architecture (ISA)](docs/PRIMITIVE_ISA.md)**
- **[Reasoning Provenance Specification (RPS)](docs/RPS_SPEC.md)**
