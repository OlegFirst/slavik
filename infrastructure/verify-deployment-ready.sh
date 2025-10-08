#!/bin/bash

# Deployment Readiness Verification Script
# Checks all infrastructure components before deployment
# Usage: ./verify-deployment-ready.sh

set -e

echo "🔍 BCM Platform Infrastructure - Deployment Readiness Check"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# Function to check file exists
check_file() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description: $file"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $description: $file NOT FOUND"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    local dir=$1
    local description=$2

    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description: $dir"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $description: $dir NOT FOUND"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check command exists
check_command() {
    local cmd=$1
    local description=$2

    if command -v $cmd &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -n 1)
        echo -e "${GREEN}✓${NC} $description: $version"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $description: $cmd NOT INSTALLED"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to validate YAML
validate_yaml() {
    local file=$1
    local description=$2

    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description: Valid YAML"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $description: Invalid YAML"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check environment variable in .env
check_env_var() {
    local var=$1
    local required=$2

    if [ -f ".env" ]; then
        if grep -q "^${var}=" .env && ! grep -q "^${var}=.*your-.*-here" .env && ! grep -q "^${var}=$" .env; then
            echo -e "${GREEN}✓${NC} Environment: $var configured"
            ((CHECKS_PASSED++))
            return 0
        else
            if [ "$required" = "true" ]; then
                echo -e "${RED}✗${NC} Environment: $var NOT CONFIGURED (required)"
                ((CHECKS_FAILED++))
                return 1
            else
                echo -e "${YELLOW}⚠${NC} Environment: $var not configured (optional)"
                ((WARNINGS++))
                return 0
            fi
        fi
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} .env file not found - copy from .env.example"
            ((CHECKS_FAILED++))
            return 1
        fi
    fi
}

echo "1. Prerequisites Check"
echo "----------------------"
check_command "docker" "Docker"
check_command "docker-compose" "Docker Compose"
check_command "python3" "Python 3"
echo ""

echo "2. Core Infrastructure Files"
echo "-----------------------------"
check_file "docker-compose.full-infrastructure.yml" "Docker Compose config"
check_file "start-all-infrastructure.sh" "Startup script"
check_file ".env.example" "Environment template"
check_file "INFRASTRUCTURE_README.md" "Infrastructure documentation"
check_file "DEPLOYMENT_READY_STATUS.md" "Deployment status"
echo ""

echo "3. YAML Validation"
echo "------------------"
validate_yaml "docker-compose.full-infrastructure.yml" "docker-compose.full-infrastructure.yml"
echo ""

echo "4. Service Directories"
echo "----------------------"
check_dir "observability" "Observability stack"
check_dir "observability/config/prometheus" "Prometheus config"
check_dir "observability/config/grafana" "Grafana config"
check_dir "observability/grafana/dashboards" "Grafana dashboards"
check_dir "observability/notification-service" "Notification service"
echo ""

echo "5. Docker Compose Services Count"
echo "---------------------------------"
SERVICE_COUNT=$(grep -c "container_name:" docker-compose.full-infrastructure.yml)
if [ "$SERVICE_COUNT" -eq 13 ]; then
    echo -e "${GREEN}✓${NC} Found $SERVICE_COUNT services (expected: 13)"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Found $SERVICE_COUNT services (expected: 13)"
    ((CHECKS_FAILED++))
fi
echo ""

echo "6. GitHub Actions Workflows"
echo "---------------------------"
check_file "../.github/workflows/ruff-lint.yml" "Ruff linting workflow"
check_file "../.github/workflows/pytest-tests.yml" "Pytest testing workflow"
check_file "../.github/workflows/bandit-security.yml" "Bandit security workflow"
check_file "../.github/workflows/dependency-check.yml" "Dependency check workflow"
check_file "../.github/workflows/docker-compose-generation.yml" "Docker compose generation workflow"
check_file "../.github/workflows/README.md" "Workflows documentation"
echo ""

echo "7. Environment Configuration"
echo "----------------------------"
if [ -f ".env" ]; then
    echo "Checking .env configuration..."
    check_env_var "SUPABASE_URL" "true"
    check_env_var "SUPABASE_KEY" "true"
    check_env_var "DATABASE_URL" "true"
    check_env_var "REDIS_URL" "true"
    check_env_var "QDRANT_URL" "true"
    check_env_var "QDRANT_API_KEY" "true"
    check_env_var "ANTHROPIC_API_KEY" "false"
    check_env_var "SMTP_HOST" "false"
    check_env_var "GITHUB_TOKEN" "false"
else
    echo -e "${YELLOW}⚠${NC} .env file not found"
    echo "   → Copy .env.example to .env and configure required variables"
    ((WARNINGS++))
fi
echo ""

echo "8. Port Availability Check"
echo "--------------------------"
REQUIRED_PORTS=(8000 8100 3000 9090 9093 3100 8035 8051 8052 8053 8046 8200)
for port in "${REQUIRED_PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Port $port is already in use"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✓${NC} Port $port is available"
        ((CHECKS_PASSED++))
    fi
done
echo ""

echo "9. Observability Configuration"
echo "------------------------------"
check_file "observability/config/prometheus/prometheus.yml" "Prometheus config"
check_file "observability/config/alertmanager/alertmanager.yml" "AlertManager config"
check_file "observability/docker-compose.monitoring.yml" "Monitoring docker-compose"

# Count Prometheus scrape targets
if [ -f "observability/config/prometheus/prometheus.yml" ]; then
    SCRAPE_JOBS=$(grep "job_name:" observability/config/prometheus/prometheus.yml | wc -l | tr -d ' ')
    echo -e "${GREEN}✓${NC} Prometheus monitoring $SCRAPE_JOBS services"
    ((CHECKS_PASSED++))
fi

# Count Grafana dashboards
if [ -d "observability/grafana/dashboards" ]; then
    DASHBOARD_COUNT=$(ls -1 observability/grafana/dashboards/*.json 2>/dev/null | wc -l | tr -d ' ')
    echo -e "${GREEN}✓${NC} Found $DASHBOARD_COUNT Grafana dashboards"
    ((CHECKS_PASSED++))
fi
echo ""

echo "10. Script Permissions"
echo "----------------------"
if [ -x "start-all-infrastructure.sh" ]; then
    echo -e "${GREEN}✓${NC} start-all-infrastructure.sh is executable"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} start-all-infrastructure.sh is not executable"
    echo "   → Run: chmod +x start-all-infrastructure.sh"
    ((CHECKS_FAILED++))
fi

if [ -x "verify-deployment-ready.sh" ]; then
    echo -e "${GREEN}✓${NC} verify-deployment-ready.sh is executable"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} verify-deployment-ready.sh is not executable"
    ((WARNINGS++))
fi
echo ""

# Summary
echo "============================================================"
echo "📊 VERIFICATION SUMMARY"
echo "============================================================"
echo -e "${GREEN}✓ Passed:${NC}  $CHECKS_PASSED"
echo -e "${RED}✗ Failed:${NC}  $CHECKS_FAILED"
echo -e "${YELLOW}⚠ Warnings:${NC} $WARNINGS"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ DEPLOYMENT READY!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Configure .env file (if not done): cp .env.example .env"
    echo "  2. Deploy infrastructure: ./start-all-infrastructure.sh"
    echo "  3. Check status: ./start-all-infrastructure.sh --status"
    echo "  4. Open Grafana: http://localhost:3000 (admin/admin)"
    echo ""
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ DEPLOYMENT NOT READY${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Please fix the failed checks above before deploying."
    echo ""
    exit 1
fi
