Feature: Secure Data Processing Pipeline
  As an API consumer
  I want to process sensitive data through CipherFlow
  So that it is validated, normalized, redacted, and optionally encrypted

  Background:
    Given the CipherFlow API is running
    And I have valid admin credentials

  Scenario: Successful authentication
    When I request a token with username "admin" and password "cipherflow-secret"
    Then I receive a valid JWT token
    And the token type is "bearer"

  Scenario: Failed authentication with wrong password
    When I request a token with username "admin" and password "wrong-password"
    Then I receive a 401 error

  Scenario: Process a valid payload without encryption
    Given I am authenticated as "admin"
    When I submit a payload with id "rec-001" and data:
      | field    | value              |
      | name     |   Alice Smith      |
      | email    | alice@example.com  |
      | password | supersecret        |
    Then the response status is "success"
    And the name field is normalized to "alice smith"
    And the password field is redacted to "***"
    And a 64-character checksum is present
    And the pipeline contains 4 stages

  Scenario: Process a valid payload with encryption
    Given I am authenticated as "admin"
    When I submit an encrypted payload with id "rec-002" and data:
      | field    | value              |
      | name     | Bob Johnson        |
      | email    | bob@example.com    |
      | ssn      | 123-45-6789        |
    Then the response status is "success"
    And the payload is encrypted
    And an encrypted blob is present
    And the pipeline contains 5 stages

  Scenario: Reject invalid payload missing required fields
    Given I am authenticated as "admin"
    When I submit a payload missing the data field
    Then I receive a 422 error

  Scenario: Health check returns OK
    When I check the API health
    Then the health status is "ok"
    And the service name is "cipherflow"
