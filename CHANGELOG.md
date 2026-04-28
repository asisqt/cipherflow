# Changelog

All notable changes to CipherFlow are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/).

## [2.1.0] - 2026-04-23

### Added
- Data classification engine with GDPR, HIPAA, PCI-DSS compliance mapping
- Input sanitizer with XSS and SQL injection detection
- Standardized error catalog with unique CF-prefixed error codes
- Pod priority classes for scheduling during resource contention
- Kubernetes network policies for pod-level isolation
- Pod disruption budgets for zero-downtime maintenance
- Horizontal pod autoscaler (CPU 70%, memory 80%)
- Resource quotas and limit ranges for namespace protection
- RBAC service accounts with least-privilege access
- Kubernetes configmap for runtime configuration
- Graceful shutdown handler for clean pod termination
- Response timing middleware (X-Process-Time header)
- Rate limit headers middleware (X-RateLimit headers)
- Request ID middleware (X-Request-ID header)
- API response envelope for consistent client parsing
- Environment profiles with production security validation
- Custom field type validators with nested detection
- Health check monitoring script
- Prometheus alerting rules for error rate, latency, pod restarts
- Structured JSON logging for log aggregators
- API versioning strategy documentation
- Deployment checklist with pre/post verification
- Production environment template (.env.production)
- MIT license

### Changed
- Docker Compose improved with isolated network and start period
- Backend Dockerfile hardened with start-period, access-log, OCI labels
- Frontend Dockerfile hardened with read-only fs, no-shell user
- README updated with CI/CD and tech stack badges
- SECURITY.md updated with incident response and secret rotation
- CONTRIBUTING.md updated with architecture overview
- pyproject.toml updated with project metadata and classifiers
- .gitignore updated with comprehensive exclusion rules
- Frontend package.json updated with metadata, engines, clean script
- requirements.txt updated with prometheus-client dependency

## [2.0.0] - 2026-04-10

### Added
- Next.js 14 frontend dashboard with Framer Motion animations
- Interactive split-screen layout with pipeline visualization
- Three demo presets (financial, healthcare, user registration)
- Live health status bar with 15s polling
- Frontend multi-stage Dockerfile (~150MB)
- Frontend Kubernetes deployment with LoadBalancer
- 6-stage CI/CD pipeline with path detection and parallel jobs
- Docker layer caching and pip caching in CI/CD

### Changed
- Backend rewritten with clean architecture (core/api/services)
- All endpoints moved under /api/v1 prefix
- CI/CD pipeline optimized from 4min to 12s

## [1.0.0] - 2026-04-06

### Added
- FastAPI backend with 5-stage processing pipeline
- JWT authentication with configurable expiry
- Fernet symmetric encryption (AES-128-CBC)
- PII auto-detection and redaction (12+ field types)
- SHA-256 integrity checksums
- 59 tests (30 unit + 22 integration + 7 BDD)
- Multi-stage backend Dockerfile (~120MB)
- Terraform IaC for DOKS cluster, DOCR registry, firewall
- GitHub Actions CI/CD pipeline
- Kubernetes deployment with health probes
- Swagger UI documentation
