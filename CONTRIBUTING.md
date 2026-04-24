# Contributing to CipherFlow

## Architecture Overview

    Browser --> Next.js Frontend (port 3000)
                    |
                    v (REST API calls)
               FastAPI Backend (port 8000)
                    |
                    v
               Processing Pipeline
               Validate -> Normalize -> Redact -> Checksum -> Encrypt

## Project Structure

    src/core/       Config, security, middleware, logging
    src/api/        Routes, dependencies, request schemas
    src/services/   Business logic, data processor, sanitizer
    frontend/       Next.js dashboard with Tailwind + Framer Motion
    k8s/            Kubernetes manifests (deployments, services, policies)
    infrastructure/ Terraform IaC (DOKS, DOCR, firewall)
    tests/          Unit (30), integration (22), BDD (7)

## Development Setup

    git clone https://github.com/asisqt/cipherflow.git
    cd cipherflow
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    make dev              # backend on :8000
    make dev-frontend     # frontend on :3000

## Running Tests

    make test             # all tests
    make test-unit        # unit only
    make test-integration # integration only
    make test-bdd         # BDD only
    make lint             # linter

## Branch Strategy

- main: production, auto-deploys to DOKS
- develop: integration branch
- Feature branches: feat/your-feature
- Hotfix branches: fix/issue-description

## Commit Convention (Conventional Commits)

- feat: new features
- fix: bug fixes
- docs: documentation changes
- perf: performance improvements
- test: adding or updating tests
- ci: CI/CD pipeline changes
- infra: infrastructure changes
- deps: dependency updates
- security: security improvements
- dx: developer experience improvements

## Pull Request Process

1. Fork and create a feature branch from develop
2. Ensure all tests pass locally (make test)
3. Ensure linter passes (make lint)
4. Update documentation if needed
5. Write meaningful commit messages following convention
6. Submit PR against develop (or main for hotfixes)
7. Wait for CI pipeline to pass before requesting review

## Code Style

- Python: enforced by ruff (see pyproject.toml)
- TypeScript: enforced by Next.js built-in linting
- Max line length: 100 characters
- Use type hints on all Python function signatures
- Use docstrings on all public modules and functions
