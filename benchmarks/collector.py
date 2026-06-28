"""
RPS Dataset Collector.

Every benchmark run serializes the full Reasoning Provenance Specification (RPS)
into a JSONL file. This is the seed for a future learning compiler.

Each line: one complete reasoning program execution record.
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from typing import Any


DATASET_PATH = os.path.join(os.path.dirname(__file__), "rps_dataset.jsonl")


def collect(
    benchmark_id: str,
    query: str,
    problem_class: str,
    strategy: dict[str, Any],
    rps_report: dict[str, Any],
) -> None:
    """Appends one reasoning execution record to the JSONL dataset."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmark_id": benchmark_id,
        "query": query,
        "problem_class": problem_class,
        "strategy": strategy,
        "rps": rps_report,
    }
    with open(DATASET_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
