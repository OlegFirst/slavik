#!/bin/bash
# ==============================================================================
# Setup Testing Infrastructure for AI-Powered BCM Platform
# ==============================================================================
# This script sets up the complete testing environment
# Usage: bash scripts/setup_testing.sh
# ==============================================================================

set -e  # Exit on error

echo "🧪 Setting up Testing Infrastructure..."
echo "======================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo -e "\n${YELLOW}Step 1: Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [[ $(echo -e "$python_version\n$required_version" | sort -V | head -n1) == "$required_version" ]]; then
    echo -e "${GREEN}✓ Python $python_version detected (>= $required_version required)${NC}"
else
    echo -e "${RED}✗ Python $python_version detected. Please install Python >= $required_version${NC}"
    exit 1
fi

# Step 2: Install testing dependencies
echo -e "\n${YELLOW}Step 2: Installing testing dependencies...${NC}"
if [ -f "requirements-test.txt" ]; then
    pip install -r requirements-test.txt
    echo -e "${GREEN}✓ Testing dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements-test.txt not found${NC}"
    exit 1
fi

# Step 3: Create test directories
echo -e "\n${YELLOW}Step 3: Creating test directory structure...${NC}"
mkdir -p tests/{unit,integration,e2e,performance,security,chaos}
mkdir -p tests/fixtures/vcr_cassettes
mkdir -p tests/helpers
mkdir -p tests/unit/{workflow_intelligence,ai-foundation,expertise-center,orchestration,collective,community_intelligence,predictive}

echo -e "${GREEN}✓ Test directories created${NC}"

# Step 4: Setup test database (PostgreSQL)
echo -e "\n${YELLOW}Step 4: Setting up test database...${NC}"
read -p "Do you want to create a test database? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    DB_NAME="test_bcm"
    DB_USER="postgres"
    DB_HOST="localhost"
    DB_PORT="5432"

    echo "Creating test database: $DB_NAME"

    # Check if PostgreSQL is running
    if pg_isready -h $DB_HOST -p $DB_PORT > /dev/null 2>&1; then
        # Create database (will fail silently if exists)
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database may already exist"
        echo -e "${GREEN}✓ Test database ready${NC}"

        # Export DATABASE_URL
        export DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
        echo "Export this in your shell:"
        echo "  export DATABASE_URL=\"$DATABASE_URL\""
    else
        echo -e "${RED}✗ PostgreSQL not running on $DB_HOST:$DB_PORT${NC}"
        echo "Please start PostgreSQL and run this script again."
    fi
fi

# Step 5: Setup Redis (optional)
echo -e "\n${YELLOW}Step 5: Checking Redis...${NC}"
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠ Redis not running (using fakeredis for tests)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Redis not installed (using fakeredis for tests)${NC}"
fi

# Step 6: Install pre-commit hooks
echo -e "\n${YELLOW}Step 6: Setting up pre-commit hooks...${NC}"
if [ -f ".pre-commit-config.yaml" ]; then
    pip install pre-commit
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠ .pre-commit-config.yaml not found (skipping)${NC}"
fi

# Step 7: Create .env.test file
echo -e "\n${YELLOW}Step 7: Creating .env.test file...${NC}"
cat > .env.test << 'EOF'
# Test Environment Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/test_bcm
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
TEMPORAL_ADDRESS=localhost:7233

# AI Provider API Keys (use test keys or mocks)
ANTHROPIC_API_KEY=test-key-or-mock
OPENAI_API_KEY=test-key-or-mock
VOYAGE_API_KEY=test-key-or-mock

# Testing Flags
PYTEST_TIMEOUT=60
COVERAGE_THRESHOLD=80
EOF

echo -e "${GREEN}✓ .env.test created${NC}"
echo "Edit .env.test to add your actual test API keys"

# Step 8: Run initial test
echo -e "\n${YELLOW}Step 8: Running initial test suite...${NC}"
if pytest tests/ --collect-only > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test discovery successful${NC}"

    # Run actual tests if any exist
    test_count=$(pytest tests/ --collect-only -q 2>&1 | grep -E "^[0-9]+" | awk '{print $1}')
    if [ "$test_count" -gt 0 ]; then
        echo "Found $test_count tests. Running..."
        pytest tests/ -v --maxfail=5
    else
        echo -e "${YELLOW}⚠ No tests found yet. Start writing tests!${NC}"
    fi
else
    echo -e "${RED}✗ Test discovery failed${NC}"
    exit 1
fi

# Step 9: Generate coverage report
echo -e "\n${YELLOW}Step 9: Generating initial coverage report...${NC}"
pytest tests/ --cov=intelligent-core --cov-report=html --cov-report=term 2>/dev/null || echo -e "${YELLOW}⚠ Coverage report skipped (no tests yet)${NC}"

# Step 10: Summary
echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}🎉 Testing Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the testing strategy: doc-project/COMPREHENSIVE_TESTING_STRATEGY.md"
echo "  2. Start writing tests for critical modules"
echo "  3. Run tests: pytest tests/"
echo "  4. Check coverage: pytest --cov=intelligent-core --cov-report=html"
echo "  5. View coverage report: open htmlcov/index.html"
echo ""
echo "Quick commands:"
echo "  pytest tests/unit                 # Run unit tests only"
echo "  pytest -m 'not slow'              # Skip slow tests"
echo "  pytest -k test_workflow           # Run tests matching pattern"
echo "  pytest --maxfail=1                # Stop on first failure"
echo "  pytest -x                         # Stop on first failure (shorthand)"
echo "  pytest --lf                       # Run last failed tests"
echo "  pytest --durations=10             # Show 10 slowest tests"
echo ""
echo -e "${GREEN}Happy Testing! 🚀${NC}"
