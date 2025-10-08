#!/bin/bash

# Authentication Service Startup Script
# Port: 8001

set -e

echo "🔐 Starting Authentication Service..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load .env if exists
if [ -f "$INFRA_DIR/.env" ]; then
    echo "📄 Loading .env from $INFRA_DIR/.env"
    export $(grep -v '^#' "$INFRA_DIR/.env" | xargs)
fi

# Set PYTHONPATH
export PYTHONPATH="$INFRA_DIR:$PYTHONPATH"
echo "📦 PYTHONPATH: $PYTHONPATH"

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "import fastapi, jwt, bcrypt, redis, asyncpg" 2>/dev/null || {
    echo "❌ Missing dependencies!"
    echo "Installing..."
    pip3 install fastapi uvicorn python-jose[cryptography] bcrypt redis asyncpg supabase python-dotenv
}

# Check Redis connection
echo "🔍 Checking Redis connection..."
if [ -n "$REDIS_URL" ]; then
    python3 -c "
import redis
import os
try:
    r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
    r.ping()
    print('✅ Redis connected')
except Exception as e:
    print(f'⚠️  Redis connection failed: {e}')
    print('Auth service will start but session storage may fail')
" || true
fi

# Check PostgreSQL connection
echo "🔍 Checking PostgreSQL connection..."
if [ -n "$DATABASE_URL" ]; then
    python3 -c "
import asyncpg
import asyncio
import os

async def test():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        await conn.close()
        print('✅ PostgreSQL connected')
    except Exception as e:
        print(f'⚠️  PostgreSQL connection failed: {e}')

asyncio.run(test())
" || true
fi

# Check if port 8001 is in use
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 8001 is already in use"
    echo "Killing process..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Generate JWT secret if not exists
if [ -z "$JWT_SECRET_KEY" ]; then
    echo "🔑 Generating JWT secret..."
    export JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> "$INFRA_DIR/.env"
    echo "✅ JWT secret saved to .env"
fi

# Start service
echo "🚀 Starting Auth Service on port 8001..."
cd "$SCRIPT_DIR"
python3 auth_service.py
