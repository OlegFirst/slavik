#!/bin/bash
# Start all intelligent-core services using wrapper scripts with proper PYTHONPATH
# 2025-10-08 - Final launch with fixes

cd /Users/MD/AI-Platform-ISO/intelligent-core

echo "Starting all intelligent-core services..."
echo ""

# Kill any existing instances
echo "Killing existing processes..."
for port in {8030..8040}; do
  lsof -ti :$port 2>/dev/null | xargs kill -9 2>/dev/null
done
sleep 2

# Start all services using wrappers
echo "Starting services..."

nohup bash wrappers/run_ai_orchestration.sh > /tmp/s-8030.log 2>&1 &
echo "ai-orchestration (8030) started"

nohup bash wrappers/run_community_intelligence.sh > /tmp/s-8031.log 2>&1 &
echo "community-intelligence (8031) started"

nohup bash wrappers/run_predictive.sh > /tmp/s-8032.log 2>&1 &
echo "predictive (8032) started"

nohup bash wrappers/run_collective.sh > /tmp/s-8033.log 2>&1 &
echo "collective (8033) started"

nohup bash wrappers/run_coordination_center.sh > /tmp/s-8034.log 2>&1 &
echo "coordination-center (8034) started"

nohup bash wrappers/run_expertise_center.sh > /tmp/s-8035.log 2>&1 &
echo "expertise-center (8035) started"

nohup bash wrappers/run_workflow_engine.sh > /tmp/s-8036.log 2>&1 &
echo "workflow-engine (8036) started"

nohup bash wrappers/run_workflow_intelligence.sh > /tmp/s-8037.log 2>&1 &
echo "workflow-intelligence (8037) started"

nohup bash wrappers/run_ai_workflow_optimizer.sh > /tmp/s-8038.log 2>&1 &
echo "ai-workflow-optimizer (8038) started"

nohup bash wrappers/run_event_intelligence.sh > /tmp/s-8039.log 2>&1 &
echo "event-intelligence (8039) started"

nohup bash wrappers/run_ai_foundation.sh > /tmp/s-8040.log 2>&1 &
echo "ai-foundation (8040) started"

echo ""
echo "Waiting 20 seconds for services to start..."
sleep 20

echo ""
echo "Checking service status..."
echo ""

for port in {8030..8040}; do
  case $port in
    8030) name="ai-orchestration" ;;
    8031) name="community-intelligence" ;;
    8032) name="predictive" ;;
    8033) name="collective" ;;
    8034) name="coordination-center" ;;
    8035) name="expertise-center" ;;
    8036) name="workflow-engine" ;;
    8037) name="workflow-intelligence" ;;
    8038) name="ai-workflow-optimizer" ;;
    8039) name="event-intelligence" ;;
    8040) name="ai-foundation" ;;
  esac

  if lsof -i :$port | grep -q LISTEN; then
    echo "RUNNING: $name ($port)"
  else
    echo "FAILED: $name ($port) - check /tmp/s-$port.log"
  fi
done

echo ""
echo "Logs available at: /tmp/s-803*.log"
echo ""
