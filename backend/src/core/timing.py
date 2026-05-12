"""Small timing helpers for production-safe duration logs."""

from __future__ import annotations

from time import perf_counter


class Timer:
    """Measure elapsed wall-clock time in milliseconds."""

    def __init__(self) -> None:
        self._started_at = perf_counter()

    @property
    def elapsed_ms(self) -> int:
        return round((perf_counter() - self._started_at) * 1000)
