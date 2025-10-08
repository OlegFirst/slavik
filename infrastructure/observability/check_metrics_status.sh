#!/bin/bash
# Check Metrics Status - All Intelligent-Core Services
# =====================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "======================================================================"
echo "🔍 Checking Metrics Status - Intelligent-Core Services"
echo "======================================================================"
echo ""

# Counters
TOTAL=0
RUNNING=0
HAS_METRICS=0
NO_METRICS=0
NOT_RUNNING=0

# Function to check service
check_service() {
    local PORT=$1
    local NAME=$2

    TOTAL=$((TOTAL + 1))

    printf "%-30s (:%s) " "$NAME" "$PORT"

    # Check if service is running
    if curl -s -f "http://localhost:$PORT/health" > /dev/null 2>&1; then
        RUNNING=$((RUNNING + 1))

        # Check if /metrics exists
        if curl -s -f "http://localhost:$PORT/metrics" > /dev/null 2>&1; then
            HAS_METRICS=$((HAS_METRICS + 1))
            METRICS_COUNT=$(curl -s "http://localhost:$PORT/metrics" | grep -c "^# HELP" || echo 0)
            echo -e "${GREEN}✅ RUNNING + METRICS${NC} ($METRICS_COUNT metrics)"
        else
            NO_METRICS=$((NO_METRICS + 1))
            echo -e "${YELLOW}⚠️  RUNNING - NO METRICS${NC}"
        fi
    else
        NOT_RUNNING=$((NOT_RUNNING + 1))
        echo -e "${RED}❌ NOT RUNNING${NC}"
    fi
}

echo "📊 Checking services..."
echo ""

# Check all services
check_service 8030 "ai-orchestration"
check_service 8031 "community-intelligence"
check_service 8032 "predictive"
check_service 8033 "collective"
check_service 8034 "coordination-center"
check_service 8035 "expertise-center"
check_service 8036 "workflow-engine"
check_service 8037 "workflow-intelligence"
check_service 8038 "ai-workflow-optimizer"
check_service 8039 "event-intelligence"
check_service 8040 "ai-foundation"

echo ""
echo "======================================================================"
echo "📈 Summary:"
echo "======================================================================"
echo ""
echo "Total services:        $TOTAL"
echo -e "Running services:      ${GREEN}$RUNNING${NC}"
echo -e "With /metrics:         ${GREEN}$HAS_METRICS${NC}"
echo -e "Without /metrics:      ${YELLOW}$NO_METRICS${NC}"
echo -e "Not running:           ${RED}$NOT_RUNNING${NC}"
echo ""

if [ $TOTAL -gt 0 ]; then
    METRICS_PERCENT=$((HAS_METRICS * 100 / TOTAL))
    echo "Metrics coverage:      $METRICS_PERCENT%"
    echo ""
fi

# Check Prometheus
echo "======================================================================"
echo "🎯 Prometheus Status"
echo "======================================================================"
echo ""

if curl -s -f "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Prometheus is running${NC}"
    echo "   URL: http://localhost:9090"
else
    echo -e "${RED}❌ Prometheus is NOT running${NC}"
fi

echo ""

# Check Grafana
echo "======================================================================"
echo "📊 Grafana Status"
echo "======================================================================"
echo ""

if curl -s -f "http://localhost:3000/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana is running${NC}"
    echo "   URL: http://localhost:3000"
    echo "   Login: admin / admin"
else
    echo -e "${RED}❌ Grafana is NOT running${NC}"
fi

echo ""
echo "======================================================================"
echo "🚀 Next Steps"
echo "======================================================================"
echo ""

if [ $NO_METRICS -gt 0 ]; then
    echo "1. Add /metrics to $NO_METRICS services without it:"
    echo "   cd infrastructure/observability"
    echo "   python3 add_metrics_to_services.py --dry-run  # Preview"
    echo "   python3 add_metrics_to_services.py            # Apply"
    echo ""
fi

if [ $NOT_RUNNING -gt 0 ]; then
    echo "2. Start $NOT_RUNNING missing services"
    echo ""
fi

echo "3. Restart Prometheus to scrape metrics:"
echo "   cd infrastructure/observability"
echo "   docker-compose -f docker-compose.monitoring.yml restart prometheus"
echo ""

echo "4. View in browser:"
echo "   Prometheus: http://localhost:9090/targets"
echo "   Grafana:    http://localhost:3000"
echo ""

echo "======================================================================"
echo ""
