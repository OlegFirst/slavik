#!/bin/bash

##############################################################################
# Start Complete Monitoring Stack with Intelligent Core
#
# This script starts:
# - Prometheus (metrics collection)
# - Grafana (visualization)
# - Alertmanager (alerts)
# - All 5 intelligent-core services
# - Redis (caching)
##############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Intelligent Core + Monitoring Stack Startup          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env file exists
if [ ! -f "../../intelligent-core/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: No .env file found!${NC}"
    echo ""
    echo "Creating .env from .env.example..."
    cp ../../intelligent-core/.env.example ../../intelligent-core/.env
    echo ""
    echo -e "${RED}❌ Please edit intelligent-core/.env with your credentials:${NC}"
    echo "   - DATABASE_URL (Supabase)"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - OPENAI_API_KEY (optional)"
    echo "   - VOYAGE_API_KEY"
    echo "   - QDRANT_URL (optional)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo -e "${GREEN}✅ .env file found${NC}"
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.intelligent-core.yml down 2>/dev/null || true
echo ""

# Pull latest images
echo -e "${BLUE}📥 Pulling latest images...${NC}"
docker-compose -f docker-compose.intelligent-core.yml pull
echo ""

# Build intelligent-core images
echo -e "${BLUE}🔨 Building intelligent-core images...${NC}"
docker-compose -f docker-compose.intelligent-core.yml build
echo ""

# Start services
echo -e "${GREEN}🚀 Starting services...${NC}"
echo ""

# Start in detached mode
docker-compose -f docker-compose.intelligent-core.yml up -d

# Wait for services to be healthy
echo ""
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
echo ""

sleep 10

# Check service health
check_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo -n "   Checking $name... "

    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ UP${NC}"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e "${RED}❌ TIMEOUT${NC}"
    return 1
}

# Check all services
check_service "Prometheus" "http://localhost:9090/-/healthy"
check_service "Grafana" "http://localhost:3000/api/health"
check_service "Alertmanager" "http://localhost:9093/-/healthy"
check_service "Redis" "http://localhost:6379" || echo -e "   ${YELLOW}(Redis doesn't have HTTP, checking with docker)${NC}"
check_service "Intelligent Core Main" "http://localhost:9000/health"
check_service "AI Foundation" "http://localhost:8030/health"
check_service "Community Intelligence" "http://localhost:8031/health"
check_service "AI Orchestration" "http://localhost:8002/health"
check_service "Coordination Center" "http://localhost:8004/coordination/health"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║             🎉 ALL SERVICES ARE UP! 🎉                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Display URLs
echo -e "${BLUE}📊 Access URLs:${NC}"
echo ""
echo -e "  ${GREEN}Grafana:${NC}           http://localhost:3000"
echo -e "                     Login: admin / admin"
echo ""
echo -e "  ${GREEN}Prometheus:${NC}        http://localhost:9090"
echo ""
echo -e "  ${GREEN}Alertmanager:${NC}      http://localhost:9093"
echo ""
echo -e "${BLUE}🤖 Intelligent Core Services:${NC}"
echo ""
echo -e "  ${GREEN}Main Gateway:${NC}      http://localhost:9000/docs"
echo -e "  ${GREEN}AI Foundation:${NC}     http://localhost:8030/docs"
echo -e "  ${GREEN}Community:${NC}         http://localhost:8031/docs"
echo -e "  ${GREEN}Orchestration:${NC}     http://localhost:8002/docs"
echo -e "  ${GREEN}Coordination:${NC}      http://localhost:8004/docs"
echo ""
echo -e "${BLUE}📈 Metrics Endpoints:${NC}"
echo ""
echo -e "  http://localhost:9000/metrics"
echo -e "  http://localhost:8030/metrics"
echo -e "  http://localhost:8031/metrics"
echo -e "  http://localhost:8002/metrics"
echo -e "  http://localhost:8004/metrics"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo ""
echo "  1. Open Grafana: http://localhost:3000"
echo "  2. Go to Dashboards → Intelligent Core - Overview"
echo "  3. Check Prometheus targets: http://localhost:9090/targets"
echo "  4. Test metrics endpoints: cd ../.. && ./test_all_metrics.sh"
echo ""
echo -e "${BLUE}🛠️  Useful Commands:${NC}"
echo ""
echo "  View logs:    docker-compose -f docker-compose.intelligent-core.yml logs -f"
echo "  Stop all:     docker-compose -f docker-compose.intelligent-core.yml down"
echo "  Restart:      docker-compose -f docker-compose.intelligent-core.yml restart"
echo "  Status:       docker-compose -f docker-compose.intelligent-core.yml ps"
echo ""
echo -e "${GREEN}Happy monitoring! 🚀${NC}"
