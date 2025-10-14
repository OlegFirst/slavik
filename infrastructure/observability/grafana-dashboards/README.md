# Grafana Security & Data Management Dashboard

Комплексный dashboard для мониторинга безопасности, Vault, архивации и хранения данных.

## 📊 Панели Dashboard

### 🔐 Security Overview (Обзор безопасности)

1. **Total Secrets in Vault** - Общее количество секретов в Supabase Vault
2. **Security Events (24h)** - События безопасности за последние 24 часа
3. **Failed Auth Attempts (24h)** - Неудачные попытки авторизации
4. **Active Sessions** - Активные сессии пользователей

### 📈 Security Timeline

5. **Security Events Timeline (7 days)** - График событий безопасности за 7 дней
6. **Secrets Distribution** - Распределение секретов по типам

### 📋 Security Logs

7. **Recent Secrets** - Последние добавленные секреты в Vault
8. **Recent Security Events** - Недавние события безопасности (auth_failed, unauthorized_access, secret_accessed)

### 📦 Archive Metrics

9. **Total Archives** - Общее количество архивов
10. **Total Archive Size** - Общий размер всех архивов (MB)
11. **Total Archived Records** - Общее количество архивированных записей
12. **Recent Archives** - Последние созданные архивы

## 🔧 Установка

### 1. Настройка PostgreSQL Data Source в Grafana

```bash
# Откройте Grafana
http://localhost:3000

# Перейдите в Configuration > Data Sources > Add data source
# Выберите PostgreSQL

# Настройки:
Host: aws-1-eu-north-1.pooler.supabase.com:5432
Database: postgres
User: postgres.tpdkhddtbhpoqzzgxfni
Password: K@x3ta9V8GK5rnW
SSL Mode: require
```

### 2. Импорт Dashboard

**Способ 1: Через UI**
1. Откройте Grafana
2. Перейдите в Dashboards > Import
3. Нажмите "Upload JSON file"
4. Выберите `security-dashboard.json`
5. Выберите PostgreSQL data source
6. Нажмите "Import"

**Способ 2: Через API**
```bash
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_GRAFANA_API_KEY" \
  -d @security-dashboard.json
```

**Способ 3: Через файловую систему (provisioning)**
```bash
# Скопируйте dashboard в Grafana provisioning
cp security-dashboard.json /etc/grafana/provisioning/dashboards/

# Перезапустите Grafana
sudo systemctl restart grafana-server
```

## 📝 Необходимые таблицы в БД

Dashboard требует следующие таблицы:

### 1. vault.secrets (Supabase Vault)
```sql
-- Уже создана Supabase Vault extension
SELECT name, description, created_at FROM vault.secrets;
```

### 2. public.security_events
```sql
CREATE TABLE IF NOT EXISTS public.security_events (
    id SERIAL PRIMARY KEY,
    event_type TEXT NOT NULL,
    user_id UUID,
    ip_address TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_security_events_created ON public.security_events(created_at);
```

### 3. public.audit_logs
```sql
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id SERIAL PRIMARY KEY,
    action TEXT NOT NULL,
    user_id UUID,
    resource_type TEXT,
    resource_id TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX idx_audit_logs_created ON public.audit_logs(created_at);
```

### 4. public.sessions
```sql
CREATE TABLE IF NOT EXISTS public.sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_expires ON public.sessions(expires_at);
```

### 5. public.archive_catalog (уже создана Archive Service)
```sql
-- Создается автоматически при первом архивировании
SELECT * FROM public.archive_catalog LIMIT 1;
```

## 🔄 Auto-Refresh

Dashboard настроен на автообновление каждые **30 секунд**.

Вы можете изменить интервал:
- 5s, 10s, 30s, 1m, 5m, 15m, 30m, 1h

## 🎨 Кастомизация

### Изменить временной диапазон
По умолчанию: **Last 7 days**

Доступные диапазоны:
- Last 5 minutes
- Last 15 minutes
- Last 30 minutes
- Last 1 hour
- Last 3 hours
- Last 6 hours
- Last 12 hours
- Last 24 hours
- Last 2 days
- Last 7 days
- Last 30 days

### Добавить новую панель

1. Нажмите "Add panel" вверху dashboard
2. Выберите тип визуализации (Graph, Stat, Table, Pie Chart и т.д.)
3. Настройте SQL запрос:
```sql
-- Пример: количество секретов по типам
SELECT
  description,
  COUNT(*) as count
FROM vault.secrets
GROUP BY description
ORDER BY count DESC
```
4. Сохраните панель

## 📊 Примеры запросов

### Топ пользователей по количеству неудачных попыток входа
```sql
SELECT
  user_id,
  COUNT(*) as failed_attempts,
  MAX(created_at) as last_attempt
FROM public.audit_logs
WHERE action = 'auth_failed'
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY user_id
ORDER BY failed_attempts DESC
LIMIT 10
```

### Активность по часам (heatmap)
```sql
SELECT
  DATE_TRUNC('hour', created_at) as hour,
  COUNT(*) as events
FROM public.security_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY hour
ORDER BY hour
```

### Размер архивов по таблицам
```sql
SELECT
  schema_name || '.' || table_name as table_name,
  COUNT(*) as archive_count,
  SUM(records_count) as total_records,
  SUM(size_bytes) / 1024 / 1024 as total_size_mb
FROM public.archive_catalog
GROUP BY schema_name, table_name
ORDER BY total_size_mb DESC
```

## 🔔 Алерты (Alerts)

### Настройка алертов в Grafana

1. Откройте панель
2. Нажмите "Edit"
3. Перейдите на вкладку "Alert"
4. Нажмите "Create Alert"

### Примеры алертов

**Alert 1: Много неудачных попыток входа**
```
Condition: WHEN count() OF query(A, 5m, now) IS ABOVE 10
Message: More than 10 failed auth attempts in 5 minutes
```

**Alert 2: Vault недоступен**
```
Condition: WHEN count() OF query(A, 1m, now) IS BELOW 1
Message: Vault is not accessible
```

**Alert 3: Большой размер архива**
```
Condition: WHEN sum() OF query(A, 1h, now) IS ABOVE 1000
Message: Archive size exceeded 1GB
```

## 🚀 Интеграция с Notification Channels

### Slack
```bash
# В Grafana UI:
Alerting > Notification channels > New channel
Type: Slack
Webhook URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
Channel: #security-alerts
```

### Email
```bash
Type: Email
Addresses: security-team@company.com
```

### Telegram
```bash
Type: Telegram
Bot API Token: YOUR_BOT_TOKEN
Chat ID: YOUR_CHAT_ID
```

## 📱 Мобильный доступ

Dashboard оптимизирован для просмотра на мобильных устройствах через Grafana Mobile App:

1. Установите Grafana Mobile (iOS/Android)
2. Добавьте сервер: http://your-grafana-url:3000
3. Войдите с вашими credentials
4. Откройте "Security & Data Management Dashboard"

## 🔒 Безопасность

### Рекомендации

1. **Ограничьте доступ к dashboard**
   - Создайте отдельную роль "Security Viewer"
   - Дайте доступ только security team

2. **Используйте HTTPS**
   ```bash
   # В grafana.ini
   [server]
   protocol = https
   cert_file = /path/to/cert.pem
   cert_key = /path/to/key.pem
   ```

3. **Включите аутентификацию**
   ```bash
   # В grafana.ini
   [auth]
   disable_login_form = false

   [auth.anonymous]
   enabled = false
   ```

## 📚 Дополнительные ресурсы

- [Grafana Documentation](https://grafana.com/docs/)
- [PostgreSQL Data Source](https://grafana.com/docs/grafana/latest/datasources/postgres/)
- [Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)
- [Alerting Guide](https://grafana.com/docs/grafana/latest/alerting/)

## 🆘 Troubleshooting

### Dashboard не показывает данные

1. **Проверьте подключение к PostgreSQL**
   ```bash
   # В Grafana UI: Data Sources > PostgreSQL > Save & Test
   ```

2. **Проверьте существование таблиц**
   ```sql
   \dt vault.secrets
   \dt public.audit_logs
   \dt public.archive_catalog
   ```

3. **Проверьте права доступа**
   ```sql
   -- Пользователь должен иметь SELECT права
   GRANT SELECT ON vault.secrets TO postgres;
   GRANT SELECT ON public.audit_logs TO postgres;
   ```

### Slow queries

1. **Добавьте индексы**
   ```sql
   CREATE INDEX IF NOT EXISTS idx_audit_created
     ON public.audit_logs(created_at);

   CREATE INDEX IF NOT EXISTS idx_security_created
     ON public.security_events(created_at);
   ```

2. **Ограничьте временной диапазон**
   - Используйте меньший timerange (Last 24h вместо Last 7d)

### Панели показывают "No Data"

- Проверьте что таблицы содержат данные:
  ```sql
  SELECT COUNT(*) FROM vault.secrets;
  SELECT COUNT(*) FROM public.audit_logs;
  ```

- Если таблицы пустые, добавьте тестовые данные или дождитесь реальных событий

---

**Status**: ✅ Ready to use
**Version**: 1.0.0
**Last Updated**: 2025-10-11
