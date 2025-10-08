#!/bin/bash

# 🚀 INTELLIGENT-CORE MASTER STARTUP SCRIPT
# ==========================================
# Starts all orchestration components in correct order

set -e

export PYTHONPATH=/Users/MD/AI-Platform-ISO:$PYTHONPATH
export PATH="/Users/MD/Library/Python/3.9/bin:$PATH"
PROJECT_ROOT=/Users/MD/AI-Platform-ISO
LOG_DIR=/tmp/intelligent-core-logs

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p $LOG_DIR

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧠 INTELLIGENT-CORE ORCHESTRATION STARTUP${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================================
# PHASE 1: Check Infrastructure
# ============================================================================

echo -e "${YELLOW}📊 PHASE 1: Infrastructure Health Check${NC}"
echo ""

# Redis
if redis-cli ping > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Redis:${NC} Running on port 6379"
else
    echo -e "  ${RED}❌ Redis:${NC} Not running"
    echo "     Start with: brew services start redis"
    exit 1
fi

# RabbitMQ
if docker ps | grep -q rabbitmq; then
    RABBITMQ_PORT=$(docker ps | grep rabbitmq | grep -oE '0\.0\.0\.0:([0-9]+)->5672' | cut -d':' -f2 | cut -d'-' -f1)
    RABBITMQ_MGMT_PORT=$(docker ps | grep rabbitmq | grep -oE '0\.0\.0\.0:([0-9]+)->15672' | cut -d':' -f2 | cut -d'-' -f1)
    export RABBITMQ_URL="amqp://bcm_platform:bcm_secure_2024@localhost:${RABBITMQ_PORT}/"
    echo -e "  ${GREEN}✅ RabbitMQ:${NC} Running on ports ${RABBITMQ_PORT}, ${RABBITMQ_MGMT_PORT}"
else
    echo -e "  ${RED}❌ RabbitMQ:${NC} Not running"
    echo "     Start with: docker start intelligent-core-rabbitmq"
    exit 1
fi

# PostgreSQL
if PGPASSWORD='K@x3ta9V8GK5rnW' psql -h aws-1-eu-north-1.pooler.supabase.com -U postgres.tpdkhddtbhpoqzzgxfni -d postgres -p 5432 -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ PostgreSQL:${NC} Connected to Supabase"
else
    echo -e "  ${YELLOW}⚠️  PostgreSQL:${NC} Connection issue (will continue)"
fi

echo ""

# ============================================================================
# PHASE 2: Start Background Workers (Celery)
# ============================================================================

echo -e "${YELLOW}🔄 PHASE 2: Starting Background Workers (Celery)${NC}"
echo ""

cd $PROJECT_ROOT/intelligent-core/orchestration/task_queue

# Start Celery workers (3 queues)
echo -e "  ${BLUE}Starting Celery worker: learning queue...${NC}"
celery -A worker worker --loglevel=INFO --queues=learning \
    --concurrency=2 --logfile=$LOG_DIR/celery-learning.log \
    --pidfile=$LOG_DIR/celery-learning.pid --detach

echo -e "  ${BLUE}Starting Celery worker: batch queue...${NC}"
celery -A worker worker --loglevel=INFO --queues=batch \
    --concurrency=4 --logfile=$LOG_DIR/celery-batch.log \
    --pidfile=$LOG_DIR/celery-batch.pid --detach

echo -e "  ${BLUE}Starting Celery worker: prediction queue...${NC}"
celery -A worker worker --loglevel=INFO --queues=prediction \
    --concurrency=2 --logfile=$LOG_DIR/celery-prediction.log \
    --pidfile=$LOG_DIR/celery-prediction.pid --detach

# Start Celery Beat (scheduler)
echo -e "  ${BLUE}Starting Celery Beat (scheduler)...${NC}"
celery -A beat beat --loglevel=INFO \
    --logfile=$LOG_DIR/celery-beat.log \
    --pidfile=$LOG_DIR/celery-beat.pid --detach

sleep 2
echo -e "  ${GREEN}✅ Celery workers started${NC}"

# Start Flower (monitoring)
echo -e "  ${BLUE}Starting Flower (Celery monitoring)...${NC}"
celery -A worker flower --port=5555 \
    --logfile=$LOG_DIR/flower.log \
    --pid=$LOG_DIR/flower.pid &

echo -e "  ${GREEN}✅ Flower started: http://localhost:5555${NC}"
echo ""

# ============================================================================
# PHASE 3: Start EventBus ← → Celery Bridge
# ============================================================================

echo -e "${YELLOW}🌉 PHASE 3: Starting EventBus Bridge${NC}"
echo ""

python3 eventbus_bridge.py > $LOG_DIR/eventbus-bridge.log 2>&1 &
BRIDGE_PID=$!
echo $BRIDGE_PID > $LOG_DIR/eventbus-bridge.pid

echo -e "  ${GREEN}✅ EventBus Bridge started (PID: $BRIDGE_PID)${NC}"
echo ""

# ============================================================================
# PHASE 4: Start Coordination Center
# ============================================================================

echo -e "${YELLOW}🎯 PHASE 4: Starting Coordination Center${NC}"
echo ""

cd $PROJECT_ROOT/intelligent-core/orchestration/coordination-center
python3 main.py > $LOG_DIR/coordination-center.log 2>&1 &
COORD_PID=$!
echo $COORD_PID > $LOG_DIR/coordination-center.pid

sleep 3

if curl -s http://localhost:8004/coordination/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Coordination Center running (Port 8004)${NC}"
else
    echo -e "  ${YELLOW}⚠️  Coordination Center starting... (check logs)${NC}"
fi

echo ""

# ============================================================================
# PHASE 5: Start Core Intelligent Services
# ============================================================================

echo -e "${YELLOW}🤖 PHASE 5: Starting Core AI Services${NC}"
echo ""

# Main Intelligent Core (includes Workflow Intelligence)
echo -e "  ${BLUE}Starting Intelligent Core API (Port 8020)...${NC}"
cd $PROJECT_ROOT/intelligent-core
uvicorn main:app --host 0.0.0.0 --port 8020 > $LOG_DIR/intelligent-core.log 2>&1 &
CORE_PID=$!
echo $CORE_PID > $LOG_DIR/intelligent-core.pid
echo -e "  ${GREEN}✅ Intelligent Core started${NC}"

# Community Intelligence (run as module to support relative imports)
echo -e "  ${BLUE}Starting Community Intelligence (Port 8031)...${NC}"
cd $PROJECT_ROOT/intelligent-core
python3 -m community_intelligence.main > $LOG_DIR/community-intelligence.log 2>&1 &
COMM_PID=$!
echo $COMM_PID > $LOG_DIR/community-intelligence.pid
echo -e "  ${GREEN}✅ Community Intelligence started${NC}"

# Predictive Service
echo -e "  ${BLUE}Starting Predictive Service (Port 8032)...${NC}"
cd $PROJECT_ROOT/intelligent-core
python3 -m predictive.main > $LOG_DIR/predictive.log 2>&1 &
PRED_PID=$!
echo $PRED_PID > $LOG_DIR/predictive.pid
echo -e "  ${GREEN}✅ Predictive Service started${NC}"

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ INTELLIGENT-CORE STARTED SUCCESSFULLY!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}📊 Running Services:${NC}"
echo ""
echo -e "  ${BLUE}Background Workers:${NC}"
echo -e "    • Celery Learning Queue:    Active"
echo -e "    • Celery Batch Queue:       Active"
echo -e "    • Celery Prediction Queue:  Active"
echo -e "    • Celery Beat (Scheduler):  Active"
echo -e "    • Flower (Monitoring):      http://localhost:5555"
echo ""
echo -e "  ${BLUE}Orchestration:${NC}"
echo -e "    • EventBus Bridge:          PID $BRIDGE_PID"
echo -e "    • Coordination Center:      http://localhost:8004"
echo ""
echo -e "  ${BLUE}AI Services:${NC}"
echo -e "    • Workflow Intelligence:    http://localhost:8020"
echo -e "    • Community Intelligence:   http://localhost:8031"
echo -e "    • Predictive Service:       http://localhost:8032"
echo ""

echo -e "${YELLOW}📝 Logs:${NC}"
echo "    $LOG_DIR/"
echo ""

echo -e "${YELLOW}🛑 To stop all services:${NC}"
echo "    $PROJECT_ROOT/stop_intelligent_core.sh"
echo ""

echo -e "${YELLOW}📊 Monitoring:${NC}"
echo "    • Flower:  http://localhost:5555"
echo "    • RabbitMQ: http://localhost:${RABBITMQ_MGMT_PORT} (guest/guest)"
echo ""

# Save PIDs for stop script
cat > $LOG_DIR/all_pids.txt << EOF
CELERY_LEARNING=$(cat $LOG_DIR/celery-learning.pid)
CELERY_BATCH=$(cat $LOG_DIR/celery-batch.pid)
CELERY_PREDICTION=$(cat $LOG_DIR/celery-prediction.pid)
CELERY_BEAT=$(cat $LOG_DIR/celery-beat.pid)
BRIDGE=$BRIDGE_PID
COORDINATION=$COORD_PID
WORKFLOW=$WF_PID
COMMUNITY=$COMM_PID
PREDICTIVE=$PRED_PID
EOF

echo -e "${GREEN}🎉 All systems operational!${NC}"
echo ""
