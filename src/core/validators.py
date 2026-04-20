"""
CipherFlow Custom Validators
==============================
Extended validation utilities for payload inspection.
Supports deep nested field detection, type coercion checks,
and configurable field-level rules.
"""

from typing import Any


SUPPORTED_TYPES = {"str", "int", "float", "bool", "dict", "list"}


def validate_field_types(data: dict[str, Any], schema: dict[str, str]) -> list[str]:
    """Validate that fields in data match expected types from schema.
    Returns a list of error messages for mismatched fields."""
    errors = []
    for field, expected_type in schema.items():
        if field not in data:
            continue
        value = data[field]
        actual_type = type(value).__name__
        if expected_type in SUPPORTED_TYPES and actual_type != expected_type:
            errors.append(f"Field '{field}' expected {expected_type}, got {actual_type}")
    return errors


def detect_nested_sensitive_fields(data: dict[str, Any], depth: int = 0, max_depth: int = 10) -> list[str]:
    """Recursively detect paths to sensitive fields in nested structures.
    Returns list of dot-notation paths like 'user.payment.credit_card'."""
    from src.services.data_processor import SENSITIVE_KEYS

    paths = []
    if depth > max_depth:
        return paths
    for key, value in data.items():
        if key.lower() in SENSITIVE_KEYS:
            paths.append(key)
        if isinstance(value, dict):
            nested = detect_nested_sensitive_fields(value, depth + 1, max_depth)
            paths.extend(f"{key}.{p}" for p in nested)
    return paths


def estimate_payload_risk(data: dict[str, Any]) -> dict[str, Any]:
    """Estimate risk level of a payload based on sensitive field count and depth."""
    sensitive_paths = detect_nested_sensitive_fields(data)
    count = len(sensitive_paths)
    if count == 0:
        level = "low"
    elif count <= 2:
        level = "medium"
    else:
        level = "high"
    return {
        "risk_level": level,
        "sensitive_field_count": count,
        "sensitive_paths": sensitive_paths,
    }
