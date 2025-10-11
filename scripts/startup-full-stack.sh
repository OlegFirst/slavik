#!/bin/bash
# AI Platform ISO - Full Stack Startup Script
# Starts all services in correct dependency order
# Date: 2025-10-11

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting AI Platform ISO Full Stack..."
echo "📂 Project root: $PROJECT_ROOT"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found. Please install docker-compose first.${NC}"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cat > "$PROJECT_ROOT/.env" <<EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/bcm_platform
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=your_api_key_here
DEBUG=false
EOF
    echo -e "${YELLOW}⚠️  Please update .env file with your credentials!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Start services by layers
echo "🔧 Starting LAYER 0: Core Infrastructure..."
docker-compose -f docker-compose.full-stack.yml up -d redis
echo "⏳ Waiting for Redis to be healthy..."
sleep 5

echo ""
echo "🔧 Starting LAYER 1: Runtime Services..."
docker-compose -f docker-compose.full-stack.yml up -d \
    service-discovery \
    message-queue \
    realtime-websocket
echo "⏳ Waiting for runtime services to be healthy..."
sleep 10

echo ""
echo "🔧 Starting LAYER 2: Intelligent Core..."
docker-compose -f docker-compose.full-stack.yml up -d \
    workflow-engine \
    ai-orchestration \
    coordination-center \
    system-bcm-service \
    community-intelligence
echo "⏳ Waiting for intelligent core to be healthy..."
sleep 15

echo ""
echo "🔧 Starting LAYER 3: Platform Services..."
docker-compose -f docker-compose.full-stack.yml up -d \
    bia-service \
    compliance-service \
    governance-service \
    risk-service \
    response-service \
    documents-service \
    plans-service
echo "⏳ Waiting for platform services to be healthy..."
sleep 10

echo ""
echo "🔧 Starting LAYER 4: AI Office Infrastructure..."
docker-compose -f docker-compose.full-stack.yml up -d \
    orchestrator \
    agent-router \
    analytics-specialist
echo "⏳ Waiting for AI office services to be healthy..."
sleep 10

echo ""
echo "🔧 Starting LAYER 5: Observability..."
docker-compose -f docker-compose.full-stack.yml up -d \
    prometheus \
    grafana
echo "⏳ Waiting for observability stack..."
sleep 5

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.full-stack.yml ps
echo ""
echo "🔍 Access Points:"
echo "  • Service Discovery: http://localhost:8500"
echo "  • AI Orchestration:  http://localhost:8031"
echo "  • Workflow Engine:   http://localhost:8036"
echo "  • Prometheus:        http://localhost:9090"
echo "  • Grafana:           http://localhost:3000 (admin/admin)"
echo ""
echo "📝 Useful Commands:"
echo "  • View logs:         docker-compose -f docker-compose.full-stack.yml logs -f"
echo "  • Stop all:          docker-compose -f docker-compose.full-stack.yml down"
echo "  • Restart service:   docker-compose -f docker-compose.full-stack.yml restart <service>"
echo "  • Check health:      ./scripts/health-check-all.sh"
echo ""
echo -e "${GREEN}🎉 Full stack is now running!${NC}"
