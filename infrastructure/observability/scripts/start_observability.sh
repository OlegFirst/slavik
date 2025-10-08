#!/bin/bash
###############################################################################
# Observability Stack Startup Script
# Launches all monitoring components in correct order
###############################################################################

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Observability Stack..."
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

###############################################################################
# 1. Check Prerequisites
###############################################################################

echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ Python 3 found${NC}"

# Check required Python packages
REQUIRED_PACKAGES=(
    "prometheus_client"
    "qdrant_client"
    "fastapi"
    "uvicorn"
    "sqlalchemy"
    "httpx"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        echo -e "${YELLOW}   ⚠️  Missing package: $package${NC}"
        echo "      Installing..."
        pip3 install -q "$package"
    fi
done
echo -e "${GREEN}   ✅ All Python packages available${NC}"

# Check .env file
if [ ! -f "$SCRIPT_DIR/../../.env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "   Create .env file with Qdrant, Redis, Supabase credentials"
    exit 1
fi
echo -e "${GREEN}   ✅ .env file found${NC}"

echo ""

###############################################################################
# 2. Kill Existing Processes (if any)
###############################################################################

echo "🔄 Checking for existing processes..."

# Kill processes on specific ports
for port in 9000 9122 8046; do
    PID=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$PID" ]; then
        echo -e "${YELLOW}   Killing process on port $port (PID: $PID)${NC}"
        kill -9 $PID 2>/dev/null || true
        sleep 1
    fi
done

echo ""

###############################################################################
# 3. Start Metrics Exporters
###############################################################################

echo "📊 Starting metrics exporters..."

# Create logs directory
mkdir -p logs

# Start Unified Exporter (Core Modules)
echo "   Starting Unified Exporter (port 9000)..."
cd exporters
nohup python3 unified_metrics_exporter.py > ../logs/unified_exporter.log 2>&1 &
UNIFIED_PID=$!
echo $UNIFIED_PID > ../logs/unified_exporter.pid
cd ..

sleep 2

# Verify Unified Exporter
if curl -sf http://localhost:9000/metrics > /dev/null; then
    echo -e "${GREEN}   ✅ Unified Exporter started (PID: $UNIFIED_PID)${NC}"
else
    echo -e "${RED}   ❌ Unified Exporter failed to start${NC}"
    cat logs/unified_exporter.log
    exit 1
fi

# Start Qdrant Exporter
echo "   Starting Qdrant Exporter (port 9122)..."
cd exporters
nohup python3 qdrant_exporter.py > ../logs/qdrant_exporter.log 2>&1 &
QDRANT_PID=$!
echo $QDRANT_PID > ../logs/qdrant_exporter.pid
cd ..

sleep 2

# Verify Qdrant Exporter
if curl -sf http://localhost:9122/metrics > /dev/null; then
    echo -e "${GREEN}   ✅ Qdrant Exporter started (PID: $QDRANT_PID)${NC}"
else
    echo -e "${YELLOW}   ⚠️  Qdrant Exporter failed (check Qdrant credentials)${NC}"
    # Don't exit - this is non-critical
fi

echo ""

###############################################################################
# 4. Start Prometheus (if Docker available)
###############################################################################

echo "📈 Starting Prometheus..."

if command -v docker &> /dev/null; then
    # Check if prometheus container exists
    if docker ps -a --format '{{.Names}}' | grep -q '^prometheus$'; then
        echo "   Stopping existing Prometheus container..."
        docker stop prometheus > /dev/null 2>&1 || true
        docker rm prometheus > /dev/null 2>&1 || true
    fi

    echo "   Starting Prometheus container..."
    docker run -d \
        --name prometheus \
        -p 9090:9090 \
        -v "$SCRIPT_DIR/config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml" \
        --add-host=host.docker.internal:host-gateway \
        prom/prometheus:latest \
        --config.file=/etc/prometheus/prometheus.yml \
        > /dev/null 2>&1

    sleep 3

    if curl -sf http://localhost:9090/-/healthy > /dev/null; then
        echo -e "${GREEN}   ✅ Prometheus started (port 9090)${NC}"
    else
        echo -e "${RED}   ❌ Prometheus failed to start${NC}"
        docker logs prometheus
        exit 1
    fi
else
    echo -e "${YELLOW}   ⚠️  Docker not available, skipping Prometheus${NC}"
    echo "      Install Docker or run manually: prometheus --config.file=config/prometheus/prometheus.yml"
fi

echo ""

###############################################################################
# 5. Start Grafana (if Docker available)
###############################################################################

echo "📊 Starting Grafana..."

if command -v docker &> /dev/null; then
    # Check if grafana container exists
    if docker ps -a --format '{{.Names}}' | grep -q '^grafana$'; then
        echo "   Stopping existing Grafana container..."
        docker stop grafana > /dev/null 2>&1 || true
        docker rm grafana > /dev/null 2>&1 || true
    fi

    echo "   Starting Grafana container..."
    docker run -d \
        --name grafana \
        -p 3000:3000 \
        -v "$SCRIPT_DIR/config/grafana/dashboards:/etc/grafana/provisioning/dashboards" \
        -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
        --add-host=host.docker.internal:host-gateway \
        grafana/grafana:latest \
        > /dev/null 2>&1

    sleep 5

    if curl -sf http://localhost:3000/api/health > /dev/null; then
        echo -e "${GREEN}   ✅ Grafana started (port 3000)${NC}"
        echo -e "      Login: ${YELLOW}admin / admin${NC}"
    else
        echo -e "${RED}   ❌ Grafana failed to start${NC}"
        docker logs grafana
        exit 1
    fi
else
    echo -e "${YELLOW}   ⚠️  Docker not available, skipping Grafana${NC}"
    echo "      Install Docker or run manually: grafana-server"
fi

echo ""

###############################################################################
# 6. Start MIO Manager
###############################################################################

echo "🤖 Starting MIO Manager..."

cd mio-manager

# Install dependencies if needed
if [ -f "requirements.txt" ]; then
    pip3 install -q -r requirements.txt
fi

# Start MIO Manager
nohup python3 main.py > ../logs/mio_manager.log 2>&1 &
MIO_PID=$!
echo $MIO_PID > ../logs/mio_manager.pid

sleep 5

cd ..

# Verify MIO Manager
if curl -sf http://localhost:8046/health > /dev/null; then
    echo -e "${GREEN}   ✅ MIO Manager started (PID: $MIO_PID)${NC}"
else
    echo -e "${RED}   ❌ MIO Manager failed to start${NC}"
    cat logs/mio_manager.log
    exit 1
fi

echo ""

###############################################################################
# 7. Verify All Services
###############################################################################

echo "🔍 Verifying all services..."
echo ""

# Check Unified Exporter
if curl -sf http://localhost:9000/metrics > /dev/null; then
    echo -e "${GREEN}✅ Unified Exporter${NC}       http://localhost:9000/metrics"
else
    echo -e "${RED}❌ Unified Exporter${NC}       http://localhost:9000/metrics"
fi

# Check Qdrant Exporter
if curl -sf http://localhost:9122/metrics > /dev/null; then
    echo -e "${GREEN}✅ Qdrant Exporter${NC}        http://localhost:9122/metrics"
else
    echo -e "${YELLOW}⚠️  Qdrant Exporter${NC}        http://localhost:9122/metrics (optional)"
fi

# Check Prometheus
if curl -sf http://localhost:9090/-/healthy > /dev/null; then
    echo -e "${GREEN}✅ Prometheus${NC}             http://localhost:9090"
else
    echo -e "${YELLOW}⚠️  Prometheus${NC}             http://localhost:9090 (not running)"
fi

# Check Grafana
if curl -sf http://localhost:3000/api/health > /dev/null; then
    echo -e "${GREEN}✅ Grafana${NC}                http://localhost:3000"
else
    echo -e "${YELLOW}⚠️  Grafana${NC}                http://localhost:3000 (not running)"
fi

# Check MIO Manager
if curl -sf http://localhost:8046/health > /dev/null; then
    echo -e "${GREEN}✅ MIO Manager${NC}            http://localhost:8046"
else
    echo -e "${RED}❌ MIO Manager${NC}            http://localhost:8046"
fi

echo ""

###############################################################################
# 8. Run Initial Service Discovery
###############################################################################

echo "🔍 Running initial service discovery..."

DISCOVERY_RESULT=$(curl -sf -X POST http://localhost:8046/api/discover 2>/dev/null || echo '{}')

if [ ! -z "$DISCOVERY_RESULT" ] && [ "$DISCOVERY_RESULT" != "{}" ]; then
    TOTAL=$(echo "$DISCOVERY_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('total_services', 0))" 2>/dev/null || echo "0")
    MONITORED=$(echo "$DISCOVERY_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('monitored_services', 0))" 2>/dev/null || echo "0")
    COVERAGE=$(echo "$DISCOVERY_RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('coverage', {}).get('percentage', 0))" 2>/dev/null || echo "0")

    echo -e "${GREEN}   ✅ Service discovery complete${NC}"
    echo "      Total services: $TOTAL"
    echo "      Monitored: $MONITORED"
    echo "      Coverage: ${COVERAGE}%"
else
    echo -e "${YELLOW}   ⚠️  Service discovery failed (will retry automatically)${NC}"
fi

echo ""

###############################################################################
# 9. Summary
###############################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Observability Stack Ready!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Metrics & Monitoring:"
echo "   • Unified Exporter:     http://localhost:9000/metrics"
echo "   • Qdrant Exporter:      http://localhost:9122/metrics"
echo "   • Prometheus:           http://localhost:9090"
echo "   • Grafana:              http://localhost:3000 (admin/admin)"
echo ""
echo "🤖 AI Management:"
echo "   • MIO Manager API:      http://localhost:8046"
echo "   • MIO Manager Docs:     http://localhost:8046/docs"
echo "   • MIO Manager Status:   http://localhost:8046/api/status"
echo ""
echo "📁 Logs:"
echo "   • Unified Exporter:     $SCRIPT_DIR/logs/unified_exporter.log"
echo "   • Qdrant Exporter:      $SCRIPT_DIR/logs/qdrant_exporter.log"
echo "   • MIO Manager:          $SCRIPT_DIR/logs/mio_manager.log"
echo ""
echo "🛑 To stop all services:"
echo "   $SCRIPT_DIR/stop_observability.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
