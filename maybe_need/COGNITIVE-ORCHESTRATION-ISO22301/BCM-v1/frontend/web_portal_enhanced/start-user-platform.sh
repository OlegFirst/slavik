#!/bin/bash

echo "🚀 Starting BCM User Platform..."
echo "================================"

# Navigate to user platform directory
cd /Users/MD/ISO-22301/frontend/web_portal_enhanced

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "📝 Creating .env from example..."
    cp .env.example .env
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Check if real services are running
echo ""
echo "🔍 Checking backend services..."

check_service() {
    local name=$1
    local port=$2
    local path=$3
    
    if curl -s --max-time 3 "http://localhost:$port$path" > /dev/null 2>&1; then
        echo "✅ $name - Port $port is available"
        return 0
    else
        echo "❌ $name - Port $port is not responding"
        return 1
    fi
}

# Check core services
AI_ORCHESTRATOR=false
BCM_CORE=false
BIA_ENGINE=false
MONITORING=false

if check_service "AI Orchestrator" 8000 "/health"; then
    AI_ORCHESTRATOR=true
fi

if check_service "BCM Core (Odoo)" 8069 "/web/health"; then
    BCM_CORE=true
fi

if check_service "BIA Engine" 8082 "/health"; then
    BIA_ENGINE=true
fi

if check_service "Grafana" 3000 "/api/health"; then
    MONITORING=true
fi

# Service availability summary
echo ""
echo "📊 Service Availability Summary:"
if [ "$AI_ORCHESTRATOR" = true ] && [ "$BCM_CORE" = true ] && [ "$BIA_ENGINE" = true ]; then
    echo "✅ Core BCM services are running - using real data"
    export VITE_ENABLE_REAL_API=true
elif [ "$AI_ORCHESTRATOR" = true ] || [ "$BCM_CORE" = true ] || [ "$BIA_ENGINE" = true ]; then
    echo "⚠️  Some BCM services are running - mixed real/mock data"
    export VITE_ENABLE_REAL_API=true
else
    echo "❌ No BCM services detected - using mock data"
    export VITE_ENABLE_REAL_API=false
    echo ""
    echo "💡 To start backend services, run:"
    echo "   cd /Users/MD/ISO-22301"
    echo "   docker-compose up -d"
fi

if [ "$MONITORING" = true ]; then
    echo "✅ Monitoring stack available"
else
    echo "❌ Monitoring stack not available"
fi

# Display connection info
echo ""
echo "🌐 Platform URLs:"
echo "   • User Platform:  http://localhost:5173"
echo "   • Admin Panel:    http://localhost:3001" 
if [ "$BCM_CORE" = true ]; then
    echo "   • BCM Core:       http://localhost:8069"
fi
if [ "$AI_ORCHESTRATOR" = true ]; then
    echo "   • AI Orchestrator: http://localhost:8000"
fi
if [ "$MONITORING" = true ]; then
    echo "   • Grafana:        http://localhost:3000"
fi

echo ""
echo "🔧 Development Features:"
echo "   • Hot reload enabled"
echo "   • Real-time data updates"
echo "   • WebSocket connections (if available)"
echo "   • Debug mode enabled"

echo ""
echo "🎯 Starting development server..."
echo "   Press Ctrl+C to stop"
echo ""

# Start the development server
npm run dev -- --port 5173 --host 0.0.0.0
