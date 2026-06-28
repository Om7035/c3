from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("c3.runtime")

def log_event(event: str, details: Any = None) -> None:
    logger.info(f"{event}: {details}")
