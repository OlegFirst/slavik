#!/bin/bash
# Start all Prometheus exporters for BCM Platform monitoring
# This script starts exporters that run outside Docker (on host machine)

set -e

PROJECT_ROOT="/Users/MD/AI-Platform-ISO"
PIDS_FILE="$PROJECT_ROOT/infrastructure/observability/.exporter_pids"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting BCM Platform Exporters${NC}"
echo "========================================"

# Clean up old PIDs file
rm -f "$PIDS_FILE"
touch "$PIDS_FILE"

# Function to start exporter
start_exporter() {
    local name=$1
    local command=$2
    local port=$3

    echo -e "${YELLOW}Starting $name on port $port...${NC}"

    # Check if port is already in use
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}⚠️  Port $port already in use, killing existing process${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi

    # Start exporter in background
    eval "$command" > "$PROJECT_ROOT/infrastructure/observability/logs/${name}.log" 2>&1 &
    local pid=$!

    # Save PID
    echo "$name:$pid:$port" >> "$PIDS_FILE"

    # Wait a bit and check if still running
    sleep 2
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name started (PID: $pid)${NC}"
        return 0
    else
        echo -e "${RED}❌ $name failed to start${NC}"
        return 1
    fi
}

# Create logs directory
mkdir -p "$PROJECT_ROOT/infrastructure/observability/logs"

# 1. Qdrant Exporter (port 9122)
start_exporter \
    "qdrant-exporter" \
    "cd $PROJECT_ROOT/infrastructure/observability && python3 exporters/qdrant_exporter.py" \
    9122

# 2. Unified Metrics Exporter - All Intelligent Core modules (port 9000)
start_exporter \
    "unified-exporter" \
    "cd $PROJECT_ROOT && python3 infrastructure/observability/unified_metrics_exporter.py" \
    9000

echo ""
echo -e "${BLUE}📊 Exporter Status:${NC}"
echo "========================================"
cat "$PIDS_FILE" | while IFS=: read name pid port; do
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name (PID: $pid, Port: $port)"
    else
        echo -e "${RED}❌${NC} $name (FAILED)"
    fi
done

echo ""
echo -e "${BLUE}📡 Metrics Endpoints:${NC}"
echo "========================================"
echo "Qdrant:          http://localhost:9122/metrics"
echo "Unified Core:    http://localhost:9000/metrics"
echo ""

echo -e "${BLUE}ℹ️  To stop all exporters:${NC}"
echo "  ./stop_all_exporters.sh"
echo ""

echo -e "${GREEN}✅ All exporters started successfully!${NC}"
