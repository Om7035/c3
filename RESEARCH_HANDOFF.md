# C³ Research Handoff — Context & Honest Assessment

**Purpose of this document:** A self-contained brief for handing off to another researcher, model (e.g. DeepSeek), or collaborator to get help improving the methodology and finding a better path forward. It includes the project description, what we actually measured, and an unvarnished list of the flaws in the current evaluation.

---

## 1. What C³ Is

C³ (Cognitive Computation Compiler) treats an LLM as a compiler front-end instead of an end-to-end answer generator. Pipeline:

```
NL Question → Adaptive Gate (compile: bool) →
  [false] → single Vanilla LLM call → answer
  [true]  → LLM Planner → Reasoning Strategy (AST) → Compiler → RIR (typed DAG)
            → Pass Manager (optimizer) → Runtime VM (executes typed primitives:
              KNOW.RETRIEVE, EXEC.PYTHON, VERI.VERIFY, REAS.INFER, REAS.SUMMARIZE)
            → Reasoning Provenance Specification (RPS, full audit trace)
```

The pitch: most agentic frameworks either (a) always run a fixed pipeline (ReAct-style — retrieve, code, verify, infer, every time, regardless of whether the question needs any of that) or (b) just call the LLM directly with tools and hope. C³'s claimed novelty is the **Adaptive Gate**: a per-query decision about whether the question is even worth compiling into a verified multi-step graph, versus just asking the LLM directly.

Code layout: `analyzer/` (gate + problem classification), `planner/` (LLM → AST), `compiler/` (AST → RIR), `optimizer/` (RIR passes), `runtime/` (executes RIR via `operators/live/*`), `benchmarks/` (eval harness + data), `paper/paper.md` (write-up).

## 2. What We Actually Measured

**Suite:** 40 hand-written questions: 17 GSM8K-*style* arithmetic, 12 HotpotQA-*style* multi-hop trivia, 11 BBH-*style* logic puzzles. **Not the real GSM8K/HotpotQA/BBH test sets** — small, hand-authored, inspired-by versions.

**Backend:** `llama-3.1-8b-instant` via Groq (free tier), single model, no cross-model validation.

**4 conditions:**
- A — Vanilla: one LLM call, no scaffolding
- B — Fixed (ReAct): unconditional `RETRIEVE → PYTHON → VERIFY → INFER` pipeline regardless of question type
- C — Full C³: Adaptive Gate decides compile vs vanilla per question
- D — C³ no-gate: same compiler/runtime as C, but gate forced to always compile

**Results (n=40):**

| | Accuracy | Cost ($) | Latency (ms) | Verification Rate |
|---|---|---|---|---|
| A — Vanilla | 1.00 | 0.0005 | 1184 | 0.00 |
| B — Fixed ReAct | 0.60 | 0.0052 | 6604 | 0.1625 |
| C — Full C³ (gated) | 1.00 | 0.0017 | 2938 | 0.0791 |
| D — C³ (no gate) | 0.725 | 0.0044 | 6719 | 0.2499 |

**The one result with real signal:** C vs D (identical compiler/runtime, gate on vs off) — gate-on is 27.5 accuracy points higher and 2.6x cheaper than gate-off. This shows that *selectively skipping* the compiler for easy questions is better than *always* compiling, holding the compiler itself fixed.

## 3. Honest Problems With This (read before sending anywhere)

1. **Circular/leaked evaluation.** The gate's keyword markers (`" in which"`, `" that released"`, `" country where"`, `" band that"`, etc., in `analyzer/gate.py`) were written by looking at the phrasing of the actual 12 HotpotQA-style test questions. The gate is being scored on the exact data it was hand-tuned against. This invalidates the gate's apparent "intelligence" — it's closer to a lookup table than a generalizing classifier. **This must be disclosed or fixed before any external review.**

2. **Vanilla never loses.** Across every run, condition A (plain LLM, no scaffolding) scores 1.0 accuracy. That means the suite contains zero questions hard enough to make a single un-augmented LLM call fail. A benchmark where the simplest baseline already gets a perfect score cannot demonstrate that a more complex system is *more accurate* — at best it can show parity. C³ has never once beaten Vanilla on accuracy in any run; it has only matched it.

3. **The ReAct baseline is arguably a strawman.** It's *forced* through retrieve→code→verify→infer even on pure arithmetic questions, where it predictably fails by trying to web-search an answer instead of computing it. That's a real failure mode worth reporting, but presenting it as "the standard ReAct baseline" overstates how representative this is of good agentic engineering — a competent ReAct implementation would also have some routing/tool-selection logic.

4. **n=40, hand-authored, single model, no confidence intervals.** Not statistically powered. Effect sizes (27.5 points) are large enough to *see* at this n but not large enough to *trust* without more data, especially given flaw #1.

5. **No demonstrated upside over Vanilla, ever.** The actual marginal value proposition that survives scrutiny is narrower than the paper's current framing: *"C³ provides verification provenance that Vanilla structurally cannot, at ~3x Vanilla's cost, without the accuracy collapse a naive always-on pipeline suffers."* That's a real, modest claim. It is not "C³ improves accuracy" — it doesn't, anywhere in the data we have.

6. **The "regret logging" instrumentation we tried to add never produced data** — the live async benchmark run kept hanging/dying in this environment before completion. We don't have an empirical regret rate for the heuristic gate. (Given flaw #1, that number would be misleading anyway until the leak is fixed.)

## 4. What Needs To Happen Before This Is a Real Result

In priority order:

1. **Fix the evaluation leak.** Split into a dev set (used to write/tune the gate's heuristics or train a learned gate) and a disjoint held-out test set (used only for final reported numbers). Currently there is no such split — same 40 questions were used to both design and evaluate the gate.

2. **Use real benchmark data, not hand-authored look-alikes.** Pull actual GSM8K test split (1319 examples), real HotpotQA dev set, real BBH tasks. Even a random 100-200 sample of each, properly held out from gate design, would be far more credible than 40 hand-written questions.

3. **Find or construct questions Vanilla actually gets wrong.** Without that, there is no headroom to show C³ adding accuracy — only headroom to show it adding verification at a cost premium. Harder multi-hop chains (3+ hops), trickier arithmetic (multi-step word problems with distractor numbers), or adversarial phrasing would create that headroom.

4. **Replace or supplement the keyword gate with a learned classifier**, trained on dev-set "regret" (cases where the empirically optimal routing — derived by comparing a vanilla-only run vs a compile-only run on the same question — disagreed with the heuristic's choice). This is the legitimate version of what we attempted; it needs to run to completion on a dev/test split, not the same 40 questions.

5. **Fix the ReAct baseline** to include at least minimal task-type routing (e.g. skip retrieval for pure arithmetic) so the comparison isn't a strawman.

6. **Scale n and add statistical reporting** — bootstrap confidence intervals or exact binomial CIs on accuracy, paired significance tests between conditions C and D and between C and A.

7. **Cross-model validation** — rerun on at least one more backend (different model family/size) to check the gate's heuristic (or learned variant) isn't overfit to this model's specific failure modes.

## 5. Questions To Hand To DeepSeek / Another Researcher

- Given the circular-evaluation problem in §3.1, what's the cleanest way to retrofit a proper dev/test split onto an adaptive-routing gate that was originally tuned on the full eval set? (Re-author the heuristic from scratch using only a dev subset? Or move straight to a learned gate trained on dev-set regret labels?)
- Is there existing literature on **learned vs heuristic gating for compute-adaptive LLM pipelines** (model cascades, routing, speculative decoding analogs) that gives a principled training objective for the regret-based gate described in §4.4, beyond "minimize disagreement with the optimal-in-hindsight route"?
- What's a good methodology for constructing a benchmark slice where a fixed, capable single-call LLM baseline has non-trivial failure rate (so there's headroom to show improvement), without resorting to adversarial/trick questions that wouldn't generalize to real-world query distributions?
- Are there standard cost-accuracy Pareto-frontier reporting conventions (from the model-routing / cascade literature) we should adopt instead of the current single-table format, to make the C vs D and C vs A comparisons more rigorous and reviewer-legible?

## 6. Files for Reference

- `analyzer/gate.py` — the heuristic gate (the part with the circularity problem)
- `benchmarks/ablation.py` — eval harness (4 conditions, includes unfinished regret-logging instrumentation)
- `benchmarks/data/{gsm8k,hotpot,bbh}_slice.json` — the 40 hand-authored questions
- `paper/paper.md` — current write-up (results section reflects the n=40 numbers above; needs the caveats in §3 added before sharing externally)
