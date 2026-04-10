"""
BDD Step Definitions
=====================
Implements the Gherkin steps for the secure_processing.feature file.
"""

from behave import given, when, then


# ── Background Steps ─────────────────────────────────────────────────────────

@given("the CipherFlow API is running")
def step_api_running(context):
    resp = context.client.get("/")
    assert resp.status_code == 200


@given("I have valid admin credentials")
def step_have_credentials(context):
    context.username = "admin"
    context.password = "cipherflow-secret"


# ── Authentication Steps ─────────────────────────────────────────────────────

@when('I request a token with username "{username}" and password "{password}"')
def step_request_token(context, username, password):
    context.response = context.client.post(
        f"{context.api}/auth/token",
        json={"username": username, "password": password},
    )


@then("I receive a valid JWT token")
def step_receive_token(context):
    assert context.response.status_code == 200
    data = context.response.json()
    assert "access_token" in data
    context.token = data["access_token"]


@then('the token type is "{token_type}"')
def step_token_type(context, token_type):
    data = context.response.json()
    assert data["token_type"] == token_type


@then("I receive a 401 error")
def step_401_error(context):
    assert context.response.status_code == 401


@then("I receive a 422 error")
def step_422_error(context):
    assert context.response.status_code == 422


# ── Auth Helper ──────────────────────────────────────────────────────────────

@given('I am authenticated as "{username}"')
def step_authenticated(context, username):
    passwords = {"admin": "cipherflow-secret", "demo": "demo1234"}
    resp = context.client.post(
        f"{context.api}/auth/token",
        json={"username": username, "password": passwords[username]},
    )
    assert resp.status_code == 200
    context.token = resp.json()["access_token"]
    context.headers = {"Authorization": f"Bearer {context.token}"}


# ── Processing Steps ─────────────────────────────────────────────────────────

@when('I submit a payload with id "{record_id}" and data')
def step_submit_payload(context, record_id):
    data = {}
    for row in context.table:
        data[row["field"].strip()] = row["value"].strip()
    context.response = context.client.post(
        f"{context.api}/process",
        json={"id": record_id, "data": data},
        headers=context.headers,
    )


@when('I submit an encrypted payload with id "{record_id}" and data')
def step_submit_encrypted(context, record_id):
    data = {}
    for row in context.table:
        data[row["field"].strip()] = row["value"].strip()
    context.response = context.client.post(
        f"{context.api}/process/encrypted",
        json={"id": record_id, "data": data},
        headers=context.headers,
    )


@when("I submit a payload missing the data field")
def step_submit_missing_data(context):
    context.response = context.client.post(
        f"{context.api}/process",
        json={"id": "rec-bad"},
        headers=context.headers,
    )


# ── Response Assertion Steps ─────────────────────────────────────────────────

@then('the response status is "{status}"')
def step_response_status(context, status):
    data = context.response.json()
    assert data["status"] == status


@then('the name field is normalized to "{expected}"')
def step_name_normalized(context, expected):
    data = context.response.json()
    assert data["processed_data"]["name"] == expected


@then('the password field is redacted to "{expected}"')
def step_password_redacted(context, expected):
    data = context.response.json()
    assert data["processed_data"]["password"] == expected


@then("a 64-character checksum is present")
def step_checksum_present(context):
    data = context.response.json()
    assert len(data["checksum"]) == 64


@then("the pipeline contains {count:d} stages")
def step_pipeline_count(context, count):
    data = context.response.json()
    assert len(data["pipeline"]) == count


@then("the payload is encrypted")
def step_payload_encrypted(context):
    data = context.response.json()
    assert data["is_encrypted"] is True


@then("an encrypted blob is present")
def step_blob_present(context):
    data = context.response.json()
    assert data["encrypted_blob"] is not None


# ── Health Steps ─────────────────────────────────────────────────────────────

@when("I check the API health")
def step_check_health(context):
    context.response = context.client.get(f"{context.api}/health")


@then('the health status is "{status}"')
def step_health_status(context, status):
    data = context.response.json()
    assert data["status"] == status


@then('the service name is "{name}"')
def step_service_name(context, name):
    data = context.response.json()
    assert data["service"] == name
