"""
Integration tests for API routes — tests how components interact end-to-end.
Uses FastAPI's TestClient (HTTPX) against a real in-process app instance.
Run: pytest tests/integration/ -v
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
API = "/api/v1"


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_token(username="admin", password="cipherflow-secret") -> str:
    resp = client.post(f"{API}/auth/token", json={"username": username, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


VALID_PAYLOAD = {
    "payload_id": "integ-001",
    "source": "integration-test",
    "data": {"name": "Ashish", "role": "DevOps Engineer"},
}


# ── Health & readiness ────────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_health_returns_200(self):
        resp = client.get(f"{API}/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_health_includes_service_name(self):
        resp = client.get(f"{API}/health")
        assert resp.json()["service"] == "cipherflow"

    def test_ready_returns_200(self):
        resp = client.get(f"{API}/ready")
        assert resp.status_code == 200
        assert resp.json()["ready"] is True


# ── Authentication ────────────────────────────────────────────────────────────

class TestAuthentication:
    def test_valid_credentials_return_token(self):
        resp = client.post(f"{API}/auth/token", json={"username": "admin", "password": "cipherflow-secret"})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_wrong_password_returns_401(self):
        resp = client.post(f"{API}/auth/token", json={"username": "admin", "password": "wrong"})
        assert resp.status_code == 401

    def test_unknown_user_returns_401(self):
        resp = client.post(f"{API}/auth/token", json={"username": "ghost", "password": "x"})
        assert resp.status_code == 401

    def test_demo_user_can_login(self):
        resp = client.post(f"{API}/auth/token", json={"username": "demo", "password": "demo1234"})
        assert resp.status_code == 200


# ── Process endpoint (unauthenticated) ────────────────────────────────────────

class TestProcessUnauthenticated:
    def test_process_without_token_returns_401(self):
        resp = client.post(f"{API}/process", json=VALID_PAYLOAD)
        assert resp.status_code == 401

    def test_process_with_bad_token_returns_401(self):
        resp = client.post(
            f"{API}/process",
            json=VALID_PAYLOAD,
            headers={"Authorization": "Bearer garbage.token.here"},
        )
        assert resp.status_code == 401


# ── Process endpoint (authenticated) ─────────────────────────────────────────

class TestProcessAuthenticated:
    @pytest.fixture(autouse=True)
    def _token(self):
        self.token = get_token()
        self.headers = auth_headers(self.token)

    def test_valid_payload_returns_200(self):
        resp = client.post(f"{API}/process", json=VALID_PAYLOAD, headers=self.headers)
        assert resp.status_code == 200

    def test_response_contains_expected_fields(self):
        resp = client.post(f"{API}/process", json=VALID_PAYLOAD, headers=self.headers)
        body = resp.json()
        for field in ("status", "record_id", "checksum", "processed", "warnings", "encrypted"):
            assert field in body, f"Missing field: {field}"

    def test_status_is_success(self):
        resp = client.post(f"{API}/process", json=VALID_PAYLOAD, headers=self.headers)
        assert resp.json()["status"] == "success"

    def test_record_id_matches_payload_id(self):
        resp = client.post(f"{API}/process", json=VALID_PAYLOAD, headers=self.headers)
        assert resp.json()["record_id"] == VALID_PAYLOAD["payload_id"]

    def test_checksum_is_64_char_hex(self):
        resp = client.post(f"{API}/process", json=VALID_PAYLOAD, headers=self.headers)
        checksum = resp.json()["checksum"]
        assert len(checksum) == 64

    def test_not_encrypted_by_default(self):
        resp = client.post(f"{API}/process", json=VALID_PAYLOAD, headers=self.headers)
        assert resp.json()["encrypted"] is False

    def test_invalid_payload_returns_422(self):
        resp = client.post(f"{API}/process", json={"payload_id": "x"}, headers=self.headers)
        assert resp.status_code == 422

    def test_data_is_normalised(self):
        payload = {**VALID_PAYLOAD, "data": {"city": "  DELHI  "}}
        resp = client.post(f"{API}/process", json=payload, headers=self.headers)
        assert resp.json()["processed"]["data"]["city"] == "delhi"


# ── Encrypted process endpoint ────────────────────────────────────────────────

class TestProcessEncrypted:
    @pytest.fixture(autouse=True)
    def _token(self):
        self.token = get_token()
        self.headers = auth_headers(self.token)

    def test_encrypted_endpoint_returns_200(self):
        resp = client.post(f"{API}/process/encrypted", json=VALID_PAYLOAD, headers=self.headers)
        assert resp.status_code == 200

    def test_encrypted_flag_is_true(self):
        resp = client.post(f"{API}/process/encrypted", json=VALID_PAYLOAD, headers=self.headers)
        assert resp.json()["encrypted"] is True

    def test_encrypted_blob_present(self):
        resp = client.post(f"{API}/process/encrypted", json=VALID_PAYLOAD, headers=self.headers)
        assert "encrypted_blob" in resp.json()["processed"]


# ── Info endpoint ─────────────────────────────────────────────────────────────

class TestInfoEndpoint:
    def test_info_requires_auth(self):
        resp = client.get(f"{API}/info")
        assert resp.status_code == 401

    def test_info_returns_build_data(self):
        token = get_token()
        resp = client.get(f"{API}/info", headers=auth_headers(token))
        assert resp.status_code == 200
        body = resp.json()
        assert body["app"] == "CipherFlow"
        assert "version" in body
        assert "build" in body
