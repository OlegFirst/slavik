#!/bin/bash

# 🧠 Запуск КООРДИНАЦИОННОГО ЯДРА системы
# Минимальный набор для управления

echo "================================================"
echo "🧠 COORDINATION CORE - Ядро системы"
echo "================================================"
echo ""

# Проверяем Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

echo "🔄 Останавливаем старые контейнеры ядра..."
docker-compose -f docker-compose-core.yml down

echo ""
echo "🚀 ЗАПУСКАЕМ КООРДИНАЦИОННОЕ ЯДРО:"
echo ""

# 1. Инфраструктура
echo "1️⃣ Запускаем базовую инфраструктуру (Redis, PostgreSQL)..."
docker-compose -f docker-compose-core.yml up -d redis postgres

# Ждем готовности
echo "   ⏳ Ждем готовности БД..."
sleep 10

# 2. EventBus
echo "2️⃣ Запускаем EventBus (нервная система)..."
docker-compose -f docker-compose-core.yml up -d eventbus

sleep 3

# 3. Service Registry
echo "3️⃣ Запускаем Service Registry (реестр сервисов)..."
docker-compose -f docker-compose-core.yml up -d service-registry

sleep 3

# 4. Workflow Engine
echo "4️⃣ Запускаем Workflow Engine (исполнитель процессов)..."
docker-compose -f docker-compose-core.yml up -d workflow-engine

echo ""
echo "================================================"
echo "✅ КООРДИНАЦИОННОЕ ЯДРО ЗАПУЩЕНО!"
echo "================================================"
echo ""
echo "📍 Компоненты ядра:"
echo "  • EventBus:         http://localhost:8001"
echo "  • Service Registry: http://localhost:8002"
echo "  • Workflow Engine:  http://localhost:8003"
echo "  • Redis:           localhost:6379"
echo "  • PostgreSQL:      localhost:5432"
echo ""
echo "📊 Статус:"
docker-compose -f docker-compose-core.yml ps

echo ""
echo "💡 Проверка здоровья:"
echo "  curl http://localhost:8001/health  # EventBus"
echo "  curl http://localhost:8002/health  # Registry"
echo ""
echo "📝 Логи:"
echo "  docker-compose -f docker-compose-core.yml logs -f"
echo ""