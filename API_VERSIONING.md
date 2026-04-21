# API Versioning Strategy

## Current Version: v1

All endpoints are prefixed with /api/v1/.

## Versioning Policy

CipherFlow follows URI-based versioning:

- v1 (current): Stable, production-ready endpoints
- v2 (planned): Will include batch processing and webhook support

## Deprecation Policy

- Minor versions: backward-compatible additions (new fields, new endpoints)
- Major versions: breaking changes (removed fields, changed schemas)
- Deprecated versions remain available for 6 months after successor release
- Deprecation warnings via X-API-Deprecation response header

## Version Negotiation

Clients specify the version in the URI path:

    POST /api/v1/process        Current stable
    POST /api/v2/process        Future version (not yet available)

## Changelog

### v1.0.0 (Initial Release)
- POST /api/v1/auth/token
- POST /api/v1/process
- POST /api/v1/process/encrypted
- GET /api/v1/health
- GET /api/v1/ready
- GET /api/v1/info

### v2.0.0 (Planned)
- POST /api/v2/batch - Process multiple payloads
- POST /api/v2/webhooks - Register callback URLs
- GET /api/v2/audit - Query processing audit log
