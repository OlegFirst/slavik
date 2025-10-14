#!/bin/bash

# Test runner script for Planning Service
# Sets up Python path and runs pytest

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set Python path to include parent directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run pytest with coverage
echo "Running Planning Service Test Suite..."
echo "======================================"

python3 -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing --cov-report=html "$@"

echo ""
echo "Coverage report generated in htmlcov/index.html"
