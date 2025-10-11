#!/bin/bash
# AI Platform ISO - Health Check All Services
# Checks health status of all running services
# Date: 2025-10-11

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🏥 AI Platform ISO - Health Check"
echo "=================================="
echo ""

# Services to check with their ports
declare -A SERVICES=(
    ["Service Discovery"]="8500"
    ["Message Queue"]="8061"
    ["Realtime WebSocket"]="8053"
    ["Workflow Engine"]="8036"
    ["AI Orchestration"]="8031"
    ["Coordination Center"]="8032"
    ["System BCM"]="8052"
    ["Community Intelligence"]="8035"
    ["BIA Service"]="8010"
    ["Compliance Service"]="8011"
    ["Governance Service"]="8012"
    ["Risk Service"]="8013"
    ["Response Service"]="8014"
    ["Documents Service"]="8015"
    ["Plans Service"]="8016"
    ["Orchestrator"]="8059"
    ["Agent Router"]="8057"
    ["Analytics Specialist"]="8058"
)

healthy=0
unhealthy=0

for service in "${!SERVICES[@]}"; do
    port="${SERVICES[$service]}"

    # Try to get health status
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${port}/health" 2>/dev/null || echo "000")

    if [ "$response" == "200" ]; then
        echo -e "${GREEN}✅ ${service} (${port})${NC}"
        ((healthy++))
    else
        echo -e "${RED}❌ ${service} (${port}) - HTTP ${response}${NC}"
        ((unhealthy++))
    fi
done

echo ""
echo "=================================="
echo -e "Summary: ${GREEN}${healthy} healthy${NC} | ${RED}${unhealthy} unhealthy${NC}"
echo ""

if [ $unhealthy -eq 0 ]; then
    echo -e "${GREEN}🎉 All services are healthy!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some services are not responding${NC}"
    echo "💡 Check logs: docker-compose -f docker-compose.full-stack.yml logs -f"
    exit 1
fi
