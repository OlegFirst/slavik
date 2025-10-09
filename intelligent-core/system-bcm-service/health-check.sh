#!/bin/bash

# System BCM - Platform Health Check Script
# Проверяет здоровье всей платформы и System BCM Service

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Functions
check_service() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo -n "Checking $name... "

    if response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null); then
        if [ "$response" -eq "$expected_code" ]; then
            echo -e "${GREEN}✅ OK${NC} (HTTP $response)"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            return 0
        else
            echo -e "${YELLOW}⚠️  WARNING${NC} (HTTP $response, expected $expected_code)"
            WARNING_CHECKS=$((WARNING_CHECKS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ FAILED${NC} (No response)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 2
    fi
}

check_docker_container() {
    local name=$1

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo -n "Checking Docker container $name... "

    if docker ps --format '{{.Names}}' | grep -q "^${name}$"; then
        status=$(docker inspect -f '{{.State.Status}}' "$name")
        if [ "$status" == "running" ]; then
            echo -e "${GREEN}✅ RUNNING${NC}"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            return 0
        else
            echo -e "${YELLOW}⚠️  STATUS: $status${NC}"
            WARNING_CHECKS=$((WARNING_CHECKS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ NOT FOUND${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 2
    fi
}

check_port() {
    local port=$1
    local name=$2

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo -n "Checking port $port ($name)... "

    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${GREEN}✅ LISTENING${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ NOT LISTENING${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 2
    fi
}

check_redis() {
    local host=${1:-localhost}
    local port=${2:-6379}

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo -n "Checking Redis at $host:$port... "

    if timeout 2 redis-cli -h "$host" -p "$port" ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PONG${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ NO RESPONSE${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 2
    fi
}

check_postgres() {
    local host=${1:-localhost}
    local port=${2:-5432}
    local user=${3:-postgres}

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo -n "Checking PostgreSQL at $host:$port... "

    if pg_isready -h "$host" -p "$port" -U "$user" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ ACCEPTING CONNECTIONS${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ NOT READY${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 2
    fi
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

print_summary() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  HEALTH CHECK SUMMARY${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "Total Checks:   $TOTAL_CHECKS"
    echo -e "${GREEN}Passed:         $PASSED_CHECKS${NC}"
    echo -e "${YELLOW}Warnings:       $WARNING_CHECKS${NC}"
    echo -e "${RED}Failed:         $FAILED_CHECKS${NC}"
    echo ""

    if [ $FAILED_CHECKS -eq 0 ] && [ $WARNING_CHECKS -eq 0 ]; then
        echo -e "${GREEN}✅ ALL SYSTEMS OPERATIONAL${NC}"
        echo ""
        return 0
    elif [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${YELLOW}⚠️  SOME WARNINGS DETECTED${NC}"
        echo ""
        return 1
    else
        echo -e "${RED}❌ CRITICAL ISSUES DETECTED${NC}"
        echo ""
        return 2
    fi
}

# Main execution
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║      System BCM - Platform Health Check              ║"
echo "║      $(date '+%Y-%m-%d %H:%M:%S')                          ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# Check Docker
# ============================================================================
print_header "Docker Infrastructure"

if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Docker is running${NC}"
fi

if docker network ls | grep -q platform_network; then
    echo -e "${GREEN}✅ platform_network exists${NC}"
else
    echo -e "${YELLOW}⚠️  platform_network not found${NC}"
fi

# ============================================================================
# Check System BCM Service
# ============================================================================
print_header "System BCM Service"

check_docker_container "system-bcm-service" || true
check_port 8050 "System BCM API" || true
check_service "System BCM Health" "http://localhost:8050/health" 200 || true
check_service "System BCM Status" "http://localhost:8050/status" 200 || true
check_service "System BCM Metrics" "http://localhost:8050/metrics" 200 || true

# ============================================================================
# Check EventBus (Redis)
# ============================================================================
print_header "EventBus (Redis)"

check_docker_container "system-bcm-redis" || check_docker_container "redis" || true
check_port 6379 "Redis" || true
check_redis "localhost" 6379 || true

# Check Redis streams
echo -n "Checking Redis Streams... "
if redis-cli XINFO STREAMS platform.* > /dev/null 2>&1; then
    stream_count=$(redis-cli XINFO STREAMS platform.* 2>/dev/null | grep -c "platform." || echo "0")
    echo -e "${GREEN}✅ $stream_count streams found${NC}"
else
    echo -e "${YELLOW}⚠️  No platform streams yet${NC}"
fi

# ============================================================================
# Check Monitoring Stack
# ============================================================================
print_header "Monitoring Stack"

check_docker_container "system-bcm-prometheus" || check_docker_container "prometheus" || true
check_port 9090 "Prometheus" || true
check_service "Prometheus" "http://localhost:9090/-/healthy" 200 || true

check_docker_container "system-bcm-grafana" || check_docker_container "grafana" || true
check_port 3000 "Grafana" || true
check_service "Grafana" "http://localhost:3000/api/health" 200 || true

# ============================================================================
# Check Platform Services (if available)
# ============================================================================
print_header "Platform Services (Optional)"

# These may not exist yet, so we don't fail if missing
check_service "API Gateway" "http://localhost:8000/health" 200 || echo -e "${YELLOW}⚠️  Not available (optional)${NC}"
check_service "Workflow Intelligence" "http://localhost:8001/health" 200 || echo -e "${YELLOW}⚠️  Not available (optional)${NC}"
check_service "RAG Service" "http://localhost:8002/health" 200 || echo -e "${YELLOW}⚠️  Not available (optional)${NC}"

# Check PostgreSQL
if command -v pg_isready > /dev/null 2>&1; then
    check_postgres "localhost" 5432 "postgres" || echo -e "${YELLOW}⚠️  Not available (optional)${NC}"
else
    echo -e "${YELLOW}⚠️  pg_isready not installed, skipping PostgreSQL check${NC}"
fi

# ============================================================================
# Check Qdrant
# ============================================================================
check_service "Qdrant" "http://localhost:6333/healthz" 200 || echo -e "${YELLOW}⚠️  Not available (optional)${NC}"

# ============================================================================
# System BCM Specific Checks
# ============================================================================
print_header "System BCM Functionality"

# Check if scenarios are loaded
echo -n "Checking BCM scenarios... "
if [ -d "scenarios" ] && [ "$(ls -A scenarios)" ]; then
    scenario_count=$(ls -1 scenarios/*.json 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ $scenario_count scenario files found${NC}"
else
    echo -e "${RED}❌ No scenarios found${NC}"
fi

# Check last cycle
echo -n "Checking last BCM cycle... "
if last_cycle=$(curl -s http://localhost:8050/status 2>/dev/null | jq -r '.last_cycle_time // empty'); then
    if [ -n "$last_cycle" ] && [ "$last_cycle" != "null" ]; then
        echo -e "${GREEN}✅ Last cycle: $last_cycle${NC}"
    else
        echo -e "${YELLOW}⚠️  No cycles executed yet${NC}"
    fi
else
    echo -e "${RED}❌ Cannot retrieve cycle info${NC}"
fi

# Check cycle count
echo -n "Checking cycle count... "
if cycle_count=$(curl -s http://localhost:8050/status 2>/dev/null | jq -r '.cycle_count // 0'); then
    if [ "$cycle_count" -gt 0 ]; then
        echo -e "${GREEN}✅ $cycle_count cycles completed${NC}"
    else
        echo -e "${YELLOW}⚠️  No cycles completed yet${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Cannot retrieve cycle count${NC}"
fi

# Check improvements
echo -n "Checking total improvements... "
if improvements=$(curl -s http://localhost:8050/status 2>/dev/null | jq -r '.total_improvements_applied // 0'); then
    if [ "$improvements" -gt 0 ]; then
        echo -e "${GREEN}✅ $improvements improvements applied${NC}"
    else
        echo -e "${YELLOW}⚠️  No improvements applied yet${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Cannot retrieve improvements count${NC}"
fi

# ============================================================================
# Check Resource Usage
# ============================================================================
print_header "Resource Usage"

if docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | grep system-bcm > /dev/null; then
    echo "System BCM Container Resources:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -E "CONTAINER|system-bcm"
else
    echo -e "${YELLOW}⚠️  Cannot retrieve resource stats${NC}"
fi

# ============================================================================
# Summary
# ============================================================================
print_summary
exit_code=$?

# ============================================================================
# Recommendations
# ============================================================================
if [ $exit_code -ne 0 ]; then
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  RECOMMENDATIONS${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""

    if [ $FAILED_CHECKS -gt 0 ]; then
        echo "Critical issues detected. Recommended actions:"
        echo "  1. Check Docker: docker-compose ps"
        echo "  2. View logs: docker-compose logs -f"
        echo "  3. Restart services: docker-compose restart"
        echo "  4. Check network: docker network inspect platform_network"
    fi

    if [ $WARNING_CHECKS -gt 0 ]; then
        echo "Warnings detected. Recommended actions:"
        echo "  1. Review service logs for warnings"
        echo "  2. Check Grafana dashboards for anomalies"
        echo "  3. Verify configuration in .env"
    fi

    echo ""
fi

exit $exit_code
