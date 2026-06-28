"""
Operator Backend Configuration.

Controls whether C³ uses live (real LLM/search) or mock operators.

Environment variables:
  C3_BACKEND         = "live" | "mock"  (default: "mock")
  OPENAI_API_KEY     = sk-...
  TAVILY_API_KEY     = tvly-...        (for KNOW.RETRIEVE)

Usage:
  C3_BACKEND=live python cli/main.py "..."
"""
from __future__ import annotations
import os


def get_backend() -> str:
    return os.environ.get("C3_BACKEND", "mock").lower()


def is_live() -> bool:
    return get_backend() == "live"


def require_env(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        raise EnvironmentError(
            f"C3_BACKEND=live requires {key} to be set. "
            f"Add it to your environment or .env file."
        )
    return val
