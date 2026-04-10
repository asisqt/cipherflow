"""
Integration Tests — API Routes
================================
Tests the full HTTP request/response cycle through FastAPI's TestClient.
Covers authentication, processing, encryption, health, and error handling.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
API = "/api/v1"


def get_token(username: str = "admin", password: str = "cipherflow-secret") -> str:
    """Helper: authenticate and return a Bearer token."""
    resp = client.post(f"{API}/auth/token", json={
        "username": username,
        "password": password,
    })
    assert resp.status_code == 200, f"Auth failed: {resp.text}"
    return resp.json()["access_token"]


# ── Root ─────────────────────────────────────────────────────────────────────


class TestRootEndpoint:
    def test_root_returns_200(self):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_root_contains_service_name(self):
        data = client.get("/").json()
        assert "CipherFlow" in data["message"]


# ── Health ───────────────────────────────────────────────────────────────────


class TestHealthEndpoints:
    def test_health_returns_200(self):
        resp = client.get(f"{API}/health")
        assert resp.status_code == 200

    def test_health_includes_service_name(self):
        data = client.get(f"{API}/health").json()
        assert data["service"] == "cipherflow"
        assert data["status"] == "ok"

    def test_ready_returns_200(self):
        resp = client.get(f"{API}/ready")
        assert resp.status_code == 200


# ── Authentication ───────────────────────────────────────────────────────────


class TestAuthentication:
    def test_valid_credentials_return_token(self):
        resp = client.post(f"{API}/auth/token", json={
            "username": "admin",
            "password": "cipherflow-secret",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_wrong_password_returns_401(self):
        resp = client.post(f"{API}/auth/token", json={
            "username": "admin",
            "password": "wrong",
        })
        assert resp.status_code == 401

    def test_unknown_user_returns_401(self):
        resp = client.post(f"{API}/auth/token", json={
            "username": "ghost",
            "password": "x",
        })
        assert resp.status_code == 401

    def test_demo_user_can_login(self):
        resp = client.post(f"{API}/auth/token", json={
            "username": "demo",
            "password": "demo1234",
        })
        assert resp.status_code == 200


# ── Process (Unauthenticated) ────────────────────────────────────────────────


class TestProcessUnauthenticated:
    def test_process_without_token_returns_403(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {"name": "Alice"},
        })
        assert resp.status_code == 403

    def test_process_with_bad_token_returns_401(self):
        resp = client.post(
            f"{API}/process",
            json={"id": "rec-001", "data": {"name": "Alice"}},
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert resp.status_code == 401


# ── Process (Authenticated) ──────────────────────────────────────────────────


class TestProcessAuthenticated:
    @pytest.fixture(autouse=True)
    def _token(self):
        self.token = get_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_valid_payload_returns_200(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {"name": "Alice", "email": "alice@example.com"},
        }, headers=self.headers)
        assert resp.status_code == 200

    def test_response_contains_expected_fields(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {"name": "Alice", "email": "alice@example.com"},
        }, headers=self.headers)
        data = resp.json()
        assert "status" in data
        assert "record_id" in data
        assert "checksum" in data
        assert "pipeline" in data

    def test_status_is_success(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {"name": "Test", "email": "test@test.com"},
        }, headers=self.headers)
        assert resp.json()["status"] == "success"

    def test_record_id_matches_payload_id(self):
        resp = client.post(f"{API}/process", json={
            "id": "my-unique-id",
            "data": {"name": "Test", "email": "t@t.com"},
        }, headers=self.headers)
        assert resp.json()["record_id"] == "my-unique-id"

    def test_checksum_is_64_char_hex(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {"name": "Test", "email": "t@t.com"},
        }, headers=self.headers)
        checksum = resp.json()["checksum"]
        assert len(checksum) == 64

    def test_not_encrypted_by_default(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {"name": "Test", "email": "t@t.com"},
        }, headers=self.headers)
        assert resp.json()["is_encrypted"] is False

    def test_invalid_payload_returns_422(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {},
        }, headers=self.headers)
        assert resp.status_code == 422

    def test_data_is_normalised(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {"name": "  ALICE  ", "email": "a@b.com"},
        }, headers=self.headers)
        assert resp.json()["processed_data"]["name"] == "alice"

    def test_sensitive_fields_redacted(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {"name": "Alice", "password": "secret", "email": "a@b.com"},
        }, headers=self.headers)
        assert resp.json()["processed_data"]["password"] == "***"

    def test_pipeline_stages_present(self):
        resp = client.post(f"{API}/process", json={
            "id": "rec-001",
            "data": {"name": "Test", "email": "t@t.com"},
        }, headers=self.headers)
        stages = [s["name"] for s in resp.json()["pipeline"]]
        assert "validation" in stages
        assert "normalization" in stages
        assert "redaction" in stages
        assert "checksum" in stages


# ── Encrypted Process ────────────────────────────────────────────────────────


class TestProcessEncrypted:
    @pytest.fixture(autouse=True)
    def _token(self):
        self.token = get_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_encrypted_endpoint_returns_200(self):
        resp = client.post(f"{API}/process/encrypted", json={
            "id": "rec-001",
            "data": {"name": "Alice", "email": "a@b.com"},
        }, headers=self.headers)
        assert resp.status_code == 200

    def test_encrypted_flag_is_true(self):
        resp = client.post(f"{API}/process/encrypted", json={
            "id": "rec-001",
            "data": {"name": "Alice", "email": "a@b.com"},
        }, headers=self.headers)
        assert resp.json()["is_encrypted"] is True

    def test_encrypted_blob_present(self):
        resp = client.post(f"{API}/process/encrypted", json={
            "id": "rec-001",
            "data": {"name": "Alice", "email": "a@b.com"},
        }, headers=self.headers)
        data = resp.json()
        assert data["encrypted_blob"] is not None
        assert data["processed_data"] is None

    def test_encrypted_pipeline_has_five_stages(self):
        resp = client.post(f"{API}/process/encrypted", json={
            "id": "rec-001",
            "data": {"name": "Alice", "email": "a@b.com"},
        }, headers=self.headers)
        stages = resp.json()["pipeline"]
        assert len(stages) == 5
        assert stages[-1]["name"] == "encryption"


# ── Info Endpoint ────────────────────────────────────────────────────────────


class TestInfoEndpoint:
    def test_info_requires_auth(self):
        resp = client.get(f"{API}/info")
        assert resp.status_code == 403

    def test_info_returns_build_data(self):
        token = get_token()
        resp = client.get(
            f"{API}/info",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "version" in data
        assert "endpoints" in data
