#!/bin/bash

# FIXED Start Script with Correct PYTHONPATH
# Ports: 8030-8040

cd /Users/MD/AI-Platform-ISO/intelligent-core

# CRITICAL FIX: Include root directory in PYTHONPATH
export PYTHONPATH=/Users/MD/AI-Platform-ISO:/Users/MD/AI-Platform-ISO/intelligent-core

echo "🚀 Starting all intelligent-core services..."
echo "PYTHONPATH=$PYTHONPATH"
echo ""

# ai-orchestration (8030)
echo "▶️  [1/11] ai-orchestration (8030)..."
nohup python3 -m orchestration.ai-orchestration.main > /tmp/service-8030.log 2>&1 &
sleep 1

# community-intelligence (8031)
echo "▶️  [2/11] community-intelligence (8031)..."
nohup python3 -m community_intelligence.main > /tmp/service-8031.log 2>&1 &
sleep 1

# predictive (8032)
echo "▶️  [3/11] predictive (8032)..."
nohup python3 -m predictive.main > /tmp/service-8032.log 2>&1 &
sleep 1

# collective (8033)
echo "▶️  [4/11] collective (8033)..."
nohup python3 -m collective.main > /tmp/service-8033.log 2>&1 &
sleep 1

# coordination-center (8034)
echo "▶️  [5/11] coordination-center (8034)..."
nohup python3 -m orchestration.coordination-center.main > /tmp/service-8034.log 2>&1 &
sleep 1

# expertise-center (8035)
echo "▶️  [6/11] expertise-center (8035)..."
nohup python3 expertise-center/service/standalone_main.py > /tmp/service-8035.log 2>&1 &
sleep 1

# workflow-engine (8036)
echo "▶️  [7/11] workflow-engine (8036)..."
nohup python3 -m workflow-engine.workflow.api.main > /tmp/service-8036.log 2>&1 &
sleep 1

# workflow-intelligence (8037)
echo "▶️  [8/11] workflow-intelligence (8037)..."
nohup python3 -m workflow_intelligence.main > /tmp/service-8037.log 2>&1 &
sleep 1

# ai-workflow-optimizer (8038)
echo "▶️  [9/11] ai-workflow-optimizer (8038)..."
nohup python3 -m ai_workflow_optimizer.main > /tmp/service-8038.log 2>&1 &
sleep 1

# event-intelligence (8039)
echo "▶️  [10/11] event-intelligence (8039)..."
nohup python3 -m event_intelligence.main > /tmp/service-8039.log 2>&1 &
sleep 1

# ai-foundation (8040)
echo "▶️  [11/11] ai-foundation (8040)..."
nohup python3 -m ai-foundation.learning-knowledge.api.main > /tmp/service-8040.log 2>&1 &
sleep 1

echo ""
echo "⏳ Ждем 15 секунд..."
sleep 15

echo ""
echo "✅ Все сервисы запущены!"
echo ""
echo "📊 Проверка статуса:"
lsof -i :8030-8040 2>/dev/null | grep LISTEN | awk '{print "✓ Port", $9}' | sort

echo ""
echo "📄 Логи в /tmp/service-*.log"
echo ""
echo "🔍 Быстрая проверка health:"
for port in {8030..8040}; do
  status=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$port/health 2>/dev/null)
  if [ "$status" = "200" ]; then
    echo "✅ Port $port: OK"
  else
    echo "❌ Port $port: FAIL ($status)"
  fi
done
