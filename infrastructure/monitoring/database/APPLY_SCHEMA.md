# 📋 Применение Схемы БД в Supabase

**Дата:** 2025-10-03
**База данных:** Supabase PostgreSQL
**Схема:** `supabase_schema.sql`

---

## 🎯 Что будет создано

### Таблицы (8 штук):
1. **notifications** - история всех уведомлений
2. **compliance_alerts** - compliance алерты
3. **nonconformities** - несоответствия ISO 10.1
4. **audits** - аудиты ISO 9.2
5. **business_metrics** - метрики RTO/RPO/MTPD
6. **service_registry** - реестр сервисов
7. **automation_jobs** - результаты автоматизации
8. **compliance_snapshots** - ежедневные снимки

### Дополнительно:
- Indexes для быстрого поиска
- Triggers для auto-update timestamps
- Row Level Security (RLS) policies
- Views для отчетов
- Functions для статистики

---

## 📝 Шаги Применения

### Шаг 1: Открыть Supabase SQL Editor

1. Перейти на https://supabase.com/dashboard
2. Выбрать проект: **tpdkhddtbhpoqzzgxfni**
3. В левом меню: **SQL Editor**
4. Нажать **New Query**

### Шаг 2: Скопировать SQL схему

```bash
# В терминале
cat /Users/MD/AI-Platform-ISO/infrastructure/monitoring/database/supabase_schema.sql
```

Или открыть файл в редакторе и скопировать весь текст.

### Шаг 3: Вставить и Выполнить

1. Вставить скопированный SQL в Supabase SQL Editor
2. Нажать **Run** (или Cmd+Enter)
3. Дождаться завершения (займет ~5-10 секунд)

### Шаг 4: Проверить Результат

Выполнить проверочный запрос:

```sql
-- Проверить что все таблицы созданы
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

**Ожидаемый результат:** 8 таблиц
- audits
- automation_jobs
- business_metrics
- compliance_alerts
- compliance_snapshots
- nonconformities
- notifications
- service_registry

### Шаг 5: Проверить Views

```sql
-- Проверить что views созданы
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public';
```

**Ожидаемый результат:** 4 views
- active_alerts
- notification_stats
- open_nonconformities
- service_health_overview

---

## ✅ Проверочные Запросы

### Проверка #1: Вставить тестовую запись

```sql
-- Вставить тестовое уведомление
INSERT INTO notifications (
    channel,
    recipients,
    subject,
    message,
    severity,
    status
) VALUES (
    'email',
    '["test@example.com"]'::jsonb,
    'Test Notification',
    'This is a test message',
    'info',
    'pending'
);

-- Проверить что запись появилась
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 1;
```

### Проверка #2: Проверить RLS policies

```sql
-- Посмотреть все policies
SELECT schemaname, tablename, policyname, roles, cmd
FROM pg_policies
WHERE schemaname = 'public';
```

### Проверка #3: Проверить triggers

```sql
-- Посмотреть все triggers
SELECT trigger_name, event_object_table, action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public';
```

---

## 🔧 Если что-то пошло не так

### Ошибка: "permission denied"

**Решение:** Убедись что используешь **service_role** ключ, не anon ключ.

В Supabase SQL Editor автоматически используется service_role.

### Ошибка: "relation already exists"

**Решение:** Таблица уже существует. Можно:

**Вариант 1: Удалить старые таблицы**
```sql
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS compliance_alerts CASCADE;
DROP TABLE IF EXISTS nonconformities CASCADE;
DROP TABLE IF EXISTS audits CASCADE;
DROP TABLE IF EXISTS business_metrics CASCADE;
DROP TABLE IF EXISTS service_registry CASCADE;
DROP TABLE IF EXISTS automation_jobs CASCADE;
DROP TABLE IF EXISTS compliance_snapshots CASCADE;

-- Потом применить схему заново
```

**Вариант 2: Использовать миграцию**
```sql
-- Добавить только новые столбцы/таблицы
-- (требует ручной модификации схемы)
```

### Ошибка: "syntax error"

**Решение:** Убедись что скопировал весь SQL файл целиком, включая:
- `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";` в начале
- Все таблицы
- Все triggers
- Все policies

---

## 📊 Тестовые Данные (Опционально)

После применения схемы можно добавить тестовые данные:

```sql
-- Тестовый сервис
INSERT INTO service_registry (
    service_name,
    service_type,
    base_url,
    health_endpoint,
    metrics_endpoint,
    port,
    criticality,
    status
) VALUES (
    'notification-service',
    'platform',
    'http://localhost:8035',
    '/health',
    '/metrics',
    8035,
    'high',
    'unknown'
);

-- Тестовый alert
INSERT INTO compliance_alerts (
    alert_id,
    alert_type,
    severity,
    service_name,
    title,
    message,
    iso_clause
) VALUES (
    'ALT_2025_001',
    'availability',
    'high',
    'validation-service',
    'Service Response Time Degraded',
    'Response time exceeded 2s threshold',
    '8.4'
);

-- Тестовая nonconformity
INSERT INTO nonconformities (
    nc_id,
    title,
    description,
    severity,
    iso_clause,
    status,
    responsible_person
) VALUES (
    'NC_2025_001',
    'Backup procedure not documented',
    'ISO 22301 requires documented backup procedures',
    'major',
    '8.3.3',
    'open',
    'john@example.com'
);

-- Проверить
SELECT * FROM service_registry;
SELECT * FROM compliance_alerts;
SELECT * FROM nonconformities;
```

---

## 📋 Следующие Шаги

После применения схемы:

1. ✅ Схема применена
2. ⏭️ Настроить `.env` переменные (см. следующий шаг)
3. ⏭️ Запустить Notification Service
4. ⏭️ Протестировать отправку уведомлений

---

## 🔗 Полезные Ссылки

- **Supabase Dashboard:** https://supabase.com/dashboard/project/tpdkhddtbhpoqzzgxfni
- **SQL Editor:** https://supabase.com/dashboard/project/tpdkhddtbhpoqzzgxfni/sql
- **Table Editor:** https://supabase.com/dashboard/project/tpdkhddtbhpoqzzgxfni/editor
- **API Docs:** https://supabase.com/dashboard/project/tpdkhddtbhpoqzzgxfni/api

---

**Готово!** После выполнения всех шагов база данных готова к использованию.
