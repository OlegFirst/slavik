#!/bin/bash

# 🧠 NUCLEUS - Запуск ядра BCM Cognitive Orchestration Platform
# Основано на BCM_ORGANISM_ARCHITECTURE.md

echo "================================================"
echo "🧠 NUCLEUS - Ядро Cognitive Orchestration"
echo "================================================"
echo ""

# Проверяем Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

# Останавливаем старые контейнеры
echo "🔄 Останавливаем старые контейнеры ядра..."
docker-compose -f docker-compose-nucleus.yml down 2>/dev/null

# Создаем сеть если её нет
echo "🌐 Создаем bcm-nucleus-network..."
docker network create bcm-nucleus-network 2>/dev/null

echo ""
echo "🚀 ЗАПУСКАЕМ NUCLEUS:"
echo ""

# 1. База и инфраструктура
echo "1️⃣ Запускаем инфраструктуру (PostgreSQL, Redis, RabbitMQ)..."
docker-compose -f docker-compose-nucleus.yml up -d postgres redis rabbitmq

# Ждем готовности
echo "   ⏳ Ждем готовности инфраструктуры..."
sleep 15

# 2. Нервная система
echo "2️⃣ Запускаем нервную систему (EventBus, Registry)..."
docker-compose -f docker-compose-nucleus.yml up -d eventbus registry

sleep 5

# 3. Процессы
echo "3️⃣ Запускаем Workflow Engine (кровеносная система)..."
docker-compose -f docker-compose-nucleus.yml up -d workflow

sleep 5

# 4. Мозг
echo "4️⃣ Запускаем Orchestrator (единый мозг)..."
docker-compose -f docker-compose-nucleus.yml up -d orchestrator

sleep 5

# 5. BCM Integration Hub
echo "5️⃣ Запускаем BCM Integration Hub (Odoo координатор)..."
docker-compose -f docker-compose-nucleus.yml up -d odoo-nucleus

echo ""
echo "================================================"
echo "✅ NUCLEUS ЗАПУЩЕН!"
echo "================================================"
echo ""
echo "📍 Компоненты ядра:"
echo "  • Orchestrator (мозг):    http://localhost:8000"
echo "  • EventBus (нервы):       http://localhost:8001"
echo "  • Registry (память):      http://localhost:8002"
echo "  • Workflow (процессы):    http://localhost:8005"
echo "  • Odoo BCM Hub:          http://localhost:8069"
echo "  • RabbitMQ UI:           http://localhost:15672"
echo ""
echo "📊 Статус:"
docker-compose -f docker-compose-nucleus.yml ps

echo ""
echo "💡 Проверка здоровья:"
echo "  curl http://localhost:8001/health  # EventBus"
echo "  curl http://localhost:8002/health  # Registry"
echo "  curl http://localhost:8000/health  # Orchestrator"
echo ""
echo "📝 Логи:"
echo "  docker-compose -f docker-compose-nucleus.yml logs -f"
echo ""