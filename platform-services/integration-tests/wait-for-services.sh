#!/bin/bash
#
# Wait for Services to be Healthy
#
# Polls service health endpoints until all are healthy
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
MAX_WAIT=${HEALTH_CHECK_TIMEOUT:-120}
INTERVAL=${HEALTH_CHECK_INTERVAL:-2}
RETRIES=${HEALTH_CHECK_RETRIES:-60}

# Service URLs
BIA_URL=${BIA_SERVICE_URL:-http://localhost:8012}
PLANNING_URL=${PLANNING_SERVICE_URL:-http://localhost:8011}
PLANS_URL=${PLANS_SERVICE_URL:-http://localhost:8023}
COMPLIANCE_URL=${COMPLIANCE_SERVICE_URL:-http://localhost:8014}

# Services to check
declare -A SERVICES=(
    ["BIA"]="${BIA_URL}/health"
    ["Planning"]="${PLANNING_URL}/health"
    ["Plans"]="${PLANS_URL}/health"
    ["Compliance"]="${COMPLIANCE_URL}/health"
)

echo -e "${YELLOW}Waiting for services to become healthy...${NC}"
echo ""

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    local attempt=0

    while [ $attempt -lt $RETRIES ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is healthy${NC}"
            return 0
        fi

        attempt=$((attempt + 1))
        sleep $INTERVAL
    done

    echo -e "${RED}❌ $name failed to become healthy after ${RETRIES} attempts${NC}"
    return 1
}

# Check all services
FAILED=0

for service_name in "${!SERVICES[@]}"; do
    service_url="${SERVICES[$service_name]}"
    echo -e "${YELLOW}Checking $service_name at $service_url...${NC}"

    if ! check_service "$service_name" "$service_url"; then
        FAILED=1
    fi
done

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some services failed health checks${NC}"
    exit 1
fi
