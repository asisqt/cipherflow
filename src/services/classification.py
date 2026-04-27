"""
CipherFlow Data Classification
=================================
Categorizes detected sensitive fields by compliance regulation.
Maps each field type to its data class, applicable regulations,
and required handling procedures.

Supports: GDPR, HIPAA, PCI-DSS, SOC2
"""

from typing import Any
from dataclasses import dataclass


@dataclass
class DataClass:
    """Classification metadata for a sensitive field type."""
    field_type: str
    category: str
    regulations: list[str]
    severity: str
    handling: str


CLASSIFICATIONS: dict[str, DataClass] = {
    "password": DataClass(
        field_type="password",
        category="authentication",
        regulations=["GDPR", "SOC2"],
        severity="high",
        handling="hash_and_redact",
    ),
    "ssn": DataClass(
        field_type="ssn",
        category="government_id",
        regulations=["GDPR", "SOC2", "HIPAA"],
        severity="critical",
        handling="redact_and_encrypt",
    ),
    "credit_card": DataClass(
        field_type="credit_card",
        category="financial",
        regulations=["PCI-DSS", "GDPR"],
        severity="critical",
        handling="redact_and_encrypt",
    ),
    "cvv": DataClass(
        field_type="cvv",
        category="financial",
        regulations=["PCI-DSS"],
        severity="critical",
        handling="never_store",
    ),
    "email": DataClass(
        field_type="email",
        category="personal_info",
        regulations=["GDPR"],
        severity="medium",
        handling="normalize_and_consent",
    ),
    "token": DataClass(
        field_type="token",
        category="authentication",
        regulations=["SOC2"],
        severity="high",
        handling="redact_and_rotate",
    ),
    "account_number": DataClass(
        field_type="account_number",
        category="financial",
        regulations=["PCI-DSS", "GDPR"],
        severity="critical",
        handling="redact_and_encrypt",
    ),
    "tax_id": DataClass(
        field_type="tax_id",
        category="government_id",
        regulations=["GDPR", "SOC2"],
        severity="critical",
        handling="redact_and_encrypt",
    ),
    "drivers_license": DataClass(
        field_type="drivers_license",
        category="government_id",
        regulations=["GDPR"],
        severity="high",
        handling="redact_and_encrypt",
    ),
    "pin": DataClass(
        field_type="pin",
        category="authentication",
        regulations=["PCI-DSS"],
        severity="high",
        handling="never_store",
    ),
}


def classify_fields(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Classify all sensitive fields found in a payload.
    Returns list of classification reports for each detected field."""
    results = []
    for key, value in data.items():
        key_lower = key.lower()
        if key_lower in CLASSIFICATIONS:
            cls = CLASSIFICATIONS[key_lower]
            results.append({
                "field": key,
                "category": cls.category,
                "severity": cls.severity,
                "regulations": cls.regulations,
                "handling": cls.handling,
            })
        if isinstance(value, dict):
            nested = classify_fields(value)
            for item in nested:
                item["field"] = f"{key}.{item['field']}"
                results.append(item)
    return results


def get_compliance_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Generate a compliance summary showing which regulations apply."""
    classifications = classify_fields(data)
    all_regulations = set()
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for cls in classifications:
        all_regulations.update(cls["regulations"])
        severity_counts[cls["severity"]] = severity_counts.get(cls["severity"], 0) + 1
    return {
        "total_sensitive_fields": len(classifications),
        "applicable_regulations": sorted(all_regulations),
        "severity_breakdown": severity_counts,
        "fields": classifications,
    }
