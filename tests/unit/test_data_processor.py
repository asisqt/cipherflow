"""
Unit tests for data_processor.py — TDD style.
Tests cover individual functions in isolation with no external dependencies.
Run: pytest tests/unit/ -v
"""

import pytest
from src.services.data_processor import (
    ProcessingStatus,
    process_payload,
    validate_payload,
    _compute_checksum,
    _normalise_strings,
    _redact_sensitive_keys,
)


# ── validate_payload ──────────────────────────────────────────────────────────

class TestValidatePayload:
    def test_valid_payload_returns_no_errors(self):
        raw = {"payload_id": "p1", "data": {"name": "Ashish"}, "source": "test"}
        assert validate_payload(raw) == []

    def test_missing_all_required_fields(self):
        errors = validate_payload({})
        assert any("Missing required fields" in e for e in errors)

    def test_missing_single_field(self):
        raw = {"payload_id": "p1", "data": {"k": "v"}}  # missing source
        errors = validate_payload(raw)
        assert any("source" in e for e in errors)

    def test_payload_id_must_be_string(self):
        raw = {"payload_id": 999, "data": {"k": "v"}, "source": "x"}
        errors = validate_payload(raw)
        assert any("payload_id" in e for e in errors)

    def test_data_must_be_dict(self):
        raw = {"payload_id": "p1", "data": "not-a-dict", "source": "x"}
        errors = validate_payload(raw)
        assert any("data must be an object" in e for e in errors)

    def test_empty_data_dict_is_invalid(self):
        raw = {"payload_id": "p1", "data": {}, "source": "x"}
        errors = validate_payload(raw)
        assert any("empty" in e for e in errors)

    def test_invalid_email_in_data(self):
        raw = {"payload_id": "p1", "data": {"email": "not-an-email"}, "source": "x"}
        errors = validate_payload(raw)
        assert any("email" in e for e in errors)

    def test_valid_email_passes(self):
        raw = {"payload_id": "p1", "data": {"email": "user@example.com"}, "source": "x"}
        assert validate_payload(raw) == []


# ── _normalise_strings ────────────────────────────────────────────────────────

class TestNormaliseStrings:
    def test_strips_whitespace(self):
        result = _normalise_strings({"name": "  Ashish  "})
        assert result["name"] == "ashish"

    def test_lowercases_values(self):
        result = _normalise_strings({"city": "DELHI"})
        assert result["city"] == "delhi"

    def test_nested_dict(self):
        result = _normalise_strings({"address": {"city": "  Mumbai  "}})
        assert result["address"]["city"] == "mumbai"

    def test_non_string_values_untouched(self):
        result = _normalise_strings({"count": 42, "flag": True})
        assert result["count"] == 42
        assert result["flag"] is True


# ── _redact_sensitive_keys ────────────────────────────────────────────────────

class TestRedactSensitiveKeys:
    def test_password_is_masked(self):
        result = _redact_sensitive_keys({"password": "super-secret"})
        assert "super-secret" not in result["password"]
        assert "*" in result["password"]

    def test_non_sensitive_key_unchanged(self):
        result = _redact_sensitive_keys({"username": "admin"})
        assert result["username"] == "admin"

    def test_custom_sensitive_set(self):
        result = _redact_sensitive_keys({"card": "1234"}, sensitive={"card"})
        assert "1234" not in result["card"]


# ── _compute_checksum ─────────────────────────────────────────────────────────

class TestComputeChecksum:
    def test_returns_64_char_hex(self):
        checksum = _compute_checksum({"a": 1})
        assert len(checksum) == 64
        assert all(c in "0123456789abcdef" for c in checksum)

    def test_same_data_same_checksum(self):
        data = {"z": 3, "a": 1, "m": 2}
        assert _compute_checksum(data) == _compute_checksum(data)

    def test_different_data_different_checksum(self):
        assert _compute_checksum({"a": 1}) != _compute_checksum({"a": 2})


# ── process_payload ───────────────────────────────────────────────────────────

class TestProcessPayload:
    def _valid(self, **overrides):
        base = {"payload_id": "p1", "data": {"name": "Test"}, "source": "unit-test"}
        return {**base, **overrides}

    def test_success_result_on_valid_input(self):
        result = process_payload(self._valid())
        assert result.status == ProcessingStatus.SUCCESS
        assert result.record_id == "p1"
        assert result.checksum != ""

    def test_failed_result_on_invalid_input(self):
        result = process_payload({})
        assert result.status == ProcessingStatus.FAILED
        assert len(result.warnings) > 0

    def test_normalisation_applied_to_data(self):
        result = process_payload(self._valid(data={"name": "  DELHI  "}))
        assert result.processed["data"]["name"] == "delhi"

    def test_encrypt_flag_produces_encrypted_blob(self):
        result = process_payload(self._valid(), encrypt=True)
        assert result.encrypted is True
        assert "encrypted_blob" in result.processed

    def test_no_encrypt_flag_returns_plain_data(self):
        result = process_payload(self._valid())
        assert result.encrypted is False
        assert "data" in result.processed

    def test_extra_top_level_keys_generate_warning(self):
        raw = self._valid()
        raw["unexpected_field"] = "surprise"
        result = process_payload(raw)
        assert any("unexpected" in w.lower() for w in result.warnings)

    def test_processed_at_is_iso_format(self):
        from datetime import datetime
        result = process_payload(self._valid())
        # Should parse without error
        datetime.fromisoformat(result.processed_at)
