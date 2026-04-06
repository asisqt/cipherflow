"""
Behave environment + step definitions for CipherFlow BDD tests.
Run: behave tests/features/
"""

import json
from fastapi.testclient import TestClient
from behave import given, when, then

from src.main import app

API = "/api/v1"

# ── Behave hooks ──────────────────────────────────────────────────────────────

def before_scenario(context, scenario):
    """Fresh TestClient per scenario — no shared state."""
    context.client  = TestClient(app)
    context.token   = None
    context.response = None
    context.payload = {}


# ── Given ─────────────────────────────────────────────────────────────────────

@given('the CipherFlow API is running')
def step_api_running(context):
    resp = context.client.get(f"{API}/health")
    assert resp.status_code == 200, "API is not running"


@given('I have valid credentials for user "{username}"')
def step_have_credentials(context, username):
    context.username = username


@given('I am authenticated as "{username}"')
def step_authenticated(context, username):
    passwords = {"admin": "cipherflow-secret", "demo": "demo1234"}
    resp = context.client.post(
        f"{API}/auth/token",
        json={"username": username, "password": passwords[username]},
    )
    assert resp.status_code == 200
    context.token = resp.json()["access_token"]


@given('I am not authenticated')
def step_not_authenticated(context):
    context.token = None


# ── When ──────────────────────────────────────────────────────────────────────

@when('I POST to "{path}" with username "{username}" and password "{password}"')
def step_post_login(context, path, username, password):
    context.response = context.client.post(
        path, json={"username": username, "password": password}
    )


@when('I submit a payload with id "{pid}" from source "{source}"')
def step_set_payload(context, pid, source):
    context.payload = {"payload_id": pid, "source": source, "data": {}}


@when('I submit an encrypted payload with id "{pid}" from source "{source}"')
def step_set_encrypted_payload(context, pid, source):
    context.payload = {"payload_id": pid, "source": source, "data": {}}
    context.encrypted = True


@when('the data contains name "{name}" and role "{role}"')
def step_add_data(context, name, role):
    context.payload["data"]["name"] = name
    context.payload["data"]["role"] = role
    headers = {}
    if context.token:
        headers["Authorization"] = f"Bearer {context.token}"
    endpoint = f"{API}/process/encrypted" if getattr(context, "encrypted", False) else f"{API}/process"
    context.response = context.client.post(endpoint, json=context.payload, headers=headers)


@when('the data contains a "{field}" field with value "{value}"')
def step_add_sensitive_field(context, field, value):
    context.payload["data"][field] = value
    headers = {}
    if context.token:
        headers["Authorization"] = f"Bearer {context.token}"
    context.response = context.client.post(
        f"{API}/process", json=context.payload, headers=headers
    )


@when('I submit an incomplete payload missing the "{field}" field')
def step_incomplete_payload(context, field):
    payload = {"payload_id": "incomplete-001", "source": "behave", "data": {"k": "v"}}
    del payload[field]
    headers = {}
    if context.token:
        headers["Authorization"] = f"Bearer {context.token}"
    context.response = context.client.post(f"{API}/process", json=payload, headers=headers)


# ── Then ──────────────────────────────────────────────────────────────────────

@then('the response status should be {code:d}')
def step_check_status(context, code):
    actual = context.response.status_code
    assert actual == code, f"Expected {code}, got {actual}: {context.response.text}"


@then('the response should contain an "{key}"')
def step_response_contains_key(context, key):
    body = context.response.json()
    assert key in body, f"Key '{key}' not in response: {body}"


@then('the token type should be "{token_type}"')
def step_token_type(context, token_type):
    assert context.response.json()["token_type"] == token_type


@then('the processing status should be "{expected}"')
def step_processing_status(context, expected):
    assert context.response.json()["status"] == expected


@then('the response should contain a checksum of 64 hex characters')
def step_checksum(context):
    checksum = context.response.json()["checksum"]
    assert len(checksum) == 64
    assert all(c in "0123456789abcdef" for c in checksum)


@then('the data name should be normalised to "{expected}"')
def step_normalised(context, expected):
    data = context.response.json()["processed"]["data"]
    assert data.get("name") == expected, f"Got: {data.get('name')}"


@then('the response should contain validation errors')
def step_validation_errors(context):
    body = context.response.json()
    assert "detail" in body


@then('the output data should not contain "{value}"')
def step_not_contain_value(context, value):
    body = json.dumps(context.response.json()["processed"])
    assert value not in body, f"Sensitive value '{value}' found in output"


@then('the output data "{field}" field should contain masked characters')
def step_field_masked(context, field):
    data = context.response.json()["processed"].get("data", {})
    assert "*" in str(data.get(field, "")), f"Field '{field}' is not masked: {data}"


@then('the "{field}" field should be true')
def step_field_true(context, field):
    assert context.response.json()[field] is True


@then('the processed output should contain an "{key}" key')
def step_output_key(context, key):
    processed = context.response.json()["processed"]
    assert key in processed, f"Key '{key}' not in processed: {processed}"
