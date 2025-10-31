#!/bin/bash

# BCM Platform - Staged Startup Script
# Поэтапный запуск: инфраструктура → Odoo основа → BCM модули

set -e

echo "🚀 BCM Platform - Staged Startup"
echo "================================="

# Phase 1: Infrastructure (Database, Cache, Message Queue)
echo ""
echo "📊 Phase 1: Starting Infrastructure Services..."
echo "-----------------------------------------------"
docker-compose up -d postgres redis rabbitmq

echo "⏳ Waiting for infrastructure to be ready..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U odoo > /dev/null 2>&1 && \
       docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Infrastructure is ready"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

# Phase 2: Odoo Base (только базовые модули)
echo ""
echo "🏗️  Phase 2: Starting Odoo with Core Modules..."
echo "-----------------------------------------------"
# Устанавливаем только базовые модули
export ODOO_INSTALL_BCM_CORE=1
export ODOO_UPGRADE_ALL=0
docker-compose up -d odoo

echo "⏳ Waiting for Odoo to initialize..."
for i in {1..60}; do
    if curl -f http://localhost:8069/web/health > /dev/null 2>&1; then
        echo "✅ Odoo is ready"
        break
    fi
    echo "   Waiting for Odoo... ($i/60)"
    sleep 5
done

# Phase 3: AI Services (независимо от BCM модулей)
echo ""
echo "🤖 Phase 3: Starting AI Services..."
echo "-----------------------------------"
docker-compose up -d ai_orchestrator bia_engine document_processor compliance_checker

echo "⏳ Waiting for AI services..."
sleep 15

# Phase 4: Additional Services
echo ""
echo "🌐 Phase 4: Starting Additional Services..."
echo "------------------------------------------"
docker-compose up -d keycloak mailhog traefik

echo ""
echo "✅ All services are starting up!"
echo ""
echo "🌐 Available interfaces:"
echo "   • Odoo BCM Platform: http://localhost:8069"
echo "   • Database: bcm_platform (admin/admin)"
echo ""
echo "📋 Next steps:"
echo "   1. Wait 2-3 minutes for full initialization"
echo "   2. Access http://localhost:8069 and login as admin/admin"
echo "   3. Install additional BCM modules through Settings → Apps"
echo ""
echo "🔧 Management commands:"
echo "   • View logs: docker-compose logs -f [service]"
echo "   • Stop all: docker-compose down"
echo "   • Install specific BCM module: ./install-bcm-module.sh [module_name]"
echo ""
echo "📊 Service status:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"