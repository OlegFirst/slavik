# BCM Platform MVP Makefile
.PHONY: help build up down logs clean test bootstrap eventbus orchestrator smoke

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)BCM Platform MVP - Available Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Environment setup
env: ## Copy .env.example to .env
	@cp .env.example .env
	@echo "$(GREEN)✓ Environment file created$(NC)"

# Docker commands (Local Development Only - Not for Railway deployment)
build: ## Build all Docker images (local development only)
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker compose -f docker-compose-configs/docker-compose.mvp.yml build
	@echo "$(GREEN)✓ Build complete$(NC)"

up: ## Start all services
	@echo "$(BLUE)Starting BCM Platform services...$(NC)"
	@docker compose -f docker-compose-configs/docker-compose.mvp.yml up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "$(BLUE)Waiting for services to be healthy...$(NC)"
	@sleep 10
	@make status

down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	@docker compose -f docker-compose-configs/docker-compose.mvp.yml down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart: down up ## Restart all services

logs: ## Show logs for all services
	@docker compose -f docker-compose-configs/docker-compose.mvp.yml logs -f

logs-eventbus: ## Show EventBus logs
	@docker compose -f docker-compose-configs/docker-compose.mvp.yml logs -f eventbus

logs-orchestrator: ## Show Orchestrator logs
	@docker compose -f docker-compose-configs/docker-compose.mvp.yml logs -f orchestrator

status: ## Check services status
	@echo "$(BLUE)Service Status:$(NC)"
	@echo -n "PostgreSQL: "; \
		(docker compose -f docker-compose-configs/docker-compose.mvp.yml exec -T postgres pg_isready > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Redis: "; \
		(docker compose -f docker-compose-configs/docker-compose.mvp.yml exec -T redis redis-cli ping > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "EventBus: "; \
		(curl -sf http://localhost:8001/health > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Orchestrator: "; \
		(curl -sf http://localhost:8002/health > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Frontend: "; \
		(curl -sf http://localhost:8081 > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Odoo: "; \
		(curl -sf http://localhost:8069 > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"

# Development commands
dev-eventbus: ## Run EventBus in development mode
	@cd backend/eventbus && \
		pip install -r requirements.txt && \
		uvicorn main:app --reload --port 8001

dev-orchestrator: ## Run Orchestrator in development mode
	@cd backend/orchestrator_service && \
		pip install -r requirements.txt && \
		uvicorn main:app --reload --port 8002

dev-frontend: ## Run Frontend in development mode
	@cd frontend/web_portal && \
		npm install && \
		npm run serve

# Testing
test-eventbus: ## Test EventBus endpoints
	@echo "$(BLUE)Testing EventBus...$(NC)"
	@curl -X POST http://localhost:8001/api/events/publish \
		-H "Content-Type: application/json" \
		-d '{"event_type":"bcm.test","tenant_id":"test","data":{"message":"Test event"}}' | jq
	@echo "$(GREEN)✓ EventBus test complete$(NC)"

test-orchestrator: ## Test Orchestrator endpoints
	@echo "$(BLUE)Testing Orchestrator...$(NC)"
	@curl -X POST http://localhost:8002/api/recommendations \
		-H "Content-Type: application/json" \
		-d '{"context":"BIA analysis","data":{},"tenant_id":"test"}' | jq
	@echo "$(GREEN)✓ Orchestrator test complete$(NC)"

test-e2e: ## Run E2E tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	@cd tests && pytest test_e2e_mvp.py -v
	@echo "$(GREEN)✓ E2E tests complete$(NC)"

# Database operations
db-init: ## Initialize databases
	@echo "$(BLUE)Initializing databases...$(NC)"
	@docker compose -f docker-compose-configs/docker-compose.mvp.yml exec -T postgres psql -U bcm -c "SELECT 1"
	@echo "$(GREEN)✓ Database initialized$(NC)"

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	@cd backend/eventbus && alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

# Cleanup
clean: ## Clean up containers and volumes
	@echo "$(RED)Cleaning up...$(NC)"
	@docker compose -f docker-compose-configs/docker-compose.mvp.yml down -v
	@docker system prune -f
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# Quick start
quickstart: env build up ## Quick start: setup env, build and start all services
	@echo "$(GREEN)"
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║           BCM Platform MVP is ready!                      ║"
	@echo "╠══════════════════════════════════════════════════════════╣"
	@echo "║  Frontend:      http://localhost:8081                     ║"
	@echo "║  EventBus API:  http://localhost:8001/docs                ║"
	@echo "║  Orchestrator:  http://localhost:8002/docs                ║"
	@echo "║  Odoo:          http://localhost:8069                     ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo "$(NC)"

# Security overlay
up-sec: ## Start with security overlay (Keycloak/Vault/Nginx)
	@echo "$(BLUE)Starting services with security overlay...$(NC)"
	@docker compose -f docker-compose-configs/docker-compose.mvp.yml -f security/docker-compose.security.yml up -d
	@echo "$(GREEN)✓ Services with security started$(NC)"

smoke: ## Run smoke tests on BCM modules
	python -m bcm_bia
	python -m bcm_plans
	python -m bcm_incident
	python -m bcm_audit
	python -m bcm_kpi
	@python -c "import requests as r; print(r.get('http://localhost:8001/health').status_code)" 2>/dev/null || echo "EventBus not running"

status: ## Check services status
	@echo "$(BLUE)Service Status:$(NC)"
	@echo -n "PostgreSQL: "; \
		(docker compose -f docker-compose-configs/docker-compose.mvp.yml exec -T postgres pg_isready > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Redis: "; \
		(docker compose -f docker-compose-configs/docker-compose.mvp.yml exec -T redis redis-cli ping > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "EventBus: "; \
		(curl -sf http://localhost:8001/health > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Orchestrator: "; \
		(curl -sf http://localhost:8002/health > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Frontend: "; \
		(curl -sf http://localhost:8081 > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"
	@echo -n "Odoo: "; \
		(curl -sf http://localhost:8069 > /dev/null 2>&1 && echo "$(GREEN)✓ Healthy$(NC)") || echo "$(RED)✗ Unhealthy$(NC)"

monitor: ## Monitor all services
	@watch -n 2 make status

# BCM module utilities
bootstrap:
	python -m pip install -U pip pip-tools
	pip-sync requirements.lock

eventbus:
	pip-sync backend/eventbus/requirements.lock
	uvicorn backend.eventbus.main:app --host 0.0.0.0 --port 8001

orchestrator:
	pip-sync backend/orchestrator/requirements.lock
	uvicorn backend.orchestrator.api_endpoints:app --host 0.0.0.0 --port 8002

test:
	pytest -q tests/smoke
