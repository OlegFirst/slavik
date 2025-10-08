#!/bin/bash

# Test all infrastructure connections
# Проверяет доступность всех критичных сервисов

set -e

echo "🔍 Testing Infrastructure Connections"
echo "======================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Test PostgreSQL
echo -n "PostgreSQL (Supabase): "
if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connected${NC}"
else
    echo -e "${RED}❌ Failed${NC}"
    echo "  Fix: Check DATABASE_URL in .env"
fi

# Test Qdrant
echo -n "Qdrant Vector DB: "
if curl -s -H "api-key: $QDRANT_API_KEY" "$QDRANT_URL/collections" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connected${NC}"

    # Check collections
    collections=$(curl -s -H "api-key: $QDRANT_API_KEY" "$QDRANT_URL/collections" | grep -o '"name":"[^"]*"' | wc -l)
    echo "  Collections: $collections"
else
    echo -e "${RED}❌ Failed${NC}"
    echo "  Fix: Check QDRANT_URL and QDRANT_API_KEY in .env"
fi

# Test Redis
echo -n "Redis: "
if redis-cli -u "$REDIS_URL" ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connected${NC}"
else
    echo -e "${YELLOW}⚠️  Not running${NC}"
    echo "  Fix: docker run -d -p 6379:6379 redis:7-alpine"
fi

# Test OpenAI (optional)
if [ -n "$OPENAI_API_KEY" ]; then
    echo -n "OpenAI API: "
    if curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
        "https://api.openai.com/v1/models" | grep -q "gpt"; then
        echo -e "${GREEN}✅ Valid key${NC}"
    else
        echo -e "${RED}❌ Invalid key${NC}"
    fi
fi

# Test Anthropic (optional)
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo -n "Anthropic API: "
    if curl -s -H "x-api-key: $ANTHROPIC_API_KEY" \
        "https://api.anthropic.com/v1/messages" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{"model":"claude-3-haiku-20240307","max_tokens":1,"messages":[{"role":"user","content":"test"}]}' \
        | grep -q "content"; then
        echo -e "${GREEN}✅ Valid key${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not verify${NC}"
    fi
fi

echo "======================================"
echo -e "${GREEN}✅ Connection tests complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. ./infrastructure/scripts/start_all.sh"
echo "  2. ./infrastructure/scripts/start_core_modules.sh"
