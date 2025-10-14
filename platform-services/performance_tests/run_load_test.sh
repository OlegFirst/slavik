#!/bin/bash

# ============================================================================
# Run Specific Load Test Scenario
# ============================================================================
# Usage:
#   ./run_load_test.sh light
#   ./run_load_test.sh medium
#   ./run_load_test.sh heavy
#   ./run_load_test.sh stress
# ============================================================================

set -e

SCENARIO="${1:-light}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$SCRIPT_DIR/reports"

echo "============================================================================"
echo "🚀 Running Load Test: $SCENARIO"
echo "============================================================================"

mkdir -p "$REPORTS_DIR"

# Activate virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# Set parameters based on scenario
case "$SCENARIO" in
    light)
        USERS=10
        SPAWN_RATE=1
        DURATION="5m"
        ;;
    medium)
        USERS=50
        SPAWN_RATE=5
        DURATION="10m"
        ;;
    heavy)
        USERS=100
        SPAWN_RATE=10
        DURATION="15m"
        ;;
    stress)
        USERS=200
        SPAWN_RATE=5
        DURATION="20m"
        ;;
    *)
        echo "❌ Unknown scenario: $SCENARIO"
        echo "Valid scenarios: light, medium, heavy, stress"
        exit 1
        ;;
esac

echo "Configuration:"
echo "  Users: $USERS"
echo "  Spawn Rate: $SPAWN_RATE/sec"
echo "  Duration: $DURATION"
echo "============================================================================"

# Run Locust load test
if [ "$SCENARIO" == "stress" ]; then
    # Stress test uses custom load shape
    locust -f "load_tests/scenario_${SCENARIO}.py" \
        --headless \
        --host=http://localhost \
        --run-time=$DURATION \
        --html="$REPORTS_DIR/locust_${SCENARIO}.html" \
        --csv="$REPORTS_DIR/locust_${SCENARIO}"
else
    locust -f "load_tests/scenario_${SCENARIO}.py" \
        --headless \
        --users=$USERS \
        --spawn-rate=$SPAWN_RATE \
        --host=http://localhost \
        --run-time=$DURATION \
        --html="$REPORTS_DIR/locust_${SCENARIO}.html" \
        --csv="$REPORTS_DIR/locust_${SCENARIO}"
fi

echo ""
echo "============================================================================"
echo "✅ Load Test Complete!"
echo "============================================================================"
echo "Results:"
echo "  - HTML: $REPORTS_DIR/locust_${SCENARIO}.html"
echo "  - CSV: $REPORTS_DIR/locust_${SCENARIO}_stats.csv"
echo ""
echo "View report:"
echo "  open $REPORTS_DIR/locust_${SCENARIO}.html"
echo "============================================================================"

deactivate
