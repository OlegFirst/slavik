#!/bin/bash

# Start Orchestration Services
# This script starts ai-orchestration and coordination-center

set -e

export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH
PROJECT_ROOT=/Users/MD/AI-Platform-ISO
LOG_DIR=/tmp/orchestration-logs

# Create log directory
mkdir -p $LOG_DIR

echo "🚀 Starting Orchestration Services..."
echo ""

# Check infrastructure
echo "📊 Checking infrastructure..."
redis-cli ping > /dev/null 2>&1 && echo "✅ Redis: Running" || echo "❌ Redis: Not running"
docker ps | grep rabbitmq > /dev/null 2>&1 && echo "✅ RabbitMQ: Running" || echo "❌ RabbitMQ: Not running"
echo ""

# Start ai-orchestration
echo "🧠 Starting ai-orchestration (Port 8002)..."
cd $PROJECT_ROOT/intelligent-core/orchestration/ai-orchestration
nohup python3 main.py > $LOG_DIR/ai-orchestration.log 2>&1 &
AI_ORCH_PID=$!
echo $AI_ORCH_PID > $LOG_DIR/ai-orchestration.pid
echo "   PID: $AI_ORCH_PID"
echo "   Log: $LOG_DIR/ai-orchestration.log"
sleep 3

# Check if started
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "   ✅ Service started successfully"
else
    echo "   ⚠️  Service starting... (check logs)"
fi
echo ""

# Start coordination-center
echo "🎯 Starting coordination-center (Port 8004)..."
cd $PROJECT_ROOT/intelligent-core/orchestration/coordination-center
nohup python3 main.py > $LOG_DIR/coordination-center.log 2>&1 &
COORD_PID=$!
echo $COORD_PID > $LOG_DIR/coordination-center.pid
echo "   PID: $COORD_PID"
echo "   Log: $LOG_DIR/coordination-center.log"
sleep 3

# Check if started
if curl -s http://localhost:8004/coordination/health > /dev/null 2>&1; then
    echo "   ✅ Service started successfully"
else
    echo "   ⚠️  Service starting... (check logs)"
fi
echo ""

echo "✅ Orchestration services started!"
echo ""
echo "📊 Status:"
echo "   ai-orchestration:    http://localhost:8002/health"
echo "   coordination-center: http://localhost:8004/coordination/health"
echo ""
echo "📝 Logs:"
echo "   tail -f $LOG_DIR/ai-orchestration.log"
echo "   tail -f $LOG_DIR/coordination-center.log"
echo ""
echo "🛑 To stop:"
echo "   kill \$(cat $LOG_DIR/ai-orchestration.pid)"
echo "   kill \$(cat $LOG_DIR/coordination-center.pid)"
