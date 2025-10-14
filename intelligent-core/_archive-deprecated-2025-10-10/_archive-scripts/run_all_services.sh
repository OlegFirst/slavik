#!/bin/bash
cd /Users/MD/AI-Platform-ISO/intelligent-core
PP="/Users/MD/AI-Platform-ISO:/Users/MD/AI-Platform-ISO/intelligent-core"

echo "🚀 Запуск всех 11 сервисов intelligent-core..."

PYTHONPATH=$PP nohup python3 -m orchestration.ai-orchestration.main > /tmp/s-8030.log 2>&1 &
PYTHONPATH=$PP nohup python3 -m community_intelligence.main > /tmp/s-8031.log 2>&1 &
PYTHONPATH=$PP nohup python3 -m predictive.main > /tmp/s-8032.log 2>&1 &
PYTHONPATH=$PP nohup python3 -m collective.main > /tmp/s-8033.log 2>&1 &
PYTHONPATH=$PP nohup python3 -m orchestration.coordination-center.main > /tmp/s-8034.log 2>&1 &
PYTHONPATH=$PP nohup python3 expertise-center/service/standalone_main.py > /tmp/s-8035.log 2>&1 &
PYTHONPATH=$PP nohup python3 -m workflow-engine.workflow.api.main > /tmp/s-8036.log 2>&1 &
PYTHONPATH=$PP nohup python3 -m workflow_intelligence.main > /tmp/s-8037.log 2>&1 &
PYTHONPATH=$PP nohup python3 -m ai_workflow_optimizer.main > /tmp/s-8038.log 2>&1 &
PYTHONPATH=$PP nohup python3 -m event_intelligence.main > /tmp/s-8039.log 2>&1 &
PYTHONPATH=$PP nohup python3 -m ai-foundation.learning-knowledge.api.main > /tmp/s-8040.log 2>&1 &

echo "⏳ Ждем 20 секунд..."
sleep 20

echo ""
lsof -i :8030-8040 2>/dev/null | grep LISTEN | awk '{print "✓", $9}' | sort || echo "Нет запущенных сервисов"
echo ""
for p in {8030..8040}; do
  s=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$p/health 2>/dev/null)
  [ "$s" = "200" ] && echo "✅ $p: OK" || echo "❌ $p: FAIL"
done
