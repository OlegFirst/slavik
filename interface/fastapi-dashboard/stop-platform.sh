#!/bin/bash

# 🛑 AI Platform ISO - Shutdown Script
# Останавливает все компоненты платформы

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=============================================="
echo "🛑 Stopping AI Platform ISO"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Stop Web UI
if [ -f "logs/web-ui.pid" ]; then
    WEB_UI_PID=$(cat logs/web-ui.pid)
    if kill -0 $WEB_UI_PID 2>/dev/null; then
        echo "Stopping Web UI (PID: $WEB_UI_PID)..."
        kill $WEB_UI_PID
        rm logs/web-ui.pid
        echo -e "${GREEN}✓${NC} Web UI stopped"
    else
        echo "Web UI not running"
        rm logs/web-ui.pid
    fi
fi

# Stop Observability Stack
echo ""
echo "Stopping Observability Stack..."
cd "$PLATFORM_ROOT/infrastructure/observability"

if [ -f "docker-compose.monitoring.yml" ]; then
    docker-compose -f docker-compose.monitoring.yml down
    echo -e "${GREEN}✓${NC} Prometheus stopped"
    echo -e "${GREEN}✓${NC} Grafana stopped"
    echo -e "${GREEN}✓${NC} Alert Manager stopped"
fi

echo ""
echo "=============================================="
echo "✅ Platform Stopped"
echo "=============================================="
echo ""
