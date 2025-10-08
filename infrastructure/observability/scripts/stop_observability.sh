#!/bin/bash
###############################################################################
# Observability Stack Shutdown Script
# Stops all monitoring components
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping Observability Stack..."
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

###############################################################################
# 1. Stop MIO Manager
###############################################################################

echo "   Stopping MIO Manager..."
if [ -f "logs/mio_manager.pid" ]; then
    PID=$(cat logs/mio_manager.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo -e "${GREEN}   ✅ MIO Manager stopped (PID: $PID)${NC}"
    else
        echo -e "${YELLOW}   ⚠️  MIO Manager not running${NC}"
    fi
    rm logs/mio_manager.pid
else
    # Fallback: kill by port
    PID=$(lsof -ti:8046 2>/dev/null || true)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo -e "${GREEN}   ✅ MIO Manager stopped (PID: $PID)${NC}"
    fi
fi

###############################################################################
# 2. Stop Exporters
###############################################################################

echo "   Stopping Unified Exporter..."
if [ -f "logs/unified_exporter.pid" ]; then
    PID=$(cat logs/unified_exporter.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo -e "${GREEN}   ✅ Unified Exporter stopped (PID: $PID)${NC}"
    fi
    rm logs/unified_exporter.pid
else
    PID=$(lsof -ti:9000 2>/dev/null || true)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo -e "${GREEN}   ✅ Unified Exporter stopped (PID: $PID)${NC}"
    fi
fi

echo "   Stopping Qdrant Exporter..."
if [ -f "logs/qdrant_exporter.pid" ]; then
    PID=$(cat logs/qdrant_exporter.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo -e "${GREEN}   ✅ Qdrant Exporter stopped (PID: $PID)${NC}"
    fi
    rm logs/qdrant_exporter.pid
else
    PID=$(lsof -ti:9122 2>/dev/null || true)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo -e "${GREEN}   ✅ Qdrant Exporter stopped (PID: $PID)${NC}"
    fi
fi

###############################################################################
# 3. Stop Docker Containers (if running)
###############################################################################

if command -v docker &> /dev/null; then
    echo "   Stopping Docker containers..."

    # Stop Prometheus
    if docker ps --format '{{.Names}}' | grep -q '^prometheus$'; then
        docker stop prometheus > /dev/null 2>&1
        docker rm prometheus > /dev/null 2>&1
        echo -e "${GREEN}   ✅ Prometheus stopped${NC}"
    fi

    # Stop Grafana
    if docker ps --format '{{.Names}}' | grep -q '^grafana$'; then
        docker stop grafana > /dev/null 2>&1
        docker rm grafana > /dev/null 2>&1
        echo -e "${GREEN}   ✅ Grafana stopped${NC}"
    fi
fi

###############################################################################
# 4. Verify All Stopped
###############################################################################

echo ""
echo "🔍 Verifying shutdown..."

RUNNING=false

for port in 9000 9122 9090 3000 8046; do
    PID=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$PID" ]; then
        echo -e "${YELLOW}   ⚠️  Port $port still in use (PID: $PID)${NC}"
        RUNNING=true
    fi
done

if [ "$RUNNING" = false ]; then
    echo -e "${GREEN}   ✅ All services stopped${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Observability Stack Stopped${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
