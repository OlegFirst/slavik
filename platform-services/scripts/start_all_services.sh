#!/bin/bash
# BCM Platform Services - Unified Startup Script
# Starts all 11 platform services on their designated ports
#
# This script runs services directly (not via Docker) for development
# Each service connects to Supabase PostgreSQL database

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   BCM Platform Services - Starting All Services           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Base directory
BASE_DIR="/Users/MD/AI-Platform-ISO/platform-services"
PYTHON_BIN="python3"

# Database configuration (Supabase)
export DATABASE_URL="postgresql://postgres.tpdkhddtbhpoqzzgxfni:K@x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres?sslmode=require"

# Redis configuration (from Gateway .env)
export REDIS_URL="redis://redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com:10023"
export REDIS_PASSWORD=""

# JWT configuration (from Gateway .env)
export JWT_SECRET="Cj8QUzVaQzC5rfn9lEUQA_jP3-y4ecoMrBDzptlokv2B0Fny3zhph3bzeyJXA4c482JlrmTBN5n5O-QEXD0ZAg"
export JWT_ALGORITHM="HS256"

# Auth Service URL
export AUTH_SERVICE_URL="http://localhost:8001"

# Log directory
LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR"

# Function to start a service
start_service() {
    local SERVICE_NAME=$1
    local SERVICE_DIR=$2
    local SERVICE_PORT=$3
    local ENV_VARS=$4

    echo -e "${YELLOW}Starting $SERVICE_NAME on port $SERVICE_PORT...${NC}"

    cd "$BASE_DIR/$SERVICE_DIR"

    # Check if main.py exists
    if [ ! -f "main.py" ]; then
        echo -e "${RED}  ✗ main.py not found in $SERVICE_DIR${NC}"
        return 1
    fi

    # Export service-specific environment variables
    export SERVICE_PORT=$SERVICE_PORT
    export PORT=$SERVICE_PORT
    eval "$ENV_VARS"

    # Start service in background, redirect output to log
    nohup $PYTHON_BIN main.py > "$LOG_DIR/$SERVICE_NAME.log" 2>&1 &
    local PID=$!

    # Save PID to file
    echo $PID > "$LOG_DIR/$SERVICE_NAME.pid"

    echo -e "${GREEN}  ✓ Started $SERVICE_NAME (PID: $PID) - logs: $LOG_DIR/$SERVICE_NAME.log${NC}"

    # Brief wait to check if service starts
    sleep 2

    # Check if process is still running
    if ! kill -0 $PID 2>/dev/null; then
        echo -e "${RED}  ✗ $SERVICE_NAME failed to start. Check logs: $LOG_DIR/$SERVICE_NAME.log${NC}"
        return 1
    fi
}

echo -e "${BLUE}📊 Starting Platform Services...${NC}"
echo ""

# Start services in order
# Format: start_service "Display Name" "directory-name" PORT "additional_env_vars"

start_service "BIA Service" "bia-service" 8012 "SERVICE_NAME=bia"
start_service "Risk Service" "risk-service" 8013 "SERVICE_NAME=risk"
start_service "Compliance Service" "compliance-service" 8014 "SERVICE_NAME=compliance"
start_service "Documents Service" "documents-service" 8015 "SERVICE_NAME=documents"
start_service "Response Service" "response-service" 8016 "SERVICE_NAME=response"
start_service "Validation Service" "validation-service" 8017 "SERVICE_NAME=validation"
start_service "Governance Service" "governance-service" 8018 "SERVICE_NAME=governance"
start_service "Planning Service" "planning_service" 8019 "SERVICE_NAME=planning"
start_service "Plans Service" "plans_service" 8020 "SERVICE_NAME=plans"
start_service "Learning Service" "learning-service" 8021 "SERVICE_NAME=learning"

# Community service doesn't have main.py, skip for now
# start_service "Community Service" "community-service" 8022 "SERVICE_NAME=community"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Service Startup Complete                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Services Started:${NC}"
echo ""
echo "  • BIA Service:        http://localhost:8012"
echo "  • Risk Service:       http://localhost:8013"
echo "  • Compliance Service: http://localhost:8014"
echo "  • Documents Service:  http://localhost:8015"
echo "  • Response Service:   http://localhost:8016"
echo "  • Validation Service: http://localhost:8017"
echo "  • Governance Service: http://localhost:8018"
echo "  • Planning Service:   http://localhost:8019"
echo "  • Plans Service:      http://localhost:8020"
echo "  • Learning Service:   http://localhost:8021"
echo ""
echo -e "${YELLOW}📋 View Logs:${NC}"
echo "  tail -f $LOG_DIR/<service-name>.log"
echo ""
echo -e "${YELLOW}🛑 Stop Services:${NC}"
echo "  ./stop_all_services.sh"
echo ""
echo -e "${BLUE}🔍 Check Gateway Health:${NC}"
echo "  curl http://localhost:8000/health | jq"
echo ""
