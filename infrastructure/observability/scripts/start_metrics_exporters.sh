#!/bin/bash
#
# 🚀 Start All Metrics Exporters
# ===============================
#
# Запускает standalone metrics exporters для всех core модулей
#

set -e

PROJECT_ROOT="/Users/MD/AI-Platform-ISO"
cd "$PROJECT_ROOT"

echo "🚀 Starting Metrics Exporters for Core Modules"
echo "=============================================="
echo ""

# Kill existing exporters if running
echo "🧹 Cleaning up existing exporters..."
pkill -f "metrics_exporter" || true
sleep 1

# Start AI-Foundation API (port 8030)
echo "1️⃣  Starting AI-Foundation API (port 8030)..."
cd "$PROJECT_ROOT/intelligent-core/ai-foundation/learning-knowledge/api"
python3 main.py > /tmp/ai-foundation-api.log 2>&1 &
AI_FOUNDATION_PID=$!
echo "   ✓ Started (PID: $AI_FOUNDATION_PID)"

# Start Workflow Intelligence Metrics Exporter (port 9001)
echo "2️⃣  Starting Workflow Intelligence Exporter (port 9001)..."
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
python3 -m intelligent_core.workflow_intelligence.metrics_exporter --port 9001 > /tmp/workflow-intelligence-metrics.log 2>&1 &
WORKFLOW_PID=$!
echo "   ✓ Started (PID: $WORKFLOW_PID)"

# Start Expertise Center Metrics Exporter (port 9002)
echo "3️⃣  Starting Expertise Center Exporter (port 9002)..."
python3 -m intelligent_core.expertise_center.metrics_exporter --port 9002 > /tmp/expertise-center-metrics.log 2>&1 &
EXPERTISE_PID=$!
echo "   ✓ Started (PID: $EXPERTISE_PID)"

# Wait a bit for services to start
echo ""
echo "⏳ Waiting for services to start..."
sleep 3

# Test endpoints
echo ""
echo "🧪 Testing Metrics Endpoints"
echo "=============================="

test_endpoint() {
    local name=$1
    local url=$2

    if curl -s "$url" > /dev/null; then
        echo "✅ $name: $url"
    else
        echo "❌ $name: $url (FAILED)"
    fi
}

test_endpoint "AI-Foundation      " "http://localhost:8030/metrics"
test_endpoint "Workflow Intelligence" "http://localhost:9001/metrics"
test_endpoint "Expertise Center   " "http://localhost:9002/metrics"

echo ""
echo "✅ All Metrics Exporters Started!"
echo ""
echo "📊 Metrics Endpoints:"
echo "   AI-Foundation:         http://localhost:8030/metrics"
echo "   Workflow Intelligence: http://localhost:9001/metrics"
echo "   Expertise Center:      http://localhost:9002/metrics"
echo ""
echo "📝 Logs:"
echo "   AI-Foundation:         tail -f /tmp/ai-foundation-api.log"
echo "   Workflow Intelligence: tail -f /tmp/workflow-intelligence-metrics.log"
echo "   Expertise Center:      tail -f /tmp/expertise-center-metrics.log"
echo ""
echo "🛑 To stop all exporters:"
echo "   kill $AI_FOUNDATION_PID $WORKFLOW_PID $EXPERTISE_PID"
echo ""

# Save PIDs
cat > /tmp/metrics_exporters.pids <<EOF
AI_FOUNDATION_PID=$AI_FOUNDATION_PID
WORKFLOW_PID=$WORKFLOW_PID
EXPERTISE_PID=$EXPERTISE_PID
EOF

echo "💾 PIDs saved to /tmp/metrics_exporters.pids"
