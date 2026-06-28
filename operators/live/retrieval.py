"""
KNOW.RETRIEVE — Live Web Retrieval Operator

Primary: Tavily Search API (designed for LLM retrieval, returns clean summaries)
Fallback: DuckDuckGo Instant Answer API (free, no key required, limited)

Confidence is derived from the number of results returned and their relevance scores.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

from operators.interfaces import Operator, OperatorResult
from core.context import ExecutionContext


class LiveRetrieveOperator(Operator):
    @property
    def name(self) -> str:
        return "KNOW.RETRIEVE"

    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> OperatorResult:
        query = inputs.get("query") or inputs.get("input_data", "")
        if not query:
            return OperatorResult(success=False, error="No query provided to KNOW.RETRIEVE", confidence=0.0)

        # Try Tavily first
        tavily_key = os.environ.get("TAVILY_API_KEY")
        if tavily_key:
            return await self._tavily_search(query, tavily_key)

        # Fallback: DuckDuckGo Instant Answer
        return await self._duckduckgo_search(query)

    async def _tavily_search(self, query: str, api_key: str) -> OperatorResult:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": api_key,
                        "query": query,
                        "search_depth": "basic",
                        "include_answer": True,
                        "max_results": 5,
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            results = data.get("results", [])
            answer = data.get("answer", "")
            documents = [
                {"title": r.get("title", ""), "content": r.get("content", ""), "url": r.get("url", "")}
                for r in results
            ]

            # Confidence: presence of direct answer + result count
            confidence = min(0.5 + 0.1 * len(results) + (0.2 if answer else 0.0), 1.0)

            return OperatorResult(
                success=True,
                data={"answer": answer, "documents": documents, "source": "tavily"},
                confidence=round(confidence, 3),
            )
        except Exception as e:
            return OperatorResult(success=False, error=f"Tavily error: {e}", confidence=0.0)

    async def _duckduckgo_search(self, query: str) -> OperatorResult:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_redirect": 1, "no_html": 1},
                )
                data = resp.json()

            abstract = data.get("AbstractText", "")
            related = [t.get("Text", "") for t in data.get("RelatedTopics", [])[:3]]
            documents = [{"title": "DuckDuckGo Abstract", "content": abstract}] if abstract else []
            documents += [{"title": "Related", "content": r} for r in related if r]

            confidence = 0.5 if abstract else 0.25

            return OperatorResult(
                success=True,
                data={"answer": abstract, "documents": documents, "source": "duckduckgo"},
                confidence=confidence,
            )
        except Exception as e:
            return OperatorResult(success=False, error=f"DuckDuckGo error: {e}", confidence=0.0)
