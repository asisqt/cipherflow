"""
CipherFlow Response Envelope
===============================
Standardized API response wrapper for consistent client-side parsing.
Every response follows the same structure regardless of endpoint.

Format:
{
    "success": true/false,
    "data": { ... },
    "meta": { "request_id": "...", "version": "2.0.0" }
}
"""

from typing import Any, Optional


def success_response(
    data: Any,
    request_id: Optional[str] = None,
    version: str = "2.0.0",
) -> dict[str, Any]:
    """Wrap successful response data in standard envelope."""
    response = {
        "success": True,
        "data": data,
        "meta": {
            "version": version,
        },
    }
    if request_id:
        response["meta"]["request_id"] = request_id
    return response


def error_response(
    message: str,
    errors: Optional[list[str]] = None,
    request_id: Optional[str] = None,
    version: str = "2.0.0",
) -> dict[str, Any]:
    """Wrap error details in standard envelope."""
    response = {
        "success": False,
        "error": {
            "message": message,
            "details": errors or [],
        },
        "meta": {
            "version": version,
        },
    }
    if request_id:
        response["meta"]["request_id"] = request_id
    return response
