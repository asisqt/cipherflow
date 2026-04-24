# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.0.x   | Yes       |
| < 2.0   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email: 1060ashish@gmail.com
3. Include steps to reproduce and potential impact
4. Allow 48 hours for initial response

## Security Measures

- JWT authentication with HS256 signing and configurable expiry
- Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256)
- PII auto-detection and redaction (12+ field types)
- SHA-256 integrity checksums for tamper detection
- XSS and SQL injection detection in input sanitizer
- Non-root Docker containers (cipherflow user, nextjs user)
- Kubernetes secrets for sensitive configuration
- Network policies for pod-level isolation
- Pod disruption budgets for availability during maintenance
- Resource quotas preventing namespace resource exhaustion
- Network firewall restricting inbound to HTTP/HTTPS/K8s API only
- GitHub push protection preventing secret leaks
- Request ID tracing via X-Request-ID header
- Response timing via X-Process-Time header

## Incident Response

1. **Detection**: Monitor health endpoints and pod logs for anomalies
2. **Containment**: Scale down affected deployment, rotate compromised secrets
3. **Recovery**: Redeploy from last known good commit SHA
4. **Post-mortem**: Document timeline, root cause, and preventive measures

## Secret Rotation

Rotate these credentials periodically:
- JWT SECRET_KEY (invalidates all active tokens)
- ENCRYPTION_KEY (requires re-encryption of stored data)
- DigitalOcean API token
- GitHub Personal Access Token
- Container registry credentials
