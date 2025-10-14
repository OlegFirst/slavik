#!/bin/bash
# ===================================================
# Scenario Intelligence - Environment Setup Script
# ===================================================

set -e  # Exit on error

echo "=========================================="
echo "Scenario Intelligence - Environment Setup"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# ===================================================
# 1. Check Prerequisites
# ===================================================
echo ""
echo "1️⃣  Checking prerequisites..."

# Python 3.9+
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status 0 "Python 3 found: $PYTHON_VERSION"
else
    print_status 1 "Python 3 not found"
    exit 1
fi

# pip
if command_exists pip3; then
    print_status 0 "pip3 found"
else
    print_status 1 "pip3 not found"
    exit 1
fi

# PostgreSQL (optional)
if command_exists psql; then
    print_status 0 "PostgreSQL client found"
else
    print_info "PostgreSQL client not found (optional)"
fi

# ===================================================
# 2. Create .env file if not exists
# ===================================================
echo ""
echo "2️⃣  Setting up environment variables..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status 0 "Created .env from .env.example"
        print_info "Please edit .env with your actual credentials"
    else
        print_status 1 ".env.example not found"
        exit 1
    fi
else
    print_status 0 ".env already exists"
fi

# ===================================================
# 3. Install Python dependencies
# ===================================================
echo ""
echo "3️⃣  Installing Python dependencies..."

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    print_status $? "Python dependencies installed"
else
    print_info "requirements.txt not found, skipping"
fi

# ===================================================
# 4. Create directories
# ===================================================
echo ""
echo "4️⃣  Creating required directories..."

mkdir -p logs
mkdir -p generated/l1_platform
mkdir -p generated/l1_applications
mkdir -p generated/l2
mkdir -p generated/l3
mkdir -p generated/l4
mkdir -p execution_reports

print_status 0 "Directories created"

# ===================================================
# 5. Test configuration
# ===================================================
echo ""
echo "5️⃣  Testing configuration..."

python3 config.py
CONFIG_VALID=$?

if [ $CONFIG_VALID -eq 0 ]; then
    print_status 0 "Configuration is valid"
else
    print_status 1 "Configuration has errors"
    print_info "Please check your .env file"
fi

# ===================================================
# 6. Database check (if configured)
# ===================================================
echo ""
echo "6️⃣  Checking database connection..."

if [ ! -z "$DATABASE_URL" ]; then
    python3 -c "
import asyncio
import sys
sys.path.insert(0, '.')
from storage.postgres_storage import PostgresScenarioStorage

async def test():
    try:
        storage = PostgresScenarioStorage(connection_string='$DATABASE_URL')
        await storage.initialize()
        stats = await storage.get_statistics()
        print(f'✅ Database connected: {stats.get(\"total_scenarios\", 0)} scenarios')
        await storage.close()
        return 0
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return 1

sys.exit(asyncio.run(test()))
"
    DB_STATUS=$?
    if [ $DB_STATUS -eq 0 ]; then
        print_status 0 "Database connection successful"
    else
        print_info "Database connection failed (check credentials in .env)"
    fi
else
    print_info "DATABASE_URL not set, skipping database check"
fi

# ===================================================
# 7. EventBus check (if configured)
# ===================================================
echo ""
echo "7️⃣  Checking EventBus connection..."

if [ ! -z "$EVENTBUS_HOST" ] && [ "$EVENTBUS_ENABLED" = "true" ]; then
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from integrations.eventbus_client import ScenarioEventBusClient
    print('✅ EventBus client available')
    sys.exit(0)
except ImportError as e:
    print(f'ℹ️  EventBus client not available: {e}')
    sys.exit(0)
"
    print_status $? "EventBus client check"
else
    print_info "EventBus not enabled, skipping"
fi

# ===================================================
# 8. Summary
# ===================================================
echo ""
echo "=========================================="
echo "✅ Environment setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit .env with your actual credentials"
echo "  2. Test the system: python3 test_system.py"
echo "  3. Start the API: python3 -m api.main"
echo ""
echo "For more information, see README.md"
