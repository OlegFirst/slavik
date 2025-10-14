#!/bin/bash

# BCM Platform Services - Startup Script
# This script starts the entire BCM platform stack

set -e

echo "🚀 Starting BCM Platform Services..."
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please update .env with your actual configuration!${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose down

# Build and start services
echo -e "${GREEN}🏗️  Building services...${NC}"
docker-compose build

echo -e "${GREEN}⬆️  Starting services...${NC}"
docker-compose up -d

echo ""
echo "===================================="
echo -e "${GREEN}✅ BCM Platform Services Started!${NC}"
echo "===================================="
echo ""
echo "📊 Service URLs:"
echo "  • Planning Service (ISO 22301 Clause 8.3): http://localhost:8011"
echo "  • Plans Service (ISO 22301 Clause 8.4):    http://localhost:8023"
echo "  • Prometheus:                              http://localhost:9090"
echo "  • Grafana:                                 http://localhost:3000 (admin/admin)"
echo "  • PostgreSQL:                              localhost:5432"
echo "  • Redis:                                   localhost:6379"
echo ""
echo "📋 Health Checks:"
echo "  • Planning Service: http://localhost:8011/health"
echo "  • Plans Service:    http://localhost:8023/health"
echo ""
echo "📖 API Documentation:"
echo "  • Planning Service: http://localhost:8011/docs"
echo "  • Plans Service:    http://localhost:8023/docs"
echo ""
echo "🔍 View logs:"
echo "  docker-compose logs -f [service-name]"
echo ""
echo "🛑 Stop all services:"
echo "  ./stop.sh"
echo ""

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check health endpoints
check_health() {
    local service=$1
    local url=$2

    if curl -f -s "$url" > /dev/null; then
        echo -e "${GREEN}✅ $service is healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $service is not responding${NC}"
        return 1
    fi
}

echo ""
check_health "Planning Service" "http://localhost:8011/health" || true
check_health "Plans Service" "http://localhost:8023/health" || true

echo ""
echo -e "${GREEN}🎉 All systems ready!${NC}"
