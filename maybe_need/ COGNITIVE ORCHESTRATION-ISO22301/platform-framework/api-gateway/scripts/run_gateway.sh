#!/bin/bash

# BCM API Gateway Deployment Script
# This script sets up and runs the BCM API Gateway service

echo "🚀 Starting BCM API Gateway Setup..."

# Set working directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8+ first.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [[ $(echo "$PYTHON_VERSION >= $REQUIRED_VERSION" | bc -l) -ne 1 ]]; then
    echo -e "${RED}❌ Python $PYTHON_VERSION is too old. Please install Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠️ .env file not found. Creating from .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env file. Please edit it with your configuration.${NC}"
    else
        echo -e "${RED}❌ No .env or .env.example file found!${NC}"
        echo "Creating basic .env file..."
        cat > .env << EOF
# BCM API Gateway Configuration
GATEWAY_PORT=8888
ODOO_URL=http://localhost:8069
ODOO_DB=bcm_db
ODOO_USER=admin
ODOO_PASSWORD=admin

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Service URLs
AI_ORCHESTRATOR_URL=http://localhost:8000
BIA_ENGINE_URL=http://localhost:8082
COMPLIANCE_CHECKER_URL=http://localhost:8084
DOCUMENT_PROCESSOR_URL=http://localhost:8083
SCENARIO_ORCHESTRATOR_URL=http://localhost:8085
AI_CONTROL_CENTER_URL=http://localhost:8200
MODULE_VALIDATOR_URL=http://localhost:5001
NOTIFICATION_SERVICE_URL=http://localhost:8002
DEPLOYER_SERVICE_URL=http://localhost:8009

# Environment
ENVIRONMENT=development
DEBUG=true
EOF
        echo -e "${GREEN}✅ Created basic .env file. Please edit it with your configuration.${NC}"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt -q

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Check if Redis is running
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠️ Redis is not running. Starting Redis...${NC}"
        if command -v brew &> /dev/null; then
            brew services start redis
        else
            redis-server --daemonize yes
        fi
    fi
else
    echo -e "${YELLOW}⚠️ Redis is not installed. Some features may not work.${NC}"
fi

# Check if Odoo is accessible
ODOO_URL=$(grep ODOO_URL .env | cut -d '=' -f2)
if curl -s -o /dev/null -w "%{http_code}" "$ODOO_URL/web/health" | grep -q "200\|302"; then
    echo -e "${GREEN}✅ Odoo is accessible at $ODOO_URL${NC}"
else
    echo -e "${YELLOW}⚠️ Cannot reach Odoo at $ODOO_URL. Make sure Odoo is running.${NC}"
fi

# Get port from .env or use default
GATEWAY_PORT=$(grep GATEWAY_PORT .env | cut -d '=' -f2)
GATEWAY_PORT=${GATEWAY_PORT:-8888}

# Kill any existing process on the port
if lsof -Pi :$GATEWAY_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}Port $GATEWAY_PORT is in use. Stopping existing process...${NC}"
    kill $(lsof -t -i:$GATEWAY_PORT) 2>/dev/null || true
    sleep 2
fi

# Start the API Gateway
echo -e "${GREEN}🚀 Starting BCM API Gateway on port $GATEWAY_PORT...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the API Gateway with uvicorn
uvicorn bcm_api_gateway:app \
    --host 0.0.0.0 \
    --port $GATEWAY_PORT \
    --reload \
    --log-level info \
    --access-log

# If the script reaches here, the server was stopped
echo ""
echo -e "${YELLOW}API Gateway stopped.${NC}"