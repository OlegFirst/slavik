#!/bin/bash

# Start all infrastructure services
# Minimal setup для запуска 3 core modules

set -e

echo "🚀 Starting Infrastructure Services"
echo "=========================================="

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create logs directory
mkdir -p logs/infrastructure

# Step 1: Redis (if not running)
echo -e "${BLUE}[1/6]${NC} Starting Redis..."
if ! redis-cli -u "$REDIS_URL" ping > /dev/null 2>&1; then
    docker run -d -p 6379:6379 --name redis-infra redis:7-alpine
    sleep 2
    echo -e "${GREEN}✅${NC} Redis started"
else
    echo -e "${GREEN}✅${NC} Redis already running"
fi

# Step 2: EventBus (memory backend for quick start)
echo -e "${BLUE}[2/6]${NC} Starting EventBus..."
cd infrastructure/runtime/eventbus

# Kill old instance if exists
pkill -f "eventbus.main" || true

# Start with memory backend (simple, no dependencies)
export EVENTBUS_TRANSPORT=memory
nohup python3 -m eventbus.main > ../../../logs/infrastructure/eventbus.log 2>&1 &

cd ../../..
sleep 2
echo -e "${GREEN}✅${NC} EventBus started (memory backend)"

# Step 3: Prometheus (optional but recommended)
echo -e "${BLUE}[3/6]${NC} Starting Monitoring..."
if docker ps | grep -q prometheus; then
    echo -e "${GREEN}✅${NC} Prometheus already running"
else
    cd infrastructure/observability
    docker-compose up -d prometheus grafana 2>/dev/null || echo "⚠️  Monitoring stack not configured (optional)"
    cd ../..
fi

# Step 4: API Gateway (basic security)
echo -e "${BLUE}[4/6]${NC} Starting API Gateway..."
cd infrastructure/gateway/api-gateway

# Kill old instance
pkill -f "api-gateway.*main:app" || true

# Ensure JWT_SECRET exists
if [ -z "$JWT_SECRET" ]; then
    export JWT_SECRET=$(openssl rand -hex 32)
    echo "⚠️  Generated temporary JWT_SECRET (add to .env for production!)"
fi

# Start API Gateway
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../../../logs/infrastructure/api-gateway.log 2>&1 &

cd ../../..
sleep 3
echo -e "${GREEN}✅${NC} API Gateway started on port 8000"

# Step 5: Service Discovery (minimal)
echo -e "${BLUE}[5/6]${NC} Starting Service Discovery..."
cd infrastructure/runtime/service-discovery

# Kill old instance
pkill -f "service_registry.py" || true

# Start service registry
nohup python3 service_registry.py > ../../logs/infrastructure/service-discovery.log 2>&1 &

cd ../..
sleep 2
echo -e "${GREEN}✅${NC} Service Discovery started"

# Step 6: Database Gateway (for unified access)
echo -e "${BLUE}[6/6]${NC} Preparing Database Gateway..."
# Note: This is usually imported as library, not standalone service
echo -e "${GREEN}✅${NC} Database managers ready (library mode)"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Infrastructure services started!${NC}"
echo ""
echo "Running services:"
echo "  Redis:              redis://localhost:6379"
echo "  EventBus:           Internal (memory backend)"
echo "  API Gateway:        http://localhost:8000"
echo "  Prometheus:         http://localhost:9090 (if configured)"
echo "  Grafana:            http://localhost:3000 (if configured)"
echo ""
echo "Logs available in: logs/infrastructure/"
echo ""
echo "Next step:"
echo "  ./infrastructure/scripts/start_core_modules.sh"
