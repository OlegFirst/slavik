#!/bin/bash

# BCM Platform Services - Status Check Script
# This script checks the status of all services

echo "📊 BCM Platform Services Status"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Show container status
docker-compose ps

echo ""
echo "🔍 Health Check Results:"
echo "===================================="

check_health() {
    local name=$1
    local url=$2

    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name: Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $name: Unhealthy or not running${NC}"
        return 1
    fi
}

check_health "Planning Service" "http://localhost:8011/health"
check_health "Plans Service" "http://localhost:8023/health"
check_health "Prometheus" "http://localhost:9090/-/healthy"
check_health "Grafana" "http://localhost:3000/api/health"

echo ""
echo "🗄️  Database Status:"
echo "===================================="

if docker-compose exec -T postgres pg_isready -U bcm_user > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL: Ready${NC}"
else
    echo -e "${RED}❌ PostgreSQL: Not ready${NC}"
fi

if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis: Ready${NC}"
else
    echo -e "${RED}❌ Redis: Not ready${NC}"
fi

echo ""
