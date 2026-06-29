"""
VERI.VERIFY — Live Verification Operator

Asks the LLM to assess the correctness of a claim given available evidence.
This is the critical first-class verification component of C³.

The verification prompt is structured as a formal judgment task:
  - Input: claim + supporting evidence (from registers)
  - Output: {verified: bool, confidence: float, reason: str}

Confidence is empirical — the model must justify its score.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import AsyncOpenAI

from operators.interfaces import Operator, OperatorResult
from core.context import ExecutionContext


class LiveVerifyOperator(Operator):
    def __init__(self):
        self._client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    @property
    def name(self) -> str:
        return "VERI.VERIFY"

    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        # Extract the claim and evidence from prior register state
        input_data = inputs.get("input_data", inputs)
        claim, evidence = self._extract_claim_and_evidence(input_data)

        prompt = f"""You are a verification engine. Assess the factual accuracy and logical consistency of the following claim given the evidence.

CLAIM: {claim}

EVIDENCE: {evidence}

Respond in this exact JSON format:
{{
  "verified": true or false,
  "confidence": <float 0.0–1.0>,
  "reason": "<one-sentence justification>"
}}

Do not include any text outside the JSON."""

        try:
            resp = await self._client.chat.completions.create(
                model=os.environ.get("C3_LLM_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a precise factual verification system. Respond only in valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=256,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content or "{}"
            result = json.loads(raw)

            verified = bool(result.get("verified", False))
            confidence = float(result.get("confidence", 0.5))
            reason = result.get("reason", "")

            return OperatorResult(
                success=True,
                data={"verified": verified, "confidence": confidence, "reason": reason, "claim": claim},
                confidence=confidence,
            )

        except json.JSONDecodeError:
            # Model returned non-JSON — try to parse heuristically
            text = resp.choices[0].message.content or ""
            verified = "true" in text.lower() and "false" not in text.lower()
            return OperatorResult(
                success=True,
                data={"verified": verified, "confidence": 0.5, "reason": "Parsed heuristically", "claim": claim},
                confidence=0.5,
            )
        except Exception as e:
            return OperatorResult(success=False, error=str(e), confidence=0.0)

    def _extract_claim_and_evidence(self, input_data: Any) -> tuple[str, str]:
        """Pull the most recent 'answer' or 'response' as the claim, rest as evidence."""
        if isinstance(input_data, dict):
            claim = (
                input_data.get("response") or
                input_data.get("output") or
                input_data.get("summary") or
                str(input_data)
            )
            evidence = (
                input_data.get("answer") or          # From KNOW.RETRIEVE
                "\n".join(
                    d.get("content", "")
                    for d in input_data.get("documents", [])[:2]
                ) or
                str(input_data)
            )
            return str(claim)[:800], str(evidence)[:800]
        return str(input_data)[:800], "No external evidence"
