# System BCM - Makefile for Automation
# All common tasks automated

.PHONY: help install test lint format build deploy clean health validate performance

# Default target
.DEFAULT_GOAL := help

# Colors for output
GREEN  := \033[0;32m
YELLOW := \033[1;33m
RED    := \033[0;31m
BLUE   := \033[0;34m
NC     := \033[0m # No Color

##@ Help

help: ## Display this help
	@echo "$(BLUE)╔═══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║   System BCM - Automated Tasks                       ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make $(YELLOW)<target>$(NC)\n\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Development

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing dev dependencies...$(NC)"
	pip install black flake8 mypy pylint pytest pytest-cov pytest-asyncio bandit safety
	@echo "$(GREEN)✅ Dev dependencies installed$(NC)"

format: ## Format code with Black
	@echo "$(BLUE)Formatting code...$(NC)"
	black --line-length 100 .
	@echo "$(GREEN)✅ Code formatted$(NC)"

lint: ## Run all linters
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "$(YELLOW)→ Black (formatting check)$(NC)"
	black --check --line-length 100 .
	@echo "$(YELLOW)→ Flake8 (style)$(NC)"
	flake8 --max-line-length=100 --ignore=E501,W503 .
	@echo "$(YELLOW)→ MyPy (type checking)$(NC)"
	mypy --ignore-missing-imports .
	@echo "$(YELLOW)→ Pylint (code quality)$(NC)"
	pylint --max-line-length=100 --disable=C0111,R0903 system_bcm/ learning/
	@echo "$(GREEN)✅ All linters passed$(NC)"

security: ## Run security scans
	@echo "$(BLUE)Running security scans...$(NC)"
	@echo "$(YELLOW)→ Safety (dependency vulnerabilities)$(NC)"
	safety check
	@echo "$(YELLOW)→ Bandit (code security)$(NC)"
	bandit -r . -f screen
	@echo "$(GREEN)✅ Security scans complete$(NC)"

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	pytest tests/ -v
	@echo "$(GREEN)✅ All tests passed$(NC)"

test-unit: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/test_unit*.py -v
	@echo "$(GREEN)✅ Unit tests passed$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/test_integration*.py -v
	@echo "$(GREEN)✅ Integration tests passed$(NC)"

test-performance: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	pytest tests/test_performance.py -v -s
	@echo "$(GREEN)✅ Performance tests passed$(NC)"

test-coverage: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report generated: htmlcov/index.html$(NC)"

##@ Docker

build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t system-bcm-service:latest .
	docker build -t system-bcm-service:$(shell date +%Y%m%d) .
	@echo "$(GREEN)✅ Docker image built$(NC)"

build-no-cache: ## Build Docker image without cache
	@echo "$(BLUE)Building Docker image (no cache)...$(NC)"
	docker build --no-cache -t system-bcm-service:latest .
	@echo "$(GREEN)✅ Docker image built$(NC)"

push: ## Push Docker image (requires registry config)
	@echo "$(BLUE)Pushing Docker image...$(NC)"
	docker tag system-bcm-service:latest ${DOCKER_REGISTRY}/system-bcm-service:latest
	docker push ${DOCKER_REGISTRY}/system-bcm-service:latest
	@echo "$(GREEN)✅ Docker image pushed$(NC)"

##@ Deployment

deploy: ## Deploy System BCM (automated)
	@echo "$(BLUE)╔═══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║   Deploying System BCM Service                       ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════════╝$(NC)"
	./integrate-with-platform.sh

deploy-manual: ## Deploy manually (docker-compose)
	@echo "$(BLUE)Deploying with docker-compose...$(NC)"
	docker network create platform_network || true
	docker-compose up -d
	@echo "$(GREEN)✅ System BCM deployed$(NC)"

stop: ## Stop System BCM service
	@echo "$(BLUE)Stopping System BCM...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ System BCM stopped$(NC)"

restart: ## Restart System BCM service
	@echo "$(BLUE)Restarting System BCM...$(NC)"
	docker-compose restart system-bcm
	@echo "$(GREEN)✅ System BCM restarted$(NC)"

logs: ## View System BCM logs
	@echo "$(BLUE)Viewing logs (Ctrl+C to exit)...$(NC)"
	docker-compose logs -f system-bcm

##@ Validation

health: ## Run health check
	@echo "$(BLUE)Running health check...$(NC)"
	./health-check.sh

validate: ## Run full deployment validation
	@echo "$(BLUE)Running full validation (40+ tests)...$(NC)"
	./validate-deployment.sh

performance: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(NC)"
	pytest tests/test_performance.py -v -s --benchmark

##@ Operations

cycle: ## Trigger BCM cycle manually
	@echo "$(BLUE)Triggering BCM cycle...$(NC)"
	curl -X POST http://localhost:8050/cycle/trigger | jq
	@echo "$(GREEN)✅ BCM cycle triggered$(NC)"

recovery: ## Trigger test recovery
	@echo "$(BLUE)Triggering test recovery...$(NC)"
	curl -X POST http://localhost:8050/recovery/trigger \
		-H "Content-Type: application/json" \
		-d '{"service": "test", "incident_type": "test"}' | jq
	@echo "$(GREEN)✅ Recovery triggered$(NC)"

insights: ## View generated insights
	@echo "$(BLUE)Fetching insights...$(NC)"
	curl http://localhost:8050/insights | jq

metrics: ## View Prometheus metrics
	@echo "$(BLUE)Fetching metrics...$(NC)"
	curl http://localhost:8050/metrics | grep system_bcm

status: ## Check service status
	@echo "$(BLUE)Checking status...$(NC)"
	curl http://localhost:8050/status | jq

##@ Monitoring

grafana: ## Open Grafana dashboard
	@echo "$(BLUE)Opening Grafana...$(NC)"
	open http://localhost:3000

prometheus: ## Open Prometheus UI
	@echo "$(BLUE)Opening Prometheus...$(NC)"
	open http://localhost:9090

dashboard: ## Open System BCM API docs
	@echo "$(BLUE)Opening Swagger docs...$(NC)"
	open http://localhost:8050/docs

##@ Cleanup

clean: ## Clean temporary files
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -delete
	find . -type f -name '.coverage' -delete
	find . -type d -name 'htmlcov' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

clean-all: clean ## Clean everything including Docker
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	docker-compose down -v
	docker volume prune -f
	@echo "$(GREEN)✅ All cleaned$(NC)"

reset: clean-all deploy ## Reset and redeploy
	@echo "$(GREEN)✅ System reset and redeployed$(NC)"

##@ Database

db-shell: ## Access PostgreSQL shell
	@echo "$(BLUE)Opening PostgreSQL shell...$(NC)"
	docker exec -it postgresql psql -U postgres -d platform

redis-shell: ## Access Redis CLI
	@echo "$(BLUE)Opening Redis CLI...$(NC)"
	docker exec -it system-bcm-redis redis-cli

##@ Documentation

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "Documentation files:"
	@ls -lh *.md | awk '{printf "  - %-50s %6s\n", $$9, $$5}'
	@echo "$(GREEN)✅ Documentation ready$(NC)"

readme: ## View README
	@cat README.md

##@ CI/CD

ci: lint test security ## Run full CI pipeline locally
	@echo "$(GREEN)✅ CI pipeline completed$(NC)"

cd: build validate deploy ## Run full CD pipeline
	@echo "$(GREEN)✅ CD pipeline completed$(NC)"

pipeline: ci cd ## Run full CI/CD pipeline
	@echo "$(GREEN)✅ Full pipeline completed$(NC)"

##@ Backup & Restore

backup: ## Backup scenarios and config
	@echo "$(BLUE)Creating backup...$(NC)"
	tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		scenarios/ .env docker-compose.yml
	@echo "$(GREEN)✅ Backup created$(NC)"

restore: ## Restore from backup (requires BACKUP_FILE=backup.tar.gz)
	@echo "$(BLUE)Restoring from $(BACKUP_FILE)...$(NC)"
	tar -xzf $(BACKUP_FILE)
	@echo "$(GREEN)✅ Restored from backup$(NC)"

##@ Quick Tasks

quick-start: install build deploy validate ## Quick start (install, build, deploy, validate)
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║   ✅ QUICK START COMPLETE                             ║$(NC)"
	@echo "$(GREEN)║   System BCM is deployed and validated!              ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════╝$(NC)"

dev: install-dev format lint test ## Development setup (install dev deps, format, lint, test)
	@echo "$(GREEN)✅ Development environment ready$(NC)"

prod: ci build deploy validate ## Production deployment (CI, build, deploy, validate)
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║   ✅ PRODUCTION DEPLOYMENT COMPLETE                    ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════╝$(NC)"

check: health status metrics ## Quick check (health, status, metrics)
	@echo "$(GREEN)✅ Health check complete$(NC)"
