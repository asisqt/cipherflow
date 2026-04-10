"""
Unit Tests — Data Processor Service
======================================
TDD-style tests for each pipeline stage and the full orchestrator.
25+ test cases covering validation, normalization, redaction,
checksum integrity, encryption, and edge cases.
"""

import pytest
from src.services.data_processor import (
    validate_payload,
    normalise_strings,
    redact_sensitive_keys,
    process_payload,
)
from src.core.security_utils import compute_checksum


# ── Validation Tests ─────────────────────────────────────────────────────────


class TestValidatePayload:
    """Stage 1: Structural and type validation."""

    def test_valid_payload_returns_no_errors(self):
        errors, warnings = validate_payload({
            "id": "rec-001",
            "data": {"name": "Alice", "email": "alice@example.com"},
        })
        assert errors == []

    def test_missing_all_required_fields(self):
        errors, _ = validate_payload({})
        assert len(errors) == 2
        assert any("id" in e for e in errors)
        assert any("data" in e for e in errors)

    def test_missing_single_field(self):
        errors, _ = validate_payload({"id": "rec-001"})
        assert len(errors) == 1
        assert "data" in errors[0]

    def test_payload_id_must_be_string(self):
        errors, _ = validate_payload({"id": 123, "data": {"name": "Bob"}})
        assert any("string" in e for e in errors)

    def test_data_must_be_dict(self):
        errors, _ = validate_payload({"id": "rec-001", "data": "not-a-dict"})
        assert any("dictionary" in e for e in errors)

    def test_empty_data_dict_is_invalid(self):
        errors, _ = validate_payload({"id": "rec-001", "data": {}})
        assert any("empty" in e for e in errors)

    def test_invalid_email_in_data(self):
        errors, _ = validate_payload({
            "id": "rec-001",
            "data": {"email": "not-an-email"},
        })
        assert any("email" in e.lower() for e in errors)

    def test_valid_email_passes(self):
        errors, _ = validate_payload({
            "id": "rec-001",
            "data": {"email": "valid@example.com"},
        })
        assert errors == []

    def test_extra_keys_generate_warning(self):
        _, warnings = validate_payload({
            "id": "rec-001",
            "data": {"name": "Eve"},
            "metadata": "extra",
        })
        assert len(warnings) == 1
        assert "metadata" in warnings[0]


# ── Normalization Tests ──────────────────────────────────────────────────────


class TestNormaliseStrings:
    """Stage 2: Whitespace stripping and lowercasing."""

    def test_strips_whitespace(self):
        result = normalise_strings({"name": "  Alice  "})
        assert result["name"] == "alice"

    def test_lowercases_values(self):
        result = normalise_strings({"city": "NEW YORK"})
        assert result["city"] == "new york"

    def test_nested_dict(self):
        result = normalise_strings({"address": {"city": "  LONDON  "}})
        assert result["address"]["city"] == "london"

    def test_non_string_values_untouched(self):
        result = normalise_strings({"count": 42, "active": True})
        assert result["count"] == 42
        assert result["active"] is True

    def test_list_values_normalized(self):
        result = normalise_strings({"tags": ["  HIGH  ", "  Low  "]})
        assert result["tags"] == ["high", "low"]


# ── Redaction Tests ──────────────────────────────────────────────────────────


class TestRedactSensitiveKeys:
    """Stage 3: Sensitive field masking."""

    def test_password_is_masked(self):
        result = redact_sensitive_keys({"password": "secret123"})
        assert result["password"] == "***"

    def test_non_sensitive_key_unchanged(self):
        result = redact_sensitive_keys({"name": "Alice"})
        assert result["name"] == "Alice"

    def test_custom_sensitive_set(self):
        result = redact_sensitive_keys(
            {"salary": "100000"},
            sensitive_keys={"salary"},
        )
        assert result["salary"] == "***"

    def test_nested_redaction(self):
        result = redact_sensitive_keys({
            "user": {"password": "secret", "name": "Bob"},
        })
        assert result["user"]["password"] == "***"
        assert result["user"]["name"] == "Bob"

    def test_multiple_sensitive_fields(self):
        result = redact_sensitive_keys({
            "password": "x",
            "ssn": "123-45-6789",
            "credit_card": "4111111111111111",
            "name": "Charlie",
        })
        assert result["password"] == "***"
        assert result["ssn"] == "***"
        assert result["credit_card"] == "***"
        assert result["name"] == "Charlie"

    def test_case_insensitive_key_matching(self):
        result = redact_sensitive_keys({"Password": "x", "SSN": "y"})
        assert result["Password"] == "***"
        assert result["SSN"] == "***"


# ── Checksum Tests ───────────────────────────────────────────────────────────


class TestComputeChecksum:
    """Stage 4: SHA-256 integrity hashing."""

    def test_returns_64_char_hex(self):
        checksum = compute_checksum({"key": "value"})
        assert len(checksum) == 64
        assert all(c in "0123456789abcdef" for c in checksum)

    def test_same_data_same_checksum(self):
        data = {"name": "alice", "count": 42}
        assert compute_checksum(data) == compute_checksum(data)

    def test_different_data_different_checksum(self):
        assert compute_checksum({"a": 1}) != compute_checksum({"a": 2})

    def test_key_order_independent(self):
        c1 = compute_checksum({"b": 2, "a": 1})
        c2 = compute_checksum({"a": 1, "b": 2})
        assert c1 == c2


# ── Full Pipeline Tests ──────────────────────────────────────────────────────


class TestProcessPayload:
    """Integration of all pipeline stages."""

    VALID_PAYLOAD = {
        "id": "rec-001",
        "data": {
            "name": "  Alice Smith  ",
            "email": "alice@example.com",
            "password": "supersecret",
        },
    }

    def test_success_result_on_valid_input(self):
        result = process_payload(self.VALID_PAYLOAD)
        assert result.status == "success"

    def test_failed_result_on_invalid_input(self):
        result = process_payload({"bad": "payload"})
        assert result.status == "failed"
        assert len(result.errors) > 0

    def test_normalisation_applied_to_data(self):
        result = process_payload(self.VALID_PAYLOAD)
        assert result.processed_data["name"] == "alice smith"

    def test_redaction_applied(self):
        result = process_payload(self.VALID_PAYLOAD)
        assert result.processed_data["password"] == "***"

    def test_checksum_is_64_char_hex(self):
        result = process_payload(self.VALID_PAYLOAD)
        assert len(result.checksum) == 64

    def test_encrypt_flag_produces_encrypted_blob(self):
        result = process_payload(self.VALID_PAYLOAD, encrypt=True)
        assert result.is_encrypted is True
        assert result.encrypted_blob is not None
        assert result.processed_data is None

    def test_no_encrypt_flag_returns_plain_data(self):
        result = process_payload(self.VALID_PAYLOAD, encrypt=False)
        assert result.is_encrypted is False
        assert result.processed_data is not None
        assert result.encrypted_blob is None

    def test_pipeline_stages_recorded(self):
        result = process_payload(self.VALID_PAYLOAD)
        stage_names = [s.name for s in result.pipeline]
        assert "validation" in stage_names
        assert "normalization" in stage_names
        assert "redaction" in stage_names
        assert "checksum" in stage_names

    def test_encrypted_pipeline_has_five_stages(self):
        result = process_payload(self.VALID_PAYLOAD, encrypt=True)
        assert len(result.pipeline) == 5
        assert result.pipeline[-1].name == "encryption"

    def test_processed_at_is_iso_format(self):
        result = process_payload(self.VALID_PAYLOAD)
        assert "T" in result.processed_at

    def test_extra_top_level_keys_generate_warning(self):
        payload = {**self.VALID_PAYLOAD, "metadata": "extra"}
        result = process_payload(payload)
        assert len(result.warnings) > 0
