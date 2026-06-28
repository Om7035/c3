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
        query = inputs.get("query") or str(inputs.get("input_data", ""))

        # Step 1: generate Python code via LLM
        code = await self._generate_code(query)
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

    async def _generate_code(self, problem: str) -> str:
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

        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
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
