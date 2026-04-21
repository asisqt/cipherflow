"""
CipherFlow Response Timing
============================
Measures and exposes request processing time via X-Process-Time header.
Useful for monitoring and debugging slow endpoints.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class TimingMiddleware(BaseHTTPMiddleware):
    """Add X-Process-Time header showing request duration in milliseconds."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Process-Time"] = f"{duration_ms}ms"
        return response
