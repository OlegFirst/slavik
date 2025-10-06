#!/bin/bash

# ============================================================================
# Run Benchmarks Only
# ============================================================================
# Runs pytest-benchmark tests without load testing
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$SCRIPT_DIR/reports"

echo "============================================================================"
echo "📊 Running Performance Benchmarks"
echo "============================================================================"

mkdir -p "$REPORTS_DIR"

# Activate virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

# Run all benchmark tests
echo "Running API benchmarks..."
pytest benchmark_tests/test_api_benchmarks.py \
    --benchmark-only \
    --benchmark-json="$REPORTS_DIR/benchmark_api.json" \
    --benchmark-min-rounds=10 \
    --benchmark-warmup=on

echo ""
echo "Running database benchmarks..."
pytest benchmark_tests/test_database_benchmarks.py \
    --benchmark-only \
    --benchmark-json="$REPORTS_DIR/benchmark_db.json" \
    --benchmark-min-rounds=5 \
    --benchmark-warmup=on

echo ""
echo "Running cache benchmarks..."
pytest benchmark_tests/test_cache_benchmarks.py \
    --benchmark-only \
    --benchmark-json="$REPORTS_DIR/benchmark_cache.json" \
    --benchmark-min-rounds=10 \
    --benchmark-warmup=on

echo ""
echo "Running bulk operation benchmarks..."
pytest benchmark_tests/test_bulk_operation_benchmarks.py \
    --benchmark-only \
    --benchmark-json="$REPORTS_DIR/benchmark_bulk.json" \
    --benchmark-min-rounds=5 \
    --benchmark-warmup=on

echo ""
echo "============================================================================"
echo "✅ Benchmarks Complete!"
echo "============================================================================"
echo "Results saved to:"
echo "  - $REPORTS_DIR/benchmark_api.json"
echo "  - $REPORTS_DIR/benchmark_db.json"
echo "  - $REPORTS_DIR/benchmark_cache.json"
echo "  - $REPORTS_DIR/benchmark_bulk.json"
echo "============================================================================"

deactivate
