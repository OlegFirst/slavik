#!/bin/bash
#
# Integration Test Runner
#
# Starts services via docker-compose and runs integration tests
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}BCM Platform Integration Test Runner${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Change to integration-tests directory
cd "$(dirname "$0")"

# Load environment variables
if [ -f .env.test ]; then
    export $(cat .env.test | grep -v '^#' | xargs)
    echo -e "${GREEN}✅ Loaded test environment variables${NC}"
else
    echo -e "${YELLOW}⚠️  No .env.test file found, using defaults${NC}"
fi

# Clean up any existing test containers
echo -e "${YELLOW}🧹 Cleaning up existing test containers...${NC}"
docker-compose -f docker-compose.test.yml down -v --remove-orphans 2>/dev/null || true
echo ""

# Start services
echo -e "${GREEN}🚀 Starting test services...${NC}"
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to become healthy...${NC}"
echo ""

MAX_WAIT=120  # Maximum wait time in seconds
ELAPSED=0
INTERVAL=5

while [ $ELAPSED -lt $MAX_WAIT ]; do
    # Check health of all services
    HEALTHY_COUNT=$(docker-compose -f docker-compose.test.yml ps | grep -c "healthy" || true)
    TOTAL_COUNT=$(docker-compose -f docker-compose.test.yml ps --services | wc -l)

    echo -e "${YELLOW}   Healthy services: ${HEALTHY_COUNT}${NC}"

    # Check if all services are healthy
    if [ "$HEALTHY_COUNT" -ge 4 ]; then
        echo -e "${GREEN}✅ All services are healthy!${NC}"
        echo ""
        break
    fi

    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo -e "${RED}❌ Services failed to become healthy within ${MAX_WAIT}s${NC}"
    echo ""
    echo "Container status:"
    docker-compose -f docker-compose.test.yml ps
    echo ""
    echo "Logs:"
    docker-compose -f docker-compose.test.yml logs --tail=50
    exit 1
fi

# Show service status
echo -e "${GREEN}Service Status:${NC}"
docker-compose -f docker-compose.test.yml ps
echo ""

# Run tests
echo -e "${GREEN}🧪 Running integration tests...${NC}"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Install dependencies if needed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
    pip install -q -r requirements.txt
fi

# Run pytest with options
PYTEST_ARGS="$@"

if [ -z "$PYTEST_ARGS" ]; then
    # Default: run all tests with verbose output
    PYTEST_ARGS="-v --tb=short --maxfail=5"
fi

echo -e "${GREEN}Running: pytest ${PYTEST_ARGS}${NC}"
echo ""

# Run tests and capture exit code
set +e  # Don't exit on test failure
pytest $PYTEST_ARGS
TEST_EXIT_CODE=$?
set -e

echo ""

# Show test summary
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ All integration tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}❌ Some integration tests failed${NC}"
    echo -e "${RED}========================================${NC}"
fi

echo ""

# Cleanup
read -p "Do you want to stop test services? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 Stopping and removing test services...${NC}"
    docker-compose -f docker-compose.test.yml down -v
    echo -e "${GREEN}✅ Cleanup complete${NC}"
else
    echo -e "${YELLOW}⚠️  Test services are still running${NC}"
    echo -e "${YELLOW}   To stop them, run: docker-compose -f docker-compose.test.yml down -v${NC}"
fi

echo ""

# Exit with test result code
exit $TEST_EXIT_CODE
