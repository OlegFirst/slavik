#!/bin/bash
# Quick Infrastructure Start
# Запускает infrastructure БЕЗ AI модулей (не нужны API ключи)

set -e

echo "🚀 Starting Infrastructure (without AI modules)"
echo "================================================"

# Load environment
export $(cat .env | grep -v '^#' | xargs)

# Step 1: Test connections
echo ""
echo "📡 Step 1: Testing connections..."

echo -n "  PostgreSQL (Supabase): "
if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌ Failed - check DATABASE_URL"
    exit 1
fi

echo -n "  Redis: "
if redis-cli -u "$REDIS_URL" ping > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌ Failed - check REDIS_URL"
    exit 1
fi

echo -n "  Qdrant: "
if curl -s -H "api-key: $QDRANT_API_KEY" "$QDRANT_URL/collections" > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌ Failed - check QDRANT_URL/QDRANT_API_KEY"
    exit 1
fi

# Step 2: Check Docker
echo ""
echo "🐳 Step 2: Checking Docker..."
if docker ps > /dev/null 2>&1; then
    echo "  ✅ Docker is running"
else
    echo "  ❌ Docker is not running - please start Docker Desktop"
    exit 1
fi

# Step 3: Start Observability Stack
echo ""
echo "📊 Step 3: Starting Observability Stack..."
cd infrastructure/observability

if [ -f "docker-compose.monitoring.yml" ]; then
    docker-compose -f docker-compose.monitoring.yml up -d \
        prometheus grafana loki promtail alertmanager node-exporter
    echo "  ✅ Started: Prometheus, Grafana, Loki, AlertManager"
else
    echo "  ⚠️  docker-compose.monitoring.yml not found, skipping"
fi

cd ../..

# Step 4: Start API Gateway
echo ""
echo "🌐 Step 4: Starting API Gateway..."

# Check if already running
if lsof -i :8000 > /dev/null 2>&1; then
    echo "  ⚠️  Port 8000 already in use, skipping"
else
    cd infrastructure/gateway/api-gateway

    # Start in background
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../../../logs/api-gateway.log 2>&1 &

    sleep 3

    if curl -s http://localhost:8000/health > /dev/null; then
        echo "  ✅ API Gateway started on port 8000"
    else
        echo "  ⚠️  API Gateway might need more time to start"
    fi

    cd ../../..
fi

# Step 5: Summary
echo ""
echo "================================================"
echo "✅ Infrastructure Started Successfully!"
echo "================================================"
echo ""
echo "🌐 Access Points:"
echo "  • API Gateway:   http://localhost:8000"
echo "  • API Gateway Docs: http://localhost:8000/docs"
echo "  • Prometheus:    http://localhost:9090"
echo "  • Grafana:       http://localhost:3000 (admin/admin123)"
echo "  • AlertManager:  http://localhost:9093"
echo ""
echo "📊 Check Status:"
echo "  docker-compose -f infrastructure/observability/docker-compose.monitoring.yml ps"
echo "  curl http://localhost:8000/health"
echo ""
echo "📝 Logs:"
echo "  • API Gateway: tail -f logs/api-gateway.log"
echo "  • Monitoring:  docker-compose -f infrastructure/observability/docker-compose.monitoring.yml logs -f"
echo ""
echo "⏹️  Stop Everything:"
echo "  docker-compose -f infrastructure/observability/docker-compose.monitoring.yml down"
echo "  pkill -f 'uvicorn main:app'"
echo ""
echo "🤖 Next Steps:"
echo "  1. Add AI API keys to .env (OPENAI_API_KEY, ANTHROPIC_API_KEY)"
echo "  2. Then start core modules:"
echo "     cd intelligent-core/ai-foundation && uvicorn main:app --port 9001"
echo "     cd intelligent-core/workflow_intelligence && uvicorn main:app --port 9002"
echo "     cd intelligent-core/expertise-center && uvicorn main:app --port 9003"
