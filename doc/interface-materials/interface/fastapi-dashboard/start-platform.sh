#!/bin/bash

# 🚀 AI Platform ISO - Complete Startup Script
# Запускает все компоненты платформы в правильном порядке

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=============================================="
echo "🚀 Starting AI Platform ISO"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running
check_service() {
    local port=$1
    local name=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${GREEN}✓${NC} $name (port $port) - already running"
        return 0
    else
        echo -e "${YELLOW}○${NC} $name (port $port) - not running"
        return 1
    fi
}

# Start Observability Stack
echo "📊 Starting Observability Stack..."
echo "---"

cd "$PLATFORM_ROOT/infrastructure/observability"

if [ -f "docker-compose.monitoring.yml" ]; then
    docker-compose -f docker-compose.monitoring.yml up -d
    echo -e "${GREEN}✓${NC} Prometheus started (http://localhost:9090)"
    echo -e "${GREEN}✓${NC} Grafana started (http://localhost:3000)"
    echo -e "${GREEN}✓${NC} Alert Manager started (http://localhost:9093)"
else
    echo -e "${RED}✗${NC} docker-compose.monitoring.yml not found"
fi

echo ""
sleep 3

# Wait for services to be ready
echo "⏳ Waiting for observability services to be ready..."
sleep 10

echo ""
echo "=============================================="
echo "🎨 Starting Web UI"
echo "=============================================="
echo ""

cd "$SCRIPT_DIR"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start Web UI in background
echo "Starting Web UI on port 8888..."
python3 main.py > logs/web-ui.log 2>&1 &
WEB_UI_PID=$!
echo $WEB_UI_PID > logs/web-ui.pid

sleep 3

if check_service 8888 "Web UI"; then
    echo -e "${GREEN}✓${NC} Web UI started successfully"
else
    echo -e "${RED}✗${NC} Web UI failed to start"
    echo "Check logs/web-ui.log for details"
fi

echo ""
echo "=============================================="
echo "✅ Platform Started!"
echo "=============================================="
echo ""
echo "Access points:"
echo "  🎨 Main Dashboard:    http://localhost:8888"
echo "  🔧 Tools Management:  http://localhost:8888/tools"
echo "  📊 Monitoring:        http://localhost:8888/monitoring"
echo "  📈 Grafana:          http://localhost:3000"
echo "  🔍 Prometheus:       http://localhost:9090"
echo ""
echo "Services status:"
check_service 8888 "Web UI"
check_service 3000 "Grafana"
check_service 9090 "Prometheus"
check_service 9093 "Alert Manager"
check_service 8051 "Analytics Specialist" || echo -e "${YELLOW}  ⚠ Start manually if needed${NC}"
echo ""
echo "To stop all services, run:"
echo "  ./stop-platform.sh"
echo ""
