#!/bin/bash

# BCM Platform Health Check Script
echo "🏥 BCM Platform Health Check"
echo "=============================="

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Счетчики
healthy_count=0
unhealthy_count=0
total_count=0

# Функция проверки здоровья
check_service() {
    local name=$1
    local port=$2
    local endpoint=${3:-"/health"}

    total_count=$((total_count + 1))

    if curl -s -f "http://localhost:$port$endpoint" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $name${NC} (port $port) - HEALTHY"
        healthy_count=$((healthy_count + 1))

        # Получаем детали health check
        response=$(curl -s "http://localhost:$port$endpoint" 2>/dev/null)
        if [[ $response == *"status"* ]]; then
            echo "   └─ $(echo $response | jq -r '.status // .service // "OK"' 2>/dev/null || echo "OK")"
        fi
    else
        echo -e "${RED}❌ $name${NC} (port $port) - FAILED"
        unhealthy_count=$((unhealthy_count + 1))
    fi
}

echo ""
echo "🔍 Checking Core Services..."
check_service "PostgreSQL Database" 5432 ""
check_service "Redis Cache" 6379 ""
check_service "Odoo BCM Platform" 8069 "/web/health"

echo ""
echo "🤖 Checking AI Services..."
check_service "AI Orchestrator" 8000
check_service "Scenario Orchestrator" 8085
check_service "Docker AI PoC" 8090
check_service "BIA Engine" 8082
check_service "Document Processor" 8083
check_service "Compliance Checker" 8084

echo ""
echo "🔗 Checking Integration Services..."
check_service "MCP Server" 8087
check_service "EventBus" 8001
check_service "Notification Service" 8002
check_service "BPMN Service" 8005

echo ""
echo "🔧 Checking Backend Services..."
check_service "Deployer" 8009
check_service "GitHub App" 8011
check_service "LMS Adapter" 8006
check_service "TheHive Adapter" 8007
check_service "Grafana Adapter" 8008

echo ""
echo "🌐 Checking Frontend Services..."
check_service "Web Portal" 3002 ""
check_service "Admin Panel" 3001 ""
check_service "Grafana Dashboard" 3003 "/api/health"

echo ""
echo "📊 Health Summary:"
echo "=================="
echo -e "${GREEN}✅ Healthy Services: $healthy_count${NC}"
echo -e "${RED}❌ Unhealthy Services: $unhealthy_count${NC}"
echo "📈 Total Services: $total_count"

# Вычисляем процент здоровья
if [ $total_count -gt 0 ]; then
    health_percentage=$((healthy_count * 100 / total_count))
    echo "🎯 Platform Health: $health_percentage%"

    if [ $health_percentage -ge 90 ]; then
        echo -e "${GREEN}🎉 Platform is in excellent health!${NC}"
    elif [ $health_percentage -ge 70 ]; then
        echo -e "${YELLOW}⚠️ Platform is mostly healthy with some issues${NC}"
    else
        echo -e "${RED}🚨 Platform has significant health issues${NC}"
    fi
fi

echo ""
echo "🔍 Quick Debug Commands:"
echo "docker-compose ps                    # Container status"
echo "docker-compose logs [service_name]   # Service logs"
echo "curl http://localhost:8069/web/health # Odoo health"

if [ $unhealthy_count -gt 0 ]; then
    echo ""
    echo "🔧 Recommended Actions:"
    echo "1. Check docker-compose logs for failed services"
    echo "2. Restart unhealthy services: docker-compose restart [service]"
    echo "3. Check .env configuration for missing variables"
    echo "4. Verify database connections and dependencies"
fi