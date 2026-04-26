"""
CipherFlow Error Catalog
==========================
Centralized error definitions with unique error codes.
Every API error maps to a code that clients can programmatically handle.
Follows the format: CF-{CATEGORY}-{NUMBER}

Categories:
    AUTH  — Authentication and authorization
    VAL   — Validation and input errors
    PROC  — Processing pipeline errors
    SYS   — System and infrastructure errors
"""

from typing import Any, Optional


class CipherFlowError:
    """Structured error with code, message, and optional details."""

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

    def to_dict(self, details: Optional[Any] = None) -> dict[str, Any]:
        error = {"code": self.code, "message": self.message}
        if details:
            error["details"] = details
        return error


# ── Authentication Errors ────────────────────────────────────────────────────
INVALID_CREDENTIALS = CipherFlowError("CF-AUTH-001", "Invalid username or password", 401)
TOKEN_EXPIRED = CipherFlowError("CF-AUTH-002", "Access token has expired", 401)
TOKEN_INVALID = CipherFlowError("CF-AUTH-003", "Access token is invalid or malformed", 401)
TOKEN_MISSING = CipherFlowError("CF-AUTH-004", "Authorization header is required", 403)

# ── Validation Errors ────────────────────────────────────────────────────────
MISSING_FIELD = CipherFlowError("CF-VAL-001", "Required field is missing", 422)
INVALID_TYPE = CipherFlowError("CF-VAL-002", "Field has incorrect type", 422)
INVALID_EMAIL = CipherFlowError("CF-VAL-003", "Email format is invalid", 422)
EMPTY_PAYLOAD = CipherFlowError("CF-VAL-004", "Payload data must not be empty", 422)
PAYLOAD_TOO_LARGE = CipherFlowError("CF-VAL-005", "Payload exceeds maximum size", 413)

# ── Processing Errors ────────────────────────────────────────────────────────
PIPELINE_FAILED = CipherFlowError("CF-PROC-001", "Processing pipeline failed", 500)
ENCRYPTION_FAILED = CipherFlowError("CF-PROC-002", "Encryption stage failed", 500)
CHECKSUM_MISMATCH = CipherFlowError("CF-PROC-003", "Data integrity check failed", 500)

# ── System Errors ────────────────────────────────────────────────────────────
SERVICE_UNAVAILABLE = CipherFlowError("CF-SYS-001", "Service temporarily unavailable", 503)
RATE_LIMIT_EXCEEDED = CipherFlowError("CF-SYS-002", "Rate limit exceeded", 429)
INTERNAL_ERROR = CipherFlowError("CF-SYS-003", "Internal server error", 500)


# ── Error Code Registry ─────────────────────────────────────────────────────
ERROR_REGISTRY: dict[str, CipherFlowError] = {
    e.code: e for e in [
        INVALID_CREDENTIALS, TOKEN_EXPIRED, TOKEN_INVALID, TOKEN_MISSING,
        MISSING_FIELD, INVALID_TYPE, INVALID_EMAIL, EMPTY_PAYLOAD, PAYLOAD_TOO_LARGE,
        PIPELINE_FAILED, ENCRYPTION_FAILED, CHECKSUM_MISMATCH,
        SERVICE_UNAVAILABLE, RATE_LIMIT_EXCEEDED, INTERNAL_ERROR,
    ]
}
