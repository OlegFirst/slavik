# 🚀 BCM Platform ISO-22301 - Инструкция по запуску

## Быстрый запуск (все команды по порядку)

```bash
# 1. Запуск базовых сервисов (БД, Redis, RabbitMQ)
DB_PASSWORD=odoo123 docker-compose up -d postgres redis rabbitmq

# 2. Ждем 10 секунд для инициализации БД
sleep 10

# 3. Запуск AI сервисов
DB_PASSWORD=odoo123 docker-compose up -d eventbus ai_orchestrator

# 4. Запуск дополнительных сервисов
DB_PASSWORD=odoo123 docker-compose up -d document_processor bia_engine notification_service compliance_checker

# 5. Запуск Odoo (основная платформа)
DB_PASSWORD=odoo123 REDIS_HOST="" docker-compose up -d odoo

# 6. Настройка ngrok (если нужен публичный доступ)
ngrok config add-authtoken YOUR_TOKEN_HERE
ngrok http 127.0.0.1:8069 &

# 7. Получить публичную ссылку
curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'
```

## Проверка статуса

```bash
# Посмотреть все запущенные сервисы
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Проверить логи Odoo
docker logs iso-22301-odoo-1 --tail 50

# Проверить доступность Odoo
curl -I http://localhost:8069
```

## Известные проблемы и решения

### 1. Odoo застревает на "wait Redis"
**Проблема**: В entrypoint скрипте нет redis-cli
**Решение**: Запускаем с `REDIS_HOST=""`
```bash
DB_PASSWORD=odoo123 REDIS_HOST="" docker-compose up -d odoo
```

### 2. Odoo показывает "Internal Server Error"
**Проблема**: База данных не инициализирована
**Решение**: Подождите 1-2 минуты после запуска, Odoo инициализирует базовые модули автоматически

### 3. ngrok ERR_NGROK_8012 (connection refused)
**Проблема**: ngrok пытается подключиться к IPv6
**Решение**: Используйте 127.0.0.1 вместо localhost
```bash
ngrok http 127.0.0.1:8069
```

### 4. ngrok ERR_NGROK_108 (multiple sessions)
**Проблема**: Уже есть активная сессия ngrok
**Решение**: Убить старые процессы
```bash
pkill -f ngrok
sleep 2
ngrok http 127.0.0.1:8069 &
```

## Порты сервисов

| Сервис | Порт | Описание |
|--------|------|----------|
| PostgreSQL | 5432 | База данных |
| Redis | 6379 | Кеш и сессии |
| RabbitMQ | 5672/15672 | Очереди сообщений |
| Odoo | 8069 | Основная BCM платформа |
| AI Orchestrator | 8000 | AI сервис |
| EventBus | 8001 | Обработка событий |
| BIA Engine | 8082 | Business Impact Analysis |
| Document Processor | 8083 | Обработка документов |
| Compliance Checker | 8084 | Проверка соответствия |
| Notification Service | 8002 | Уведомления |

## Остановка платформы

```bash
# Остановить все сервисы
docker-compose stop

# Удалить все контейнеры (данные сохранятся в volumes)
docker-compose down

# Полная очистка (включая volumes) - ОСТОРОЖНО!
docker-compose down -v
```

## Переменные окружения

Создайте файл `.env` в корне проекта:
```env
DB_PASSWORD=odoo123
REDIS_HOST=redis
REDIS_PORT=6379
NGROK_TOKEN=your_token_here
```

## Актуальные директории

- `/workspaces/ISO-22301/core/database` - настройки PostgreSQL
- `/workspaces/ISO-22301/services/document_processor` - активный document_processor
- `/workspaces/ISO-22301/core/odoo-18.0/addons` - модули BCM для Odoo

## Примечания

1. Базовые модули Odoo загружаются автоматически при первом запуске
2. Дополнительные BCM модули устанавливаются через интерфейс Odoo
3. Первый запуск может занять 3-5 минут для инициализации всех сервисов
4. ngrok ссылка меняется при каждом перезапуске