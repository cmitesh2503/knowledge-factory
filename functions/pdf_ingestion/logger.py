"""
Logging utilities for Knowledge Factory Ingestion.
"""

import logging
import time


def configure_logger() -> logging.Logger:
    """
    Configure and return the application logger.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        force=True,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    logger = logging.getLogger("knowledge_factory")
    logger.setLevel(logging.INFO)
    logger.propagate = True

    for handler in root_logger.handlers:
        handler.setLevel(logging.INFO)

    return logger


class Timer:
    """
    Simple execution timer.
    """

    def __init__(self) -> None:
        self.start = time.perf_counter()

    @property
    def elapsed(self) -> float:
        return round(time.perf_counter() - self.start, 2)
