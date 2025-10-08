#!/bin/bash

# Start All Intelligent-Core Services
# Ports: 8030-8040

cd /Users/MD/AI-Platform-ISO/intelligent-core
export PYTHONPATH=/Users/MD/AI-Platform-ISO:/Users/MD/AI-Platform-ISO/intelligent-core

# Load environment variables
export $(grep -v '^#' /Users/MD/AI-Platform-ISO/.env | xargs)

echo "🚀 Starting all intelligent-core services (ports 8030-8040)..."
echo ""

# ai-orchestration (8030)
echo "▶️  Starting ai-orchestration (8030)..."
nohup python3 -m orchestration.ai-orchestration.main > /tmp/service-8030.log 2>&1 &
sleep 1

# community-intelligence (8031)
echo "▶️  Starting community-intelligence (8031)..."
nohup python3 -m community_intelligence.main > /tmp/service-8031.log 2>&1 &
sleep 1

# predictive (8032)
echo "▶️  Starting predictive (8032)..."
nohup python3 -m predictive.main > /tmp/service-8032.log 2>&1 &
sleep 1

# collective (8033)
echo "▶️  Starting collective (8033)..."
nohup python3 -m collective.main > /tmp/service-8033.log 2>&1 &
sleep 1

# coordination-center (8034)
echo "▶️  Starting coordination-center (8034)..."
nohup python3 -m orchestration.coordination-center.main > /tmp/service-8034.log 2>&1 &
sleep 1

# expertise-center (8035)
echo "▶️  Starting expertise-center (8035)..."
nohup python3 expertise-center/service/standalone_main.py > /tmp/service-8035.log 2>&1 &
sleep 1

# workflow-engine (8036)
echo "▶️  Starting workflow-engine (8036)..."
nohup python3 -m workflow-engine.workflow.api.main > /tmp/service-8036.log 2>&1 &
sleep 1

# workflow-intelligence (8037)
echo "▶️  Starting workflow-intelligence (8037)..."
nohup python3 -m workflow_intelligence.main > /tmp/service-8037.log 2>&1 &
sleep 1

# ai-workflow-optimizer (8038)
echo "▶️  Starting ai-workflow-optimizer (8038)..."
nohup python3 -m ai_workflow_optimizer.main > /tmp/service-8038.log 2>&1 &
sleep 1

# event-intelligence (8039)
echo "▶️  Starting event-intelligence (8039)..."
nohup python3 -m event_intelligence.main > /tmp/service-8039.log 2>&1 &
sleep 1

# ai-foundation (8040)
echo "▶️  Starting ai-foundation (8040)..."
nohup python3 -m ai-foundation.learning-knowledge.api.main > /tmp/service-8040.log 2>&1 &
sleep 1

echo ""
echo "⏳ Waiting 10 seconds for services to start..."
sleep 10

echo ""
echo "✅ All services started!"
echo ""
echo "📋 Check status:"
echo "   lsof -i :8030-8040 | grep LISTEN"
echo ""
echo "📄 Check logs:"
echo "   tail -f /tmp/service-8030.log"
echo "   tail -f /tmp/service-8031.log"
echo "   ... (8032-8040)"
echo ""
echo "🔍 Quick health check:"
echo "   for port in {8030..8040}; do curl -s http://localhost:\$port/health | jq -r '.status // \"DOWN\"' | xargs echo \"Port \$port:\"; done"
