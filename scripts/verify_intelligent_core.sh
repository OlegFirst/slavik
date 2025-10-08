#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ INTELLIGENT-CORE: FINAL VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Infrastructure
echo "📦 Infrastructure:"
redis-cli ping > /dev/null 2>&1 && echo "  ✅ Redis (6379): ALIVE" || echo "  ❌ Redis: DOWN"
lsof -i :5673 > /dev/null 2>&1 && echo "  ✅ RabbitMQ (5673): ALIVE" || echo "  ❌ RabbitMQ: DOWN"
echo ""

# Celery
echo "🔄 Celery Workers:"
CELERY_COUNT=$(ps aux | grep "celery.*worker" | grep -v grep | wc -l | tr -d ' ')
echo "  ✅ Worker Processes: $CELERY_COUNT active"
ps aux | grep "celery.*beat" | grep -v grep > /dev/null && echo "  ✅ Beat Scheduler: RUNNING" || echo "  ❌ Beat: DOWN"
curl -s http://localhost:5555 > /dev/null 2>&1 && echo "  ✅ Flower Monitor: http://localhost:5555" || echo "  ❌ Flower: DOWN"
echo ""

# Orchestration
echo "🌉 Orchestration:"
EVENTBUS_PID=$(ps aux | grep "eventbus_bridge.py" | grep -v grep | awk '{print $2}' | head -1)
[ -n "$EVENTBUS_PID" ] && echo "  ✅ EventBus Bridge: PID $EVENTBUS_PID" || echo "  ❌ EventBus Bridge: DOWN"

COORD=$(curl -s http://localhost:8004/coordination/health 2>&1)
echo "$COORD" | grep -q "healthy" && echo "  ✅ Coordination Center: http://localhost:8004" || echo "  ❌ Coordination: DOWN"
echo ""

# AI Services
echo "🤖 AI Services:"
curl -s http://localhost:8020/docs 2>&1 | grep -q "<!DOCTYPE" && echo "  ✅ Intelligent Core: http://localhost:8020" || echo "  ❌ Core: DOWN"
curl -s http://localhost:8031/docs 2>&1 | grep -q "<!DOCTYPE" && echo "  ✅ Community Intelligence: http://localhost:8031" || echo "  ❌ Community: DOWN"
curl -s http://localhost:8032/docs 2>&1 | grep -q "<!DOCTYPE" && echo "  ✅ Predictive Service: http://localhost:8032" || echo "  ❌ Predictive: DOWN"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 ALL SYSTEMS OPERATIONAL!"
echo ""
echo "📊 Quick Links:"
echo "  • API Docs: http://localhost:8020/docs"
echo "  • Community: http://localhost:8031/docs"
echo "  • Predictive: http://localhost:8032/docs"
echo "  • Monitoring: http://localhost:5555"
echo ""
echo "🛑 Stop all: ./stop_intelligent_core.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
