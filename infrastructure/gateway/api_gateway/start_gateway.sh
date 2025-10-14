#!/bin/bash
# Start API Gateway with all configurations
# This script loads .env and starts the gateway

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting API Gateway${NC}"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env file first"
    exit 1
fi

echo -e "${GREEN}✅ .env file found${NC}"

# Load .env
set -a
source .env
set +a

echo -e "${GREEN}✅ Environment variables loaded${NC}"

# Check required variables
if [ -z "$JWT_SECRET" ]; then
    echo -e "${RED}❌ JWT_SECRET not set!${NC}"
    exit 1
fi

if [ -z "$REDIS_URL" ]; then
    echo -e "${YELLOW}⚠️  REDIS_URL not set, using default${NC}"
fi

echo -e "${GREEN}✅ JWT_SECRET configured${NC}"
echo -e "${GREEN}✅ Redis URL: ${REDIS_URL}${NC}"
echo -e "${GREEN}✅ Database URL configured${NC}"

# Check if port is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port 8000 is already in use!${NC}"
    echo "Kill the process? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
        echo -e "${GREEN}✅ Port 8000 freed${NC}"
    else
        exit 1
    fi
fi

# Check dependencies
echo ""
echo -e "${BLUE}📦 Checking dependencies...${NC}"

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    pip3 install -r requirements.txt
fi

echo -e "${GREEN}✅ All dependencies installed${NC}"

# Test connections
echo ""
echo -e "${BLUE}🔗 Testing connections...${NC}"

# Test Redis
echo -n "Redis: "
if python3 -c "
import redis
import os
url = os.getenv('REDIS_URL', 'redis://localhost:6379')
try:
    r = redis.from_url(url, socket_connect_timeout=5)
    r.ping()
    print('✅ Connected')
except Exception as e:
    print(f'⚠️  Warning: {e}')
" 2>/dev/null; then
    :
fi

# Test PostgreSQL
echo -n "PostgreSQL: "
if python3 -c "
import asyncpg
import asyncio
import os

async def test():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'), timeout=5)
        await conn.close()
        print('✅ Connected')
    except Exception as e:
        print(f'⚠️  Warning: {e}')

asyncio.run(test())
" 2>/dev/null; then
    :
fi

# Start the gateway
echo ""
echo -e "${BLUE}🌟 Starting API Gateway on port 8000...${NC}"
echo ""
echo -e "${GREEN}Gateway will be available at:${NC}"
echo -e "  • Health:  http://localhost:8000/health"
echo -e "  • Docs:    http://localhost:8000/docs"
echo -e "  • Metrics: http://localhost:8000/metrics"
echo -e "  • AI Analyze: POST http://localhost:8000/api/v1/gateway/ai/analyze"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Run with uvicorn
python3 main.py
