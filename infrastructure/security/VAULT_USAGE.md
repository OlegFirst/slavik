# Supabase Vault - Управление Секретами

Руководство по использованию Supabase Vault для безопасного хранения секретов в AI-Platform-ISO.

## Обзор

**Supabase Vault** - зашифрованное хранилище секретов, встроенное в PostgreSQL. Заменяет хранение секретов в `.env` файлах и environment переменных.

**Преимущества:**
- ✅ Шифрование AES-256 на уровне БД
- ✅ Централизованное управление
- ✅ Audit trail (кто и когда создал/обновил секрет)
- ✅ Нет риска случайно закоммитить в Git
- ✅ Автоматическая интеграция с Python сервисами

## Созданные Секреты

| Секрет | Описание | Статус |
|--------|----------|--------|
| `encryption_key` | Мастер-ключ для шифрования PII/health data (AES-256-CBC) | ✅ Настроен |
| `smtp_password` | Пароль для SMTP сервера (email уведомления) | ⚠️ Placeholder |
| `slack_webhook_url` | Slack webhook URL для уведомлений | ⚠️ Placeholder |
| `pagerduty_api_key` | PagerDuty API key для критических эскалаций | ⚠️ Placeholder |
| `jwt-secret` | JWT signing secret | ✅ Настроен |
| `anthropic-api-key` | Claude API key | ✅ Настроен |
| `redis-password` | Upstash Redis password | ✅ Настроен |
| `database-password` | PostgreSQL password | ✅ Настроен |

## SQL - Управление Секретами

### Создать Секрет

```sql
-- Создать новый секрет
SELECT vault.create_secret(
    'your-secret-value-here',           -- значение секрета
    'secret_name',                       -- имя секрета (уникальное)
    'Description of what this secret is' -- описание
) AS secret_id;

-- Пример: создать Slack webhook
SELECT vault.create_secret(
    'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    'slack_webhook_url',
    'Slack webhook URL for governance notifications'
);
```

### Обновить Секрет

```sql
-- Обновить существующий секрет
SELECT vault.update_secret(
    '974026dc-79d9-4ca2-8111-ce10319ae2de'::uuid,  -- secret_id (UUID)
    'new-secret-value',                             -- новое значение
    NULL,                                           -- оставить имя без изменений
    NULL                                            -- оставить описание без изменений
);

-- Пример: обновить SMTP password
SELECT vault.update_secret(
    (SELECT id FROM vault.secrets WHERE name = 'smtp_password'),
    'your-real-smtp-password-here'
);
```

### Прочитать Секрет (Расшифрованный)

```sql
-- Прочитать расшифрованный секрет
SELECT
    id,
    name,
    decrypted_secret,
    description
FROM vault.decrypted_secrets
WHERE name = 'encryption_key';

-- ⚠️ ВНИМАНИЕ: decrypted_secret содержит реальное значение!
-- Используй только в защищенной среде (psql, не логируй!)
```

### Список Всех Секретов (Без Значений)

```sql
-- Список секретов (значения зашифрованы)
SELECT
    id,
    name,
    description,
    created_at,
    updated_at
FROM vault.secrets
ORDER BY created_at DESC;
```

### Удалить Секрет

```sql
-- Удалить секрет (осторожно!)
DELETE FROM vault.secrets
WHERE name = 'old_secret_name';
```

## Python - Использование Vault

### Базовое Использование

```python
from infrastructure.security import get_vault_client

# Получить Vault client (singleton)
vault = get_vault_client()

# Прочитать секрет
encryption_key = vault.get_secret('encryption_key')
smtp_password = vault.get_secret('smtp_password')

# Прочитать с fallback на env переменную
slack_webhook = vault.get_secret_with_fallback(
    'slack_webhook_url',  # имя в Vault
    'SLACK_WEBHOOK_URL',  # env переменная
    None                  # default если ничего нет
)

# Список всех секретов
secret_names = vault.list_secrets()
print(f"Available secrets: {secret_names}")
```

### Автоматическая Интеграция

**EncryptionService** и **NotificationService** автоматически используют Vault:

```python
from infrastructure.security import get_encryption_service
from infrastructure.policy_engine.notifications import get_notification_service

# EncryptionService автоматически читает encryption_key из Vault
encryption = get_encryption_service()
encrypted = encryption.encrypt_health_data(patient_data)

# NotificationService автоматически читает smtp_password, slack_webhook, pagerduty_key
notifications = get_notification_service()
notifications.send_approval_request(...)
```

**Приоритет источников:**
1. **Vault** - пытается прочитать из Supabase Vault
2. **Environment** - fallback на env переменную
3. **Error** - если ни Vault ни env не содержат секрет

### Настройка Vault Client

```python
from infrastructure.security.vault_client import SupabaseVaultClient

# Кастомная настройка
vault = SupabaseVaultClient(
    supabase_url='https://your-project.supabase.co',
    service_key='your-service-role-key',
    cache_enabled=True  # кэширование секретов в памяти
)

# Очистить кэш (если секрет обновлен)
vault.clear_cache()
```

## Настройка Environment Переменных

Vault client требует настройки Supabase:

```bash
# .env (для локальной разработки)
SUPABASE_URL=https://tpdkhddtbhpoqzzgxfni.supabase.co
SUPABASE_SERVICE_KEY=<service-role-key>

# Для продакшена - установи через Docker/K8s secrets
```

**⚠️ ВАЖНО:** `SUPABASE_SERVICE_KEY` - это **service role key**, не anon key! Service role key имеет доступ к `vault.decrypted_secrets`.

## Безопасность

### ✅ Best Practices

1. **Используй Vault для всех секретов**
   - Пароли (SMTP, Redis, DB)
   - API ключи (Anthropic, PagerDuty)
   - Webhook URLs (Slack)
   - Encryption keys

2. **Никогда не коммить секреты в Git**
   ```bash
   # .gitignore
   .env
   .env.local
   secrets.json
   ```

3. **Ротация секретов**
   ```sql
   -- Регулярно меняй критичные секреты
   SELECT vault.update_secret(
       (SELECT id FROM vault.secrets WHERE name = 'encryption_key'),
       'new-encryption-key-value'
   );
   ```

4. **Аудит доступа**
   ```sql
   -- Проверяй кто читал секреты (если включен аудит)
   SELECT * FROM vault.secrets ORDER BY updated_at DESC;
   ```

### ❌ Чего НЕ делать

1. ❌ **Не логируй decrypted_secret**
2. ❌ **Не передавай service role key в клиентские приложения**
3. ❌ **Не храни секреты в коде** (`password = "hardcoded"`)
4. ❌ **Не используй placeholder'ы в продакшене**

## Миграция из .env в Vault

### Пошаговая миграция

**Шаг 1:** Создай секрет в Vault
```sql
SELECT vault.create_secret(
    '<значение из .env>',
    'secret_name',
    'Migrated from .env'
);
```

**Шаг 2:** Обнови код чтобы читал из Vault
```python
# До
password = os.getenv('SMTP_PASSWORD')

# После
vault = get_vault_client()
password = vault.get_secret_with_fallback('smtp_password', 'SMTP_PASSWORD')
```

**Шаг 3:** Удали из .env (но оставь в .env.example как документацию)
```bash
# .env.example
# SMTP_PASSWORD=<migrated to Vault>
```

**Шаг 4:** Обнови README с инструкциями для новых разработчиков

### Автоматическая миграция (SQL)

```sql
-- Миграция всех env переменных в Vault (один раз)
DO $$
BEGIN
    -- Пример: мигрируем SMTP_PASSWORD
    IF current_setting('env.SMTP_PASSWORD', true) IS NOT NULL THEN
        PERFORM vault.create_secret(
            current_setting('env.SMTP_PASSWORD'),
            'smtp_password',
            'Migrated from environment variable'
        );
    END IF;
END $$;
```

## Обновление Placeholder'ов

**Замени placeholder секреты на реальные:**

```sql
-- 1. SMTP Password
SELECT vault.update_secret(
    (SELECT id FROM vault.secrets WHERE name = 'smtp_password'),
    '<your-real-smtp-password>'
);

-- 2. Slack Webhook
SELECT vault.update_secret(
    (SELECT id FROM vault.secrets WHERE name = 'slack_webhook_url'),
    'https://hooks.slack.com/services/YOUR/REAL/WEBHOOK'
);

-- 3. PagerDuty API Key
SELECT vault.update_secret(
    (SELECT id FROM vault.secrets WHERE name = 'pagerduty_api_key'),
    '<your-real-pagerduty-api-key>'
);
```

## Troubleshooting

### Проблема: "Vault client not available"

**Причина:** Нет настройки SUPABASE_URL или SUPABASE_SERVICE_KEY

**Решение:**
```bash
export SUPABASE_URL=https://tpdkhddtbhpoqzzgxfni.supabase.co
export SUPABASE_SERVICE_KEY=<service-role-key>
```

### Проблема: "Secret not found in Vault"

**Причина:** Секрет не создан

**Решение:**
```sql
SELECT vault.create_secret('value', 'secret_name', 'description');
```

### Проблема: "Permission denied to read vault.decrypted_secrets"

**Причина:** Используешь anon key вместо service role key

**Решение:** Убедись что `SUPABASE_SERVICE_KEY` - это **service_role** key из Supabase Settings → API.

## Дополнительно

### Ротация Encryption Key

```sql
-- 1. Создай новый ключ
SELECT vault.create_secret(
    '<new-32-byte-key>',
    'encryption_key_v2',
    'New encryption key (v2)'
) AS new_key_id;

-- 2. Обнови все зашифрованные данные (миграция)
-- TODO: скрипт для ре-шифрования всех BYTEA полей

-- 3. Переключись на новый ключ
SELECT vault.update_secret(
    (SELECT id FROM vault.secrets WHERE name = 'encryption_key'),
    (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'encryption_key_v2')
);

-- 4. Удали старый ключ v2
DELETE FROM vault.secrets WHERE name = 'encryption_key_v2';
```

### Backup Секретов

```sql
-- Экспорт секретов (зашифрованных) для backup
COPY (
    SELECT id, name, description, secret, nonce, created_at
    FROM vault.secrets
) TO '/tmp/vault_backup.csv' CSV HEADER;

-- ⚠️ ВНИМАНИЕ: Храни backup в безопасном месте!
```

## Ссылки

- [Supabase Vault Documentation](https://supabase.com/docs/guides/database/vault)
- [PostgreSQL Encryption](https://www.postgresql.org/docs/current/encryption-options.html)
- [Vault Best Practices](https://www.vaultproject.io/docs/internals/security)
