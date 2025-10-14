#!/bin/bash

# BCM Platform Services - Stop Script
# This script stops all BCM platform services

set -e

echo "🛑 Stopping BCM Platform Services..."
echo "===================================="

# Colors
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Stop all services
docker-compose down

echo ""
echo -e "${GREEN}✅ All services stopped!${NC}"
echo ""
echo "To remove all data (volumes), run:"
echo "  docker-compose down -v"
