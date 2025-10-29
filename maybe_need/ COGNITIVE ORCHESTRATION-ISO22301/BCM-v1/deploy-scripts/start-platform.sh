#!/bin/bash
# ПРАВИЛЬНЫЙ ЗАПУСК BCM PLATFORM
# Фиксируем последовательность чтобы не забыть!

echo "========================================="
echo "🚀 STARTING BCM PLATFORM"
echo "========================================="

# Останавливаем если что-то запущено
echo "📦 Stopping any running services..."
docker-compose down

echo ""
echo "1️⃣ Starting database and cache..."
docker-compose up -d postgres redis rabbitmq

echo "⏳ Waiting for database initialization (10s)..."
sleep 10

echo ""
echo "2️⃣ Starting AI Orchestrator (Odoo needs it!)..."
docker-compose up -d ai_orchestrator

echo ""
echo "3️⃣ Starting EventBus..."
docker-compose up -d eventbus

echo "⏳ Waiting for services to be ready (5s)..."
sleep 5

echo ""
echo "4️⃣ Starting Odoo (will wait for AI Orchestrator)..."
docker-compose up -d odoo

echo ""
echo "========================================="
echo "✅ PLATFORM STARTED SUCCESSFULLY!"
echo "========================================="
echo ""
echo "📌 Access points:"
echo "   • Odoo: http://localhost:8069"
echo "   • EventBus: http://localhost:8001"
echo "   • AI Orchestrator: http://localhost:8000"
echo "   • RabbitMQ: http://localhost:15672"
echo ""
echo "📋 Check status: docker-compose ps"
echo "📋 View logs: docker-compose logs -f odoo"