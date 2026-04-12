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

- JWT authentication with HS256 signing
- Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256)
- PII auto-detection and redaction (12+ field types)
- SHA-256 integrity checksums
- Non-root Docker containers
- Kubernetes secrets for sensitive config
- Network firewall restricting inbound to HTTP/HTTPS/K8s API only
- GitHub push protection preventing secret leaks
