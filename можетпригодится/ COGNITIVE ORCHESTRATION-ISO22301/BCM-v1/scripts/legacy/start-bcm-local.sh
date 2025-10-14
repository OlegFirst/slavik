#!/bin/bash

echo "🚀 Запуск BCM Platform (локально без Docker)"
echo "=============================================="

# Проверка зависимостей
echo "📋 Проверка зависимостей..."

# Проверка PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL не установлен. Запустите: brew install postgresql@15"
    exit 1
fi

# Проверка Redis
if ! command -v redis-cli &> /dev/null; then
    echo "❌ Redis не установлен. Запустите: brew install redis"
    exit 1
fi

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не установлен"
    exit 1
fi

# Экспорт переменных окружения
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/bcm_platform"
export REDIS_URL="redis://localhost:6379/0"

echo "✅ Зависимости проверены"

# Запуск сервисов
echo "🔄 Запуск сервисов..."

# Запуск PostgreSQL если не запущен
if ! brew services list | grep postgresql@15 | grep started > /dev/null; then
    echo "📊 Запуск PostgreSQL..."
    brew services start postgresql@15
fi

# Запуск Redis если не запущен
if ! brew services list | grep redis | grep started > /dev/null; then
    echo "🔴 Запуск Redis..."
    brew services start redis
fi

# Создание базы данных если не существует
echo "🗄️  Проверка базы данных..."
if ! psql -lqt | cut -d \| -f 1 | grep -qw bcm_platform; then
    echo "📊 Создание базы данных bcm_platform..."
    createdb bcm_platform
fi

# Применение SQL схем
echo "📋 Применение SQL схем..."
if [ -f "database/schema/init_schema.sql" ]; then
    psql bcm_platform < database/schema/init_schema.sql
    echo "✅ Схемы применены"
fi

# Статус сервисов
echo ""
echo "📊 Статус сервисов:"
echo "- PostgreSQL: $(brew services list | grep postgresql@15 | awk '{print $2}')"
echo "- Redis:      $(brew services list | grep redis | awk '{print $2}')"

# Тест подключений
echo ""
echo "🔌 Тест подключений:"
if psql bcm_platform -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ PostgreSQL: подключение успешно"
else
    echo "❌ PostgreSQL: ошибка подключения"
fi

if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: подключение успешно"
else
    echo "❌ Redis: ошибка подключения"
fi

echo ""
echo "🎉 BCM Platform готова к работе!"
echo ""
echo "📊 Доступные подключения:"
echo "- PostgreSQL: localhost:5432/bcm_platform"
echo "- Redis:      localhost:6379"
echo ""
echo "🔧 Переменные окружения:"
echo "export DATABASE_URL=$DATABASE_URL"
echo "export REDIS_URL=$REDIS_URL"
echo ""
echo "🛑 Для остановки сервисов:"
echo "brew services stop postgresql@15 redis"
