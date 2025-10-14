#!/bin/bash
# BCM Platform Services - Stop All Services

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

LOG_DIR="/Users/MD/AI-Platform-ISO/platform-services/logs"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   BCM Platform Services - Stopping All Services           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Stop service by PID file
stop_service() {
    local SERVICE_NAME=$1
    local PID_FILE="$LOG_DIR/$SERVICE_NAME.pid"

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo -e "${YELLOW}Stopping $SERVICE_NAME (PID: $PID)...${NC}"
            kill $PID
            sleep 1
            if kill -0 $PID 2>/dev/null; then
                echo -e "${RED}  Force killing $SERVICE_NAME...${NC}"
                kill -9 $PID
            fi
            echo -e "${GREEN}  ✓ Stopped $SERVICE_NAME${NC}"
        else
            echo -e "${YELLOW}  $SERVICE_NAME not running (stale PID file)${NC}"
        fi
        rm -f "$PID_FILE"
    else
        echo -e "${YELLOW}  $SERVICE_NAME: no PID file found${NC}"
    fi
}

# Stop all services
stop_service "BIA Service"
stop_service "Risk Service"
stop_service "Compliance Service"
stop_service "Documents Service"
stop_service "Response Service"
stop_service "Validation Service"
stop_service "Governance Service"
stop_service "Planning Service"
stop_service "Plans Service"
stop_service "Learning Service"
stop_service "Community Service"

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""
