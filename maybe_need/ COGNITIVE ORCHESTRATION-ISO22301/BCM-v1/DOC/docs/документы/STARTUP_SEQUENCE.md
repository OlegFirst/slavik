# 🚀 ПРАВИЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ЗАПУСКА BCM PLATFORM

## ⚠️ ВАЖНО: Odoo ВСЕГДА ждет AI Orchestrator!

## ✅ ПРАВИЛЬНЫЙ ПОРЯДОК ЗАПУСКА:

```bash
# 1. Базовые сервисы (БД и кэш)
docker-compose up -d postgres redis

# 2. Ждем готовности БД (10 сек)
sleep 10

# 3. Запускаем RabbitMQ для AI Orchestrator
docker-compose up -d rabbitmq

# 4. Запускаем AI Orchestrator (Odoo его ждет!)
docker-compose up -d ai_orchestrator

# 5. Запускаем EventBus
docker-compose up -d eventbus

# 6. ТОЛЬКО ТЕПЕРЬ запускаем Odoo
docker-compose up -d odoo
```

## 🔴 ПРОБЛЕМА:
- Odoo в entrypoint проверяет: `wait AI http://ai_orchestrator:8000/health`
- Если AI Orchestrator не запущен - Odoo зависает навсегда!

## ✅ РЕШЕНИЕ - ОДИН СКРИПТ:

```bash
#!/bin/bash
# start-platform.sh

echo "🚀 Starting BCM Platform..."

# Очистка если нужно
docker-compose down

# Запуск в правильном порядке
docker-compose up -d postgres redis rabbitmq
sleep 10
docker-compose up -d ai_orchestrator eventbus
sleep 5
docker-compose up -d odoo

echo "✅ Platform started! Check http://localhost:8069"
```

## 📋 ТЕКУЩИЕ МОДУЛИ:
- 125 модулей в addons/
- 20 BCM модулей
- 105 системных модулей
- Все работает без изменений!