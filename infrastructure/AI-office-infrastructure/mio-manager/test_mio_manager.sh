#!/bin/bash

# ================================================================
# MIO Manager v2.0 - Скрипт быстрой проверки
# ================================================================
# Проверяет что все критичные компоненты работают правильно
#
# Usage:
#   chmod +x test_mio_manager.sh
#   ./test_mio_manager.sh
# ================================================================

echo "🚀 MIO Manager v2.0 - Quick Test"
echo "================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ================================================================
# Test function
# ================================================================
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "Testing $name... "

    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        if [ -z "$expected" ] || echo "$body" | grep -q "$expected"; then
            echo -e "${GREEN}✅ PASSED${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            echo -e "${RED}❌ FAILED${NC} (response doesn't contain '$expected')"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ FAILED${NC} (HTTP $http_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# ================================================================
# 1. MIO Manager Core
# ================================================================
echo "📊 1. MIO Manager Core"
echo "----------------------"

test_endpoint "MIO Manager Health" \
    "http://localhost:8046/health" \
    "healthy"

test_endpoint "MIO Manager Metrics" \
    "http://localhost:8046/metrics" \
    "mio_"

echo ""

# ================================================================
# 2. Critical Integrations
# ================================================================
echo "🔌 2. Critical Integrations"
echo "---------------------------"

# Compliance Monitoring (КРИТИЧНО для специалиста!)
test_endpoint "Compliance Monitoring Health" \
    "http://localhost:8779/health" \
    "healthy"

test_endpoint "Compliance Status" \
    "http://localhost:8779/services/compliance" \
    "compliance_score"

# Other critical services
test_endpoint "Workflow Intelligence (Brain)" \
    "http://localhost:8050/health" \
    "healthy"

test_endpoint "Predictive Service" \
    "http://localhost:8052/health" \
    "healthy"

test_endpoint "Optimizer Service" \
    "http://localhost:8051/health" \
    "healthy"

test_endpoint "Coordination Center" \
    "http://localhost:8053/health" \
    "healthy"

echo ""

# ================================================================
# 3. Database Connectivity
# ================================================================
echo "💾 3. Database Connectivity"
echo "---------------------------"

# Supabase PostgreSQL (Compliance data)
echo -n "Testing Supabase PostgreSQL... "

export PGPASSWORD='K@x3ta9V8GK5rnW'
result=$(psql -h aws-1-eu-north-1.pooler.supabase.com \
    -U postgres.tpdkhddtbhpoqzzgxfni \
    -d postgres -p 5432 \
    -t -c "SELECT COUNT(*) FROM compliance_snapshots;" 2>/dev/null)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED${NC} (found $result snapshots)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Redis (EventBus)
echo -n "Testing Redis... "

redis_result=$(redis-cli ping 2>/dev/null)

if [ "$redis_result" = "PONG" ]; then
    echo -e "${GREEN}✅ PASSED${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ================================================================
# 4. Service Discovery
# ================================================================
echo "🔍 4. Service Discovery & Metrics"
echo "---------------------------------"

# Check if MIO Manager discovers all services
echo -n "Testing service discovery... "

discovery_response=$(curl -s "http://localhost:8046/api/services/discover" 2>/dev/null)

if echo "$discovery_response" | grep -q "total_services"; then
    total_services=$(echo "$discovery_response" | grep -o '"total_services":[0-9]*' | grep -o '[0-9]*')
    coverage=$(echo "$discovery_response" | grep -o '"percentage":[0-9.]*' | grep -o '[0-9.]*')

    echo -e "${GREEN}✅ PASSED${NC} (discovered $total_services services, coverage: ${coverage}%)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ================================================================
# 5. Scheduler Status
# ================================================================
echo "🗓️  5. SmartScheduler Status"
echo "---------------------------"

echo -n "Testing scheduler stats... "

scheduler_response=$(curl -s "http://localhost:8046/api/scheduler/stats" 2>/dev/null)

if echo "$scheduler_response" | grep -q "health_checks"; then
    health_checks=$(echo "$scheduler_response" | grep -o '"health_checks":[0-9]*' | grep -o '[0-9]*')
    daily_analyses=$(echo "$scheduler_response" | grep -o '"daily_analyses":[0-9]*' | grep -o '[0-9]*')

    echo -e "${GREEN}✅ PASSED${NC} (health_checks: $health_checks, daily_analyses: $daily_analyses)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ================================================================
# 6. Temporal Worker
# ================================================================
echo "⚙️  6. Temporal Worker"
echo "---------------------"

echo -n "Checking Temporal Worker process... "

# Check if worker process is running
if pgrep -f "run_worker.py" > /dev/null; then
    echo -e "${GREEN}✅ RUNNING${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  NOT RUNNING${NC}"
    echo "   → Start with: python run_worker.py"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ================================================================
# 7. Compliance Data Validation (КРИТИЧНО!)
# ================================================================
echo "📋 7. Compliance Data Validation"
echo "--------------------------------"

echo -n "Checking compliance tables... "

export PGPASSWORD='K@x3ta9V8GK5rnW'
tables=$(psql -h aws-1-eu-north-1.pooler.supabase.com \
    -U postgres.tpdkhddtbhpoqzzgxfni \
    -d postgres -p 5432 \
    -t -c "SELECT COUNT(*) FROM information_schema.tables
           WHERE table_schema = 'public'
           AND table_name IN ('notifications', 'compliance_alerts', 'nonconformities',
                              'audits', 'business_metrics', 'service_registry',
                              'automation_jobs', 'compliance_snapshots');" 2>/dev/null)

if [ "$tables" -eq 8 ]; then
    echo -e "${GREEN}✅ PASSED${NC} (all 8 tables exist)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAILED${NC} (found $tables/8 tables)"
    echo "   → Apply migration: see infrastructure/observability/services/compliance-monitoring/database/APPLY_SCHEMA.md"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ================================================================
# Final Results
# ================================================================
echo "================================="
echo "📊 Test Results:"
echo "================================="
echo ""
echo "Total tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo "🚀 MIO Manager v2.0 is BATTLE READY!"
    exit 0
else
    echo -e "${YELLOW}⚠️  SOME TESTS FAILED${NC}"
    echo "See QUICK_RECOVERY_GUIDE.md for troubleshooting"
    exit 1
fi
