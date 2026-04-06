# CipherFlow BDD Feature: Secure Data Processing
# Run: behave tests/features/

Feature: Secure payload processing
  As an authenticated API consumer
  I want to submit data payloads for secure processing
  So that sensitive fields are redacted and outputs are verifiable via checksum

  Background:
    Given the CipherFlow API is running
    And I have valid credentials for user "admin"

  # ── Authentication scenarios ──────────────────────────────────────────────

  Scenario: Successful login returns a JWT token
    When I POST to "/api/v1/auth/token" with username "admin" and password "cipherflow-secret"
    Then the response status should be 200
    And the response should contain an "access_token"
    And the token type should be "bearer"

  Scenario: Login with wrong password is rejected
    When I POST to "/api/v1/auth/token" with username "admin" and password "wrongpass"
    Then the response status should be 401

  # ── Processing scenarios ──────────────────────────────────────────────────

  Scenario: Authenticated user can process a valid payload
    Given I am authenticated as "admin"
    When I submit a payload with id "bdd-001" from source "behave-test"
    And the data contains name "Ashish Khatri" and role "DevOps Engineer"
    Then the response status should be 200
    And the processing status should be "success"
    And the response should contain a checksum of 64 hex characters
    And the data name should be normalised to "ashish khatri"

  Scenario: Unauthenticated request is rejected
    Given I am not authenticated
    When I submit a payload with id "bdd-002" from source "behave-test"
    And the data contains name "test" and role "tester"
    Then the response status should be 401

  Scenario: Payload with missing required fields returns validation errors
    Given I am authenticated as "admin"
    When I submit an incomplete payload missing the "source" field
    Then the response status should be 422
    And the response should contain validation errors

  Scenario: Sensitive password field is redacted in output
    Given I am authenticated as "admin"
    When I submit a payload with id "bdd-003" from source "behave-test"
    And the data contains a "password" field with value "super-secret-123"
    Then the response status should be 200
    And the output data should not contain "super-secret-123"
    And the output data "password" field should contain masked characters

  Scenario: Encrypted processing returns a Fernet blob
    Given I am authenticated as "admin"
    When I submit an encrypted payload with id "bdd-004" from source "behave-test"
    And the data contains name "test" and role "engineer"
    Then the response status should be 200
    And the "encrypted" field should be true
    And the processed output should contain an "encrypted_blob" key
