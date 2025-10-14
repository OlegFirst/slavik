# 🚀 Grafana Security Dashboard - Quick Start

## Статус: ✅ ВСЁ ГОТОВО

### Что уже сделано:

1. ✅ PostgreSQL datasource добавлен в Grafana provisioning
2. ✅ Security Dashboard скопирован в `/config/grafana/dashboards/bcm-platform/`
3. ✅ Таблицы созданы в БД:
   - `public.security_events` (5 записей)
   - `public.audit_logs` (6 записей)
   - `public.sessions` (3 записи)
   - `vault.secrets` (4 секрета)
4. ✅ docker-compose.grafana.yml создан

---

## 🏃 Запуск (когда Docker работает)

### Шаг 1: Запустить Docker

```bash
# Запустите Docker Desktop или
open -a Docker

# Подождите пока Docker запустится (~30 сек)
docker ps
```

### Шаг 2: Запустить Grafana + Prometheus

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/observability

# Запуск
docker-compose -f docker-compose.grafana.yml up -d

# Проверка
docker-compose -f docker-compose.grafana.yml ps
```

### Шаг 3: Открыть Grafana

```bash
# Откроется автоматически
open http://localhost:3000

# Логин:
# Username: admin
# Password: admin
```

### Шаг 4: Найти Security Dashboard

```
1. После входа в Grafana
2. Перейти в Dashboards (слева)
3. Найти "Security & Data Management Dashboard"
4. Готово! 🎉
```

---

## 📊 Что вы увидите в Dashboard

### Security Metrics (4 панели)
- Total Secrets in Vault: **4**
- Security Events (24h): **5**
- Failed Auth Attempts (24h): **3**
- Active Sessions: **3**

### Archive Metrics (4 панели)
- Total Archives: **0** (создадутся после первой архивации)
- Archive Size: **0 MB**
- Archived Records: **0**
- Recent Archives: *пусто*

### Logs (2 панели)
- Recent Secrets: 4 секрета из Vault
- Recent Security Events: 6 audit log записей

---

## 🧪 Если нужны больше данных

### Добавить больше Security Events

```sql
PGPASSWORD='K@x3ta9V8GK5rnW' psql -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.tpdkhddtbhpoqzzgxfni -d postgres -p 5432 << 'EOF'

INSERT INTO public.security_events (event_type, severity, user_id, ip_address, action, success, metadata)
VALUES
    ('authentication', 'critical', gen_random_uuid(), '10.0.0.50', 'bruteforce_detected', false, '{"attempts": 10}'),
    ('data_access', 'warning', gen_random_uuid(), '10.0.0.51', 'bulk_export', true, '{"records": 1000}'),
    ('configuration', 'critical', gen_random_uuid(), '10.0.0.52', 'security_disabled', true, '{"setting": "firewall"}');

SELECT '✅ Added ' || COUNT(*) || ' new security events' FROM public.security_events;
EOF
```

### Добавить больше Audit Logs

```sql
PGPASSWORD='K@x3ta9V8GK5rnW' psql -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.tpdkhddtbhpoqzzgxfni -d postgres -p 5432 << 'EOF'

INSERT INTO public.audit_logs (request_id, user_id, method, path, status_code, ip_address, metadata)
VALUES
    ('req-101', 'hacker-001', 'POST', '/api/auth/login', 401, '99.99.99.99', '{"error": "invalid_password"}'),
    ('req-102', 'hacker-001', 'POST', '/api/auth/login', 401, '99.99.99.99', '{"error": "invalid_password", "attempt": 2}'),
    ('req-103', 'hacker-001', 'POST', '/api/auth/login', 401, '99.99.99.99', '{"error": "account_locked"}');

SELECT '✅ Added ' || COUNT(*) || ' new audit logs' FROM public.audit_logs WHERE request_id LIKE 'req-1%';
EOF
```

---

## 🔧 Troubleshooting

### Grafana не показывает данные

**Проблема**: Панели пустые или "No Data"

**Решение**:
```bash
# 1. Проверьте что PostgreSQL datasource работает
# В Grafana: Configuration > Data Sources > PostgreSQL > Save & Test

# 2. Проверьте что данные есть
PGPASSWORD='K@x3ta9V8GK5rnW' psql -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.tpdkhddtbhpoqzzgxfni -d postgres -p 5432 -c \
  "SELECT 'vault.secrets' as table, COUNT(*) FROM vault.secrets
   UNION ALL
   SELECT 'security_events', COUNT(*) FROM public.security_events
   UNION ALL
   SELECT 'audit_logs', COUNT(*) FROM public.audit_logs
   UNION ALL
   SELECT 'sessions', COUNT(*) FROM public.sessions;"
```

### Docker not running

```bash
# Запустите Docker Desktop
open -a Docker

# Или через brew services
brew services start docker
```

### Порт 3000 уже занят

```bash
# Найти что использует порт 3000
lsof -i :3000

# Убить процесс
kill -9 <PID>

# Или изменить порт в docker-compose.grafana.yml
# Замените "3000:3000" на "3001:3000"
```

---

## 📈 Следующие шаги

### 1. Настроить Alerts

В Grafana:
1. Откройте панель "Failed Auth Attempts (24h)"
2. Edit > Alert
3. Create Alert
4. Условие: `WHEN count() IS ABOVE 10`
5. Save

### 2. Добавить Notification Channels

```
Alerting > Notification channels > New channel

Slack:
  - Type: Slack
  - Webhook URL: https://hooks.slack.com/services/YOUR/WEBHOOK
  - Channel: #security-alerts

Email:
  - Type: Email
  - Addresses: security@company.com
```

### 3. Протестировать Archive & Partitioning

```bash
# Archive API
curl http://localhost:8050/archive/stats

# Partitioning API
curl http://localhost:8050/partitioning/status

# Retention API
curl http://localhost:8050/retention/status
```

---

## 🎯 Готовые команды

### Проверить всё работает
```bash
# Grafana
curl -s http://localhost:3000/api/health

# Prometheus
curl -s http://localhost:9090/-/healthy

# PostgreSQL
PGPASSWORD='K@x3ta9V8GK5rnW' psql -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.tpdkhddtbhpoqzzgxfni -d postgres -p 5432 \
  -c "SELECT COUNT(*) FROM vault.secrets;"
```

### Остановить Grafana
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/observability
docker-compose -f docker-compose.grafana.yml down
```

### Перезапустить Grafana
```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/observability
docker-compose -f docker-compose.grafana.yml restart
```

---

## ✅ Checklist

- [x] PostgreSQL datasource настроен
- [x] Security Dashboard готов
- [x] Таблицы созданы
- [x] Тестовые данные добавлены
- [ ] Docker запущен
- [ ] Grafana запущена
- [ ] Dashboard импортирован
- [ ] Alerts настроены

---

**Когда запустите Docker - просто выполните команды из "Шаг 2" и всё заработает!** 🚀
