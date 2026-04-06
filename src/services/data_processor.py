"""
CipherFlow Data Processor
--------------------------
Accepts raw payload dicts, validates them, applies transformations,
and returns a structured ProcessingResult. All sensitive fields are
encrypted before storage or transmission.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.core.security_utils import encrypt_payload, mask_sensitive


class ProcessingStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED  = "failed"


@dataclass
class ProcessingResult:
    status:     ProcessingStatus
    record_id:  str
    checksum:   str
    processed:  dict[str, Any]
    warnings:   list[str] = field(default_factory=list)
    encrypted:  bool = False
    processed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ── Validation ────────────────────────────────────────────────────────────────

REQUIRED_FIELDS = {"payload_id", "data", "source"}
EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[a-z]{2,}$", re.I)


def validate_payload(raw: dict) -> list[str]:
    """
    Returns a list of validation error strings.
    Empty list means the payload is valid.
    """
    errors: list[str] = []

    missing = REQUIRED_FIELDS - raw.keys()
    if missing:
        errors.append(f"Missing required fields: {sorted(missing)}")

    if "payload_id" in raw and not isinstance(raw["payload_id"], str):
        errors.append("payload_id must be a string")

    if "data" in raw:
        if not isinstance(raw["data"], dict):
            errors.append("data must be an object")
        elif len(raw["data"]) == 0:
            errors.append("data must not be empty")

    if "email" in raw.get("data", {}):
        if not EMAIL_RE.match(str(raw["data"]["email"])):
            errors.append("data.email is not a valid email address")

    return errors


# ── Transformations ───────────────────────────────────────────────────────────

def _normalise_strings(data: dict) -> dict:
    """Recursively strip and lowercase all string values."""
    out = {}
    for k, v in data.items():
        if isinstance(v, str):
            out[k] = v.strip().lower()
        elif isinstance(v, dict):
            out[k] = _normalise_strings(v)
        else:
            out[k] = v
    return out


def _redact_sensitive_keys(data: dict, sensitive: set[str] | None = None) -> dict:
    """Replace values of known sensitive keys with masked versions."""
    if sensitive is None:
        sensitive = {"password", "token", "secret", "api_key", "credit_card"}
    return {
        k: mask_sensitive(str(v)) if k.lower() in sensitive else v
        for k, v in data.items()
    }


def _compute_checksum(data: dict) -> str:
    serialised = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialised.encode()).hexdigest()


# ── Public processor ──────────────────────────────────────────────────────────

def process_payload(raw: dict, encrypt: bool = False) -> ProcessingResult:
    """
    Main entry point for data processing.

    Steps:
      1. Validate required fields and field types
      2. Normalise string values
      3. Redact sensitive keys
      4. Compute a SHA-256 checksum of the clean record
      5. Optionally encrypt the entire processed payload with Fernet
    """
    warnings: list[str] = []

    # 1. Validate
    errors = validate_payload(raw)
    if errors:
        return ProcessingResult(
            status=ProcessingStatus.FAILED,
            record_id=str(raw.get("payload_id", "unknown")),
            checksum="",
            processed={},
            warnings=errors,
        )

    inner_data: dict = raw["data"]

    # 2. Normalise
    normalised = _normalise_strings(inner_data)

    # 3. Redact
    clean = _redact_sensitive_keys(normalised)

    # Warn if unexpected extra top-level keys were sent
    extra = set(raw.keys()) - REQUIRED_FIELDS - {"email", "metadata"}
    if extra:
        warnings.append(f"Unexpected fields ignored: {sorted(extra)}")

    # 4. Checksum
    checksum = _compute_checksum(clean)

    processed: dict[str, Any] = {
        "payload_id": raw["payload_id"],
        "source":     raw["source"],
        "data":       clean,
        "checksum":   checksum,
    }

    # 5. Optionally encrypt
    encrypted = False
    if encrypt:
        serialised = json.dumps(processed, default=str)
        processed = {"encrypted_blob": encrypt_payload(serialised)}
        encrypted = True

    return ProcessingResult(
        status=ProcessingStatus.SUCCESS,
        record_id=raw["payload_id"],
        checksum=checksum,
        processed=processed,
        warnings=warnings,
        encrypted=encrypted,
    )
