.PHONY: help dev test lint build push deploy clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Run backend locally
	uvicorn src.main:app --reload --port 8000

dev-frontend: ## Run frontend locally
	cd frontend && npm run dev

test: ## Run all tests
	pytest tests/unit/ -v --cov=src --cov-report=term-missing
	pytest tests/integration/ -v
	behave tests/features/ --no-capture

test-unit: ## Run unit tests only
	pytest tests/unit/ -v --cov=src --cov-report=term-missing

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-bdd: ## Run BDD tests only
	behave tests/features/ --no-capture

lint: ## Run linter
	ruff check src/ tests/

lint-fix: ## Auto-fix lint issues
	ruff check --fix src/ tests/

build: ## Build Docker images
	docker build -t cipherflow-api .
	docker build -t cipherflow-frontend ./frontend

up: ## Start local stack with Docker Compose
	docker-compose up --build

down: ## Stop local stack
	docker-compose down

clean: ## Remove cache and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage coverage.xml htmlcov/
	rm -rf frontend/.next frontend/node_modules
