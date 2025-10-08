#!/bin/bash

# AI Event Manager - Start Script
# =================================

echo "🚀 Starting AI Event Manager with Full Integration"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check dependencies
echo "Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found${NC}"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ main.py not found. Are you in the right directory?${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt --quiet

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Check if other services are running
echo "Checking integration services..."

# Function to check if service is running
check_service() {
    local url=$1
    local name=$2

    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
        echo -e "${GREEN}✅ $name is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $name not available (optional)${NC}"
        return 1
    fi
}

# Check each service
check_service "http://localhost:8039/health" "Event Intelligence"
check_service "http://localhost:8050/health" "DevOps Agent"
check_service "http://localhost:8051/health" "GitHub Integration"
check_service "http://localhost:8046/health" "MIO Manager"

echo ""
echo "==========================================="
echo "AI Event Manager v2.0 - Full Integration"
echo "==========================================="
echo ""
echo "Capabilities:"
echo "  • Event analysis with AI"
echo "  • Continuous infrastructure scanning"
echo "  • Automatic gap detection"
echo "  • GitHub issue creation"
echo "  • EventBus integration"
echo "  • MIO Manager coordination"
echo ""
echo "API: http://localhost:8055"
echo "Docs: http://localhost:8055/docs"
echo "Metrics: http://localhost:8055/metrics"
echo ""
echo "==========================================="
echo ""

# Start the service
python3 main.py
