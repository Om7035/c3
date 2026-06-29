"""
EXEC.PYTHON — Sandboxed Python Execution Operator

Generates Python code from the input context using an LLM,
then executes it in an isolated subprocess with a strict timeout.

Confidence:
  - 1.0 if the code executes without error and produces output
  - 0.0 if the code raises an exception
  - 0.3 if execution times out
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import textwrap
import tempfile
from typing import Any

from openai import AsyncOpenAI

from operators.interfaces import Operator, OperatorResult
from core.context import ExecutionContext

EXECUTION_TIMEOUT_S = 10


class LivePythonOperator(Operator):
    def __init__(self):
        self._client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    @property
    def name(self) -> str:
        return "EXEC.PYTHON"

    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        query = inputs.get("query") or context.objective
        raw_data = inputs.get("input_data") if not inputs.get("query") else None

        # Retrieved data (e.g. from KNOW.RETRIEVE) often contains quotes/unicode that
        # break if the LLM hand-copies it into a string literal. Serialize it ourselves
        # and have the generated script load it from disk instead of embedding it inline.
        data_path = None
        if raw_data is not None:
            data_path = self._write_data_file(raw_data)

        try:
            # Step 1: generate Python code via LLM
            code = await self._generate_code(query, data_path, raw_data)
            if not code:
                return OperatorResult(success=False, error="Code generation failed", confidence=0.0)

            # Step 2: execute in subprocess sandbox
            output, error, timed_out = await self._run_subprocess(code)

            if timed_out:
                return OperatorResult(
                    success=False,
                    data={"code": code},
                    error=f"Execution timed out after {EXECUTION_TIMEOUT_S}s",
                    confidence=0.3,
                )

            if error and not output:
                return OperatorResult(
                    success=False,
                    data={"code": code, "stderr": error},
                    error=f"Python execution error: {error[:200]}",
                    confidence=0.0,
                )

            return OperatorResult(
                success=True,
                data={"code": code, "output": output, "stderr": error},
                confidence=1.0,
            )
        finally:
            if data_path:
                try:
                    os.unlink(data_path)
                except OSError:
                    pass

    def _write_data_file(self, data: Any) -> str:
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f, default=str)
            return f.name

    def _describe_data(self, data: Any, depth: int = 0) -> str:
        """Describe the actual shape of upstream data — recursively, since
        the code-gen LLM needs nested keys too (e.g. each dict inside a
        'documents' list), not just the top-level keys. Upstream can be
        KNOW.RETRIEVE output, a prior EXEC.PYTHON's output, etc. — each has
        a different shape, so inspect the real object rather than assuming
        one fixed schema."""
        if depth >= 2:
            return f"{type(data).__name__}"
        if isinstance(data, dict):
            parts = [f"'{k}': {self._describe_data(v, depth + 1)}" for k, v in data.items()]
            return "dict {" + ", ".join(parts) + "}"
        if isinstance(data, list):
            if not data:
                return "empty list"
            return f"list of {len(data)}x {self._describe_data(data[0], depth + 1)}"
        return type(data).__name__

    async def _generate_code(self, problem: str, data_path: str | None = None, data: Any = None) -> str:
        if data_path:
            prompt = textwrap.dedent(f"""
                Write a Python script that solves the following problem.
                Reference data for this problem is saved as JSON at this exact path:
                {data_path}
                Load it with `json.load(open(r"{data_path}", encoding="utf-8"))`. The loaded object
                is {self._describe_data(data)} — do NOT assume any other keys exist beyond what's
                listed, and do NOT index into it with problem-specific keys you haven't confirmed.
                Do NOT copy any of its text into hardcoded string literals in your script — it may contain quotes
                or unicode that will break Python syntax. Only access it by loading the file.
                Output ONLY executable Python code, no markdown fences, no explanation.
                The script must print its final answer to stdout.

                Problem: {problem}
            """).strip()
        else:
            prompt = textwrap.dedent(f"""
                Write a Python script that solves the following problem.
                Output ONLY executable Python code, no markdown fences, no explanation.
                The script must print its final answer to stdout.

                Problem: {problem}
            """).strip()
        try:
            resp = await self._client.chat.completions.create(
                model=os.environ.get("C3_LLM_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=512,
            )
            code = resp.choices[0].message.content or ""
            # Strip markdown fences if model includes them despite instructions
            code = code.replace("```python", "").replace("```", "").strip()
            return code
        except Exception:
            return ""

    async def _run_subprocess(self, code: str) -> tuple[str, str, bool]:
        """Execute code in a subprocess, return (stdout, stderr, timed_out)."""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write(code)
            tmp_path = f.name

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=EXECUTION_TIMEOUT_S
                )
                return stdout.decode(errors="replace"), stderr.decode(errors="replace"), False
            except asyncio.TimeoutError:
                proc.kill()
                return "", "", True
        except Exception as e:
            return "", str(e), False
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
