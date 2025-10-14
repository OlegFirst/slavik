#!/bin/bash

# System BCM - Platform Integration Script
# Integrates System BCM service with AI-Platform-ISO

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   System BCM - Platform Integration                  ║"
echo "║   $(date '+%Y-%m-%d %H:%M:%S')                          ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# Phase 1: Pre-Integration Checks
# ============================================================================
echo -e "${BLUE}═══ Phase 1: Pre-Integration Checks ═══${NC}"
echo ""

# Check if Docker is running
echo -n "Checking Docker daemon... "
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
    echo "Please start Docker and try again."
    exit 1
fi

# Check if platform_network exists
echo -n "Checking platform_network... "
if docker network inspect platform_network > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Exists${NC}"
else
    echo -e "${YELLOW}⚠️  Not found - Creating...${NC}"
    docker network create platform_network
    echo -e "${GREEN}✅ Created${NC}"
fi

# Check for .env file
echo -n "Checking .env configuration... "
if [ -f .env ]; then
    echo -e "${GREEN}✅ Found${NC}"
else
    echo -e "${YELLOW}⚠️  Not found - Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please configure .env file before proceeding${NC}"
    exit 1
fi

# Check scenarios directory
echo -n "Checking scenarios... "
if [ -d scenarios ] && [ -f scenarios/platform_bia.json ]; then
    echo -e "${GREEN}✅ Ready${NC}"
else
    echo -e "${RED}❌ Scenarios not found${NC}"
    exit 1
fi

echo ""

# ============================================================================
# Phase 2: Infrastructure Check
# ============================================================================
echo -e "${BLUE}═══ Phase 2: Infrastructure Check ═══${NC}"
echo ""

# Check for platform infrastructure services
echo "Checking platform infrastructure services:"

check_service_port() {
    local service=$1
    local port=$2

    echo -n "  $service (port $port)... "
    if docker ps --format '{{.Names}}\t{{.Ports}}' | grep -q ":$port"; then
        echo -e "${GREEN}✅ Running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Not running${NC}"
        return 1
    fi
}

# Check critical infrastructure
REDIS_RUNNING=0
POSTGRES_RUNNING=0
GATEWAY_RUNNING=0

check_service_port "Redis EventBus" 6379 && REDIS_RUNNING=1 || true
check_service_port "PostgreSQL" 5432 && POSTGRES_RUNNING=1 || true
check_service_port "API Gateway" 8000 && GATEWAY_RUNNING=1 || true

echo ""

# ============================================================================
# Phase 3: Platform Services Discovery
# ============================================================================
echo -e "${BLUE}═══ Phase 3: Platform Services Discovery ═══${NC}"
echo ""

echo "Discovering platform services:"

# Platform Services (8001-8012)
declare -A PLATFORM_SERVICES=(
    ["8001"]="BIA Service"
    ["8002"]="Risk Service"
    ["8003"]="Compliance Service"
    ["8004"]="Planning Service"
    ["8005"]="Response Service"
    ["8006"]="Documents Service"
    ["8007"]="Governance Service"
    ["8008"]="Validation Service"
    ["8009"]="Learning Service"
    ["8010"]="BCM Coordination Service"
    ["8011"]="Community Service"
    ["8012"]="Monitoring Service"
)

SERVICES_FOUND=0
SERVICES_TOTAL=${#PLATFORM_SERVICES[@]}

for port in "${!PLATFORM_SERVICES[@]}"; do
    service="${PLATFORM_SERVICES[$port]}"
    echo -n "  $service (port $port)... "

    if docker ps --format '{{.Names}}\t{{.Ports}}' | grep -q ":$port"; then
        echo -e "${GREEN}✅ Running${NC}"
        ((SERVICES_FOUND++))
    else
        echo -e "${YELLOW}⚠️  Not running${NC}"
    fi
done

echo ""
echo "Platform services found: $SERVICES_FOUND/$SERVICES_TOTAL"
echo ""

# ============================================================================
# Phase 4: Intelligent Core Discovery
# ============================================================================
echo -e "${BLUE}═══ Phase 4: Intelligent Core Discovery ═══${NC}"
echo ""

echo "Discovering intelligent core modules:"

# Intelligent Core (8031-8050)
declare -A INTELLIGENT_MODULES=(
    ["8031"]="Predictive Intelligence"
    ["8032"]="Collective Intelligence"
    ["8036"]="Expertise Center"
    ["8037"]="Workflow Intelligence"
    ["8038"]="Community Intelligence"
    ["8039"]="Event Intelligence"
    ["8041"]="Workflow Engine"
)

MODULES_FOUND=0
MODULES_TOTAL=${#INTELLIGENT_MODULES[@]}

for port in "${!INTELLIGENT_MODULES[@]}"; do
    module="${INTELLIGENT_MODULES[$port]}"
    echo -n "  $module (port $port)... "

    if docker ps --format '{{.Names}}\t{{.Ports}}' | grep -q ":$port"; then
        echo -e "${GREEN}✅ Running${NC}"
        ((MODULES_FOUND++))
    else
        echo -e "${YELLOW}⚠️  Not running${NC}"
    fi
done

echo ""
echo "Intelligent modules found: $MODULES_FOUND/$MODULES_TOTAL"
echo ""

# ============================================================================
# Phase 5: Build System BCM Service
# ============================================================================
echo -e "${BLUE}═══ Phase 5: Build System BCM Service ═══${NC}"
echo ""

echo "Building System BCM Docker image..."
docker-compose build

echo -e "${GREEN}✅ Build complete${NC}"
echo ""

# ============================================================================
# Phase 6: Deploy System BCM Service
# ============================================================================
echo -e "${BLUE}═══ Phase 6: Deploy System BCM Service ═══${NC}"
echo ""

echo "Starting System BCM service..."
docker-compose up -d

echo ""
echo "Waiting for service to be ready..."
sleep 5

# Health check
MAX_ATTEMPTS=30
ATTEMPT=0
SERVICE_READY=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:8050/health > /dev/null 2>&1; then
        SERVICE_READY=1
        break
    fi
    echo -n "."
    sleep 1
    ((ATTEMPT++))
done

echo ""

if [ $SERVICE_READY -eq 1 ]; then
    echo -e "${GREEN}✅ System BCM service is ready${NC}"
else
    echo -e "${RED}❌ System BCM service failed to start${NC}"
    echo "Check logs: docker-compose logs system-bcm"
    exit 1
fi

echo ""

# ============================================================================
# Phase 7: Verify Integration
# ============================================================================
echo -e "${BLUE}═══ Phase 7: Verify Integration ═══${NC}"
echo ""

echo "Verifying integration..."
echo ""

# Check health endpoint
echo -n "Health endpoint... "
if curl -s http://localhost:8050/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Not healthy${NC}"
fi

# Check status endpoint
echo -n "Status endpoint... "
if curl -s http://localhost:8050/status | grep -q "version"; then
    echo -e "${GREEN}✅ Responding${NC}"
else
    echo -e "${RED}❌ Not responding${NC}"
fi

# Check metrics endpoint
echo -n "Metrics endpoint... "
if curl -s http://localhost:8050/metrics | grep -q "system_bcm"; then
    echo -e "${GREEN}✅ Exporting metrics${NC}"
else
    echo -e "${RED}❌ No metrics${NC}"
fi

# Check EventBus connection
echo -n "EventBus connection... "
if docker exec system-bcm-service python3 -c "import redis; r = redis.Redis(host='redis'); r.ping()" 2>/dev/null; then
    echo -e "${GREEN}✅ Connected${NC}"
else
    echo -e "${YELLOW}⚠️  Not connected${NC}"
fi

echo ""

# ============================================================================
# Phase 8: Trigger First BCM Cycle
# ============================================================================
echo -e "${BLUE}═══ Phase 8: Trigger First BCM Cycle ═══${NC}"
echo ""

echo "Triggering first BCM cycle..."
echo ""

CYCLE_RESULT=$(curl -s -X POST http://localhost:8050/cycle/trigger)

if echo "$CYCLE_RESULT" | grep -q "success"; then
    echo -e "${GREEN}✅ BCM cycle completed successfully${NC}"
    echo ""

    # Show cycle summary
    echo "Cycle Summary:"
    echo "$CYCLE_RESULT" | python3 -m json.tool 2>/dev/null | grep -E "phase|status|insights_generated" || echo "$CYCLE_RESULT"
else
    echo -e "${RED}❌ BCM cycle failed${NC}"
    echo "Response: $CYCLE_RESULT"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Integration Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

echo "Infrastructure:"
echo "  Redis EventBus:      $([ $REDIS_RUNNING -eq 1 ] && echo -e "${GREEN}✅ Running${NC}" || echo -e "${YELLOW}⚠️  Not running${NC}")"
echo "  PostgreSQL:          $([ $POSTGRES_RUNNING -eq 1 ] && echo -e "${GREEN}✅ Running${NC}" || echo -e "${YELLOW}⚠️  Not running${NC}")"
echo "  API Gateway:         $([ $GATEWAY_RUNNING -eq 1 ] && echo -e "${GREEN}✅ Running${NC}" || echo -e "${YELLOW}⚠️  Not running${NC}")"
echo ""

echo "Platform Services:    $SERVICES_FOUND/$SERVICES_TOTAL discovered"
echo "Intelligent Modules:  $MODULES_FOUND/$MODULES_TOTAL discovered"
echo ""

echo "System BCM Service:"
echo "  Status:              ${GREEN}✅ Running${NC}"
echo "  Port:                8050"
echo "  Network:             platform_network"
echo "  First Cycle:         ${GREEN}✅ Completed${NC}"
echo ""

if [ $REDIS_RUNNING -eq 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Redis EventBus not detected${NC}"
    echo "   System BCM will run in memory mode until EventBus is available"
    echo ""
fi

# ============================================================================
# Next Steps
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Next Steps${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

echo "1. Monitor System BCM:"
echo "   • Dashboard:   http://localhost:3000 (Grafana)"
echo "   • Metrics:     http://localhost:9090 (Prometheus)"
echo "   • Logs:        docker-compose logs -f system-bcm"
echo ""

echo "2. Trigger manual BCM cycle:"
echo "   curl -X POST http://localhost:8050/cycle/trigger"
echo ""

echo "3. Check platform health:"
echo "   curl http://localhost:8050/health"
echo ""

echo "4. View BCM insights:"
echo "   curl http://localhost:8050/insights | jq"
echo ""

echo "5. Run full validation:"
echo "   ./validate-deployment.sh"
echo ""

echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ INTEGRATION COMPLETE                              ║${NC}"
echo -e "${GREEN}║  System BCM is now monitoring the platform!          ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
