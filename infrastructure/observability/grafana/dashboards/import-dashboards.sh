#!/bin/bash
#
# Grafana Dashboard Import Script
# Imports all platform-services dashboards via Grafana API
#
# Usage: ./import-dashboards.sh [grafana_url] [username] [password]
#

set -e

# Configuration
GRAFANA_URL="${1:-http://localhost:3000}"
GRAFANA_USER="${2:-admin}"
GRAFANA_PASS="${3:-admin}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Dashboard files to import
DASHBOARDS=(
    "platform-services-overview.json"
    "process-analytics.json"
    "compliance-monitoring.json"
    "living-docs.json"
    "community-services.json"
    "digital-twin.json"
    "ml-pipeline.json"
)

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Platform Services Grafana Dashboard Importer          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo -e "  Grafana URL: ${GRAFANA_URL}"
echo -e "  Username:    ${GRAFANA_USER}"
echo ""

# Check if Grafana is accessible
echo -e "${YELLOW}Checking Grafana connectivity...${NC}"
if curl -s -f -u "$GRAFANA_USER:$GRAFANA_PASS" "$GRAFANA_URL/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Grafana is accessible${NC}"
else
    echo -e "${RED}✗ Cannot connect to Grafana at $GRAFANA_URL${NC}"
    echo -e "${RED}  Please check if Grafana is running and credentials are correct${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Importing dashboards...${NC}"
echo ""

# Counter for tracking
SUCCESS_COUNT=0
FAILED_COUNT=0

# Import each dashboard
for dashboard in "${DASHBOARDS[@]}"; do
    if [ ! -f "$dashboard" ]; then
        echo -e "${RED}✗ File not found: $dashboard${NC}"
        ((FAILED_COUNT++))
        continue
    fi

    echo -n "  Importing $dashboard... "

    # Read dashboard JSON and wrap it for import
    DASHBOARD_JSON=$(cat "$dashboard")

    # Create import payload
    IMPORT_PAYLOAD=$(jq -n \
        --argjson dashboard "$DASHBOARD_JSON" \
        '{
            "dashboard": $dashboard,
            "overwrite": true,
            "inputs": [],
            "folderId": 0
        }')

    # Import dashboard
    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -u "$GRAFANA_USER:$GRAFANA_PASS" \
        "$GRAFANA_URL/api/dashboards/db" \
        -d "$IMPORT_PAYLOAD")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
        DASHBOARD_URL=$(echo "$RESPONSE_BODY" | jq -r '.url // empty')
        echo -e "${GREEN}✓ Success${NC}"
        if [ -n "$DASHBOARD_URL" ]; then
            echo -e "    URL: ${GRAFANA_URL}${DASHBOARD_URL}"
        fi
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}✗ Failed (HTTP $HTTP_CODE)${NC}"
        ERROR_MSG=$(echo "$RESPONSE_BODY" | jq -r '.message // .error // "Unknown error"')
        echo -e "    Error: $ERROR_MSG"
        ((FAILED_COUNT++))
    fi
done

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Import Summary:${NC}"
echo -e "  ${GREEN}✓ Successful: $SUCCESS_COUNT${NC}"
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "  ${RED}✗ Failed:     $FAILED_COUNT${NC}"
fi
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ $SUCCESS_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ Dashboards imported successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Access your dashboards at:${NC}"
    echo -e "  Main Overview:  ${GRAFANA_URL}/d/platform-services-overview"
    echo -e "  All Dashboards: ${GRAFANA_URL}/dashboards"
    echo ""
fi

if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}Some dashboards failed to import. Please check the errors above.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All dashboards imported successfully!${NC}"
exit 0
