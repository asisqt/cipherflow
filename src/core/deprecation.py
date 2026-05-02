"""
CipherFlow API Deprecation Headers
=====================================
Adds Sunset and Deprecation headers to API responses when endpoints
are scheduled for removal. Follows the IETF Sunset Header draft spec
(draft-wilde-sunset-header) for standards-compliant deprecation notices.

Usage:
    Register deprecated endpoints in DEPRECATED_ENDPOINTS dict.
    Middleware automatically adds headers to matching responses.
"""

from datetime import datetime
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


DEPRECATED_ENDPOINTS: dict[str, dict[str, str]] = {
    # Example: when v2 launches, deprecate v1
    # "/api/v1/process": {
    #     "sunset": "2027-01-01T00:00:00Z",
    #     "replacement": "/api/v2/process",
    #     "message": "v1 will be removed on 2027-01-01. Migrate to v2.",
    # },
}


class DeprecationMiddleware(BaseHTTPMiddleware):
    """Add deprecation headers to responses for endpoints scheduled for removal."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        path = request.url.path

        deprecation = DEPRECATED_ENDPOINTS.get(path)
        if deprecation:
            response.headers["Sunset"] = deprecation["sunset"]
            response.headers["Deprecation"] = "true"
            response.headers["Link"] = (
                f'<{deprecation["replacement"]}>; rel="successor-version"'
            )
            response.headers["X-Deprecation-Notice"] = deprecation["message"]

        return response
