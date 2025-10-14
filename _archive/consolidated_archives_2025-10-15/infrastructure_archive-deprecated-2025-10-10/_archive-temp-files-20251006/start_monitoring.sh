#!/bin/bash
# BCM Platform - Start Observability Stack

set -e

echo "🚀 Starting BCM Platform Observability Stack..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your actual credentials!${NC}"
    echo ""
fi

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Create network if doesn't exist
if ! docker network inspect bcm-platform-network > /dev/null 2>&1; then
    echo -e "${YELLOW}📡 Creating bcm-platform-network...${NC}"
    docker network create bcm-platform-network
fi

echo -e "${GREEN}✅ Network ready${NC}"
echo ""

# Start services
echo "🐳 Starting containers..."
docker-compose -f docker-compose.monitoring.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check services
echo ""
echo "📊 Service Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus:            http://localhost:9090${NC}"
else
    echo -e "${RED}❌ Prometheus:            http://localhost:9090 (not ready)${NC}"
fi

# Grafana
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana:               http://localhost:3000${NC}"
    echo "   Login: admin / admin"
else
    echo -e "${RED}❌ Grafana:               http://localhost:3000 (not ready)${NC}"
fi

# Loki
if curl -s http://localhost:3100/ready > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Loki:                  http://localhost:3100${NC}"
else
    echo -e "${YELLOW}⚠️  Loki:                  http://localhost:3100 (not ready)${NC}"
fi

# AlertManager
if curl -s http://localhost:9093/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✅ AlertManager:          http://localhost:9093${NC}"
else
    echo -e "${YELLOW}⚠️  AlertManager:          http://localhost:9093 (not ready)${NC}"
fi

# Compliance Monitoring
if curl -s http://localhost:8779/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Compliance Monitoring: http://localhost:8779${NC}"
else
    echo -e "${YELLOW}⚠️  Compliance Monitoring: http://localhost:8779 (not ready)${NC}"
fi

# Process Analytics
if curl -s http://localhost:8780/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Process Analytics:     http://localhost:8780${NC}"
else
    echo -e "${YELLOW}⚠️  Process Analytics:     http://localhost:8780 (not ready)${NC}"
fi

# Qdrant Exporter
if curl -s http://localhost:9122/metrics > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Qdrant Exporter:       http://localhost:9122/metrics${NC}"
else
    echo -e "${YELLOW}⚠️  Qdrant Exporter:       http://localhost:9122/metrics (not ready)${NC}"
fi

# Notification Service
if curl -s http://localhost:8035/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Notification Service:  http://localhost:8035${NC}"
else
    echo -e "${YELLOW}⚠️  Notification Service:  http://localhost:8035 (not ready)${NC}"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📝 To view logs:"
echo "   docker-compose -f docker-compose.monitoring.yml logs -f"
echo ""
echo "🛑 To stop:"
echo "   docker-compose -f docker-compose.monitoring.yml down"
echo ""
echo -e "${GREEN}🎉 Monitoring stack is starting up!${NC}"
echo "   Give it 30-60 seconds for all services to be fully ready."
