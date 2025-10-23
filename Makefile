.PHONY: help build up down logs migrate shell test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker compose build

up: ## Start all services
	docker compose up -d

up-build: ## Build and start all services
	docker compose up -d --build

down: ## Stop all services
	docker compose down

logs: ## View logs from all services
	docker compose logs -f

logs-api: ## View logs from API service only
	docker compose logs -f api

migrate: ## Run database migrations
	docker compose exec api alembic upgrade head

generate: ## Create new migration (usage: make generate msg="your message")
	docker compose exec api alembic revision --autogenerate -m "$(msg)"

migrate-rollback: ## Rollback last migration
	docker compose exec api alembic downgrade -1

shell: ## Open Python shell in API container
	docker compose exec api python

db-shell: ## Open PostgreSQL shell
	docker compose exec db psql -U postgres -d coffee_shop

redis-cli: ## Open Redis CLI
	docker compose exec redis redis-cli

celery-logs: ## View Celery worker logs
	docker compose logs -f celery_worker

restart: ## Restart all services
	docker compose restart

restart-api: ## Restart API service only
	docker compose restart api

test: ## Run all tests
	docker compose exec api pytest

test-unit: ## Run unit tests only
	docker compose exec api pytest tests/unit/

test-integration: ## Run integration tests only
	docker compose exec api pytest tests/integration/

test-e2e: ## Run end-to-end tests only
	docker compose exec api pytest tests/e2e/

test-cov: ## Run tests with coverage report
	docker compose exec api pytest --cov=app --cov-report=html --cov-report=term

test-cov-html: ## Run tests with HTML coverage report and open it
	docker compose exec api pytest --cov=app --cov-report=html
	@echo "Opening coverage report..."
	@open htmlcov/index.html || xdg-open htmlcov/index.html || start htmlcov/index.html

test-verbose: ## Run tests with verbose output
	docker compose exec api pytest -vv

test-failed: ## Run only failed tests from last run
	docker compose exec api pytest --lf


ruff: ## Run ruff linter
	docker compose exec api ruff check .
