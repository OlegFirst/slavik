#!/bin/bash
# ============================================================================
# Docker Health Test - Test all container health endpoints
# ============================================================================
# Usage: ./docker-test-health.sh
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Health Check - AI-Powered BCM Platform      ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if containers are running
if ! docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
    echo -e "${RED}❌ No containers are running${NC}"
    echo -e "${YELLOW}Start containers first:${NC}"
    echo -e "   docker-compose -f docker-compose.production.yml up -d"
    exit 1
fi

# Track results
PASSED=0
FAILED=0
WARNINGS=0
FAILED_SERVICES=()

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    printf "%-40s" "$name"

    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)

    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL (HTTP $response)${NC}"
        FAILED=$((FAILED + 1))
        FAILED_SERVICES+=("$name")
        return 1
    fi
}

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Core Infrastructure${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Redis" "http://localhost:6379" || true
test_endpoint "EventBus" "http://localhost:8001/health"
test_endpoint "API Gateway" "http://localhost:8000/health"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Platform Services (Business Logic)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Planning Service" "http://localhost:8011/health"
test_endpoint "BIA Service" "http://localhost:8012/health"
test_endpoint "Compliance Service" "http://localhost:8014/health"
test_endpoint "Learning Service" "http://localhost:8021/health"
test_endpoint "Documents Service" "http://localhost:8022/health"
test_endpoint "Plans Service" "http://localhost:8023/health"
test_endpoint "Governance Service" "http://localhost:8025/health"
test_endpoint "Risk Service" "http://localhost:8026/health"
test_endpoint "Response Service" "http://localhost:8027/health"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Intelligent Core (AI/ML Services)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "AI Orchestration" "http://localhost:8002/health"
test_endpoint "Workflow Intelligence" "http://localhost:8028/health"
test_endpoint "Community Intelligence" "http://localhost:8030/health"
test_endpoint "Predictive Service" "http://localhost:8031/health"
test_endpoint "Event Intelligence" "http://localhost:8032/health"
test_endpoint "Collective" "http://localhost:8034/health"
test_endpoint "AI Workflow Optimizer" "http://localhost:8038/health"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}AI Office (Internal Agents)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "AI Event Manager" "http://localhost:8055/health"
test_endpoint "Analytics Specialist" "http://localhost:8056/health"
test_endpoint "MIO Manager" "http://localhost:8057/health"
test_endpoint "DevOps Agent" "http://localhost:8058/health"
test_endpoint "Agent Router" "http://localhost:8059/health"
test_endpoint "Project Agent" "http://localhost:8060/health"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Monitoring & Observability${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Prometheus" "http://localhost:9090/-/healthy"
test_endpoint "Monitoring Backend" "http://localhost:8050/health"
test_endpoint "Service Catalog" "http://localhost:8052/health"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Security Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Auth Service" "http://localhost:8081/health"
test_endpoint "Secrets Manager" "http://localhost:8084/health"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Runtime Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Realtime WebSocket" "http://localhost:8082/health"
test_endpoint "Message Queue" "http://localhost:8085/health"
test_endpoint "Service Discovery" "http://localhost:8086/health"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Database Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "DB Intelligence" "http://localhost:8051/health"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Frontend Interfaces${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "Admin Panel" "http://localhost:3000" || true
test_endpoint "User Portal" "http://localhost:3001" || true
test_endpoint "Control Center" "http://localhost:3002" || true

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}External Integrations${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

test_endpoint "GitHub Integration" "http://localhost:8087/health"
test_endpoint "MCP Server" "http://localhost:8088/health"
test_endpoint "Partisia Contracts" "http://localhost:8089/health"

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Health Check Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    echo -e "${RED}Failed Services:${NC}"
    for service in "${FAILED_SERVICES[@]}"; do
        echo -e "${RED}  - $service${NC}"
    done
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo -e "1. Check container logs: docker logs bcm-<service>"
    echo -e "2. Check all containers: docker-compose ps"
    echo -e "3. Enter container: docker exec -it bcm-<service> /bin/bash"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 Platform is ready for use!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}Access Points:${NC}"
    echo -e "  API Gateway:    http://localhost:8000"
    echo -e "  Admin Panel:    http://localhost:3000"
    echo -e "  User Portal:    http://localhost:3001"
    echo -e "  Control Center: http://localhost:3002"
    echo -e "  Prometheus:     http://localhost:9090"
    echo ""
fi
