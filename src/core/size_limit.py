"""
CipherFlow Request Size Limiter
==================================
Rejects payloads exceeding the configured maximum size before
they reach the processing pipeline. Prevents memory exhaustion
from oversized requests and potential DoS attacks.

Default limit: 1MB (1,048,576 bytes)
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with bodies exceeding the configured size limit."""

    def __init__(self, app, max_bytes: int = 1_048_576):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")

        if content_length and int(content_length) > self.max_bytes:
            max_mb = round(self.max_bytes / 1_048_576, 1)
            return JSONResponse(
                status_code=413,
                content={
                    "success": False,
                    "error": {
                        "code": "CF-VAL-005",
                        "message": f"Payload exceeds maximum size of {max_mb}MB",
                    },
                },
            )

        return await call_next(request)
