#!/bin/bash

# Sequential BCM Platform Startup 
# Решает проблемы с конфликтами cron jobs и одновременным запуском

set -e

echo "🚀 BCM Platform - Sequential Startup (Anti-Conflict)"
echo "===================================================="

# Phase 1: Infrastructure only
echo ""
echo "📊 Phase 1: Infrastructure Services..."
echo "--------------------------------------"
docker-compose down
docker-compose up -d postgres redis

echo "⏳ Waiting for infrastructure..."
for i in {1..20}; do
    if docker-compose exec -T postgres pg_isready -U odoo > /dev/null 2>&1 && \
       docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Infrastructure ready"
        break
    fi
    echo "   Infrastructure starting... ($i/20)"
    sleep 3
done

# Phase 2: Odoo ONLY (no AI services)
echo ""
echo "🏗️  Phase 2: Odoo Core (Single Worker)..."
echo "----------------------------------------"
# Temporarily disable AI dependency check
export SKIP_AI_CHECK=1
docker-compose up -d odoo

echo "⏳ Waiting for Odoo core to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:8069/web/health > /dev/null 2>&1; then
        echo "✅ Odoo core ready"
        break
    fi
    echo "   Odoo initializing... ($i/30)"
    sleep 5
done

# Phase 3: Check Odoo is accessible
echo ""
echo "🔍 Phase 3: Verifying Odoo Access..."
echo "-----------------------------------"
if curl -s http://localhost:8069 | grep -q "odoo"; then
    echo "✅ Odoo web interface accessible"
    echo ""
    echo "🎉 BCM Platform Ready!"
    echo "====================="
    echo "🌐 Odoo Admin: http://localhost:8069"
    echo "👤 Login: admin / admin"
    echo "📦 BCM Modules: Available in Apps menu"
    echo ""
    echo "💡 Forward port 8069 in Codespaces for external access"
else
    echo "❌ Odoo web interface has issues"
    echo "Check logs: docker logs iso-22301-odoo-1"
fi

echo ""
echo "📊 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"