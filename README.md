# CipherFlow



**Secure Data Processing Pipeline**

A production-grade, cloud-native application demonstrating enterprise DevOps practices: JWT authentication, Fernet encryption, PII redaction, CI/CD automation, Infrastructure as Code, and Kubernetes orchestration.

> **Live**: [http://64.225.84.36](http://64.225.84.36) &nbsp;|&nbsp; **Docs**: [/docs](http://64.225.84.36/docs)

---

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────┐
│   Browser    │────▶│           Next.js Frontend                   │
│              │◀────│   Landing · Auth · Dashboard · Animations    │
└─────────────┘     └──────────────┬───────────────────────────────┘
                                   │ REST API
                    ┌──────────────▼───────────────────────────────┐
                    │           FastAPI Backend                     │
                    │   /auth/token  /process  /process/encrypted  │
                    └──────────────┬───────────────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────────────┐
                    │       5-Stage Processing Pipeline             │
                    │                                               │
                    │  Validate → Normalize → Redact → Checksum    │
                    │                                 → Encrypt     │
                    └──────────────────────────────────────────────┘
```

## Tech Stack

| Layer          | Technology                                           |
|----------------|------------------------------------------------------|
| Frontend       | Next.js 14, React 18, Tailwind CSS, Framer Motion   |
| Backend        | Python 3.12, FastAPI, Pydantic, Uvicorn              |
| Security       | JWT (python-jose), Fernet (cryptography), bcrypt     |
| Testing        | pytest (unit + integration), Behave (BDD), ruff      |
| Containers     | Docker multi-stage builds, Docker Compose             |
| Orchestration  | Kubernetes (DigitalOcean DOKS)                       |
| Infrastructure | Terraform (DOKS cluster, DOCR registry, firewall)    |
| CI/CD          | GitHub Actions (lint → test → build → deploy)        |
| Registry       | DigitalOcean Container Registry (DOCR)               |

## Processing Pipeline

Every payload passes through a five-stage pipeline with per-stage timing metrics:

1. **Validation** — Structural checks: required fields, type enforcement, email format validation
2. **Normalization** — Whitespace stripping, Unicode lowercasing across nested structures
3. **Redaction** — PII detection and masking (`password`, `ssn`, `credit_card`, `cvv`, `token`, `pin`, etc.)
4. **Checksum** — SHA-256 integrity hash of canonicalized JSON for tamper detection
5. **Encryption** *(optional)* — Fernet symmetric encryption producing an opaque, decryptable blob

## Project Structure

```
cipherflow/
├── .github/workflows/
│   └── ci_cd_pipeline.yml           # 4-stage CI/CD: lint → test → build → deploy
├── infrastructure/
│   ├── main.tf                      # DOKS cluster + DOCR registry
│   ├── variables.tf                 # Parameterized configuration
│   └── security.tf                  # Firewall rules and security groups
├── src/
│   ├── main.py                      # FastAPI application entry point
│   ├── api/
│   │   ├── routes.py                # All HTTP endpoints with Pydantic schemas
│   │   └── dependencies.py          # JWT Bearer authentication middleware
│   ├── core/
│   │   ├── config.py                # Environment variable management (Pydantic Settings)
│   │   └── security_utils.py        # JWT, Fernet, checksums, user auth
│   └── services/
│       └── data_processor.py        # 5-stage processing pipeline with timing
├── tests/
│   ├── unit/
│   │   └── test_data_processor.py   # 30 unit tests (TDD)
│   ├── integration/
│   │   └── test_api_routes.py       # 22 integration tests (HTTP lifecycle)
│   └── features/
│       ├── secure_processing.feature # 7 BDD scenarios (Gherkin)
│       ├── environment.py
│       └── steps/processing_steps.py
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Root layout with dark theme
│   │   ├── page.tsx                 # Landing + Auth + Dashboard (SPA)
│   │   └── globals.css              # Tailwind + custom animations
│   ├── lib/api.ts                   # Typed API client + demo presets
│   ├── Dockerfile                   # Multi-stage Next.js build
│   └── package.json
├── k8s/
│   ├── api-deployment.yaml          # Backend pods + ClusterIP service
│   ├── frontend-deployment.yaml     # Frontend pods + LoadBalancer service
│   └── secrets.yaml                 # Kubernetes secrets template
├── Dockerfile                       # Multi-stage backend build (~120MB)
├── docker-compose.yml               # Local development stack
├── requirements.txt                 # Pinned Python dependencies
└── README.md
```

## API Endpoints

| Method | Path                       | Auth | Description                     |
|--------|----------------------------|------|---------------------------------|
| GET    | `/`                        | No   | API info and documentation link |
| POST   | `/api/v1/auth/token`       | No   | Obtain JWT access token         |
| POST   | `/api/v1/process`          | Yes  | Process payload (4 stages)      |
| POST   | `/api/v1/process/encrypted`| Yes  | Process + encrypt (5 stages)    |
| GET    | `/api/v1/health`           | No   | Health check + uptime           |
| GET    | `/api/v1/ready`            | No   | Kubernetes readiness probe      |
| GET    | `/api/v1/info`             | Yes  | Build and deployment info       |
| GET    | `/docs`                    | No   | Swagger UI                      |

## Quick Start

### Local Development

```bash
# Clone
git clone https://github.com/asisqt/cipherflow.git
cd cipherflow

# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm run dev

# Or use Docker Compose
docker-compose up --build
```

### Run Tests

```bash
# Unit tests with coverage
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Integration tests
pytest tests/integration/ -v

# BDD tests
behave tests/features/ --no-capture

# Lint
ruff check src/ tests/
```

## CI/CD Pipeline

Every push to `main` triggers a four-stage automated pipeline:

```
┌─────────┐    ┌─────────┐    ┌──────────────┐    ┌────────────┐
│  Lint    │───▶│  Test   │───▶│ Build & Push │───▶│ Deploy to  │
│  (ruff)  │    │ 59 tests│    │  (DOCR)      │    │   DOKS     │
└─────────┘    └─────────┘    └──────────────┘    └────────────┘
```

- **Lint**: ruff static analysis
- **Test**: 30 unit + 22 integration + 7 BDD tests
- **Build**: Multi-stage Docker images pushed to DOCR with SHA tags
- **Deploy**: Rolling update to Kubernetes with health-check gating

## Infrastructure as Code

Terraform provisions all cloud resources:

```bash
cd infrastructure
terraform init
terraform plan -var "do_token=$DO_TOKEN"
terraform apply -var "do_token=$DO_TOKEN" -auto-approve
```

**Resources provisioned**:
- DigitalOcean Kubernetes cluster (blr1 region)
- Container registry for Docker images
- Firewall rules (HTTPS, HTTP, K8s API only)

## Security Features

- **Authentication**: JWT Bearer tokens with configurable expiration
- **Encryption**: Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256)
- **PII Redaction**: Automatic detection and masking of 12+ sensitive field types
- **Integrity**: SHA-256 checksums for tamper detection
- **Infrastructure**: Non-root Docker containers, K8s secrets, network firewall
- **CI/CD**: GitHub push protection, no secrets in code

## Demo Credentials

| Username | Password           |
|----------|--------------------|
| admin    | cipherflow-secret  |
| demo     | demo1234           |
| analyst  | analyst-pass       |

---

Built by **Ashish Khatri** — [GitHub](https://github.com/asisqt) · [LinkedIn](https://linkedin.com/in/ashishkhatri)
# Last verified: Fri Apr 10 22:11:02 UTC 2026
