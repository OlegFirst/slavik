#!/bin/bash

# Stop All Platform Services
# Usage: ./scripts/stop_platform_services.sh

echo "🛑 Stopping All Platform Services..."
echo "====================================="
echo ""

# Log directory
LOG_DIR="/Users/MD/AI-Platform-ISO/platform-services/logs"

# Find and kill all PID files
if [ -d "$LOG_DIR" ]; then
    for pidfile in "$LOG_DIR"/*.pid; do
        if [ -f "$pidfile" ]; then
            service=$(basename "$pidfile" .pid)
            pid=$(cat "$pidfile")

            echo "Stopping $service (PID: $pid)..."

            if kill -0 $pid 2>/dev/null; then
                kill $pid
                echo "  ✅ Stopped"
            else
                echo "  ⚠️  Process not running"
            fi

            rm "$pidfile"
        fi
    done
else
    echo "⚠️  No PID files found in $LOG_DIR"
fi

# Also kill any uvicorn processes (cleanup)
echo ""
echo "Cleaning up any remaining uvicorn processes..."
pkill -f "uvicorn main:app"

echo ""
echo "====================================="
echo "✅ All services stopped!"
