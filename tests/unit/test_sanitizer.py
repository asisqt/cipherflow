"""
Unit Tests — Input Sanitizer
==============================
Tests for XSS prevention, SQL injection detection,
and recursive payload sanitization.
"""

from src.services.sanitizer import (
    strip_html_tags,
    detect_injection,
    sanitize_payload,
)


class TestStripHtmlTags:
    def test_removes_script_tags(self):
        assert strip_html_tags("<script>alert('xss')</script>") == "alert('xss')"

    def test_removes_nested_tags(self):
        assert strip_html_tags("<div><b>text</b></div>") == "text"

    def test_preserves_plain_text(self):
        assert strip_html_tags("hello world") == "hello world"

    def test_handles_empty_string(self):
        assert strip_html_tags("") == ""


class TestDetectInjection:
    def test_detects_xss_javascript(self):
        threats = detect_injection("javascript:alert(1)")
        assert "xss" in threats

    def test_detects_xss_event_handler(self):
        threats = detect_injection("onload=steal()")
        assert "xss" in threats

    def test_detects_sql_injection(self):
        threats = detect_injection("'; SELECT * FROM users; --")
        assert "sql_injection" in threats

    def test_clean_input_returns_empty(self):
        threats = detect_injection("Ashish Khatri")
        assert threats == []


class TestSanitizePayload:
    def test_strips_tags_from_values(self):
        data = {"name": "<b>Ashish</b>", "email": "a@b.com"}
        sanitized, _ = sanitize_payload(data)
        assert sanitized["name"] == "Ashish"

    def test_warns_on_xss(self):
        data = {"bio": "javascript:alert(1)"}
        _, warnings = sanitize_payload(data)
        assert any("xss" in w for w in warnings)

    def test_handles_nested_dicts(self):
        data = {"user": {"name": "<script>x</script>"}}
        sanitized, _ = sanitize_payload(data)
        assert sanitized["user"]["name"] == "x"

    def test_handles_lists(self):
        data = {"tags": ["<b>admin</b>", "user"]}
        sanitized, _ = sanitize_payload(data)
        assert sanitized["tags"] == ["admin", "user"]

    def test_non_string_values_untouched(self):
        data = {"count": 42, "active": True}
        sanitized, warnings = sanitize_payload(data)
        assert sanitized["count"] == 42
        assert warnings == []
