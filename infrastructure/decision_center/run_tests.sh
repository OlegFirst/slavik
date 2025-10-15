#!/bin/bash
#
# Run Decision Center Tests
#
# Usage:
#   ./run_tests.sh                    # Run all tests
#   ./run_tests.sh test_name          # Run specific test
#   ./run_tests.sh --with-api         # Run with API key (set ANTHROPIC_API_KEY)
#

set -e

# Change to infrastructure directory (parent of decision_center)
cd "$(dirname "$0")/.."

# Set PYTHONPATH to include infrastructure directory
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "==================================="
echo "Decision Center Test Runner"
echo "==================================="
echo "PYTHONPATH: $PYTHONPATH"
echo "Working dir: $(pwd)"
echo ""

# Check if API key is set
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ ANTHROPIC_API_KEY is set - will test real AI"
else
    echo "⚠️  ANTHROPIC_API_KEY not set - will test fallback only"
fi

echo "==================================="
echo ""

# Run pytest from infrastructure directory
if [ $# -eq 0 ]; then
    # Run all tests
    python3 -m pytest decision_center/tests/ -v -s
elif [ "$1" == "--with-api" ]; then
    # Run tests that require API
    python3 -m pytest decision_center/tests/test_ai_integration_e2e.py -v -s -k "real_api or consultation_with"
else
    # Run specific test
    python3 -m pytest decision_center/tests/test_ai_integration_e2e.py::$1 -v -s
fi
