#!/bin/bash

# Start ACE Service
# =================

set -e

echo "🚀 Starting ACE Service..."
echo ""

# Load environment
if [ -f "../../.env" ]; then
    export $(cat ../../.env | grep -v '^#' | xargs)
    echo "✅ Loaded environment from .env"
else
    echo "❌ .env file not found!"
    exit 1
fi

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set!"
    exit 1
fi

echo "📊 Database: Connected to Supabase"
echo "🌐 Service will run on: http://localhost:8050"
echo ""

# Check if already running
if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8050 is already in use"
    echo "   Kill existing process? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        lsof -ti:8050 | xargs kill -9 2>/dev/null || true
        echo "✅ Killed existing process"
        sleep 2
    else
        echo "❌ Cannot start - port already in use"
        exit 1
    fi
fi

# Start service
echo "🔄 Starting ACE Service..."
echo ""

# Option 1: Foreground (with logs)
if [ "$1" == "--foreground" ] || [ "$1" == "-f" ]; then
    python3 main.py

# Option 2: Background (default)
else
    nohup python3 main.py > ace_service.log 2>&1 &
    ACE_PID=$!
    echo "✅ ACE Service started (PID: $ACE_PID)"
    echo "📝 Logs: tail -f ace_service.log"
    echo ""

    # Wait for service to start
    echo "⏳ Waiting for service to initialize..."
    sleep 3

    # Check if it's running
    if ps -p $ACE_PID > /dev/null 2>&1; then
        echo "✅ Service is running!"
        echo ""
        echo "🔗 Health check: curl http://localhost:8050/health"
        echo "📊 Stats: curl http://localhost:8050/stats"
        echo "📈 Analytics: curl http://localhost:8050/api/v1/ace/analytics"
        echo ""
        echo "🛑 To stop: kill $ACE_PID"
    else
        echo "❌ Service failed to start - check ace_service.log"
        cat ace_service.log 2>/dev/null || echo "No log file found"
        exit 1
    fi
fi
