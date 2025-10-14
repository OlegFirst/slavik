#!/bin/bash

# Security Test Suite Runner
# Runs all security tests for Workflow Intelligence

set -e  # Exit on error

echo "=========================================="
echo "  Workflow Intelligence Security Tests"
echo "=========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-asyncio pytest-cov
fi

# Check database connection
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set. Using default:"
    export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_bcm"
    echo "   $DATABASE_URL"
    echo ""
fi

# Test files
SQL_INJECTION_TESTS="test_sql_injection.py"
VALIDATION_TESTS="test_validation.py"
RLS_TESTS="test_rls.py"
INTEGRATION_TESTS="test_integration_security.py"

# Change to tests directory
cd "$(dirname "$0")"

echo "Running security test suite..."
echo ""

# Option 1: Run all tests together
if [ "$1" == "all" ] || [ -z "$1" ]; then
    echo "📋 Running ALL security tests..."
    echo ""
    pytest $SQL_INJECTION_TESTS $VALIDATION_TESTS $RLS_TESTS $INTEGRATION_TESTS -v --tb=short

    RESULT=$?
    echo ""
    if [ $RESULT -eq 0 ]; then
        echo "✅ All security tests PASSED!"
    else
        echo "❌ Some tests FAILED. Review output above."
        exit $RESULT
    fi
fi

# Option 2: Run individual test suites
if [ "$1" == "sql" ]; then
    echo "🛡️  Running SQL Injection tests..."
    pytest $SQL_INJECTION_TESTS -v
fi

if [ "$1" == "validation" ]; then
    echo "✔️  Running Validation tests..."
    pytest $VALIDATION_TESTS -v
fi

if [ "$1" == "rls" ]; then
    echo "🔒 Running RLS tests..."
    pytest $RLS_TESTS -v
fi

if [ "$1" == "integration" ]; then
    echo "🔗 Running Integration Security tests..."
    pytest $INTEGRATION_TESTS -v
fi

# Option 3: Run with coverage
if [ "$1" == "coverage" ]; then
    echo "📊 Running tests with coverage..."
    echo ""
    pytest $SQL_INJECTION_TESTS $VALIDATION_TESTS $RLS_TESTS $INTEGRATION_TESTS \
        --cov=../workflow_intelligence \
        --cov-report=html \
        --cov-report=term-missing \
        -v

    echo ""
    echo "📈 Coverage report generated: htmlcov/index.html"

    # Open coverage report if on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open htmlcov/index.html
    fi
fi

# Option 4: Quick smoke test
if [ "$1" == "quick" ]; then
    echo "⚡ Running quick smoke test..."
    pytest $SQL_INJECTION_TESTS::test_sql_injection_in_workflow_id \
           $VALIDATION_TESTS::test_workflow_metrics_numeric_validation \
           $RLS_TESTS::test_tenant_isolation_workflow_contexts \
           $INTEGRATION_TESTS::test_complete_workflow_tenant_isolation \
           -v
fi

echo ""
echo "=========================================="
echo "  Test run complete"
echo "=========================================="
