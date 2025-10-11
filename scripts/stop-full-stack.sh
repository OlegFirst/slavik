#!/bin/bash
# AI Platform ISO - Stop Full Stack
# Gracefully stops all services
# Date: 2025-10-11

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🛑 Stopping AI Platform ISO Full Stack..."
echo ""

cd "$PROJECT_ROOT"

# Stop services
docker-compose -f docker-compose.full-stack.yml down

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""
echo "💡 To remove volumes as well, use:"
echo "   docker-compose -f docker-compose.full-stack.yml down -v"
