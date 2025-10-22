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

down: ## Stop all services
	docker compose down

logs: ## View logs from all services
	docker compose logs -f

logs-api: ## View logs from API service only
	docker compose logs -f api

migrate: ## Run database migrations
	docker compose exec api alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create msg="your message")
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

test: ## Run tests (to be implemented)
	docker compose exec api pytest

clean: ## Remove all containers and volumes
	docker compose down -v
	docker system prune -f

restart: ## Restart all services
	docker compose restart

restart-api: ## Restart API service only
	docker compose restart api


create-admin: ## Create an admin user (usage: make create-admin email=your_email password=your_password)
	docker compose exec api python scripts/create_admin.py
