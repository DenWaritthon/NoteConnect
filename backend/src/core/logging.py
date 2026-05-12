"""Logging setup for the backend runtime."""

from __future__ import annotations

import logging


def configure_logging(level_name: str) -> None:
    """Configure process-wide logging with a compact production-safe format."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
