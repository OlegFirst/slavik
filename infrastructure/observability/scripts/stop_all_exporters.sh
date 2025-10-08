#!/bin/bash
# Stop all Prometheus exporters

set -e

PROJECT_ROOT="/Users/MD/AI-Platform-ISO"
PIDS_FILE="$PROJECT_ROOT/infrastructure/observability/.exporter_pids"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛑 Stopping BCM Platform Exporters${NC}"
echo "========================================"

if [ ! -f "$PIDS_FILE" ]; then
    echo -e "${RED}No running exporters found (PID file missing)${NC}"
    exit 0
fi

# Read PIDs and kill processes
while IFS=: read name pid port; do
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "Stopping $name (PID: $pid)..."
        kill $pid 2>/dev/null || true
        sleep 1

        # Force kill if still running
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null || true
        fi

        echo -e "${GREEN}✅ Stopped $name${NC}"
    else
        echo -e "${RED}⚠️  $name not running (PID: $pid)${NC}"
    fi
done < "$PIDS_FILE"

# Clean up
rm -f "$PIDS_FILE"

echo ""
echo -e "${GREEN}✅ All exporters stopped${NC}"
