#!/bin/bash
# BCM Platform - Full Infrastructure Startup Script
# ==================================================
#
# Запускает ВСЮ инфраструктуру платформы
#
# Usage:
#   ./start-all-infrastructure.sh          # Start all
#   ./start-all-infrastructure.sh gateway  # Start only gateway layer
#   ./start-all-infrastructure.sh --stop   # Stop all

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Banner
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  BCM Platform - Infrastructure Startup                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found!${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found!${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check .env file
if [ ! -f "../.env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found in project root${NC}"
    echo "Creating .env.example..."
    cat > ../.env.example << 'EOF'
# BCM Platform - Environment Variables
# =====================================

# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_ANON_KEY=your-anon-key
DATABASE_URL=postgresql://user:password@host:5432/database

# Redis (Required)
REDIS_URL=redis://localhost:6379
UPSTASH_REDIS_URL=redis://default:password@host:port

# Qdrant (Optional)
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-api-key

# AI Services (Optional)
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key

# SMTP (Optional for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
SMTP_FROM=noreply@bcm-platform.com

# GitHub Integration (Optional)
GITHUB_TOKEN=your-github-token
GITHUB_WEBHOOK_SECRET=your-webhook-secret
EOF
    echo -e "${GREEN}✅ Created .env.example${NC}"
    echo "Please copy it to .env and fill in your credentials:"
    echo "  cp ../.env.example ../.env"
    echo "  nano ../.env"
    exit 1
fi

# Function to start layer
start_layer() {
    local layer=$1
    echo -e "${BLUE}🚀 Starting $layer layer...${NC}"

    case $layer in
        gateway)
            docker-compose -f docker-compose.full-infrastructure.yml up -d \
                api-gateway
            ;;
        runtime)
            docker-compose -f docker-compose.full-infrastructure.yml up -d \
                realtime-websocket
            ;;
        observability)
            docker-compose -f docker-compose.full-infrastructure.yml up -d \
                prometheus grafana loki promtail alertmanager notification-service
            ;;
        ai-office)
            docker-compose -f docker-compose.full-infrastructure.yml up -d \
                analytics-specialist db-intelligence ai-event-manager mio-manager
            ;;
        integration)
            docker-compose -f docker-compose.full-infrastructure.yml up -d \
                github-integration
            ;;
        all)
            docker-compose -f docker-compose.full-infrastructure.yml up -d
            ;;
        *)
            echo -e "${RED}❌ Unknown layer: $layer${NC}"
            echo "Available layers: gateway, runtime, observability, ai-office, integration, all"
            exit 1
            ;;
    esac
}

# Function to stop all
stop_all() {
    echo -e "${YELLOW}🛑 Stopping all infrastructure...${NC}"
    docker-compose -f docker-compose.full-infrastructure.yml down
    echo -e "${GREEN}✅ All infrastructure stopped${NC}"
}

# Function to check status
check_status() {
    echo -e "${BLUE}📊 Infrastructure Status:${NC}"
    echo ""

    docker-compose -f docker-compose.full-infrastructure.yml ps

    echo ""
    echo -e "${BLUE}🔍 Health Checks:${NC}"
    echo ""

    # Check each service
    declare -A services=(
        ["API Gateway"]="8000"
        ["Realtime WebSocket"]="8100"
        ["Prometheus"]="9090"
        ["Grafana"]="3000"
        ["Loki"]="3100"
        ["AlertManager"]="9093"
        ["Notification Service"]="8035"
        ["Analytics Specialist"]="8051"
        ["DB Intelligence"]="8052"
        ["AI Event Manager"]="8053"
        ["MIO Manager"]="8046"
        ["GitHub Integration"]="8200"
    )

    for service in "${!services[@]}"; do
        port=${services[$service]}
        if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✅ $service${NC} (http://localhost:$port)"
        else
            echo -e "  ${RED}❌ $service${NC} (port $port not responding)"
        fi
    done

    echo ""
    echo -e "${BLUE}🌐 Access URLs:${NC}"
    echo ""
    echo -e "  Grafana:         ${GREEN}http://localhost:3000${NC} (admin/admin)"
    echo -e "  Prometheus:      ${GREEN}http://localhost:9090${NC}"
    echo -e "  AlertManager:    ${GREEN}http://localhost:9093${NC}"
    echo -e "  API Gateway:     ${GREEN}http://localhost:8000${NC}"
    echo ""
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}📋 Showing logs (Ctrl+C to exit)...${NC}"
    docker-compose -f docker-compose.full-infrastructure.yml logs -f --tail=50
}

# Main script
LAYER="${1:-all}"

case $LAYER in
    --stop)
        stop_all
        ;;
    --status)
        check_status
        ;;
    --logs)
        show_logs
        ;;
    --restart)
        echo -e "${YELLOW}♻️  Restarting infrastructure...${NC}"
        stop_all
        sleep 2
        start_layer all
        sleep 5
        check_status
        ;;
    *)
        # Start infrastructure
        echo -e "${GREEN}Starting layer: $LAYER${NC}"
        echo ""

        start_layer $LAYER

        echo ""
        echo -e "${GREEN}✅ Infrastructure started!${NC}"
        echo ""

        # Wait for services to start
        echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
        sleep 10

        # Check status
        check_status

        echo ""
        echo -e "${BLUE}💡 Useful commands:${NC}"
        echo "  ./start-all-infrastructure.sh --status    # Check status"
        echo "  ./start-all-infrastructure.sh --logs      # View logs"
        echo "  ./start-all-infrastructure.sh --restart   # Restart all"
        echo "  ./start-all-infrastructure.sh --stop      # Stop all"
        echo ""
        ;;
esac
