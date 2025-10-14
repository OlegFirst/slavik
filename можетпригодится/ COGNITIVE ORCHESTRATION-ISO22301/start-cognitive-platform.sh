#!/bin/bash

# 🚀 COGNITIVE ORCHESTRATION PLATFORM - Quick Start
# Запуск всей интеллектуальной платформы одной командой

echo "================================================"
echo "🧠 COGNITIVE ORCHESTRATION PLATFORM"
echo "================================================"
echo ""

# Проверяем Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

# Останавливаем старые контейнеры если есть
echo "🔄 Останавливаем старые контейнеры..."
docker-compose -f docker-compose-cognitive.yml down 2>/dev/null

# Создаем сеть если её нет
echo "🌐 Создаем cognitive-network..."
docker network create cognitive-network 2>/dev/null

# Запускаем инфраструктуру
echo "🏗️ Запускаем инфраструктуру (PostgreSQL, Redis)..."
docker-compose -f docker-compose-cognitive.yml up -d postgres redis

# Ждем готовности БД
echo "⏳ Ждем готовности базы данных..."
sleep 10

# Запускаем Neural Fabric
echo "🧠 Запускаем Neural Fabric (EventBus, Registry)..."
docker-compose -f docker-compose-cognitive.yml up -d eventbus service-registry

sleep 5

# Запускаем Cognitive Orchestrator
echo "🎯 Запускаем Cognitive Orchestrator..."
docker-compose -f docker-compose-cognitive.yml up -d cognitive-orchestrator

sleep 5

# Запускаем бизнес-сервисы
echo "📦 Запускаем бизнес-сервисы (Odoo, Document Processor)..."
docker-compose -f docker-compose-cognitive.yml up -d odoo document-processor

# Запускаем мониторинг
echo "📊 Запускаем мониторинг (Prometheus, Grafana)..."
docker-compose -f docker-compose-cognitive.yml up -d prometheus grafana

# Запускаем внешние интеграции
echo "🔌 Запускаем интеграции (TheHive, Moodle)..."
docker-compose -f docker-compose-cognitive.yml up -d thehive moodle

echo ""
echo "================================================"
echo "✅ ПЛАТФОРМА ЗАПУЩЕНА!"
echo "================================================"
echo ""
echo "📍 Точки доступа:"
echo "  • Cognitive Brain:    http://localhost:8000"
echo "  • API Gateway:        http://localhost:8080"
echo "  • Odoo BCM:          http://localhost:8069"
echo "  • Grafana:           http://localhost:3000"
echo "  • TheHive:           http://localhost:9000"
echo ""
echo "📊 Статус сервисов:"
docker-compose -f docker-compose-cognitive.yml ps

echo ""
echo "💡 Команды управления:"
echo "  • Остановить:  docker-compose -f docker-compose-cognitive.yml down"
echo "  • Логи:        docker-compose -f docker-compose-cognitive.yml logs -f"
echo "  • Статус:      docker-compose -f docker-compose-cognitive.yml ps"
echo ""