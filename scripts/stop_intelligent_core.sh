#!/bin/bash

# 🛑 STOP ALL INTELLIGENT-CORE SERVICES

LOG_DIR=/tmp/intelligent-core-logs

echo "🛑 Stopping intelligent-core services..."

if [ -f "$LOG_DIR/all_pids.txt" ]; then
    source $LOG_DIR/all_pids.txt

    # Stop all processes
    [ ! -z "$CELERY_LEARNING" ] && kill $CELERY_LEARNING 2>/dev/null && echo "  ✅ Stopped Celery Learning"
    [ ! -z "$CELERY_BATCH" ] && kill $CELERY_BATCH 2>/dev/null && echo "  ✅ Stopped Celery Batch"
    [ ! -z "$CELERY_PREDICTION" ] && kill $CELERY_PREDICTION 2>/dev/null && echo "  ✅ Stopped Celery Prediction"
    [ ! -z "$CELERY_BEAT" ] && kill $CELERY_BEAT 2>/dev/null && echo "  ✅ Stopped Celery Beat"
    [ ! -z "$BRIDGE" ] && kill $BRIDGE 2>/dev/null && echo "  ✅ Stopped EventBus Bridge"
    [ ! -z "$COORDINATION" ] && kill $COORDINATION 2>/dev/null && echo "  ✅ Stopped Coordination Center"
    [ ! -z "$WORKFLOW" ] && kill $WORKFLOW 2>/dev/null && echo "  ✅ Stopped Workflow Intelligence"
    [ ! -z "$COMMUNITY" ] && kill $COMMUNITY 2>/dev/null && echo "  ✅ Stopped Community Intelligence"
    [ ! -z "$PREDICTIVE" ] && kill $PREDICTIVE 2>/dev/null && echo "  ✅ Stopped Predictive Service"

    # Stop Flower
    pkill -f "celery.*flower" && echo "  ✅ Stopped Flower"

    rm $LOG_DIR/all_pids.txt
fi

# Fallback: kill all Python processes
# pkill -f "python3 main.py"

echo ""
echo "✅ All services stopped!"
