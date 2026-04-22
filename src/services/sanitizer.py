"""
CipherFlow Input Sanitizer
============================
Prevents XSS and injection attacks by stripping dangerous characters
from string values before processing. Runs before the main pipeline.
"""

import re
from typing import Any


HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
SCRIPT_PATTERN = re.compile(r"(javascript|on\w+)\s*[:=]", re.IGNORECASE)
SQL_INJECTION_PATTERN = re.compile(
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b.*\b(FROM|INTO|TABLE|SET)\b)",
    re.IGNORECASE,
)


def strip_html_tags(value: str) -> str:
    """Remove all HTML tags from a string."""
    return HTML_TAG_PATTERN.sub("", value)


def detect_injection(value: str) -> list[str]:
    """Detect potential injection patterns. Returns list of threat types found."""
    threats = []
    if SCRIPT_PATTERN.search(value):
        threats.append("xss")
    if SQL_INJECTION_PATTERN.search(value):
        threats.append("sql_injection")
    return threats


def sanitize_payload(data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Recursively sanitize all string values in a payload.
    Returns (sanitized_data, list_of_warnings)."""
    sanitized = {}
    warnings = []
    for key, value in data.items():
        if isinstance(value, str):
            threats = detect_injection(value)
            if threats:
                warnings.append(f"Potential {', '.join(threats)} detected in field '{key}'")
            sanitized[key] = strip_html_tags(value)
        elif isinstance(value, dict):
            nested, nested_warnings = sanitize_payload(value)
            sanitized[key] = nested
            warnings.extend(nested_warnings)
        elif isinstance(value, list):
            clean_list = []
            for item in value:
                if isinstance(item, str):
                    clean_list.append(strip_html_tags(item))
                else:
                    clean_list.append(item)
            sanitized[key] = clean_list
        else:
            sanitized[key] = value
    return sanitized, warnings
