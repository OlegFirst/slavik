#!/bin/bash

# BCM Platform System Diagnostics
# Проверяет состояние всех компонентов системы

echo "🔍 BCM Platform System Diagnostics"
echo "===================================="
echo ""

# Функция для проверки HTTP эндпоинта
check_endpoint() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"
    
    echo -n "[$name] $url ... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_code" ]; then
        echo "✅ OK ($response)"
        return 0
    else
        echo "❌ FAIL (HTTP $response)"
        return 1
    fi
}

# Функция для проверки порта
check_port() {
    local name="$1"
    local host="$2"
    local port="$3"
    
    echo -n "[$name] $host:$port ... "
    
    if nc -z "$host" "$port" 2>/dev/null; then
        echo "✅ Open"
        return 0
    else
        echo "❌ Closed"
        return 1
    fi
}

# Проверка Docker сервисов
echo "🐳 Docker Services Status:"
echo "-------------------------"
if command -v docker &> /dev/null; then
    docker compose ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}"
else
    echo "❌ Docker not installed or not in PATH"
fi
echo ""

# Проверка основных портов
echo "🌐 Port Connectivity:"
echo "-------------------"
check_port "PostgreSQL" "localhost" "5432"
check_port "Redis" "localhost" "6379"
check_port "RabbitMQ" "localhost" "5672"
check_port "RabbitMQ Management" "localhost" "15672"
check_port "Keycloak" "localhost" "8080"
check_port "Odoo" "localhost" "8069"
check_port "AI Orchestrator" "localhost" "8000"
check_port "Frontend v2" "localhost" "5173"
check_port "BIA Engine" "localhost" "8082"
check_port "Document Processor" "localhost" "8083"
check_port "Compliance Checker" "localhost" "8084"
echo ""

# Проверка HTTP эндпоинтов
echo "🔗 HTTP Endpoints:"
echo "-----------------"
check_endpoint "Odoo Web" "http://localhost:8069/web/health"
check_endpoint "Odoo Database" "http://localhost:8069/web/database/selector"
check_endpoint "AI Orchestrator" "http://localhost:8000/health"
check_endpoint "Keycloak Health" "http://localhost:8080/health/ready"
check_endpoint "RabbitMQ Management" "http://localhost:15672"
check_endpoint "Frontend v2" "http://localhost:5173"
check_endpoint "BIA Engine" "http://localhost:8082/health"
check_endpoint "Document Processor" "http://localhost:8083/health"
check_endpoint "Compliance Checker" "http://localhost:8084/health"
echo ""

# Проверка Odoo API
echo "🔧 Odoo API Tests:"
echo "-----------------"

# Тест подключения к базе данных
echo -n "[Odoo DB] Database access ... "
db_test=$(curl -s -X POST http://localhost:8069/web/dataset/call_kw \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"call","params":{"service":"db","method":"list"},"id":1}' 2>/dev/null)
    
if echo "$db_test" | grep -q "bcm_platform"; then
    echo "✅ OK (bcm_platform found)"
else
    echo "❌ FAIL (database not accessible)"
fi

# Тест JSON-RPC эндпоинта
echo -n "[Odoo RPC] JSON-RPC endpoint ... "
jsonrpc_test=$(curl -s -X POST http://localhost:8069/jsonrpc \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"call","params":{"service":"common","method":"version"},"id":1}' 2>/dev/null)
    
if echo "$jsonrpc_test" | grep -q "server_version"; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo ""

# Проверка логов
echo "📝 Recent Logs (last 10 lines):"
echo "-------------------------------"

if [ -d "/var/log/odoo" ]; then
    echo "[Odoo Logs]"
    tail -5 /var/log/odoo/*.log 2>/dev/null || echo "No Odoo logs found"
else
    echo "[Docker Odoo Logs]"
    docker compose logs --tail=5 odoo 2>/dev/null || echo "No Docker logs available"
fi

echo ""

# Проверка ресурсов системы
echo "💻 System Resources:"
echo "-------------------"
echo "Memory usage:"
free -h 2>/dev/null || echo "Memory info not available"
echo ""
echo "Disk usage:"
df -h . 2>/dev/null || echo "Disk info not available"
echo ""

# Итоговые рекомендации
echo "💡 Recommendations:"
echo "------------------"
echo "1. If Odoo is not responding, try: docker compose restart odoo"
echo "2. If database issues persist, try: docker compose down && docker compose up -d postgres && sleep 10 && docker compose up -d"
echo "3. Check frontend console for specific errors: http://localhost:5173"
echo "4. For detailed logs: docker compose logs -f [service_name]"
echo ""
echo "🏁 Diagnostics Complete"
