# CipherFlow Testing Strategy

## Testing Pyramid

    ┌─────────────────┐
    │   7 BDD Tests   │  ← User workflow validation (behave + Gherkin)
    ├─────────────────┤
    │ 22 Integration  │  ← HTTP lifecycle through FastAPI TestClient
    ├─────────────────┤
    │  30+ Unit Tests  │  ← Individual function logic (pytest)
    └─────────────────┘

## Test Categories

### Unit Tests (tests/unit/)
- **Purpose:** Verify individual functions in isolation
- **Framework:** pytest 8.2.0
- **Coverage tool:** pytest-cov 5.0.0
- **Threshold:** 40% minimum (enforced in CI)
- **What's tested:**
  - Payload validation (required fields, types, email format)
  - String normalization (whitespace, casing, nested structures)
  - Sensitive field redaction (12+ field patterns)
  - SHA-256 checksum generation and determinism
  - Full pipeline orchestration with timing

### Integration Tests (tests/integration/)
- **Purpose:** Verify full HTTP request/response cycle
- **Framework:** pytest + FastAPI TestClient
- **What's tested:**
  - Authentication flow (login, token validation, rejection)
  - Protected endpoint access (Bearer token enforcement)
  - Processing with and without encryption
  - Error handling (422 for bad payloads, 401/403 for auth)
  - Response schema compliance

### BDD Tests (tests/features/)
- **Purpose:** Validate user-facing workflows in plain English
- **Framework:** Behave 1.2.6 with Gherkin syntax
- **What's tested:**
  - End-to-end authentication scenario
  - Data processing with field-level assertions
  - Encrypted processing with blob verification
  - Invalid input rejection
  - Health check verification

## Running Tests

    make test             # All tests
    make test-unit        # Unit only with coverage
    make test-integration # Integration only
    make test-bdd         # BDD scenarios only
    make lint             # Static analysis with ruff

## CI/CD Integration

Tests run automatically on every push via GitHub Actions:
1. Lint job runs ruff in parallel with test job
2. Test job runs unit → integration → BDD sequentially
3. Coverage report uploaded as build artifact
4. Build and deploy only proceed if all tests pass

## Adding New Tests

- Unit tests: Add to tests/unit/test_*.py matching the module under test
- Integration tests: Add to tests/integration/test_api_routes.py
- BDD scenarios: Add to tests/features/secure_processing.feature with steps in tests/features/steps/
