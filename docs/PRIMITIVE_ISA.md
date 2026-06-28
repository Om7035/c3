# Primitive Instruction Set Architecture (ISA)

## Philosophy
C³ does not have "tools" or "agents". It has Primitives.
Primitives are the atomic instructions of reasoning, analogous to CPU instructions in a traditional architecture. The C³ compiler can only emit nodes that map to these exact opcodes.

## Category 1: Knowledge Primitives (`KNOW.*`)
Instructions that bring external information into the execution context.
- **`KNOW.RETRIEVE`**: Fetch documents based on a semantic query.
- **`KNOW.SEARCH`**: Execute a targeted web search (e.g., Google/Bing API).
- **`KNOW.MEMORY`**: Load previously cached context or conversation history.
- **`KNOW.SQL`**: Execute a structured query against a relational database.

## Category 2: Reasoning Primitives (`REAS.*`)
Instructions that process, transform, or evaluate information natively via LLM sub-calls.
- **`REAS.INFER`**: Deduce a conclusion given a set of premises.
- **`REAS.COMPARE`**: Evaluate two disparate pieces of data for differences/similarities.
- **`REAS.SUMMARIZE`**: Condense a large register payload into a succinct output.
- **`REAS.CRITIQUE`**: Generate constructive feedback or identify flaws in an input.

## Category 3: Execution Primitives (`EXEC.*`)
Instructions that execute deterministic logic outside the LLM.
- **`EXEC.PYTHON`**: Run an isolated Python script (useful for math, formatting, data manipulation).
- **`EXEC.SHELL`**: Execute a safe bash command (useful for local system tasks).
- **`EXEC.API`**: Trigger an external REST endpoint.

## Category 4: Verification Primitives (`VERI.*`)
Instructions that halt, validate, or score the graph's intermediate states.
- **`VERI.VERIFY`**: Check an intermediate claim against retrieved evidence (returns boolean).
- **`VERI.VOTE`**: Run a multi-agent consensus vote on an ambiguous output.
- **`VERI.CONFIDENCE`**: Emit a probability score (0.0 to 1.0) of correctness for a given register.
