#!/bin/bash
# Start All Infrastructure Services
# ==================================

echo "🚀 Starting All Infrastructure Services..."
echo ""

# Kill old processes
echo "🧹 Cleaning old processes..."
killall -9 prometheus python3 2>/dev/null
sleep 2

# Create log directory
mkdir -p /tmp/ai-platform-logs

echo "📊 Starting Core Infrastructure..."

# 1. Prometheus
echo "  Starting Prometheus (9090)..."
cd /Users/MD/AI-Platform-ISO/infrastructure/monitoring/prometheus
prometheus --config.file=prometheus.yml --web.enable-lifecycle > /tmp/ai-platform-logs/prometheus.log 2>&1 &
sleep 2

# 2. monitoring-backend
echo "  Starting monitoring-backend (8050)..."
cd /Users/MD/AI-Platform-ISO/infrastructure/observability/monitoring-backend
python3 main.py > /tmp/ai-platform-logs/monitoring_backend.log 2>&1 &
sleep 2

# 3. auth-service
echo "  Starting auth-service (8081)..."
cd /Users/MD/AI-Platform-ISO/infrastructure/security/auth
PORT=8081 python3 main.py > /tmp/ai-platform-logs/auth.log 2>&1 &
sleep 2

# 4. realtime-websocket
echo "  Starting realtime-websocket (8082)..."
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/realtime-websocket
PORT=8082 python3 main.py > /tmp/ai-platform-logs/realtime_ws.log 2>&1 &
sleep 2

# 5. notification-service
echo "  Starting notification-service (8083)..."
cd /Users/MD/AI-Platform-ISO/infrastructure/observability/notification-service
PORT=8083 python3 main.py > /tmp/ai-platform-logs/notification.log 2>&1 &
sleep 2

echo ""
echo "🤖 Starting AI Office Infrastructure..."

# 6. ai-event-manager
echo "  Starting ai-event-manager (8055)..."
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/ai-event-manager
python3 main.py > /tmp/ai-platform-logs/ai_event_manager.log 2>&1 &
sleep 2

# 7. analytics-specialist (FIXED)
echo "  Starting analytics-specialist (8056)..."
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/analytics-specialist
python3 main.py > /tmp/ai-platform-logs/analytics_specialist.log 2>&1 &
sleep 3

# 8. db-intelligence (FIXED)
echo "  Starting db-intelligence (8051)..."
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/db-intelligence
DB_INTELLIGENCE_PORT=8051 python3 main.py > /tmp/ai-platform-logs/db_intelligence.log 2>&1 &
sleep 3

# 9. mio-manager (FIXED)
echo "  Starting mio-manager (8046)..."
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/mio-manager
python3 main.py > /tmp/ai-platform-logs/mio_manager.log 2>&1 &
sleep 4

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "=== 📊 SERVICE STATUS CHECK ==="
echo ""

# Check all services
curl -s http://localhost:9090/-/healthy > /dev/null && echo "✅ Prometheus (9090)" || echo "❌ Prometheus (9090)"
curl -s http://localhost:8050/health > /dev/null && echo "✅ monitoring-backend (8050)" || echo "❌ monitoring-backend (8050)"
curl -s http://localhost:8081/health > /dev/null && echo "✅ auth-service (8081)" || echo "❌ auth-service (8081)"
curl -s http://localhost:8082/ > /dev/null && echo "✅ realtime-websocket (8082)" || echo "❌ realtime-websocket (8082)"
curl -s http://localhost:8083/ > /dev/null && echo "✅ notification-service (8083)" || echo "❌ notification-service (8083)"
curl -s http://localhost:8055/health > /dev/null && echo "✅ ai-event-manager (8055)" || echo "❌ ai-event-manager (8055)"
curl -s http://localhost:8056/health > /dev/null && echo "✅ analytics-specialist (8056)" || echo "❌ analytics-specialist (8056)"
curl -s http://localhost:8051/health > /dev/null && echo "✅ db-intelligence (8051)" || echo "❌ db-intelligence (8051)"
curl -s http://localhost:8046/health > /dev/null && echo "✅ mio-manager (8046)" || echo "❌ mio-manager (8046)"

echo ""
echo "✅ All services started! Logs in /tmp/ai-platform-logs/"
echo ""
echo "🔍 Quick Links:"
echo "  - Prometheus: http://localhost:9090"
echo "  - Monitoring: http://localhost:8050/health"
echo "  - МиО Manager: http://localhost:8046/health"
echo "  - Analytics: http://localhost:8056/health"
echo ""
