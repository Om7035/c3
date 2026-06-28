"""
REAS.INFER + REAS.SUMMARIZE — Live LLM Reasoning Operators

Both call an LLM with structured prompts.

Confidence is derived by appending a self-assessment question to each prompt
and parsing the model's response. This gives a calibrated, model-reported
uncertainty score rather than a hardcoded value.
"""
from __future__ import annotations

import os
import re
from typing import Any

from openai import AsyncOpenAI

from operators.interfaces import Operator, OperatorResult
from core.context import ExecutionContext


def _extract_confidence(text: str) -> float:
    """
    Parse a confidence score from model output.
    Looks for patterns like: 'Confidence: 0.87' or 'confidence: 87%'
    Falls back to 0.75 if none found.
    """
    patterns = [
        r"[Cc]onfidence[:\s]+([0-9]+\.?[0-9]*)\s*%",
        r"[Cc]onfidence[:\s]+([0-9]+\.?[0-9]*)",
        r"([0-9]+\.?[0-9]*)\s*/\s*10",  # '8/10' style
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            val = float(m.group(1))
            if val > 1.0:
                val /= 100.0  # Convert percentage
            return round(min(max(val, 0.0), 1.0), 3)
    return 0.75  # Default: moderate confidence


def _strip_confidence_line(text: str) -> str:
    """Remove the appended confidence line from the final answer."""
    return re.sub(r"\n?[Cc]onfidence[:\s]+.*$", "", text, flags=re.MULTILINE).strip()


class LiveInferOperator(Operator):
    def __init__(self):
        self._client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    @property
    def name(self) -> str:
        return "REAS.INFER"

    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context_text = _format_context(inputs)
        prompt = (
            f"{context_text}\n\n"
            "Provide a clear, well-reasoned answer. "
            "At the end, on a new line, state your confidence as: 'Confidence: X.XX' "
            "(a number between 0.0 and 1.0)."
        )
        return await self._call_llm(prompt, "REAS.INFER")

    async def _call_llm(self, prompt: str, label: str) -> OperatorResult:
        try:
            resp = await self._client.chat.completions.create(
                model=os.environ.get("C3_LLM_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a precise, analytical reasoning engine."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1024,
            )
            raw = resp.choices[0].message.content or ""
            confidence = _extract_confidence(raw)
            answer = _strip_confidence_line(raw)
            return OperatorResult(
                success=True,
                data={"response": answer, "raw": raw, "operator": label},
                confidence=confidence,
            )
        except Exception as e:
            return OperatorResult(success=False, error=str(e), confidence=0.0)


class LiveSummarizeOperator(Operator):
    def __init__(self):
        self._client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    @property
    def name(self) -> str:
        return "REAS.SUMMARIZE"

    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        context_text = _format_context(inputs)
        prompt = (
            f"Summarize the following into a concise, accurate answer.\n\n"
            f"{context_text}\n\n"
            "Provide only the summary. At the end, on a new line: 'Confidence: X.XX'"
        )
        try:
            resp = await self._client.chat.completions.create(
                model=os.environ.get("C3_LLM_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=512,
            )
            raw = resp.choices[0].message.content or ""
            confidence = _extract_confidence(raw)
            answer = _strip_confidence_line(raw)
            return OperatorResult(
                success=True,
                data={"summary": answer, "operator": "REAS.SUMMARIZE"},
                confidence=confidence,
            )
        except Exception as e:
            return OperatorResult(success=False, error=str(e), confidence=0.0)


def _format_context(inputs: dict[str, Any]) -> str:
    """Convert operator inputs into a readable context string for the LLM."""
    if "query" in inputs:
        return f"Question: {inputs['query']}"
    if "input_data" in inputs:
        data = inputs["input_data"]
        if isinstance(data, dict):
            # Flatten known fields
            parts = []
            if "answer" in data:
                parts.append(f"Retrieved Answer: {data['answer']}")
            if "documents" in data:
                for i, doc in enumerate(data["documents"][:3]):
                    parts.append(f"Source {i+1}: {doc.get('content','')[:400]}")
            if "output" in data:
                parts.append(f"Computation Result: {data['output']}")
            if "response" in data:
                parts.append(f"Prior Reasoning: {data['response']}")
            if "verified" in data:
                parts.append(f"Verification: {'Confirmed' if data['verified'] else 'Not confirmed'} (confidence: {data.get('confidence',0):.2f})")
            return "\n".join(parts) if parts else str(data)
        return str(data)
    return str(inputs)
