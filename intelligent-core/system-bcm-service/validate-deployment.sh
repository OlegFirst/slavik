#!/bin/bash

# System BCM - Deployment Validation Script
# Validates full deployment and integration

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name=$1
    local test_command=$2

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Test $TESTS_RUN: $test_name... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

run_test_with_output() {
    local test_name=$1
    local test_command=$2
    local expected_output=$3

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Test $TESTS_RUN: $test_name... "

    output=$(eval "$test_command" 2>&1)

    if echo "$output" | grep -q "$expected_output"; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "  Expected: $expected_output"
        echo "  Got: $output"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║   System BCM - Deployment Validation                  ║"
echo "║   $(date '+%Y-%m-%d %H:%M:%S')                          ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# Phase 1: Infrastructure Tests
# ============================================================================
print_header "Phase 1: Infrastructure Validation"

run_test "Docker is running" "docker info"
run_test "Docker Compose is available" "docker-compose --version"
run_test "platform_network exists" "docker network ls | grep platform_network"

# ============================================================================
# Phase 2: Service Availability Tests
# ============================================================================
print_header "Phase 2: Service Availability"

run_test "System BCM container running" "docker ps | grep system-bcm-service"
run_test "Redis container running" "docker ps | grep redis"
run_test "Prometheus container running" "docker ps | grep prometheus"
run_test "Grafana container running" "docker ps | grep grafana"

run_test "System BCM port 8050 open" "curl -s http://localhost:8050/health"
run_test "Redis port 6379 open" "redis-cli -h localhost -p 6379 ping"
run_test "Prometheus port 9090 open" "curl -s http://localhost:9090/-/healthy"
run_test "Grafana port 3000 open" "curl -s http://localhost:3000/api/health"

# ============================================================================
# Phase 3: API Endpoint Tests
# ============================================================================
print_header "Phase 3: API Endpoints"

run_test_with_output "Health endpoint returns healthy" \
    "curl -s http://localhost:8050/health" \
    "healthy"

run_test_with_output "Status endpoint returns version" \
    "curl -s http://localhost:8050/status" \
    "1.0.0"

run_test "Metrics endpoint returns data" \
    "curl -s http://localhost:8050/metrics | grep system_bcm"

# ============================================================================
# Phase 4: Scenarios Tests
# ============================================================================
print_header "Phase 4: BCM Scenarios"

run_test "Scenarios directory exists" "[ -d scenarios ]"
run_test "platform_bia.json exists" "[ -f scenarios/platform_bia.json ]"
run_test "platform_risks.json exists" "[ -f scenarios/platform_risks.json ]"
run_test "recovery_procedures.json exists" "[ -f scenarios/recovery_procedures.json ]"
run_test "resource_priorities.json exists" "[ -f scenarios/resource_priorities.json ]"

run_test "platform_bia.json is valid JSON" "jq empty scenarios/platform_bia.json"
run_test "platform_risks.json is valid JSON" "jq empty scenarios/platform_risks.json"
run_test "recovery_procedures.json is valid JSON" "jq empty scenarios/recovery_procedures.json"
run_test "resource_priorities.json is valid JSON" "jq empty scenarios/resource_priorities.json"

# ============================================================================
# Phase 5: Functional Tests
# ============================================================================
print_header "Phase 5: Functional Tests"

echo "Triggering BCM cycle (this may take a few seconds)..."
if curl -s -X POST http://localhost:8050/cycle/trigger > /tmp/cycle_result.json 2>&1; then
    echo -e "${GREEN}✅ Cycle triggered successfully${NC}"

    # Wait for cycle to complete
    sleep 3

    # Check cycle result
    run_test_with_output "Cycle completed successfully" \
        "cat /tmp/cycle_result.json" \
        "success"

    run_test_with_output "BIA phase completed" \
        "cat /tmp/cycle_result.json" \
        "bia"

    run_test_with_output "Risk assessment completed" \
        "cat /tmp/cycle_result.json" \
        "risk_assessment"

    run_test_with_output "Recovery setup completed" \
        "cat /tmp/cycle_result.json" \
        "recovery_setup"

    run_test_with_output "Priority application completed" \
        "cat /tmp/cycle_result.json" \
        "priority_application"

    # Check insights generated
    insights_count=$(jq '.learning_results.insights_generated | length' /tmp/cycle_result.json 2>/dev/null || echo "0")
    if [ "$insights_count" -gt 0 ]; then
        echo -e "Test: Insights generated... ${GREEN}✅ PASS${NC} ($insights_count insights)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "Test: Insights generated... ${YELLOW}⚠️  WARN${NC} (0 insights)"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))

else
    echo -e "${RED}❌ Failed to trigger cycle${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# ============================================================================
# Phase 6: EventBus Tests
# ============================================================================
print_header "Phase 6: EventBus Integration"

# Check if events were published
echo "Checking for BCM events in Redis..."

if redis-cli XINFO STREAMS platform.bcm.* 2>/dev/null | grep -q "platform.bcm"; then
    echo -e "${GREEN}✅ BCM events found in EventBus${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))

    # Count events
    event_count=$(redis-cli XLEN platform.bcm.cycle.completed 2>/dev/null || echo "0")
    echo "  └─ platform.bcm.cycle.completed: $event_count events"

else
    echo -e "${YELLOW}⚠️  No BCM events yet (may be normal on first run)${NC}"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# ============================================================================
# Phase 7: Monitoring Tests
# ============================================================================
print_header "Phase 7: Monitoring Stack"

# Check Prometheus targets
echo "Checking Prometheus targets..."
if curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | select(.labels.job=="system-bcm") | .health' | grep -q "up"; then
    echo -e "${GREEN}✅ System BCM target is up in Prometheus${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️  System BCM target not found or down${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Check if metrics are being scraped
echo "Checking if metrics are being scraped..."
if curl -s "http://localhost:9090/api/v1/query?query=system_bcm_running" | jq -r '.data.result[0].value[1]' | grep -q "1"; then
    echo -e "${GREEN}✅ Metrics being scraped successfully${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️  Metrics not found (may take a minute)${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Check Grafana datasource
echo "Checking Grafana datasource..."
if curl -s -u admin:admin http://localhost:3000/api/datasources | jq -r '.[].type' | grep -q "prometheus"; then
    echo -e "${GREEN}✅ Prometheus datasource configured in Grafana${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️  Prometheus datasource not configured${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_RUN=$((TESTS_RUN + 1))

# ============================================================================
# Phase 8: Performance Tests
# ============================================================================
print_header "Phase 8: Performance Validation"

# Measure cycle time
echo "Measuring cycle performance..."
start_time=$(date +%s)
curl -s -X POST http://localhost:8050/cycle/trigger > /dev/null
end_time=$(date +%s)
cycle_time=$((end_time - start_time))

if [ $cycle_time -lt 10 ]; then
    echo -e "${GREEN}✅ Cycle completed in ${cycle_time}s (target: <10s)${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️  Cycle took ${cycle_time}s (target: <10s)${NC}"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Check resource usage
echo "Checking resource usage..."
cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" system-bcm-service | sed 's/%//')
mem_usage=$(docker stats --no-stream --format "{{.MemPerc}}" system-bcm-service | sed 's/%//')

echo "  CPU: ${cpu_usage}%"
echo "  Memory: ${mem_usage}%"

if (( $(echo "$cpu_usage < 50" | bc -l) )); then
    echo -e "${GREEN}✅ CPU usage normal${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️  High CPU usage${NC}"
fi
TESTS_RUN=$((TESTS_RUN + 1))

if (( $(echo "$mem_usage < 50" | bc -l) )); then
    echo -e "${GREEN}✅ Memory usage normal${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️  High memory usage${NC}"
fi
TESTS_RUN=$((TESTS_RUN + 1))

# ============================================================================
# Summary
# ============================================================================
print_header "Validation Summary"

echo "Tests run:    $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"

success_rate=$((TESTS_PASSED * 100 / TESTS_RUN))
echo ""
echo "Success rate: ${success_rate}%"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ DEPLOYMENT VALIDATION SUCCESSFUL                  ║${NC}"
    echo -e "${GREEN}║  System BCM Service is fully operational!            ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Monitor Grafana dashboard: http://localhost:3000"
    echo "  2. Check Prometheus metrics: http://localhost:9090"
    echo "  3. View service logs: docker-compose logs -f system-bcm"
    echo "  4. Trigger manual cycle: curl -X POST http://localhost:8050/cycle/trigger"
    echo ""
    exit 0
elif [ $success_rate -ge 80 ]; then
    echo -e "${YELLOW}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  ⚠️  DEPLOYMENT VALIDATION: WARNINGS DETECTED         ║${NC}"
    echo -e "${YELLOW}║  System is functional but some issues found          ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Review warnings above and:"
    echo "  1. Check service logs: docker-compose logs"
    echo "  2. Run health check: ./health-check.sh"
    echo "  3. Review configuration: .env"
    echo ""
    exit 1
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ DEPLOYMENT VALIDATION FAILED                      ║${NC}"
    echo -e "${RED}║  Critical issues detected - DO NOT USE IN PRODUCTION ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Critical issues detected. Please:"
    echo "  1. Check service logs: docker-compose logs"
    echo "  2. Verify all containers running: docker-compose ps"
    echo "  3. Check network: docker network inspect platform_network"
    echo "  4. Review errors above"
    echo ""
    exit 2
fi
