#!/bin/bash

# ============================================================================
# BCM Platform Performance Test Suite Runner
# ============================================================================
# Runs complete performance testing suite including:
# - Service health checks
# - Baseline benchmarks
# - Load tests (light, medium, heavy)
# - Metrics collection
# - Report generation
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$SCRIPT_DIR/reports"
TEST_SCENARIO="${1:-light}"  # Default to light load

echo "============================================================================"
echo "🚀 BCM Platform Performance Test Suite"
echo "============================================================================"
echo "Test Scenario: $TEST_SCENARIO"
echo "Platform Dir: $PLATFORM_DIR"
echo "Reports Dir: $REPORTS_DIR"
echo "============================================================================"

# Create reports directory
mkdir -p "$REPORTS_DIR"

# ============================================================================
# Step 1: Check Prerequisites
# ============================================================================
echo ""
echo -e "${BLUE}Step 1: Checking Prerequisites...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

# Check if services are up
echo "Checking if services are running..."
cd "$PLATFORM_DIR"

if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Services not running. Starting services...${NC}"
    docker-compose up -d

    echo "Waiting for services to be healthy..."
    sleep 30

    # Wait for health checks
    max_attempts=12
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:8012/health > /dev/null 2>&1 && \
           curl -f http://localhost:8014/health > /dev/null 2>&1 && \
           curl -f http://localhost:8011/health > /dev/null 2>&1 && \
           curl -f http://localhost:8023/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ All services are healthy${NC}"
            break
        fi

        attempt=$((attempt + 1))
        echo "Attempt $attempt/$max_attempts - Waiting for services..."
        sleep 10
    done

    if [ $attempt -eq $max_attempts ]; then
        echo -e "${RED}❌ Services failed to become healthy${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Services are already running${NC}"
fi

# Check Python dependencies
cd "$SCRIPT_DIR"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# ============================================================================
# Step 2: Run Baseline Benchmarks
# ============================================================================
echo ""
echo -e "${BLUE}Step 2: Running Baseline Benchmarks...${NC}"

echo "Running API benchmarks..."
pytest benchmark_tests/test_api_benchmarks.py --benchmark-only \
    --benchmark-json="$REPORTS_DIR/benchmark_api.json" \
    --benchmark-min-rounds=5 || true

echo "Running database benchmarks..."
pytest benchmark_tests/test_database_benchmarks.py --benchmark-only \
    --benchmark-json="$REPORTS_DIR/benchmark_db.json" \
    --benchmark-min-rounds=3 || true

echo "Running cache benchmarks..."
pytest benchmark_tests/test_cache_benchmarks.py --benchmark-only \
    --benchmark-json="$REPORTS_DIR/benchmark_cache.json" \
    --benchmark-min-rounds=5 || true

echo -e "${GREEN}✅ Benchmarks completed${NC}"

# ============================================================================
# Step 3: Start Metrics Collection
# ============================================================================
echo ""
echo -e "${BLUE}Step 3: Starting Metrics Collection...${NC}"

# Determine collection duration based on scenario
if [ "$TEST_SCENARIO" == "light" ]; then
    DURATION=300  # 5 minutes
    USERS=10
    SPAWN_RATE=1
    RUN_TIME="5m"
elif [ "$TEST_SCENARIO" == "medium" ]; then
    DURATION=600  # 10 minutes
    USERS=50
    SPAWN_RATE=5
    RUN_TIME="10m"
elif [ "$TEST_SCENARIO" == "heavy" ]; then
    DURATION=900  # 15 minutes
    USERS=100
    SPAWN_RATE=10
    RUN_TIME="15m"
elif [ "$TEST_SCENARIO" == "stress" ]; then
    DURATION=1200  # 20 minutes
    USERS=200
    SPAWN_RATE=5
    RUN_TIME="20m"
else
    echo -e "${RED}❌ Unknown test scenario: $TEST_SCENARIO${NC}"
    echo "Valid scenarios: light, medium, heavy, stress"
    exit 1
fi

# Start metrics collector in background
python metrics_collector.py --duration $DURATION --interval 10 --output "$REPORTS_DIR/metrics.json" &
METRICS_PID=$!
echo -e "${GREEN}✅ Metrics collection started (PID: $METRICS_PID)${NC}"

# ============================================================================
# Step 4: Run Load Tests
# ============================================================================
echo ""
echo -e "${BLUE}Step 4: Running Load Tests ($TEST_SCENARIO scenario)...${NC}"
echo "Configuration: $USERS users, $SPAWN_RATE/sec spawn rate, $RUN_TIME duration"

if [ "$TEST_SCENARIO" == "stress" ]; then
    # Stress test uses custom load shape
    locust -f "load_tests/scenario_${TEST_SCENARIO}.py" \
        --headless \
        --host=http://localhost \
        --run-time=$RUN_TIME \
        --html="$REPORTS_DIR/locust_report_${TEST_SCENARIO}.html" \
        --csv="$REPORTS_DIR/locust_stats_${TEST_SCENARIO}"
else
    # Standard load tests
    locust -f "load_tests/scenario_${TEST_SCENARIO}.py" \
        --headless \
        --users=$USERS \
        --spawn-rate=$SPAWN_RATE \
        --host=http://localhost \
        --run-time=$RUN_TIME \
        --html="$REPORTS_DIR/locust_report_${TEST_SCENARIO}.html" \
        --csv="$REPORTS_DIR/locust_stats_${TEST_SCENARIO}"
fi

echo -e "${GREEN}✅ Load tests completed${NC}"

# ============================================================================
# Step 5: Wait for Metrics Collection
# ============================================================================
echo ""
echo -e "${BLUE}Step 5: Waiting for Metrics Collection...${NC}"

wait $METRICS_PID
echo -e "${GREEN}✅ Metrics collection completed${NC}"

# ============================================================================
# Step 6: Generate Performance Report
# ============================================================================
echo ""
echo -e "${BLUE}Step 6: Generating Performance Report...${NC}"

python generate_report.py \
    --locust-stats "$REPORTS_DIR/locust_stats_${TEST_SCENARIO}_stats.csv" \
    --benchmark "$REPORTS_DIR/benchmark_api.json" \
    --metrics "$REPORTS_DIR/metrics.json" \
    --output "$REPORTS_DIR/performance_report_${TEST_SCENARIO}.html"

echo -e "${GREEN}✅ Performance report generated${NC}"

# ============================================================================
# Step 7: Summary
# ============================================================================
echo ""
echo "============================================================================"
echo -e "${GREEN}🎉 Performance Testing Complete!${NC}"
echo "============================================================================"
echo ""
echo "📊 Generated Reports:"
echo "  - HTML Report: $REPORTS_DIR/performance_report_${TEST_SCENARIO}.html"
echo "  - Locust Report: $REPORTS_DIR/locust_report_${TEST_SCENARIO}.html"
echo "  - Metrics JSON: $REPORTS_DIR/metrics.json"
echo "  - Benchmarks: $REPORTS_DIR/benchmark_*.json"
echo ""
echo "🔍 View HTML Report:"
echo "  open $REPORTS_DIR/performance_report_${TEST_SCENARIO}.html"
echo ""
echo "============================================================================"

# Deactivate virtual environment
deactivate
