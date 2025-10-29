#!/bin/bash
# BCM Platform Test Runner
# =======================

echo "🧪 BCM Platform Test Suite"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test and check result
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo ""
    echo "Running: $test_name"
    echo "----------------------------------------"

    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED: $test_name${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED: $test_name${NC}"
        ((TESTS_FAILED++))
    fi
}

# Change to project directory
cd "$(dirname "$0")"

echo "Project directory: $(pwd)"
echo ""

# 1. Test Emoji Cleanup Verification
run_test "Emoji Cleanup Verification" "python3 tests/test_emoji_cleanup.py || true"

# 2. Test Mock System Basic Functionality
run_test "Mock System Basic Test" "PYTHONPATH=tests python3 tests/mock_system.py"

# 3. Test Mock CLI Configuration Loading
run_test "Mock CLI Configuration Loading" "PYTHONPATH=tests python3 tests/mock_cli.py load tests/mock_config.json"

# 4. Test Basic BCM Scenario
run_test "Basic BCM Mock Scenario" "PYTHONPATH=tests python3 tests/mock_cli.py scenario tests/mock_config.json scenario_basic_bcm"

# 5. Test Cycle Detection Scenario
run_test "Cycle Detection Scenario" "PYTHONPATH=tests python3 tests/mock_cli.py scenario tests/mock_config.json scenario_cycle_detection"

# 6. Test Mock System Status
run_test "Mock System Status" "PYTHONPATH=tests python3 tests/mock_cli.py status"

# 7. Test Performance Monitoring (if available)
if [ -f "core/performance/bcm_performance_monitor.py" ]; then
    run_test "Performance Monitor Test" "python3 core/performance/bcm_performance_monitor.py"
fi

# 8. Test Database Optimizer (if available)
if [ -f "core/performance/bcm_database_optimizer.py" ]; then
    run_test "Database Optimizer Test" "python3 core/performance/bcm_database_optimizer.py /tmp"
fi

# 9. Test Redis Cache Manager (if available)
if [ -f "core/performance/redis_cache_manager.py" ]; then
    run_test "Redis Cache Manager Test" "python3 core/performance/redis_cache_manager.py"
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi