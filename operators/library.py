"""
Operator registry — returns live or mock operators based on C3_BACKEND env var.
"""
from __future__ import annotations
from operators.interfaces import Operator
from operators.config import is_live


def get_operator_registry() -> dict[str, Operator]:
    if is_live():
        return _get_live_registry()
    return _get_mock_registry()


def _get_live_registry() -> dict[str, Operator]:
    from operators.live.retrieval import LiveRetrieveOperator
    from operators.live.execution import LivePythonOperator
    from operators.live.reasoning import LiveInferOperator, LiveSummarizeOperator
    from operators.live.verification import LiveVerifyOperator

    # Memory operator has no live equivalent — use mock (no external call needed)
    from operators.library import MemoryOperator

    return {
        "KNOW.RETRIEVE": LiveRetrieveOperator(),
        "KNOW.MEMORY":   MemoryOperator(),
        "EXEC.PYTHON":   LivePythonOperator(),
        "REAS.INFER":    LiveInferOperator(),
        "REAS.SUMMARIZE":LiveSummarizeOperator(),
        "VERI.VERIFY":   LiveVerifyOperator(),
    }


def _get_mock_registry() -> dict[str, Operator]:
    from operators.mock_library import (
        RetrieveOperator, PythonOperator, SummarizeOperator,
        VerifyOperator, MemoryOperator, InferOperator
    )
    return {
        "KNOW.RETRIEVE": RetrieveOperator(),
        "KNOW.MEMORY":   MemoryOperator(),
        "EXEC.PYTHON":   PythonOperator(),
        "REAS.INFER":    InferOperator(),
        "REAS.SUMMARIZE":SummarizeOperator(),
        "VERI.VERIFY":   VerifyOperator(),
    }
