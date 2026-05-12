"""Logging setup for the backend runtime."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.responses import Response

from src.core.timing import Timer


def configure_logging(level_name: str) -> None:
    """Configure process-wide logging with a compact production-safe format."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def install_request_logging(
    app: FastAPI,
    *,
    enabled: bool,
    slow_request_ms: int,
) -> None:
    """Install one request logging middleware when enabled by config."""
    if not enabled:
        return

    logger = logging.getLogger("src.api.requests")

    @app.middleware("http")
    async def log_request(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        timer = Timer()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = timer.elapsed_ms
            # Slow requests are warnings because they are operational signals;
            # request details stay compact and avoid logging bodies or API keys.
            level = logging.WARNING if duration_ms >= slow_request_ms else logging.INFO
            logger.log(
                level,
                "request method=%s path=%s status=%s duration_ms=%s",
                request.method,
                request.url.path,
                status_code,
                duration_ms,
            )
