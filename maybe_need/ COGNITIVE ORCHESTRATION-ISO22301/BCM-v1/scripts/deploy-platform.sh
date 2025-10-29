#!/bin/bash

# BCM Platform Deployment Script
# Usage: ./deploy-platform.sh [development|production]

set -e

MODE=${1:-development}
COMPOSE_FILE=""
ENV_FILE=""

echo "🚀 BCM Platform Deployment Script"
echo "================================="

# Determine configuration files
if [ "$MODE" = "production" ]; then
    COMPOSE_FILE="docker-compose.production.yml"
    ENV_FILE=".env.production"
    echo "📦 Deploying in PRODUCTION mode"
else
    COMPOSE_FILE="docker-compose.yml"
    ENV_FILE=".env"
    echo "🔧 Deploying in DEVELOPMENT mode"
fi

# Check if files exist
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Error: $COMPOSE_FILE not found"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE not found"
    echo "💡 Copy .env.example to $ENV_FILE and configure it"
    exit 1
fi

# Export environment variables
export $(cat $ENV_FILE | grep -v ^# | xargs)

echo "📋 Configuration Summary:"
echo "  - Compose file: $COMPOSE_FILE"
echo "  - Environment: $ENV_FILE"
echo "  - Database: PostgreSQL"
echo "  - Cache: Redis"
echo "  - Message Queue: RabbitMQ"
echo ""

# Stop existing services
echo "⏹️  Stopping existing services..."
docker-compose -f $COMPOSE_FILE down --remove-orphans

# Pull latest images (production only)
if [ "$MODE" = "production" ]; then
    echo "📥 Pulling latest images..."
    docker-compose -f $COMPOSE_FILE pull
fi

# Build custom images
echo "🔨 Building custom images..."
docker-compose -f $COMPOSE_FILE build --no-cache

# Start infrastructure services first
echo "🏗️  Starting infrastructure services..."
docker-compose -f $COMPOSE_FILE up -d postgres redis rabbitmq

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 15

# Start core services
echo "💻 Starting core services..."
docker-compose -f $COMPOSE_FILE up -d odoo unified_database_gateway

# Start gateway services
echo "🌉 Starting gateway services..."
docker-compose -f $COMPOSE_FILE up -d unified_api_gateway crm_bridge

# Wait for core services
echo "⏳ Waiting for core services to be ready..."
sleep 20

# Start AI services
echo "🤖 Starting AI services..."
docker-compose -f $COMPOSE_FILE up -d ai_orchestrator ai_control_center

# Start business services
echo "📊 Starting business services..."
docker-compose -f $COMPOSE_FILE up -d bcm_platform_api websocket_server bia_engine document_processor compliance_checker

# Start frontend services
echo "🎨 Starting frontend services..."
docker-compose -f $COMPOSE_FILE up -d admin_panel unified_platform web_portal bcm_platform_ui

# Start monitoring services
echo "📈 Starting monitoring services..."
docker-compose -f $COMPOSE_FILE up -d grafana traefik

echo ""
echo "✅ BCM Platform deployment completed!"
echo ""
echo "🌐 Access URLs:"
echo "  - Admin Panel:         http://localhost:3001"
echo "  - Unified Platform:    http://localhost:3002"
echo "  - Web Portal:          http://localhost:3000"
echo "  - BCM Platform UI:     http://localhost:3004"
echo ""
echo "🔗 API Endpoints:"
echo "  - Main API:            http://localhost:5001"
echo "  - Unified API Gateway: http://localhost:8777"
echo "  - Database Gateway:    http://localhost:8888"
echo "  - CRM Bridge:          http://localhost:8778"
echo ""
echo "🤖 AI & Core Services:"
echo "  - Odoo:               http://localhost:8069"
echo "  - AI Orchestrator:    http://localhost:8000"
echo "  - AI Control:         http://localhost:8200"
echo ""
echo "📊 Monitoring:"
echo "  - Grafana:            http://localhost:3003"
echo "  - Traefik:            http://localhost:8080"
echo ""

# Health check
echo "🏥 Performing health checks..."
sleep 10

SERVICES=(
    "http://localhost:5001/api/modules/list"
    "http://localhost:8000/health"
    "http://localhost:8069/web/health"
    "http://localhost:3003/api/health"
)

for url in "${SERVICES[@]}"; do
    if curl -f -s "$url" > /dev/null; then
        echo "  ✅ $url - OK"
    else
        echo "  ❌ $url - FAILED"
    fi
done

echo ""
echo "📝 To view logs: docker-compose -f $COMPOSE_FILE logs -f [service_name]"
echo "🛑 To stop all: docker-compose -f $COMPOSE_FILE down"
echo ""

# Show running containers
echo "🔍 Running containers:"
docker-compose -f $COMPOSE_FILE ps

echo "🎉 BCM Platform is ready!"