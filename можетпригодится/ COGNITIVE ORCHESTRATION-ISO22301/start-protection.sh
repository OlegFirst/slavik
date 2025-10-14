#!/bin/bash

# 🛡️ PROTECTION LAYER - Запуск защитного слоя
# Защита и мониторинг для ядра системы

echo "================================================"
echo "🛡️ PROTECTION LAYER - Защитный слой"
echo "================================================"
echo ""

# Проверяем что ядро запущено
if ! docker ps | grep -q "nucleus-orchestrator"; then
    echo "⚠️ Сначала запустите ядро системы:"
    echo "  ./start-nucleus.sh"
    exit 1
fi

echo "✅ Ядро системы обнаружено"
echo ""

# Запускаем защитный слой
echo "🚀 ЗАПУСКАЕМ ЗАЩИТНЫЙ СЛОЙ:"
echo ""

# 1. Безопасность
echo "1️⃣ Запускаем Auth Service (страж у ворот)..."
docker-compose -f docker-compose-protection.yml up -d auth-service

sleep 3

# 2. Конфигурация
echo "2️⃣ Запускаем Config Service (хранитель настроек)..."
docker-compose -f docker-compose-protection.yml up -d config-service

sleep 3

# 3. API Gateway
echo "3️⃣ Запускаем API Gateway (главные ворота)..."
docker-compose -f docker-compose-protection.yml up -d api-gateway

sleep 3

# 4. Мониторинг
echo "4️⃣ Запускаем мониторинг (Prometheus, Grafana, Loki)..."
docker-compose -f docker-compose-protection.yml up -d prometheus grafana loki promtail

sleep 5

# 5. Нотификации
echo "5️⃣ Запускаем Notification Service (коммуникатор)..."
docker-compose -f docker-compose-protection.yml up -d notification-service

# 6. Rate Limiting
echo "6️⃣ Запускаем Rate Limiter (защита от DDoS)..."
docker-compose -f docker-compose-protection.yml up -d rate-limiter

echo ""
echo "================================================"
echo "✅ ЗАЩИТНЫЙ СЛОЙ АКТИВИРОВАН!"
echo "================================================"
echo ""
echo "📍 Точки доступа:"
echo "  • API Gateway:      http://localhost:8080  (главный вход)"
echo "  • Auth Service:     http://localhost:8003"
echo "  • Config Service:   http://localhost:8004"
echo "  • Grafana:         http://localhost:3000  (admin/admin)"
echo "  • Prometheus:      http://localhost:9090"
echo "  • Notifications:    http://localhost:8006"
echo ""
echo "🔐 Теперь доступ к ядру только через API Gateway!"
echo ""
echo "📊 Статус:"
docker-compose -f docker-compose-protection.yml ps

echo ""
echo "💡 Команды управления:"
echo "  • Остановить:  docker-compose -f docker-compose-protection.yml down"
echo "  • Логи:        docker-compose -f docker-compose-protection.yml logs -f"
echo "  • Статус:      docker-compose -f docker-compose-protection.yml ps"
echo ""