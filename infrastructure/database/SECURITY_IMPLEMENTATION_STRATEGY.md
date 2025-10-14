# 🔒 СТРАТЕГИЯ ВНЕДРЕНИЯ БЕЗОПАСНОСТИ
## Security Implementation Strategy

**Дата**: 2025-10-11
**Проект**: AI-Platform-ISO v2.0 (BCM ISO 22301)
**Статус**: Action Plan Ready

---

## 📋 EXECUTIVE SUMMARY

**Текущая ситуация**:
- 🔴 **CRITICAL**: Credentials хранятся в `.env` файлах (plaintext)
- 🔴 **CRITICAL**: Service Role Key используется везде (bypass RLS)
- 🔴 **CRITICAL**: JWT_SECRET - дефолтное значение
- 🟢 **GOOD**: RLS отлично настроен (90/100)
- 🟢 **GOOD**: База данных структурирована правильно

**Приоритет**: Week 1 Critical Fixes (48 hours work)

---

## 🎯 ВЫБОР РЕШЕНИЯ ДЛЯ SECRETS MANAGEMENT

### Сравнительная таблица

| Критерий | Supabase Vault | HashiCorp Vault | AWS Secrets Manager | Azure Key Vault |
|----------|---------------|-----------------|---------------------|-----------------|
| **Стоимость** | ✅ Бесплатно (включено) | 🟡 $0 (self-hosted) | 🔴 ~$0.40/secret/month | 🔴 ~$0.03/10k ops |
| **Скорость внедрения** | ✅ 2-4 часа | 🟡 8-12 часов | 🟡 4-6 часов | 🟡 4-6 часов |
| **Сложность** | ✅ Низкая | 🔴 Средняя | 🟡 Низкая | 🟡 Низкая |
| **Vendor lock-in** | 🟡 Supabase only | ✅ Независимый | 🔴 AWS only | 🔴 Azure only |
| **Production-ready** | ✅ Да | ✅ Да | ✅ Да | ✅ Да |
| **Ротация секретов** | 🟡 Ручная | ✅ Автоматическая | ✅ Автоматическая | ✅ Автоматическая |
| **Audit logging** | ✅ Да | ✅ Да | ✅ Да | ✅ Да |
| **Интеграция с БД** | ✅ Нативная | 🟡 Требует настройки | 🟡 Требует настройки | 🟡 Требует настройки |
| **Multi-cloud** | ❌ Нет | ✅ Да | ❌ Нет | ❌ Нет |

### Рекомендация: **Supabase Vault** (Phase 1) + **HashiCorp Vault** (Phase 2)

**Обоснование**:

1. **Phase 1 (Week 1-2): Supabase Vault**
   - ✅ Уже включён в Supabase (не требует установки)
   - ✅ Нулевая стоимость
   - ✅ Быстрая интеграция (2-4 часа)
   - ✅ Нативная работа с PostgreSQL
   - ✅ Решает 80% проблем немедленно

2. **Phase 2 (Month 2-3): Миграция на HashiCorp Vault**
   - ✅ Enterprise-grade решение
   - ✅ Автоматическая ротация
   - ✅ Multi-cloud support
   - ✅ Независимость от vendor
   - 🎯 Для production и compliance требований

---

## 📅 ПЛАН ВНЕДРЕНИЯ (WEEK 1-4)

### 🔴 Week 1: CRITICAL - Supabase Vault Setup

#### **Day 1: Настройка Supabase Vault (4 часа)**

**Шаг 1: Включить Vault extension**
```sql
-- Выполнить в Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vault;

-- Проверить установку
SELECT * FROM pg_extension WHERE extname = 'vault';
```

**Шаг 2: Создать secrets**
```sql
-- Хранить API ключи
SELECT vault.create_secret(
    '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',
    'anthropic-api-key'
);

-- Service Role Key (критично!)
SELECT vault.create_secret(
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwZGtoZGR0Ymhwb3F6emd4Zm5pIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTQwMDgxNSwiZXhwIjoyMDc0OTc2ODE1fQ.TzoQ0fvqXsIO8dS54uxfpGHJsz8MJe5fvo-bLq4Lafk',
    'supabase-service-role-key'
);

-- Redis password
SELECT vault.create_secret(
    'tldJWwUq7lAwOHuCa9pSD7sVfjQFYPYN',
    'redis-password'
);

-- JWT Secret (сгенерировать новый!)
SELECT vault.create_secret(
    '<GENERATE_STRONG_64_BYTE_KEY>',
    'jwt-secret'
);
```

**Шаг 3: Создать функцию доступа**
```sql
-- Helper function для чтения секретов
CREATE OR REPLACE FUNCTION public.get_secret(secret_name TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    secret_value TEXT;
BEGIN
    SELECT decrypted_secret INTO secret_value
    FROM vault.decrypted_secrets
    WHERE name = secret_name;

    RETURN secret_value;
END;
$$;

-- Тестирование
SELECT public.get_secret('anthropic-api-key');
```

**Шаг 4: Настроить Row Level Security для vault**
```sql
-- Только service role может читать секреты
ALTER TABLE vault.secrets ENABLE ROW LEVEL SECURITY;

CREATE POLICY vault_service_role_only ON vault.secrets
    FOR ALL
    USING (auth.role() = 'service_role');
```

#### **Day 2: Рефакторинг сервисов (4 часа)**

**Обновить код сервисов:**

```python
# Старый код (УДАЛИТЬ):
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Новый код:
from supabase import create_client
import os

supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Только для Vault access!
supabase = create_client(supabase_url, supabase_service_key)

def get_secret(secret_name: str) -> str:
    """Получить секрет из Supabase Vault"""
    result = supabase.rpc('get_secret', {'secret_name': secret_name}).execute()
    return result.data

# Использование:
ANTHROPIC_API_KEY = get_secret('anthropic-api-key')
REDIS_PASSWORD = get_secret('redis-password')
JWT_SECRET = get_secret('jwt-secret')
```

**Создать централизованный secrets manager:**

```python
# /infrastructure/security/secrets-management/vault_client.py

from supabase import create_client
from functools import lru_cache
import os

class VaultClient:
    """Централизованный клиент для Supabase Vault"""

    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )

    @lru_cache(maxsize=100)
    def get_secret(self, secret_name: str) -> str:
        """Получить секрет с кэшированием"""
        result = self.supabase.rpc(
            'get_secret',
            {'secret_name': secret_name}
        ).execute()

        if not result.data:
            raise ValueError(f"Secret '{secret_name}' not found")

        return result.data

    def rotate_secret(self, secret_name: str, new_value: str):
        """Ротация секрета"""
        # Update в vault
        self.supabase.table('vault.secrets').update({
            'secret': new_value
        }).eq('name', secret_name).execute()

        # Clear cache
        self.get_secret.cache_clear()

# Singleton instance
vault = VaultClient()

# Использование в сервисах:
from infrastructure.security.secrets_management.vault_client import vault

ANTHROPIC_API_KEY = vault.get_secret('anthropic-api-key')
```

#### **Day 3: JWT Secret Rotation (2 часа)**

**Шаг 1: Сгенерировать сильный JWT secret**
```bash
# Генерация криптографически сильного ключа
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Пример результата:
# XhJ9k3LmP4nQ7rS2tU8vW1xY5zA0bC6dE9fG3hI7jK1lM4nO8pQ2rS6tU0vW5xY9zA3bC6dE9fG3hI7jK1lM4nO8pQ2rS6
```

**Шаг 2: Обновить в Vault**
```sql
SELECT vault.create_secret(
    'XhJ9k3LmP4nQ7rS2tU8vW1xY5zA0bC6dE9fG3hI7jK1lM4nO8pQ2rS6tU0vW5xY9zA3bC6dE9fG3hI7jK1lM4nO8pQ2rS6',
    'jwt-secret'
);
```

**Шаг 3: Обновить все сервисы для чтения из Vault**

#### **Day 4-5: Service Role Key Refactoring (12 часов)**

**Проблема**: Service Role Key bypass'ит RLS везде

**Решение**:

```python
# ❌ ПЛОХО (текущий код во многих сервисах):
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# ✅ ХОРОШО (новая архитектура):

# 1. User-facing endpoints - используют ANON key + user JWT
class UserSupabaseClient:
    def __init__(self, user_jwt: str):
        self.client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        self.client.auth.set_session(user_jwt)  # RLS работает!

    def get_processes(self):
        # Автоматически фильтруется по organization_id из JWT
        return self.client.table('bia.processes').select('*').execute()

# 2. Admin/Background jobs - используют Service Role (логируется!)
class AdminSupabaseClient:
    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        self.logger = logging.getLogger("admin_operations")

    def admin_operation(self, operation: str):
        self.logger.warning(f"🔐 SERVICE_ROLE used: {operation}")
        # ... выполнить admin операцию
```

**Обновить все 15 сервисов**:

```bash
# Поиск использований Service Role Key
grep -r "SUPABASE_SERVICE_ROLE_KEY" /Users/MD/AI-Platform-ISO/platform-services/

# Рефакторинг каждого сервиса:
# 1. BIA Service - User endpoints → Anon Key
# 2. Governance Service - User endpoints → Anon Key
# 3. Plans Service - User endpoints → Anon Key
# ... (all 15 services)
```

---

### 🟡 Week 2: HIGH Priority Security

#### **Day 6-7: Audit Logging (8 часов)**

**Создать audit trail для security events:**

```sql
-- Создать audit schema
CREATE SCHEMA IF NOT EXISTS audit;

-- Security events таблица
CREATE TABLE audit.security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(20) NOT NULL,  -- 'auth', 'access', 'admin', 'secret'
    user_id UUID,
    organization_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    severity VARCHAR(10),  -- 'info', 'warning', 'critical'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы для быстрого поиска
CREATE INDEX idx_security_events_type ON audit.security_events(event_type);
CREATE INDEX idx_security_events_user ON audit.security_events(user_id);
CREATE INDEX idx_security_events_created ON audit.security_events(created_at DESC);
CREATE INDEX idx_security_events_severity ON audit.security_events(severity);

-- RLS для audit таблицы
ALTER TABLE audit.security_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_admin_only ON audit.security_events
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');
```

**Middleware для логирования:**

```python
# /infrastructure/security/audit_logger.py

from fastapi import Request
import logging
from datetime import datetime
from supabase import create_client
import os

class SecurityAuditor:
    def __init__(self):
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )

    def log_event(
        self,
        event_type: str,
        category: str,
        severity: str = "info",
        user_id: str = None,
        org_id: str = None,
        ip: str = None,
        user_agent: str = None,
        details: dict = None
    ):
        """Логировать security event"""
        self.supabase.table('audit.security_events').insert({
            'event_type': event_type,
            'event_category': category,
            'severity': severity,
            'user_id': user_id,
            'organization_id': org_id,
            'ip_address': ip,
            'user_agent': user_agent,
            'details': details
        }).execute()

# Middleware для FastAPI
from fastapi import FastAPI, Request

app = FastAPI()
auditor = SecurityAuditor()

@app.middleware("http")
async def security_audit_middleware(request: Request, call_next):
    # Логировать использование Service Role Key
    apikey = request.headers.get("apikey", "")
    if "service_role" in apikey:
        auditor.log_event(
            event_type="service_role_usage",
            category="access",
            severity="warning",
            ip=request.client.host,
            user_agent=request.headers.get("user-agent"),
            details={
                "method": request.method,
                "path": request.url.path
            }
        )

    # Логировать failed auth attempts
    response = await call_next(request)

    if response.status_code == 401:
        auditor.log_event(
            event_type="failed_authentication",
            category="auth",
            severity="warning",
            ip=request.client.host,
            details={"path": request.url.path}
        )

    return response
```

#### **Day 8-9: Connection Limits & SSL (6 часов)**

**Connection pooling по сервисам:**

```python
# Каждый сервис - ограниченный pool
from sqlalchemy import create_engine

# BIA Service
engine = create_engine(
    DATABASE_URL,
    pool_size=5,              # Максимум 5 connections
    max_overflow=5,           # +5 overflow
    pool_pre_ping=True,       # Health check
    pool_recycle=3600         # Recycling каждый час
)

# Monitoring connection usage
from prometheus_client import Gauge

db_connections_gauge = Gauge(
    'db_connections_active',
    'Active database connections',
    ['service']
)

# Update метрика
db_connections_gauge.labels(service='bia-service').set(engine.pool.size())
```

**SSL/TLS enforcement:**

```bash
# Проверить DATABASE_URL
# Должен быть: ?sslmode=require
DATABASE_URL=postgresql://...?sslmode=require

# Для Redis (если удалённый):
REDIS_URL=rediss://:password@host:port  # 's' = SSL
```

---

### 🟢 Week 3-4: MEDIUM Priority

#### **Rate Limiting (4 часа)**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/sensitive")
@limiter.limit("10/minute")  # 10 requests per minute
async def sensitive_endpoint():
    pass
```

#### **Query Monitoring (4 часа)**

```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Monitor slow queries
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 20;
```

#### **Caching (8 часов)**

```python
import redis
from functools import wraps

redis_client = redis.from_url(REDIS_URL)

def cache(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

## 📊 GRAFANA SECURITY DASHBOARD

### Создать dashboard для мониторинга безопасности

**Metrics для отслеживания:**

```yaml
Security Metrics:
  - failed_login_attempts_last_hour
  - failed_login_attempts_last_24h
  - service_role_key_usage_count (by service)
  - jwt_validation_failures
  - rls_policy_violations
  - vault_secret_access_count

Performance Metrics:
  - db_connection_count (current vs max)
  - db_connection_pool_usage_percent
  - slow_queries_count (>1s, >5s, >10s)
  - db_response_time_p50
  - db_response_time_p95
  - db_response_time_p99
  - cache_hit_rate

Database Metrics:
  - db_size_mb
  - table_size_top10
  - index_usage_stats
  - vacuum_last_run
  - bloat_percentage
```

**Alerts:**

```yaml
Critical Alerts:
  - 🚨 > 10 failed logins in 5 minutes
  - 🚨 Service Role Key usage outside business hours (9-18 UTC)
  - 🚨 DB connections > 80% capacity (48/60)
  - 🚨 Vault secret access failure
  - 🚨 RLS policy violation detected

Warning Alerts:
  - ⚠️ > 100 slow queries (>1s) per hour
  - ⚠️ DB connections > 60% capacity
  - ⚠️ Cache hit rate < 80%
  - ⚠️ JWT validation failures > 10/hour
```

**Grafana Dashboard JSON:**

```json
{
  "dashboard": {
    "title": "Security & Performance Dashboard",
    "panels": [
      {
        "id": 1,
        "title": "Failed Login Attempts (Last 24h)",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "sum(security_events_total{event_type=\"failed_authentication\"})"
          }
        ]
      },
      {
        "id": 2,
        "title": "Service Role Key Usage",
        "type": "table",
        "datasource": "PostgreSQL",
        "rawSql": "SELECT event_type, COUNT(*) as count, details->>'path' as endpoint FROM audit.security_events WHERE event_type = 'service_role_usage' AND created_at > NOW() - INTERVAL '24 hours' GROUP BY event_type, endpoint ORDER BY count DESC"
      },
      {
        "id": 3,
        "title": "Database Connections",
        "type": "gauge",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends{datname=\"postgres\"}"
          }
        ],
        "thresholds": [
          {"value": 48, "color": "yellow"},
          {"value": 54, "color": "red"}
        ]
      },
      {
        "id": 4,
        "title": "Slow Queries (>1s)",
        "type": "graph",
        "datasource": "PostgreSQL",
        "rawSql": "SELECT DATE_TRUNC('hour', NOW() - INTERVAL '24 hours') + INTERVAL '1 hour' * generate_series(0, 23) as time, COALESCE(COUNT(*), 0) as count FROM pg_stat_statements WHERE mean_exec_time > 1000 GROUP BY time ORDER BY time"
      }
    ]
  }
}
```

---

## 🔄 PHASE 2: HASHICORP VAULT (Month 2-3)

### Когда переходить на HashiCorp Vault?

**Критерии для миграции:**

1. ✅ > 100 secrets в системе
2. ✅ Требуется автоматическая ротация
3. ✅ Multi-cloud deployment
4. ✅ Compliance требования (SOC 2, ISO 27001)
5. ✅ > 10 микросервисов

### План миграции

#### **Шаг 1: Установка Vault (4 часа)**

```bash
# Docker deployment
docker run -d \
  --name vault \
  -p 8200:8200 \
  -v /vault/data:/vault/data \
  -v /vault/config:/vault/config \
  --cap-add=IPC_LOCK \
  vault:latest server
```

**Vault config:**

```hcl
# /vault/config/vault.hcl

storage "postgresql" {
  connection_url = "postgres://vault:password@postgres:5432/vault?sslmode=require"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 0
  tls_cert_file = "/vault/tls/vault.crt"
  tls_key_file  = "/vault/tls/vault.key"
}

api_addr = "https://vault.bcm-platform.com:8200"
cluster_addr = "https://vault.bcm-platform.com:8201"

ui = true

# Auto unseal (AWS KMS)
seal "awskms" {
  region     = "eu-west-1"
  kms_key_id = "arn:aws:kms:eu-west-1:123456789:key/vault-unseal"
}
```

#### **Шаг 2: Миграция секретов (8 часов)**

```bash
# Export from Supabase Vault
psql $DATABASE_URL -c "SELECT name, decrypted_secret FROM vault.decrypted_secrets;" -t -A -F"," > secrets_export.csv

# Import to HashiCorp Vault
while IFS=',' read -r name secret; do
  vault kv put secret/$name value="$secret"
done < secrets_export.csv

# Verify
vault kv list secret/
```

#### **Шаг 3: Обновить код (12 часов)**

```python
# /infrastructure/security/vault_client.py

import hvac

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url='https://vault.bcm-platform.com:8200',
            token=os.getenv('VAULT_TOKEN')
        )

    def get_secret(self, secret_path: str) -> str:
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=secret_path
        )
        return secret['data']['data']['value']

    def rotate_secret(self, secret_path: str, new_value: str):
        self.client.secrets.kv.v2.create_or_update_secret(
            path=secret_path,
            secret={'value': new_value}
        )

# Использование
vault = VaultClient()
ANTHROPIC_API_KEY = vault.get_secret('anthropic-api-key')
```

#### **Шаг 4: Автоматическая ротация (8 часов)**

```python
# Celery task для автоматической ротации

from celery import Celery
from celery.schedules import crontab

app = Celery('security')

@app.task
def rotate_jwt_secret():
    """Ротация JWT secret каждые 90 дней"""
    import secrets
    new_secret = secrets.token_urlsafe(64)

    vault = VaultClient()
    vault.rotate_secret('jwt-secret', new_secret)

    # Notify team
    send_notification("JWT secret rotated successfully")

# Schedule
app.conf.beat_schedule = {
    'rotate-jwt-secret': {
        'task': 'rotate_jwt_secret',
        'schedule': crontab(day_of_month='1', hour='3')  # 1st day, 3 AM
    }
}
```

---

## ✅ PRODUCTION READINESS CHECKLIST

### Security

```bash
□ Secrets в Vault (не в .env)
□ JWT_SECRET - сильный и уникальный (64+ bytes)
□ Service Role Key - ограниченное использование
□ Audit logging активирован
□ Rate limiting настроен
□ SSL/TLS enforcement для всех connections
□ RLS policies протестированы
□ Security incident response plan создан
```

### Performance

```bash
□ Connection pooling настроен (5-10 per service)
□ Slow query monitoring активирован
□ Redis caching для read-heavy операций
□ Index optimization проверен
□ Query explain analysis выполнен
```

### Monitoring

```bash
□ Grafana Security Dashboard создан
□ Prometheus metrics экспортируются
□ Alerts настроены (PagerDuty/Slack)
□ Log aggregation (ELK/Loki)
□ APM tracing (Jaeger)
```

### Compliance (ISO 22301)

```bash
□ Backup & recovery протестирован
□ Audit trail для всех critical operations
□ Incident response plan документирован
□ Security training для команды проведён
□ Penetration testing выполнен
```

---

## 📈 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

### Week 1 (Supabase Vault)

**Улучшения безопасности:**
- ✅ 0% credentials в plaintext
- ✅ 100% secrets в Vault
- ✅ Service Role Key usage сократится на 80%
- ✅ JWT secret - криптографически сильный

**Metrics:**
- Security Score: 30/100 → 75/100 (+150%)
- Time to compromise: <1 day → >30 days
- Audit coverage: 0% → 80%

### Week 2-4 (Полная реализация)

**Улучшения безопасности:**
- ✅ Audit logging для всех операций
- ✅ Connection limits предотвращают DoS
- ✅ SSL/TLS enforcement
- ✅ Rate limiting защита

**Metrics:**
- Security Score: 75/100 → 90/100
- Incident detection time: N/A → <5 minutes
- MTTR (Mean Time To Recovery): N/A → <30 minutes

### Month 2-3 (HashiCorp Vault)

**Enterprise-grade security:**
- ✅ Автоматическая ротация секретов
- ✅ Multi-cloud support
- ✅ Zero-downtime secret updates
- ✅ Compliance-ready (SOC 2, ISO 27001)

**Metrics:**
- Security Score: 90/100 → 95/100
- Secrets rotation: Manual → Automated (90 days)
- Vendor lock-in: High → Zero

---

## 💰 COST ANALYSIS

### Supabase Vault (Phase 1)

```
Cost: $0 (included in Supabase plan)
Time: 22 hours (Week 1)
ROI: Immediate security improvement
```

### HashiCorp Vault (Phase 2 - Self-hosted)

```
Infrastructure cost: ~$50/month (AWS EC2 t3.medium)
Time: 32 hours (Month 2-3)
ROI: Enterprise compliance + automation
```

### Alternative: AWS Secrets Manager

```
Cost: ~$0.40/secret/month × 50 secrets = $20/month
API calls: ~$0.05/10k calls × 1M calls = $5/month
Total: ~$25/month
```

**Рекомендация**: Supabase Vault (Phase 1) → HashiCorp Vault (Phase 2) - лучший баланс cost/benefit.

---

## 🎓 ОБУЧЕНИЕ КОМАНДЫ

### Week 1: Security Training (4 часа)

**Topics:**
1. Почему secrets в .env - плохо
2. Как работает Vault
3. Service Role vs Anon Key
4. RLS best practices
5. Incident response

**Materials:**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Supabase Security Best Practices](https://supabase.com/docs/guides/platform/going-into-prod)
- Internal: `/docs/SECURITY_IMPLEMENTATION_STRATEGY.md`

---

## 📞 SUPPORT & ESCALATION

### Security Incidents

**Level 1 - Low** (Response: 24h)
- Minor security warnings
- Failed logins < 10/hour
- Slow queries

**Level 2 - Medium** (Response: 4h)
- Service Role Key usage spike
- RLS policy violations
- Connection pool > 80%

**Level 3 - High** (Response: 1h)
- Vault access failure
- DB credentials leak suspicion
- DDoS attack

**Level 4 - Critical** (Response: 15min)
- Confirmed credentials leak
- Database breach
- System-wide compromise

**Escalation contacts:**
- Security Lead: [TBD]
- Database Admin: [TBD]
- DevOps Lead: [TBD]

---

## 📚 REFERENCES

### Documentation

- [Supabase Vault Official Docs](https://supabase.com/docs/guides/database/vault)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [ISO 22301 Security Requirements](https://www.iso.org/standard/75106.html)

### Internal Docs

- [SECURITY_AUDIT_EXECUTIVE_SUMMARY_RU.md](/Users/MD/AI-Platform-ISO/SECURITY_AUDIT_EXECUTIVE_SUMMARY_RU.md)
- [SECURITY_PERFORMANCE_DATABASE_AUDIT.md](/Users/MD/AI-Platform-ISO/SECURITY_PERFORMANCE_DATABASE_AUDIT.md)
- [DATABASE_SETUP_GUIDE.md](/Users/MD/AI-Platform-ISO/infrastructure/database/DATABASE_SETUP_GUIDE.md)

---

## ✍️ CHANGELOG

**2025-10-11**: Initial strategy document created
- Сравнительный анализ Vault решений
- Week 1-4 implementation plan
- Grafana dashboard specifications
- Phase 2 migration guide

---

**Документ создан**: 2025-10-11
**Статус**: ✅ Ready for Implementation
**Следующий шаг**: Week 1 Day 1 - Настройка Supabase Vault

---

**END OF STRATEGY DOCUMENT**
