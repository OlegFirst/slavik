#!/bin/bash
# AI Platform ISO - Check Prerequisites
# Validates system requirements before startup
# Date: 2025-10-11

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🔍 Checking prerequisites..."
echo ""

errors=0
warnings=0

# Check Docker
if command -v docker &> /dev/null; then
    docker_version=$(docker --version | awk '{print $3}' | tr -d ',')
    echo -e "${GREEN}✅ Docker found: ${docker_version}${NC}"
else
    echo -e "${RED}❌ Docker not found${NC}"
    echo "   Install from: https://docs.docker.com/get-docker/"
    ((errors++))
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version | awk '{print $4}' | tr -d ',')
    echo -e "${GREEN}✅ docker-compose found: ${compose_version}${NC}"
else
    echo -e "${RED}❌ docker-compose not found${NC}"
    echo "   Install from: https://docs.docker.com/compose/install/"
    ((errors++))
fi

# Check Docker daemon
if docker info &> /dev/null; then
    echo -e "${GREEN}✅ Docker daemon running${NC}"
else
    echo -e "${RED}❌ Docker daemon not running${NC}"
    echo "   Start Docker Desktop or run: sudo systemctl start docker"
    ((errors++))
fi

# Check .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"

    # Check required variables
    if grep -q "DATABASE_URL=" "$PROJECT_ROOT/.env" && \
       grep -q "REDIS_URL=" "$PROJECT_ROOT/.env" && \
       grep -q "ANTHROPIC_API_KEY=" "$PROJECT_ROOT/.env"; then
        echo -e "${GREEN}✅ Required environment variables present${NC}"

        # Check if API key is set
        if grep -q "ANTHROPIC_API_KEY=your_api_key_here" "$PROJECT_ROOT/.env" || \
           grep -q "ANTHROPIC_API_KEY=$" "$PROJECT_ROOT/.env"; then
            echo -e "${YELLOW}⚠️  ANTHROPIC_API_KEY not configured${NC}"
            echo "   AI features may not work without API key"
            ((warnings++))
        fi
    else
        echo -e "${RED}❌ Missing required environment variables in .env${NC}"
        echo "   Required: DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY"
        ((errors++))
    fi
else
    echo -e "${RED}❌ .env file not found${NC}"
    echo "   Create .env file in project root"
    ((errors++))
fi

# Check port availability
echo ""
echo "🔌 Checking port availability..."

critical_ports=(6379 8500 8061 8036 8031 9090 3000)
ports_in_use=()

for port in "${critical_ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        ports_in_use+=($port)
    fi
done

if [ ${#ports_in_use[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All critical ports available${NC}"
else
    echo -e "${YELLOW}⚠️  Ports in use: ${ports_in_use[*]}${NC}"
    echo "   These ports need to be free to start services"
    ((warnings++))
fi

# Check disk space
echo ""
echo "💾 Checking disk space..."
available_space=$(df -h . | tail -1 | awk '{print $4}')
echo "   Available: $available_space"

if df -h . | tail -1 | awk '{print $5}' | grep -q '9[0-9]%\|100%'; then
    echo -e "${YELLOW}⚠️  Low disk space${NC}"
    ((warnings++))
else
    echo -e "${GREEN}✅ Sufficient disk space${NC}"
fi

# Summary
echo ""
echo "=================================="
if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo "   Ready to start full stack"
    exit 0
elif [ $errors -eq 0 ]; then
    echo -e "${YELLOW}⚠️  ${warnings} warnings${NC}"
    echo "   You can proceed but some features may be limited"
    exit 0
else
    echo -e "${RED}❌ ${errors} errors, ${warnings} warnings${NC}"
    echo "   Fix errors before starting"
    exit 1
fi
