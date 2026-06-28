"""
LLM-as-Judge for C³ Benchmark Evaluation.

Evaluates rubric-type answers (planning, critical evaluation, interpretive)
by asking a capable LLM to score the answer against a predefined rubric.

Returns a score in [0.0, 1.0].
"""
from __future__ import annotations
import json
import os
from openai import AsyncOpenAI

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client


async def judge_rubric(answer: str, rubric: str, question: str) -> dict:
    """
    Asks GPT-4o to score an answer against a rubric.
    Returns {"score": float, "passed_criteria": int, "total_criteria": int, "feedback": str}
    """
    prompt = f"""You are an expert evaluator. Score the following answer against the rubric.

QUESTION: {question}

RUBRIC (what a good answer requires): {rubric}

ANSWER TO EVALUATE:
{answer[:1500]}

Respond in this exact JSON format:
{{
  "score": <float 0.0 to 1.0>,
  "passed_criteria": <number of rubric criteria clearly met>,
  "total_criteria": <total rubric criteria you identified>,
  "feedback": "<one sentence summary of what was good or missing>"
}}"""

    client = _get_client()
    try:
        resp = await client.chat.completions.create(
            model=os.environ.get("C3_JUDGE_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are an expert academic evaluator. Respond only in JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=256,
            response_format={"type": "json_object"},
        )
        result = json.loads(resp.choices[0].message.content or "{}")
        return {
            "score": float(result.get("score", 0.0)),
            "passed_criteria": result.get("passed_criteria", 0),
            "total_criteria": result.get("total_criteria", 1),
            "feedback": result.get("feedback", ""),
        }
    except Exception as e:
        return {"score": 0.0, "passed_criteria": 0, "total_criteria": 1, "feedback": str(e)}


def judge_exact(answer: str, ground_truth: str, aliases: list[str]) -> dict:
    """
    Exact match evaluation for factual and numeric questions.
    Normalizes both strings (lowercase, strip punctuation, strip whitespace).
    """
    def normalize(s: str) -> str:
        import re
        s = s.lower().strip()
        s = re.sub(r"[^\w\s\.\-]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    answer_norm = normalize(answer)
    all_targets = [normalize(ground_truth)] + [normalize(a) for a in aliases]

    # Direct substring or equality match
    for target in all_targets:
        if target in answer_norm or answer_norm in target:
            return {"score": 1.0, "matched": target, "method": "substring"}

    return {"score": 0.0, "matched": None, "method": "no_match"}


def judge_numeric(answer: str, ground_truth: str, tolerance: float = 0.02) -> dict:
    """
    Numeric match with relative tolerance (default 2%).
    Extracts the first number from the answer string.
    """
    import re
    nums = re.findall(r"[-+]?\d*\.?\d+", answer.replace(",", ""))
    try:
        expected = float(ground_truth.replace(",", ""))
    except ValueError:
        return {"score": 0.0, "matched": None, "method": "parse_error"}

    for num_str in nums:
        try:
            candidate = float(num_str)
            if expected == 0:
                if abs(candidate) < 1e-9:
                    return {"score": 1.0, "matched": candidate, "method": "numeric_exact"}
            elif abs(candidate - expected) / abs(expected) <= tolerance:
                return {"score": 1.0, "matched": candidate, "method": "numeric_tolerance"}
        except ValueError:
            continue

    return {"score": 0.0, "matched": nums[:3] if nums else None, "method": "no_match"}
