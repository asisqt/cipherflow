# CipherFlow API Usage Examples

Quick reference for interacting with the CipherFlow API using curl.

## Authentication

    # Get a JWT token
    curl -X POST http://YOUR_API_URL/api/v1/auth/token \
      -H "Content-Type: application/json" \
      -d '{"username": "admin", "password": "cipherflow-secret"}'

    # Response:
    # {"access_token": "eyJhbG...", "token_type": "bearer", "expires_in": 3600}

## Process Data (without encryption)

    curl -X POST http://YOUR_API_URL/api/v1/process \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "id": "txn-001",
        "data": {
          "name": "Ashish Khatri",
          "email": "ashish@example.com",
          "password": "secret123",
          "credit_card": "4111-1111-1111-1111"
        }
      }'

    # Result: password and credit_card redacted to "***"
    # Name normalized to lowercase, whitespace stripped
    # SHA-256 checksum generated for integrity

## Process Data (with encryption)

    curl -X POST http://YOUR_API_URL/api/v1/process/encrypted \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "id": "patient-001",
        "data": {
          "name": "Priya Sharma",
          "ssn": "987-65-4321",
          "diagnosis": "Type 2 Diabetes"
        }
      }'

    # Result: entire processed payload encrypted into a Fernet blob
    # Only someone with the encryption key can decrypt it

## Health Check

    curl http://YOUR_API_URL/api/v1/health

    # Response:
    # {"status": "ok", "service": "cipherflow", "version": "2.0.0", "uptime_seconds": 3600}

## Python Example

    import requests

    API = "http://YOUR_API_URL/api/v1"

    # Login
    auth = requests.post(f"{API}/auth/token", json={
        "username": "admin",
        "password": "cipherflow-secret"
    })
    token = auth.json()["access_token"]

    # Process
    result = requests.post(
        f"{API}/process",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": "rec-001",
            "data": {"name": "Test User", "password": "secret", "email": "test@test.com"}
        }
    )
    print(result.json())

## JavaScript Example

    const API = "http://YOUR_API_URL/api/v1";

    // Login
    const auth = await fetch(API + "/auth/token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: "admin", password: "cipherflow-secret" })
    });
    const { access_token } = await auth.json();

    // Process
    const result = await fetch(API + "/process", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token
        },
        body: JSON.stringify({
            id: "rec-001",
            data: { name: "Test User", password: "secret", email: "test@test.com" }
        })
    });
    console.log(await result.json());
