#!/bin/bash

##############################################################################
# Test All Metrics Endpoints
#
# Tests all 5 intelligent-core services for /metrics endpoint availability
##############################################################################

echo "🧪 Testing All Metrics Endpoints"
echo "================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local url=$2

    echo -n "Testing $name ($url)... "

    # Check if endpoint is up
    response=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null)

    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC}"

        # Get first few lines of metrics
        echo "   Sample metrics:"
        curl -s $url 2>/dev/null | head -5 | sed 's/^/   /'
        echo ""
        return 0
    elif [ "$response" = "000" ]; then
        echo -e "${RED}❌ NOT RUNNING${NC}"
        echo "   Service appears to be down. Start it first."
        echo ""
        return 1
    else
        echo -e "${RED}❌ ERROR (HTTP $response)${NC}"
        echo ""
        return 1
    fi
}

# Test all services
success_count=0
total_count=5

echo "Testing 5 intelligent-core services:"
echo ""

# 1. Main Gateway
if test_endpoint "Main Gateway" "http://localhost:9000/metrics"; then
    ((success_count++))
fi

# 2. AI Foundation (Learning & Knowledge)
if test_endpoint "AI Foundation" "http://localhost:8030/metrics"; then
    ((success_count++))
fi

# 3. Community Intelligence (port conflict - might be 8031 after fix)
echo -e "${YELLOW}⚠️  Note: Community Intelligence has port conflict (currently 8030, should be 8031)${NC}"
if test_endpoint "Community Intelligence" "http://localhost:8030/metrics"; then
    ((success_count++))
else
    echo "   Trying alternate port 8031..."
    if test_endpoint "Community Intelligence (alt)" "http://localhost:8031/metrics"; then
        ((success_count++))
    fi
fi

# 4. AI Orchestration
if test_endpoint "AI Orchestration" "http://localhost:8002/metrics"; then
    ((success_count++))
fi

# 5. Coordination Center
if test_endpoint "Coordination Center" "http://localhost:8004/metrics"; then
    ((success_count++))
fi

# Summary
echo "================================="
echo "Summary: $success_count/$total_count services responding"
echo ""

if [ $success_count -eq $total_count ]; then
    echo -e "${GREEN}✅ All services have working /metrics endpoints!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure Prometheus to scrape these endpoints"
    echo "2. Set up Grafana dashboards"
    echo "3. Configure alerts"
    exit 0
elif [ $success_count -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Some services are not running or have issues${NC}"
    echo ""
    echo "To start services:"
    echo "  cd /Users/MD/AI-Platform-ISO/intelligent-core"
    echo "  uvicorn main:app --host 0.0.0.0 --port 9000 &"
    echo ""
    echo "  cd ai-foundation/learning-knowledge/api"
    echo "  uvicorn main:app --host 0.0.0.0 --port 8030 &"
    echo ""
    echo "  cd ../../community_intelligence"
    echo "  uvicorn main:app --host 0.0.0.0 --port 8031 &  # Changed from 8030"
    echo ""
    echo "  cd ../orchestration/ai-orchestration"
    echo "  uvicorn main:app --host 0.0.0.0 --port 8002 &"
    echo ""
    echo "  cd ../coordination-center"
    echo "  uvicorn main:app --host 0.0.0.0 --port 8004 &"
    exit 1
else
    echo -e "${RED}❌ No services are running${NC}"
    echo ""
    echo "Start services first, then run this test again."
    exit 1
fi
