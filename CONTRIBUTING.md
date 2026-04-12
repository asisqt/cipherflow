# Contributing to CipherFlow

## Development Setup

```bash
git clone https://github.com/asisqt/cipherflow.git
cd cipherflow
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Running Tests

```bash
pytest tests/unit/ -v                    # Unit tests
pytest tests/integration/ -v             # Integration tests
behave tests/features/ --no-capture      # BDD tests
ruff check src/ tests/                   # Linting
```

## Branch Strategy

- `main` — production, auto-deploys to DOKS
- `develop` — integration branch
- Feature branches: `feat/your-feature`

## Commit Convention

- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation
- `perf:` performance improvements
- `test:` adding tests
- `ci:` CI/CD changes

## Pull Request Process

1. Fork and create a feature branch
2. Ensure all tests pass locally
3. Update documentation if needed
4. Submit PR against `main`
