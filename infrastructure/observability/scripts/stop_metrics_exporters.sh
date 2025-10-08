#!/bin/bash
#
# 🛑 Stop All Metrics Exporters
# ==============================
#

echo "🛑 Stopping Metrics Exporters..."

# Stop by PIDs if file exists
if [ -f /tmp/metrics_exporters.pids ]; then
    source /tmp/metrics_exporters.pids

    echo "   Stopping AI-Foundation (PID: $AI_FOUNDATION_PID)..."
    kill $AI_FOUNDATION_PID 2>/dev/null || true

    echo "   Stopping Workflow Intelligence (PID: $WORKFLOW_PID)..."
    kill $WORKFLOW_PID 2>/dev/null || true

    echo "   Stopping Expertise Center (PID: $EXPERTISE_PID)..."
    kill $EXPERTISE_PID 2>/dev/null || true

    rm /tmp/metrics_exporters.pids
fi

# Fallback: kill by name
pkill -f "ai-foundation.*main.py" || true
pkill -f "workflow_intelligence.metrics_exporter" || true
pkill -f "expertise_center.metrics_exporter" || true

# Kill by port
lsof -ti:8030 | xargs kill -9 2>/dev/null || true
lsof -ti:9001 | xargs kill -9 2>/dev/null || true
lsof -ti:9002 | xargs kill -9 2>/dev/null || true

echo "✅ All exporters stopped"
