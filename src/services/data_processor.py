"""
CipherFlow Data Processor
===========================
The core processing pipeline that transforms raw payloads through
five sequential stages: Validation → Normalization → Redaction →
Checksum → Encryption. Each stage is independently testable and
reports timing metrics for observability.
"""

import re
import time
from typing import Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

from src.core.security_utils import compute_checksum, encrypt_data


# ── Constants ────────────────────────────────────────────────────────────────

SENSITIVE_KEYS: set[str] = {
    "password", "ssn", "credit_card", "card_number",
    "cvv", "secret", "token", "pin", "account_number",
    "routing_number", "tax_id", "drivers_license",
}

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

REQUIRED_FIELDS: set[str] = {"id", "data"}


# ── Pipeline Stage Result ────────────────────────────────────────────────────

@dataclass
class StageResult:
    """Result of a single pipeline stage."""
    name: str
    status: str = "completed"
    duration_ms: float = 0.0


@dataclass
class PipelineResult:
    """Complete result of the processing pipeline."""
    status: str = "success"
    record_id: str = ""
    processed_data: Optional[dict[str, Any]] = None
    encrypted_blob: Optional[str] = None
    is_encrypted: bool = False
    checksum: str = ""
    processed_at: str = ""
    warnings: list[str] = field(default_factory=list)
    pipeline: list[StageResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


# ── Stage 1: Validation ─────────────────────────────────────────────────────

def validate_payload(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Validate the incoming payload structure and data types.
    Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    # Check required top-level fields
    if "id" not in payload:
        errors.append("Missing required field: 'id'")
    elif not isinstance(payload["id"], str):
        errors.append("Field 'id' must be a string")

    if "data" not in payload:
        errors.append("Missing required field: 'data'")
    elif not isinstance(payload["data"], dict):
        errors.append("Field 'data' must be a dictionary")
    elif len(payload["data"]) == 0:
        errors.append("Field 'data' must not be empty")

    # Check for extra top-level keys
    extra_keys = set(payload.keys()) - REQUIRED_FIELDS
    if extra_keys:
        warnings.append(f"Extra top-level keys ignored: {', '.join(sorted(extra_keys))}")

    # Validate email format if present
    data = payload.get("data", {})
    if isinstance(data, dict):
        email = data.get("email")
        if email is not None and isinstance(email, str):
            if not EMAIL_REGEX.match(email):
                errors.append(f"Invalid email format: '{email}'")

    return errors, warnings


# ── Stage 2: Normalization ───────────────────────────────────────────────────

def normalise_strings(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively strip whitespace and lowercase all string values."""
    normalised: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            normalised[key] = value.strip().lower()
        elif isinstance(value, dict):
            normalised[key] = normalise_strings(value)
        elif isinstance(value, list):
            normalised[key] = [
                v.strip().lower() if isinstance(v, str) else v
                for v in value
            ]
        else:
            normalised[key] = value
    return normalised


# ── Stage 3: Redaction ───────────────────────────────────────────────────────

def redact_sensitive_keys(
    data: dict[str, Any],
    sensitive_keys: Optional[set[str]] = None,
) -> dict[str, Any]:
    """Replace values of sensitive keys with '***'.
    Operates recursively on nested dicts."""
    keys = sensitive_keys or SENSITIVE_KEYS
    redacted: dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in keys:
            redacted[key] = "***"
        elif isinstance(value, dict):
            redacted[key] = redact_sensitive_keys(value, keys)
        else:
            redacted[key] = value
    return redacted


# ── Stage 4: Checksum ────────────────────────────────────────────────────────
# Uses compute_checksum from security_utils (SHA-256 of canonicalized JSON)


# ── Stage 5: Encryption ─────────────────────────────────────────────────────
# Uses encrypt_data from security_utils (Fernet symmetric encryption)


# ── Full Pipeline Orchestrator ───────────────────────────────────────────────

def process_payload(
    payload: dict[str, Any],
    encrypt: bool = False,
) -> PipelineResult:
    """Execute the full five-stage processing pipeline.

    Stages:
        1. Validate  — structural and type checks
        2. Normalize — whitespace stripping, lowercasing
        3. Redact    — mask sensitive fields
        4. Checksum  — SHA-256 integrity hash
        5. Encrypt   — optional Fernet encryption

    Returns a PipelineResult with stage timings for observability.
    """
    result = PipelineResult()
    result.processed_at = datetime.now(timezone.utc).isoformat()

    # ── Stage 1: Validate ────────────────────────────────────────────────
    t0 = time.perf_counter()
    errors, warnings = validate_payload(payload)
    stage_time = (time.perf_counter() - t0) * 1000
    result.pipeline.append(StageResult("validation", "completed", round(stage_time, 2)))
    result.warnings.extend(warnings)

    if errors:
        result.status = "failed"
        result.errors = errors
        result.pipeline[-1].status = "failed"
        return result

    result.record_id = payload["id"]
    data = payload["data"]

    # ── Stage 2: Normalize ───────────────────────────────────────────────
    t0 = time.perf_counter()
    data = normalise_strings(data)
    stage_time = (time.perf_counter() - t0) * 1000
    result.pipeline.append(StageResult("normalization", "completed", round(stage_time, 2)))

    # ── Stage 3: Redact ──────────────────────────────────────────────────
    t0 = time.perf_counter()
    data = redact_sensitive_keys(data)
    stage_time = (time.perf_counter() - t0) * 1000
    result.pipeline.append(StageResult("redaction", "completed", round(stage_time, 2)))

    # ── Stage 4: Checksum ────────────────────────────────────────────────
    t0 = time.perf_counter()
    result.checksum = compute_checksum(data)
    stage_time = (time.perf_counter() - t0) * 1000
    result.pipeline.append(StageResult("checksum", "completed", round(stage_time, 2)))

    # ── Stage 5: Encrypt (optional) ──────────────────────────────────────
    if encrypt:
        t0 = time.perf_counter()
        result.encrypted_blob = encrypt_data(data)
        result.is_encrypted = True
        stage_time = (time.perf_counter() - t0) * 1000
        result.pipeline.append(StageResult("encryption", "completed", round(stage_time, 2)))
    else:
        result.processed_data = data

    return result
