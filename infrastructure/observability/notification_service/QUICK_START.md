# 🚀 Notification Service - Quick Start

**Версия:** 1.0
**Дата:** 2025-10-03

---

## ✅ Предварительные Требования

- [x] Supabase схема применена (см. `../monitoring/database/APPLY_SCHEMA.md`)
- [x] Redis доступен (Upstash)
- [x] Docker установлен
- [x] `.env` файл настроен

---

## 📋 Шаг 1: Применить Схему БД

### Инструкция:

1. Открыть https://supabase.com/dashboard/project/tpdkhddtbhpoqzzgxfni/sql
2. Скопировать содержимое файла:
   ```bash
   cat /Users/MD/AI-Platform-ISO/infrastructure/monitoring/database/supabase_schema.sql
   ```
3. Вставить в SQL Editor
4. Нажать **Run**
5. Дождаться завершения (~5-10 сек)

### Проверка:

```sql
-- Должно вернуть 8 таблиц
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'notifications',
    'compliance_alerts',
    'nonconformities',
    'audits',
    'business_metrics',
    'service_registry',
    'automation_jobs',
    'compliance_snapshots'
  );
```

---

## 🔧 Шаг 2: Настроить `.env`

Файл `/Users/MD/AI-Platform-ISO/.env` уже обновлен с переменными для Notification Service.

### Обязательные переменные (уже заполнены):

```bash
SUPABASE_URL=https://tpdkhddtbhpoqzzgxfni.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbG... (уже есть)
REDIS_URL=redis://:tldJWwUq...@redis-10023... (уже есть)
```

### Опциональные (можно заполнить позже):

```bash
# Email уведомления
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Получатели
COMPLIANCE_OFFICERS_EMAILS=officer1@company.com,officer2@company.com
AUDIT_TEAM_EMAILS=auditor@company.com

# Slack (опционально)
SLACK_ENABLED=false
SLACK_WEBHOOK_URL=

# Teams (опционально)
TEAMS_ENABLED=false
TEAMS_WEBHOOK_URL=
```

**Примечание:** Для тестирования можно оставить опциональные переменные пустыми. Сервис будет работать с Supabase + Redis.

---

## 🐳 Шаг 3: Запустить Docker Compose

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/observability

# Запустить все сервисы мониторинга (включая Notification Service)
docker-compose -f docker-compose.monitoring.yml up -d

# Проверить статус
docker-compose -f docker-compose.monitoring.yml ps

# Посмотреть логи Notification Service
docker logs bcm-notification-service -f
```

### Ожидаемые логи:

```
✅ Connected to Supabase PostgreSQL
✅ Connected to Redis
ℹ️  RabbitMQ not configured (direct delivery only)
🚀 Notification Service started successfully
INFO:     Uvicorn running on http://0.0.0.0:8035
```

---

## 🧪 Шаг 4: Протестировать Сервис

### Тест 1: Health Check

```bash
curl http://localhost:8035/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "service": "notification_service",
  "version": "1.0.0",
  "components": {
    "redis": "connected",
    "rabbitmq": "disconnected"
  }
}
```

### Тест 2: Отправить Email уведомление

```bash
curl -X POST http://localhost:8035/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["test@example.com"],
    "subject": "Test Notification",
    "body": "This is a test from BCM Notification Service"
  }'
```

**Ожидаемый ответ:**
```json
{
  "status": "success",
  "message": "Email queued for delivery",
  "notification_id": "550e8400-e29b-41d4-a716-446655440000",
  "recipients": 1
}
```

### Тест 3: Проверить в Supabase

Открыть https://supabase.com/dashboard/project/tpdkhddtbhpoqzzgxfni/editor

Выполнить:
```sql
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 5;
```

Должна появиться запись с тестовым уведомлением!

### Тест 4: Проверить историю через API

```bash
curl http://localhost:8035/notifications/history?limit=10
```

### Тест 5: Проверить Prometheus метрики

```bash
curl http://localhost:8035/metrics
```

Должны быть метрики:
```
notifications_sent_total{channel="email",status="success"} 1
notification_duration_seconds_count{channel="email"} 1
```

---

## 🎯 Шаг 5: Проверить в Prometheus

1. Открыть http://localhost:9090
2. В поиске ввести: `up{job="notification-service"}`
3. Должно показать: `up{job="notification-service"} = 1`

Также проверить:
```
notifications_sent_total
notification_duration_seconds
```

---

## 📊 Проверить Автоматическую Регистрацию

Notification Service должен автоматически зарегистрироваться в Prometheus через service discovery.

### Проверка:

```bash
# Посмотреть targets в Prometheus
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="notification-service")'
```

Или открыть в браузере:
http://localhost:9090/targets

Найти `notification-service` - статус должен быть **UP** (зеленый).

---

## 🐛 Troubleshooting

### Проблема: "Failed to connect to Supabase"

**Решение:**
```bash
# Проверить переменные окружения
docker exec bcm-notification-service env | grep SUPABASE

# Должно быть:
# SUPABASE_URL=https://tpdkhddtbhpoqzzgxfni.supabase.co
# SUPABASE_SERVICE_ROLE_KEY=eyJhbG...
```

### Проблема: "Failed to connect to Redis"

**Решение:**
```bash
# Проверить Redis URL
docker exec bcm-notification-service env | grep REDIS_URL

# Проверить подключение к Redis
docker exec bcm-notification-service python -c "
import redis
r = redis.from_url('redis://:tldJWwUq7lAwOHuCa9pSD7sVfjQFYPYN@redis-10023.c8.us-east-1-4.ec2.redns.redis-cloud.com:10023')
print('Ping:', r.ping())
"
```

### Проблема: "Container keeps restarting"

**Решение:**
```bash
# Посмотреть логи
docker logs bcm-notification-service --tail 50

# Проверить что все зависимости установлены
docker exec bcm-notification-service pip list | grep -E "supabase|redis|prometheus"
```

### Проблема: "Notifications not saved to database"

**Решение:**
```bash
# Проверить что схема применена в Supabase
# Открыть https://supabase.com/dashboard/project/tpdkhddtbhpoqzzgxfni/editor
# Должна быть таблица 'notifications'

# Проверить RLS policies
# В Supabase: Authentication → Policies
# Должна быть policy: "Service role can do everything on notifications"
```

---

## ✅ Checklist

После выполнения всех шагов:

- [ ] Supabase схема применена (8 таблиц + 4 views)
- [ ] `.env` файл настроен
- [ ] Docker Compose запущен
- [ ] Health check возвращает "healthy"
- [ ] Тестовое уведомление отправлено
- [ ] Уведомление появилось в Supabase
- [ ] Prometheus метрики доступны
- [ ] Notification Service зарегистрирован в Prometheus

---

## 🎉 Готово!

Notification Service настроен и работает!

### Что дальше:

1. ✅ **Протестировать интеграцию с ISO 22301 Compliance API**
   - Создать alert → должно прийти уведомление

2. ✅ **Настроить SMTP** (если нужны реальные email)
   - Добавить `SMTP_USER` и `SMTP_PASSWORD` в `.env`
   - Перезапустить: `docker-compose restart notification-service`

3. ✅ **Настроить Slack/Teams** (опционально)
   - Создать webhook
   - Добавить в `.env`
   - Установить `SLACK_ENABLED=true`

4. ✅ **Создать Grafana Dashboard**
   - Визуализация метрик уведомлений
   - Alerts на failure rate

---

## 📚 Документация

- **Полная интеграция:** `INTEGRATION_COMPLETE.md`
- **Применение схемы:** `../monitoring/database/APPLY_SCHEMA.md`
- **API Reference:** http://localhost:8035/docs (Swagger UI)

---

**Вопросы?** Проверь `INTEGRATION_COMPLETE.md` для детальной информации.
