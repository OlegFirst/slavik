#!/bin/bash

# Health Check All Services
# Usage: ./scripts/health_check_all.sh

echo "🏥 AI-Platform BCM - Health Check All Services"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
TOTAL=0
HEALTHY=0
UNHEALTHY=0

check_service() {
    local name=$1
    local url=$2

    TOTAL=$((TOTAL + 1))

    echo -n "Checking $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)

    if [ "$response" = "200" ] || [ "$response" = "204" ]; then
        echo -e "${GREEN}✅ Healthy${NC} (HTTP $response)"
        HEALTHY=$((HEALTHY + 1))
    else
        echo -e "${RED}❌ Unhealthy${NC} (HTTP $response)"
        UNHEALTHY=$((UNHEALTHY + 1))
    fi
}

echo "📊 Infrastructure Services"
echo "-------------------------"
check_service "PostgreSQL" "http://localhost:5432" || echo "  (Database - check manually)"
check_service "Redis" "http://localhost:6379" || echo "  (Redis - check manually)"
check_service "API Gateway" "http://localhost:3001/health"
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3002/api/health"

echo ""
echo "💼 Platform Services"
echo "-------------------"
check_service "BIA Service" "http://localhost:8001/health"
check_service "Risk Service" "http://localhost:8002/health"
check_service "Compliance Service" "http://localhost:8003/health"
check_service "Documents Service" "http://localhost:8004/health"
check_service "Response Service" "http://localhost:8005/health"
check_service "Validation Service" "http://localhost:8006/health"
check_service "Governance Service" "http://localhost:8007/health"
check_service "Planning Service" "http://localhost:8008/health"
check_service "Plans Service" "http://localhost:8009/health"
check_service "Learning Service" "http://localhost:8010/health"
check_service "Community Service" "http://localhost:8011/health"

echo ""
echo "🧠 Intelligent Core"
echo "------------------"
check_service "Workflow Intelligence" "http://localhost:9001/health"
check_service "AI Experts" "http://localhost:9002/health"
check_service "Coordination Center" "http://localhost:8004/health"
check_service "Learning System" "http://localhost:9003/health"
check_service "Predictive Services" "http://localhost:9004/health"

echo ""
echo "🖥️  Human Interface"
echo "------------------"
check_service "Web Application" "http://localhost:3001"

echo ""
echo "=============================================="
echo "📊 Summary:"
echo "  Total services: $TOTAL"
echo -e "  ${GREEN}Healthy: $HEALTHY${NC}"
echo -e "  ${RED}Unhealthy: $UNHEALTHY${NC}"

if [ $UNHEALTHY -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Some services are unhealthy. Check logs.${NC}"
    exit 1
fi
