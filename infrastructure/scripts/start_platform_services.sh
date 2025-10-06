#!/bin/bash

# Start All Platform Services
# Usage: ./scripts/start_platform_services.sh

echo "🚀 Starting All Platform Services..."
echo "====================================="
echo ""

# Base directory
BASE_DIR="/Users/MD/AI-Platform-ISO/platform-services"

# Services configuration
declare -A SERVICES=(
    ["bia-service"]=8001
    ["risk-service"]=8002
    ["compliance-service"]=8003
    ["documents-service"]=8004
    ["response-service"]=8005
    ["validation-service"]=8006
    ["governance-service"]=8007
    ["planning_service"]=8008
    ["plans_service"]=8009
    ["learning-service"]=8010
    ["community-service"]=8011
)

# Log directory
LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR"

# Start each service
for service in "${!SERVICES[@]}"; do
    port=${SERVICES[$service]}
    service_dir="$BASE_DIR/$service"

    if [ -d "$service_dir" ]; then
        echo "Starting $service on port $port..."

        cd "$service_dir"

        # Install dependencies if needed
        if [ -f "requirements.txt" ] && [ ! -d "venv" ]; then
            echo "  Installing dependencies..."
            pip install -q -r requirements.txt
        fi

        # Start service in background
        nohup uvicorn main:app --host 0.0.0.0 --port $port \
            > "$LOG_DIR/${service}.log" 2>&1 &

        echo "  ✅ Started on port $port (PID: $!)"
        echo $! > "$LOG_DIR/${service}.pid"
    else
        echo "  ⚠️  Service directory not found: $service_dir"
    fi

    echo ""
done

echo "====================================="
echo "✅ All services started!"
echo ""
echo "📝 Logs directory: $LOG_DIR"
echo "🏥 Check health: ./scripts/health_check_all.sh"
echo ""
echo "To stop all services:"
echo "  ./scripts/stop_platform_services.sh"
