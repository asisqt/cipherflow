"""
CipherFlow Rate Limit Headers
===============================
Adds X-RateLimit headers to every response for API consumers.
Informational only — no actual throttling (would require Redis in production).
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """Add rate limit headers to inform API consumers of usage limits."""

    LIMIT = 100
    WINDOW = "60s"

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.LIMIT)
        response.headers["X-RateLimit-Window"] = self.WINDOW
        response.headers["X-RateLimit-Policy"] = "100;w=60"
        return response
