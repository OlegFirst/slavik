#!/bin/bash
# Test Runner for AI-Platform-ISO
# Provides convenient commands to run different test suites

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function to print colored output
print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Installing..."
    pip install -r tests/requirements-test.txt
fi

# Function to run tests
run_tests() {
    local test_path="$1"
    local description="$2"
    local extra_args="${3:-}"

    print_status "Running $description..."

    if pytest "$test_path" $extra_args -v; then
        print_success "$description passed"
        return 0
    else
        print_error "$description failed"
        return 1
    fi
}

# Main menu
case "${1:-help}" in
    all)
        print_status "Running ALL tests..."
        pytest tests/ -v
        ;;

    unit)
        print_status "Running UNIT tests only..."
        pytest tests/unit/ -v -m "unit"
        ;;

    integration)
        print_status "Running INTEGRATION tests only..."
        pytest tests/integration/ -v -m "integration"
        ;;

    e2e)
        print_status "Running E2E tests only..."
        pytest tests/e2e/ -v -m "e2e"
        ;;

    performance)
        print_status "Running PERFORMANCE tests only..."
        pytest tests/performance/ -v -m "performance"
        ;;

    security)
        print_status "Running SECURITY tests only..."
        pytest tests/ -v -m "security"
        ;;

    platform)
        print_status "Running Platform Services tests..."
        pytest tests/unit/platform-services/ -v
        ;;

    intelligent)
        print_status "Running Intelligent Core tests..."
        pytest tests/unit/intelligent-core/ -v
        ;;

    infrastructure)
        print_status "Running Infrastructure tests..."
        pytest tests/unit/infrastructure/ -v
        ;;

    fast)
        print_status "Running FAST tests only (excluding slow)..."
        pytest tests/ -v -m "not slow"
        ;;

    coverage)
        print_status "Running tests with coverage report..."
        pytest tests/ --cov=platform-services --cov=intelligent-core --cov=infrastructure \
               --cov-report=html --cov-report=term-missing -v
        print_success "Coverage report generated in htmlcov/"
        ;;

    watch)
        print_status "Running tests in watch mode..."
        print_warning "This requires pytest-watch (pip install pytest-watch)"
        ptw tests/ -- -v
        ;;

    failed)
        print_status "Re-running only FAILED tests from last run..."
        pytest tests/ --lf -v
        ;;

    specific)
        if [ -z "$2" ]; then
            print_error "Please specify test file or path"
            print_status "Usage: ./run_tests.sh specific tests/unit/platform-services/bia-service/"
            exit 1
        fi
        print_status "Running specific test: $2"
        pytest "$2" -v
        ;;

    bia)
        run_tests "tests/unit/platform-services/bia-service/" "BIA Service tests"
        ;;

    risk)
        run_tests "tests/unit/platform-services/risk-service/" "Risk Service tests"
        ;;

    compliance)
        run_tests "tests/unit/platform-services/compliance-service/" "Compliance Service tests"
        ;;

    workflow)
        run_tests "tests/unit/intelligent-core/workflow-intelligence/" "Workflow Intelligence tests"
        ;;

    orchestration)
        run_tests "tests/unit/intelligent-core/ai-orchestration/" "AI Orchestration tests"
        ;;

    help|*)
        echo ""
        echo "AI-Platform-ISO Test Runner"
        echo "============================"
        echo ""
        echo "Usage: ./run_tests.sh [command]"
        echo ""
        echo "Commands:"
        echo "  all              Run all tests"
        echo "  unit             Run unit tests only"
        echo "  integration      Run integration tests only"
        echo "  e2e              Run end-to-end tests only"
        echo "  performance      Run performance tests only"
        echo "  security         Run security tests only"
        echo ""
        echo "By Category:"
        echo "  platform         Run all Platform Services tests"
        echo "  intelligent      Run all Intelligent Core tests"
        echo "  infrastructure   Run all Infrastructure tests"
        echo ""
        echo "By Service:"
        echo "  bia              Run BIA Service tests"
        echo "  risk             Run Risk Service tests"
        echo "  compliance       Run Compliance Service tests"
        echo "  workflow         Run Workflow Intelligence tests"
        echo "  orchestration    Run AI Orchestration tests"
        echo ""
        echo "Options:"
        echo "  fast             Run fast tests (exclude slow)"
        echo "  coverage         Run with coverage report"
        echo "  watch            Run in watch mode (auto-rerun on changes)"
        echo "  failed           Re-run only failed tests from last run"
        echo "  specific <path>  Run specific test file or directory"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh unit              # Run all unit tests"
        echo "  ./run_tests.sh platform          # Run all platform services tests"
        echo "  ./run_tests.sh coverage          # Run with coverage"
        echo "  ./run_tests.sh specific tests/unit/platform-services/bia-service/"
        echo ""
        ;;
esac

# Exit with appropriate code
exit $?
