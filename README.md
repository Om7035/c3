<div align="center">

# C³: Cognitive Computation Compiler

**Typed, Verifiable, Per-Query Reasoning Programs with Full Provenance.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status: Research](https://img.shields.io/badge/Status-Research_Prototype-blue.svg)]()
[![Model Support](https://img.shields.io/badge/Supported_Models-Groq_%7C_OpenAI_%7C_Gemini-purple.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

<p align="center">
  <a href="#-the-core-hypothesis">Hypothesis</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quickstart">Quickstart</a> •
  <a href="#-benchmarks">Benchmarks</a> •
  <a href="#-documentation">Documentation</a>
</p>

</div>

---

## The Core Hypothesis

Current AI architectures (RAG, ReAct, custom LangChain/CrewAI flows) deploy **fixed reasoning workflows**. Whether relying on heuristic search (ADAS, AFlow) or fixed agent loops, the computational structure remains static for every problem.

**C³ operates on a fundamentally different paradigm:**
> Every problem deserves its own dynamically synthesized, typed computation.

Instead of routing natural language through a static inference pipeline, C³ acts as a compiler for Large Language Models. It lowers natural language into a **Reasoning Intermediate Representation (RIR)**—a strictly typed, register-based Directed Acyclic Graph (DAG)—which is optimized and executed by a deterministic virtual machine. 

The output is not just an answer, but a **Reasoning Provenance Specification (RPS)**: a fully auditable trace of every logical step, retrieval, execution, and validation.

---

## Architecture

C³ is heavily inspired by classical compiler design (like LLVM), strictly separating planning (Front-End) from execution (Back-End).

<div align="center">
  <img src="https://raw.githubusercontent.com/Om7035/c3/main/docs/assets/c3_beautiful_architecture.svg" alt="C3 Compiler Architecture" width="900"/>
</div>

### Why Types Matter in Reasoning
By enforcing strict typing via RIR, C³ unlocks capabilities impossible in standard agent frameworks:
1. **Safety:** Invalid execution plans are rejected mathematically *before* running.
2. **Optimization:** Pass managers can execute dead-node elimination, verification fusion, and register lifetime analysis.
3. **Auditable Provenance:** Every claim is gated by the `VERI.VERIFY` primitive, shifting the system from "self-reported confidence" to cryptographic-style trust.

---

## Quickstart

Experience the dynamic compilation of reasoning programs in real-time through the Web Observatory UI.

### 1. Installation

```bash
git clone https://github.com/yourusername/C3.git
cd C3
pip install fastapi uvicorn httpx pydantic networkx openai python-dotenv tenacity
```

### 2. Configuration

Create a `.env` file in the project root. We recommend **Groq** for lightning-fast, free inference, but OpenAI or Gemini will also work.

```env
# Example using Groq (Recommended for speed and generous free tiers)
OPENAI_API_KEY="gsk_your_groq_api_key_here"
OPENAI_BASE_URL="https://api.groq.com/openai/v1"
C3_LLM_MODEL="llama-3.1-70b-versatile"

# Optional: For optimized web search primitives
TAVILY_API_KEY="tvly-your_tavily_key"

# Required flag
C3_BACKEND="live"
```

### 3. Run the Observatory

```bash
# Start the API server
uvicorn api.server:app --port 8000

# Open the UI
start ui/index.html   # On Windows
open ui/index.html    # On Mac
```

---

## Benchmarks & Ablation

To prove the scientific hypothesis, C³ evaluates against the **Cost-Accuracy Pareto Frontier**. The framework includes an ablation suite testing three modes across heterogeneous datasets (GSM8K, HotpotQA, BBH):

1. **Vanilla LLM + Tools:** A standard frontier model given raw tool access.
2. **Fixed ReAct:** A static `Retrieve -> Python -> Verify -> Infer` loop.
3. **Full C³:** Per-query synthesized IR with full runtime optimization.

**Run the ablation study yourself:**
```bash
python benchmarks/ablation.py
```
*Outputs a full Pareto matrix comparing Token Cost, Latency, Accuracy, and Verification Rate.*

---

## Documentation

Dive deeper into the theory and specification of C³:

- **[Research Paper: Formal Semantics](paper/paper.md)**
- **[C³ Specification & RIR Design](docs/C3_SPEC.md)**
- **[Primitive Instruction Set Architecture (ISA)](docs/PRIMITIVE_ISA.md)**
- **[Reasoning Provenance Specification (RPS)](docs/RPS_SPEC.md)**

---

<div align="center">
  <i>Built for the future of verifiable artificial intelligence.</i>
</div>
