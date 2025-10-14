#!/bin/bash

# System BCM Service - Quick Start Script
# Запускает весь стек System BCM в production

set -e

echo "🚀 Starting System BCM Service..."
echo "=================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo "Please start Docker and try again."
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Create platform network if it doesn't exist
if ! docker network ls | grep -q platform_network; then
    echo -e "${YELLOW}📡 Creating platform_network...${NC}"
    docker network create platform_network
    echo -e "${GREEN}✅ Network created${NC}"
else
    echo -e "${GREEN}✅ platform_network exists${NC}"
fi

# Copy scenarios if needed
if [ ! -d "scenarios" ]; then
    echo -e "${YELLOW}📋 Copying scenarios...${NC}"
    mkdir -p scenarios
    cp -r ../ai-foundation/learning-knowledge/scenarios/system_scenarios scenarios/
    echo -e "${GREEN}✅ Scenarios copied${NC}"
else
    echo -e "${GREEN}✅ Scenarios directory exists${NC}"
fi

# Build and start services
echo -e "${YELLOW}🏗️  Building and starting services...${NC}"
docker-compose up --build -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 5

# Check health
echo ""
echo "🔍 Checking service health..."
echo "=================================="

# Check System BCM
if curl -s http://localhost:8050/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ System BCM Service: RUNNING${NC}"
    curl -s http://localhost:8050/health | python3 -m json.tool
else
    echo -e "${RED}❌ System BCM Service: NOT RESPONDING${NC}"
fi

echo ""

# Check Redis
if docker-compose ps redis | grep -q "Up"; then
    echo -e "${GREEN}✅ Redis: RUNNING${NC}"
else
    echo -e "${RED}❌ Redis: NOT RUNNING${NC}"
fi

# Check Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus: RUNNING${NC}"
else
    echo -e "${YELLOW}⚠️  Prometheus: NOT READY YET${NC}"
fi

# Check Grafana
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana: RUNNING${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana: NOT READY YET${NC}"
fi

echo ""
echo "=================================="
echo -e "${GREEN}✅ System BCM Service is UP!${NC}"
echo "=================================="
echo ""
echo "📊 Access Points:"
echo "  - System BCM API:  http://localhost:8050"
echo "  - API Docs:        http://localhost:8050/docs"
echo "  - Health Check:    http://localhost:8050/health"
echo "  - Metrics:         http://localhost:8050/metrics"
echo "  - Prometheus:      http://localhost:9090"
echo "  - Grafana:         http://localhost:3000 (admin/admin)"
echo ""
echo "📋 Quick Commands:"
echo "  - View logs:       docker-compose logs -f system-bcm"
echo "  - Check status:    curl http://localhost:8050/status"
echo "  - Trigger cycle:   curl -X POST http://localhost:8050/cycle/trigger"
echo "  - Stop services:   docker-compose down"
echo ""
echo "🎓 The platform is now LIVING BCM through practice!"
echo ""
