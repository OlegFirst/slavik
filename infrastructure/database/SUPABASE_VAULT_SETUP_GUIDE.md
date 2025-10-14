# 🔐 SUPABASE VAULT - ПОШАГОВАЯ ИНСТРУКЦИЯ
## Step-by-Step Setup Guide

**Дата**: 2025-10-11
**Время выполнения**: 2-4 часа
**Сложность**: Средняя

---

## 📋 ЧТО МЫ БУДЕМ ДЕЛАТЬ

1. ✅ Включить Supabase Vault extension
2. ✅ Мигрировать все секреты из `.env` в Vault
3. ✅ Создать функции доступа к секретам
4. ✅ Настроить Row Level Security для Vault
5. ✅ Обновить код сервисов для чтения из Vault
6. ✅ Протестировать и валидировать

---

## ⚠️ PREREQUISITES (Проверьте перед началом)

```bash
# 1. Доступ к Supabase Dashboard
✅ URL: https://supabase.com/dashboard
✅ Project: tpdkhddtbhpoqzzgxfni

# 2. Текущие credentials (для миграции)
✅ Файл .env существует и заполнен
✅ Backup .env создан

# 3. PostgreSQL доступ
✅ psql установлен
✅ DATABASE_URL работает
```

**Создать backup:**
```bash
cp /Users/MD/AI-Platform-ISO/.env /Users/MD/AI-Platform-ISO/.env.backup.$(date +%Y%m%d)
```

---

## 🚀 ШАГ 1: ВКЛЮЧИТЬ VAULT EXTENSION (15 минут)

### Вариант A: Через Supabase Dashboard (рекомендуется)

1. Открыть [Supabase Dashboard](https://supabase.com/dashboard)
2. Выбрать проект: `tpdkhddtbhpoqzzgxfni`
3. Перейти: **Database** → **Extensions**
4. Найти `vault` в списке
5. Нажать **Enable** (справа от названия)
6. Подтвердить

### Вариант B: Через SQL Editor

1. Перейти: **SQL Editor**
2. Создать новый query
3. Выполнить:

```sql
-- Включить Vault extension
CREATE EXTENSION IF NOT EXISTS vault WITH SCHEMA vault;

-- Проверить установку
SELECT * FROM pg_extension WHERE extname = 'vault';
```

**Ожидаемый результат:**
```
 oid  | extname | extowner | extnamespace | ...
------+---------+----------+--------------+-----
 16502| vault   | 10       | 16501        | ...
```

### Вариант C: Через psql (терминал)

```bash
# Подключиться к БД
psql "postgresql://postgres.tpdkhddtbhpoqzzgxfni:K@x3ta9V8GK5rnW@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"

-- В psql выполнить:
CREATE EXTENSION IF NOT EXISTS vault WITH SCHEMA vault;

-- Проверить
\dx vault
```

---

## 🔒 ШАГ 2: СОЗДАТЬ СЕКРЕТЫ В VAULT (30 минут)

### 2.1 Сгенерировать новый JWT Secret

**ВАЖНО**: Не используйте старый дефолтный JWT_SECRET!

```bash
# Сгенерировать криптографически сильный ключ
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Сохранить результат (пример):
# XhJ9k3LmP4nQ7rS2tU8vW1xY5zA0bC6dE9fG3hI7jK1lM4nO8pQ2rS6tU0vW5xY9zA3
```

### 2.2 Мигрировать секреты в Vault

Откройте **SQL Editor** в Supabase Dashboard и выполните:

```sql
-- 1. Anthropic API Key
SELECT vault.create_secret(
    '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',
    'anthropic-api-key',
    'Anthropic Claude API key for AI services'
);

-- 2. Supabase Service Role Key (критично!)
SELECT vault.create_secret(
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwZGtoZGR0Ymhwb3F6emd4Zm5pIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTQwMDgxNSwiZXhwIjoyMDc0OTc2ODE1fQ.TzoQ0fvqXsIO8dS54uxfpGHJsz8MJe5fvo-bLq4Lafk',
    'supabase-service-role-key',
    'Supabase Service Role Key - ADMIN ACCESS'
);

-- 3. Redis Password
SELECT vault.create_secret(
    'tldJWwUq7lAwOHuCa9pSD7sVfjQFYPYN',
    'redis-password',
    'Upstash Redis password'
);

-- 4. JWT Secret (НОВЫЙ сгенерированный!)
SELECT vault.create_secret(
    'XhJ9k3LmP4nQ7rS2tU8vW1xY5zA0bC6dE9fG3hI7jK1lM4nO8pQ2rS6tU0vW5xY9zA3',
    'jwt-secret',
    'JWT signing secret - STRONG 64 bytes'
);

-- 5. Database Password
SELECT vault.create_secret(
    'K@x3ta9V8GK5rnW',
    'database-password',
    'PostgreSQL password'
);

-- 6. Temporal API Key (если используется)
SELECT vault.create_secret(
    'eyJhbGciOiJFUzI1NiIsImtpZCI6Ild2dHdhQSJ9.eyJhY2NvdW50X2lkIjoicjNneHAiLCJhdWQiOlsidGVtcG9yYWwuaW8iXSwiZXhwIjoxODIyODA3OTE3LCJpc3MiOiJ0ZW1wb3JhbC5pbyIsImp0aSI6IjlPOWR5aUl4T3VweGI0QUZGc2ZNT2REdkduZ1BMeEM2Iiwia2V5X2lkIjoiOU85ZHlpSXhPdXB4YjRBRkZzZk1PZER2R25nUEx4QzYiLCJzdWIiOiIxNjVhM2FkOWRlYzQ0OTc4YTE1MWQ2ZDc4NGM2OTBkYSJ9.zKNZU45ikBOY6CETUH7haMsUWhF55M37eCXN_6Vqz_87RNwr9C_pWEoAkVewr1OEq7YU0kseMqO6X5Di0hiALw',
    'temporal-api-key',
    'Temporal Cloud API key'
);

-- 7. Qdrant API Key
SELECT vault.create_secret(
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwiZXhwIjoxNzYwNjU1NDMyfQ.efuzaW9KZeAZbujOWbX33wzgtCGblTANCIgJXyNcjfw',
    'qdrant-api-key',
    'Qdrant vector database API key'
);

-- 8. Ngrok Auth Token (если используется)
SELECT vault.create_secret(
    '2wbM1vt2feyHnzoluwngV6yw9cN_7zujqcuBJMHWVhuzDGYPS',
    'ngrok-auth-token',
    'Ngrok tunneling auth token'
);
```

### 2.3 Проверить созданные секреты

```sql
-- Посмотреть все секреты (без значений)
SELECT id, name, description, created_at
FROM vault.secrets
ORDER BY created_at DESC;

-- Проверить расшифровку (ТОЛЬКО для тестирования!)
SELECT name, decrypted_secret
FROM vault.decrypted_secrets
WHERE name = 'jwt-secret';
```

**Ожидаемый результат:**
```
        name        |                         decrypted_secret
--------------------+----------------------------------------------------------------
 jwt-secret         | XhJ9k3LmP4nQ7rS2tU8vW1xY5zA0bC6dE9fG3hI7jK1lM4nO8pQ2rS6tU0vW5xY9zA3
```

---

## 🔧 ШАГ 3: СОЗДАТЬ ФУНКЦИИ ДОСТУПА (20 минут)

### 3.1 Функция для чтения секрета

```sql
-- Функция для безопасного чтения секрета
CREATE OR REPLACE FUNCTION public.get_secret(secret_name TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER  -- Выполняется с правами владельца (postgres)
SET search_path = public, vault
AS $$
DECLARE
    secret_value TEXT;
BEGIN
    -- Проверка: только service_role может читать
    IF current_setting('request.jwt.claims', true)::json->>'role' != 'service_role' THEN
        RAISE EXCEPTION 'Only service role can access secrets';
    END IF;

    -- Получить секрет
    SELECT decrypted_secret INTO secret_value
    FROM vault.decrypted_secrets
    WHERE name = secret_name;

    IF secret_value IS NULL THEN
        RAISE EXCEPTION 'Secret % not found', secret_name;
    END IF;

    RETURN secret_value;
END;
$$;

-- Дать права на выполнение
GRANT EXECUTE ON FUNCTION public.get_secret(TEXT) TO service_role;
REVOKE EXECUTE ON FUNCTION public.get_secret(TEXT) FROM anon;
REVOKE EXECUTE ON FUNCTION public.get_secret(TEXT) FROM authenticated;
```

### 3.2 Функция для ротации секрета

```sql
-- Функция для обновления секрета
CREATE OR REPLACE FUNCTION public.rotate_secret(
    secret_name TEXT,
    new_value TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, vault
AS $$
BEGIN
    -- Проверка: только service_role может ротировать
    IF current_setting('request.jwt.claims', true)::json->>'role' != 'service_role' THEN
        RAISE EXCEPTION 'Only service role can rotate secrets';
    END IF;

    -- Обновить секрет
    UPDATE vault.secrets
    SET
        secret = vault.encrypt_secret(new_value),
        updated_at = NOW()
    WHERE name = secret_name;

    -- Логировать ротацию
    INSERT INTO audit.security_events (
        event_type,
        event_category,
        severity,
        details
    ) VALUES (
        'secret_rotated',
        'secret',
        'info',
        jsonb_build_object('secret_name', secret_name)
    );

    RETURN TRUE;
END;
$$;

GRANT EXECUTE ON FUNCTION public.rotate_secret(TEXT, TEXT) TO service_role;
```

### 3.3 Тестирование функций

```sql
-- Тест 1: Прочитать секрет (через service_role)
SELECT public.get_secret('jwt-secret');

-- Тест 2: Ротация секрета
SELECT public.rotate_secret('jwt-secret', 'NEW_STRONG_KEY_HERE');

-- Тест 3: Проверка обновления
SELECT public.get_secret('jwt-secret');
```

---

## 🛡️ ШАГ 4: НАСТРОИТЬ ROW LEVEL SECURITY (15 минут)

### 4.1 Включить RLS для Vault таблиц

```sql
-- Включить RLS на vault.secrets
ALTER TABLE vault.secrets ENABLE ROW LEVEL SECURITY;

-- Политика: только service_role может читать
CREATE POLICY vault_service_role_read ON vault.secrets
    FOR SELECT
    USING (
        current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
    );

-- Политика: только service_role может обновлять
CREATE POLICY vault_service_role_update ON vault.secrets
    FOR UPDATE
    USING (
        current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
    );

-- Политика: только service_role может создавать
CREATE POLICY vault_service_role_insert ON vault.secrets
    FOR INSERT
    WITH CHECK (
        current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
    );

-- Запретить DELETE (секреты только rotate, не delete)
CREATE POLICY vault_no_delete ON vault.secrets
    FOR DELETE
    USING (false);
```

### 4.2 Создать audit таблицу для логирования

```sql
-- Audit schema (если еще не создана)
CREATE SCHEMA IF NOT EXISTS audit;

-- Таблица для security events
CREATE TABLE IF NOT EXISTS audit.security_events (
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

-- Индексы
CREATE INDEX idx_security_events_type ON audit.security_events(event_type);
CREATE INDEX idx_security_events_created ON audit.security_events(created_at DESC);
CREATE INDEX idx_security_events_severity ON audit.security_events(severity);

-- RLS для audit
ALTER TABLE audit.security_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_service_role_only ON audit.security_events
    FOR ALL
    USING (
        current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
    );
```

---

## 💻 ШАГ 5: ОБНОВИТЬ КОД СЕРВИСОВ (60 минут)

### 5.1 Создать централизованный Vault Client

Создать файл: `/Users/MD/AI-Platform-ISO/infrastructure/security/secrets-management/vault_client.py`

```python
"""
Supabase Vault Client
Централизованный клиент для работы с секретами
"""

from supabase import create_client, Client
from functools import lru_cache
import os
import logging

logger = logging.getLogger(__name__)

class SupabaseVaultClient:
    """Клиент для Supabase Vault"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.supabase_url or not self.service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

        self.client: Client = create_client(
            self.supabase_url,
            self.service_role_key
        )

    @lru_cache(maxsize=100)
    def get_secret(self, secret_name: str) -> str:
        """
        Получить секрет из Vault с кэшированием

        Args:
            secret_name: Имя секрета в Vault

        Returns:
            str: Значение секрета

        Raises:
            ValueError: Если секрет не найден
        """
        try:
            result = self.client.rpc(
                'get_secret',
                {'secret_name': secret_name}
            ).execute()

            if not result.data:
                raise ValueError(f"Secret '{secret_name}' not found in Vault")

            logger.info(f"✅ Retrieved secret: {secret_name}")
            return result.data

        except Exception as e:
            logger.error(f"❌ Failed to retrieve secret '{secret_name}': {e}")
            raise

    def rotate_secret(self, secret_name: str, new_value: str) -> bool:
        """
        Ротация секрета

        Args:
            secret_name: Имя секрета
            new_value: Новое значение

        Returns:
            bool: True если успешно
        """
        try:
            result = self.client.rpc(
                'rotate_secret',
                {
                    'secret_name': secret_name,
                    'new_value': new_value
                }
            ).execute()

            # Очистить кэш
            self.get_secret.cache_clear()

            logger.warning(f"🔄 Secret rotated: {secret_name}")
            return bool(result.data)

        except Exception as e:
            logger.error(f"❌ Failed to rotate secret '{secret_name}': {e}")
            raise

    def list_secrets(self) -> list:
        """Получить список всех секретов (без значений)"""
        try:
            result = self.client.table('vault.secrets').select('id, name, description, created_at').execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to list secrets: {e}")
            raise


# Singleton instance
_vault_instance = None

def get_vault_client() -> SupabaseVaultClient:
    """Получить singleton instance Vault client"""
    global _vault_instance
    if _vault_instance is None:
        _vault_instance = SupabaseVaultClient()
    return _vault_instance


# Convenience function
def get_secret(secret_name: str) -> str:
    """Удобная функция для получения секрета"""
    vault = get_vault_client()
    return vault.get_secret(secret_name)
```

### 5.2 Обновить главный `.env` файл

```bash
# Оставить только эти переменные в .env:
SUPABASE_URL=https://tpdkhddtbhpoqzzgxfni.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Остальные секреты - удалить (теперь в Vault)
# ANTHROPIC_API_KEY - УДАЛИТЬ
# REDIS_PASSWORD - УДАЛИТЬ
# JWT_SECRET - УДАЛИТЬ
# и т.д.
```

### 5.3 Обновить сервисы

**Пример: BIA Service**

Файл: `/Users/MD/AI-Platform-ISO/platform-services/bia-service/main.py`

```python
# Старый код (УДАЛИТЬ):
# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# JWT_SECRET = os.getenv("JWT_SECRET")

# Новый код:
from infrastructure.security.secrets_management.vault_client import get_secret

# Читать из Vault
ANTHROPIC_API_KEY = get_secret('anthropic-api-key')
JWT_SECRET = get_secret('jwt-secret')
REDIS_PASSWORD = get_secret('redis-password')

# Использовать как раньше
import anthropic
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
```

**Пример: Все сервисы - массовая замена**

```bash
# Создать скрипт для обновления всех сервисов
cat > /Users/MD/AI-Platform-ISO/update_services_to_vault.sh << 'EOF'
#!/bin/bash

SERVICES=(
    "bia-service"
    "governance-service"
    "compliance-service"
    "plans_service"
    "planning-service"
    "learning-service"
    "response-service"
    "risk-service"
    "validation-service"
    "documents-service"
)

for service in "${SERVICES[@]}"; do
    echo "Updating $service..."

    # Добавить import
    sed -i '' '1i\
from infrastructure.security.secrets_management.vault_client import get_secret
' "/Users/MD/AI-Platform-ISO/platform-services/$service/main.py"

    # Заменить ANTHROPIC_API_KEY
    sed -i '' 's/ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")/ANTHROPIC_API_KEY = get_secret("anthropic-api-key")/' "/Users/MD/AI-Platform-ISO/platform-services/$service/main.py"

    # Заменить JWT_SECRET
    sed -i '' 's/JWT_SECRET = os.getenv("JWT_SECRET")/JWT_SECRET = get_secret("jwt-secret")/' "/Users/MD/AI-Platform-ISO/platform-services/$service/main.py"
done

echo "✅ All services updated!"
EOF

chmod +x /Users/MD/AI-Platform-ISO/update_services_to_vault.sh
```

---

## ✅ ШАГ 6: ТЕСТИРОВАНИЕ (30 минут)

### 6.1 Unit тесты

Создать: `/Users/MD/AI-Platform-ISO/infrastructure/security/secrets-management/test_vault_client.py`

```python
import pytest
from vault_client import SupabaseVaultClient, get_secret

def test_get_secret():
    """Тест получения секрета"""
    secret = get_secret('jwt-secret')
    assert secret is not None
    assert len(secret) > 32  # Минимум 32 символа

def test_get_nonexistent_secret():
    """Тест несуществующего секрета"""
    with pytest.raises(ValueError, match="not found"):
        get_secret('nonexistent-secret-12345')

def test_list_secrets():
    """Тест списка секретов"""
    vault = SupabaseVaultClient()
    secrets = vault.list_secrets()
    assert len(secrets) > 0
    assert 'jwt-secret' in [s['name'] for s in secrets]

def test_rotate_secret():
    """Тест ротации секрета"""
    vault = SupabaseVaultClient()

    # Создать тестовый секрет
    vault.client.rpc('create_secret', {
        'secret_value': 'old-value',
        'secret_name': 'test-secret',
        'description': 'Test secret'
    }).execute()

    # Ротировать
    result = vault.rotate_secret('test-secret', 'new-value')
    assert result is True

    # Проверить новое значение
    new_val = vault.get_secret('test-secret')
    assert new_val == 'new-value'
```

### 6.2 Integration тесты

```bash
# Запустить BIA service с Vault
cd /Users/MD/AI-Platform-ISO/platform-services/bia-service
python main.py

# Ожидаемый вывод:
# ✅ Retrieved secret: anthropic-api-key
# ✅ Retrieved secret: jwt-secret
# ✅ BIA Service started on port 8012

# Тест API endpoint
curl http://localhost:8012/health

# Ожидаемый ответ:
# {"status": "healthy", "vault": "connected"}
```

### 6.3 Security тесты

```python
# Тест: Anon key НЕ может читать секреты
from supabase import create_client
import os

supabase_anon = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")  # Anon key!
)

# Это должно вызвать ошибку
try:
    result = supabase_anon.rpc('get_secret', {'secret_name': 'jwt-secret'}).execute()
    print("❌ SECURITY FAIL: Anon can read secrets!")
except Exception as e:
    print("✅ SECURITY OK: Anon cannot read secrets")
```

---

## 📊 ШАГ 7: МОНИТОРИНГ И ВАЛИДАЦИЯ (20 минут)

### 7.1 Проверить логи Vault access

```sql
-- Посмотреть последние 10 обращений к секретам
SELECT
    event_type,
    details->>'secret_name' as secret,
    created_at
FROM audit.security_events
WHERE event_category = 'secret'
ORDER BY created_at DESC
LIMIT 10;
```

### 7.2 Добавить метрики Prometheus

```python
# В каждом сервисе
from prometheus_client import Counter

vault_secret_access_counter = Counter(
    'vault_secret_access_total',
    'Total Vault secret accesses',
    ['secret_name', 'service']
)

# При каждом get_secret():
vault_secret_access_counter.labels(
    secret_name=secret_name,
    service='bia-service'
).inc()
```

### 7.3 Создать health check endpoint

```python
# В main.py каждого сервиса
@app.get("/health")
async def health_check():
    try:
        # Проверить Vault доступ
        test_secret = get_secret('jwt-secret')
        vault_status = "connected" if test_secret else "disconnected"
    except Exception as e:
        vault_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "vault": vault_status,
        "service": "bia-service",
        "timestamp": datetime.now().isoformat()
    }
```

---

## ✅ CHECKLIST - Финальная проверка

```bash
# 1. Vault extension установлен
□ psql -c "SELECT * FROM pg_extension WHERE extname = 'vault';"

# 2. Секреты созданы (минимум 8)
□ psql -c "SELECT COUNT(*) FROM vault.secrets;" # Должно быть >= 8

# 3. Функции доступа работают
□ psql -c "SELECT public.get_secret('jwt-secret');" # Возвращает значение

# 4. RLS настроен
□ psql -c "SELECT COUNT(*) FROM pg_policies WHERE tablename = 'secrets';" # >= 4

# 5. Код обновлён
□ grep -r "get_secret" platform-services/*/main.py # Должны быть результаты

# 6. .env очищен
□ grep -c "ANTHROPIC_API_KEY" .env # Должно быть 0

# 7. Сервисы запускаются
□ python platform-services/bia-service/main.py # Без ошибок

# 8. Health checks работают
□ curl http://localhost:8012/health # {"vault": "connected"}
```

---

## 🚨 TROUBLESHOOTING

### Проблема 1: Vault extension не устанавливается

**Симптом:**
```
ERROR: extension "vault" is not available
```

**Решение:**
```sql
-- Проверить доступные extensions
SELECT * FROM pg_available_extensions WHERE name LIKE '%vault%';

-- Если нет - обратиться в Supabase Support
-- Vault доступен на всех планах, включая Free tier
```

### Проблема 2: Функция get_secret возвращает NULL

**Симптом:**
```
Secret 'jwt-secret' not found
```

**Решение:**
```sql
-- Проверить существование секрета
SELECT name FROM vault.secrets WHERE name = 'jwt-secret';

-- Если нет - создать заново
SELECT vault.create_secret('YOUR_VALUE', 'jwt-secret');
```

### Проблема 3: RLS блокирует доступ

**Симптом:**
```
new row violates row-level security policy
```

**Решение:**
```sql
-- Проверить текущую роль
SELECT current_setting('request.jwt.claims', true)::json->>'role';

-- Должно быть 'service_role'
-- Если нет - используете неправильный ключ
```

### Проблема 4: Кэш не очищается после ротации

**Симптом:**
```python
# После rotate_secret() всё ещё старое значение
```

**Решение:**
```python
from vault_client import get_vault_client

vault = get_vault_client()
vault.get_secret.cache_clear()  # Очистить кэш вручную
```

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Документация

- [Supabase Vault Official Docs](https://supabase.com/docs/guides/database/vault)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Python LRU Cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)

### Полезные SQL запросы

```sql
-- Все секреты с метаданными
SELECT id, name, description, created_at, updated_at
FROM vault.secrets
ORDER BY created_at DESC;

-- Размер Vault
SELECT pg_size_pretty(pg_total_relation_size('vault.secrets'));

-- Audit trail за последние 24 часа
SELECT * FROM audit.security_events
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Топ используемых секретов
SELECT
    details->>'secret_name' as secret,
    COUNT(*) as access_count
FROM audit.security_events
WHERE event_category = 'secret'
GROUP BY secret
ORDER BY access_count DESC;
```

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

После завершения Supabase Vault setup:

1. ✅ **Week 1 Day 4-5**: Service Role Key Refactoring
   - Разделить использование Service Role vs Anon Key
   - Добавить audit logging

2. ✅ **Week 2**: Audit Logging & Monitoring
   - Настроить Grafana dashboard
   - Alerts для security events

3. ✅ **Month 2-3**: Миграция на HashiCorp Vault (опционально)
   - Для enterprise требований
   - Автоматическая ротация

---

**Дата создания**: 2025-10-11
**Статус**: ✅ Ready to Execute
**Время выполнения**: 2-4 часа
**Следующий документ**: [SECURITY_IMPLEMENTATION_STRATEGY.md](/Users/MD/AI-Platform-ISO/SECURITY_IMPLEMENTATION_STRATEGY.md)

---

**END OF GUIDE**
