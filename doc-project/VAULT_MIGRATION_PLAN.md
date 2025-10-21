# Vault Migration Plan - Полная Миграция Секретов

## Текущий Статус

### ✅ Уже в Supabase Vault (8 секретов)

| Секрет | Описание | Статус |
|--------|----------|--------|
| `encryption_key` | Master encryption key (AES-256-CBC) | ✅ PRODUCTION KEY |
| `jwt-secret` | JWT signing secret | ✅ Настроен |
| `anthropic-api-key` | Claude API key | ✅ Настроен |
| `redis-password` | Upstash Redis password | ✅ Настроен |
| `database-password` | PostgreSQL password | ✅ Настроен |
| `smtp_password` | SMTP password для email | ⚠️ PLACEHOLDER - заменить! |
| `slack_webhook_url` | Slack webhook URL | ⚠️ PLACEHOLDER - заменить! |
| `pagerduty_api_key` | PagerDuty API key | ⚠️ PLACEHOLDER - заменить! |

### ❌ НЕ В VAULT - Нужно Мигрировать (12 секретов)

**Высокий приоритет (критичные):**
1. `OPENAI_API_KEY` - OpenAI API key (если используется как fallback)
2. `RABBITMQ_PASSWORD` - RabbitMQ password
3. `VAULT_TOKEN` - HashiCorp Vault token (если используется)
4. `TEMPORAL_API_KEY` - Temporal Cloud API key

**Средний приоритет (интеграции):**
5. `TWILIO_AUTH_TOKEN` - SMS уведомления через Twilio
6. `BCM_API_KEY` - External BCM API
7. `KEYCLOAK_CLIENT_SECRET` - SSO (Keycloak)
8. `QDRANT_API_KEY` - Vector DB API key

**Низкий приоритет (инфраструктура):**
9. `GRAFANA_ADMIN_PASSWORD` - Grafana admin
10. `S3_ACCESS_KEY` - S3/Object storage access key
11. `S3_SECRET_KEY` - S3/Object storage secret key
12. `GITHUB_APP_ID` - GitHub integration (если используется)

## План Миграции

### Фаза 1: Обновить Placeholders (СРОЧНО)

Замени placeholder секреты на реальные значения:

```sql
-- 1. SMTP Password
PGPASSWORD='K@x3ta9V8GK5rnW' psql -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.tpdkhddtbhpoqzzgxfni -d postgres -p 5432 << 'EOF'
SELECT vault.update_secret(
    (SELECT id FROM vault.secrets WHERE name = 'smtp_password'),
    '<твой-реальный-smtp-пароль>'
);
EOF

-- 2. Slack Webhook
PGPASSWORD='K@x3ta9V8GK5rnW' psql -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.tpdkhddtbhpoqzzgxfni -d postgres -p 5432 << 'EOF'
SELECT vault.update_secret(
    (SELECT id FROM vault.secrets WHERE name = 'slack_webhook_url'),
    'https://hooks.slack.com/services/YOUR/REAL/WEBHOOK'
);
EOF

-- 3. PagerDuty API Key
PGPASSWORD='K@x3ta9V8GK5rnW' psql -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.tpdkhddtbhpoqzzgxfni -d postgres -p 5432 << 'EOF'
SELECT vault.update_secret(
    (SELECT id FROM vault.secrets WHERE name = 'pagerduty_api_key'),
    '<твой-pagerduty-api-key>'
);
EOF
```

### Фаза 2: Мигрировать Критичные Секреты

```sql
-- OpenAI API Key (если используется)
SELECT vault.create_secret(
    '<твой-openai-api-key>',
    'openai_api_key',
    'OpenAI API key for fallback LLM'
);

-- RabbitMQ Password
SELECT vault.create_secret(
    '<rabbitmq-password>',
    'rabbitmq_password',
    'RabbitMQ message queue password'
);

-- Temporal Cloud API Key
SELECT vault.create_secret(
    '<temporal-api-key>',
    'temporal_api_key',
    'Temporal Cloud API key for workflow engine'
);

-- HashiCorp Vault Token (если используется)
SELECT vault.create_secret(
    '<vault-token>',
    'vault_token',
    'HashiCorp Vault access token'
);
```

### Фаза 3: Мигрировать Интеграции

```sql
-- Twilio (SMS)
SELECT vault.create_secret(
    '<twilio-auth-token>',
    'twilio_auth_token',
    'Twilio SMS service auth token'
);

-- Qdrant (Vector DB)
SELECT vault.create_secret(
    '<qdrant-api-key>',
    'qdrant_api_key',
    'Qdrant vector database API key'
);

-- Keycloak (SSO)
SELECT vault.create_secret(
    '<keycloak-client-secret>',
    'keycloak_client_secret',
    'Keycloak SSO client secret'
);

-- BCM External API
SELECT vault.create_secret(
    '<bcm-api-key>',
    'bcm_api_key',
    'External BCM API key'
);
```

### Фаза 4: Мигрировать Инфраструктуру

```sql
-- Grafana Admin
SELECT vault.create_secret(
    '<grafana-admin-password>',
    'grafana_admin_password',
    'Grafana admin panel password'
);

-- S3 Storage
SELECT vault.create_secret(
    '<s3-access-key>',
    's3_access_key',
    'S3/Object storage access key'
);

SELECT vault.create_secret(
    '<s3-secret-key>',
    's3_secret_key',
    'S3/Object storage secret key'
);
```

### Фаза 5: Обновить Код для Чтения из Vault

После миграции секрета в Vault, обнови код:

**До:**
```python
openai_api_key = os.getenv('OPENAI_API_KEY')
```

**После:**
```python
from infrastructure.security import get_vault_client

vault = get_vault_client()
openai_api_key = vault.get_secret_with_fallback(
    'openai_api_key',  # имя в Vault
    'OPENAI_API_KEY',  # fallback на env
    None               # default
)
```

### Фаза 6: Удалить из .env Файлов

```bash
# После миграции в Vault - удали секреты из .env
# НО ОСТАВЬ в .env.example для документации

# .env.example
OPENAI_API_KEY=<from-vault:openai_api_key>  # Migrated to Vault

# .env (локальный - удали полностью или закомментируй)
# OPENAI_API_KEY=sk-... # ❌ DELETED - now in Vault
```

## Проверка После Миграции

### 1. Проверить что секрет в Vault

```sql
SELECT
    name,
    description,
    created_at,
    updated_at
FROM vault.secrets
WHERE name = 'openai_api_key';
```

### 2. Проверить что код читает из Vault

```python
from infrastructure.security import get_secret

# Должен вернуть секрет без ошибки
openai_key = get_secret('openai_api_key')
print(f"Key loaded: {openai_key[:10]}...")  # Первые 10 символов
```

### 3. Проверить fallback на env

```bash
# Временно отключи Vault (удали SUPABASE_SERVICE_KEY)
unset SUPABASE_SERVICE_KEY

# Установи env переменную
export OPENAI_API_KEY=test-key

# Запусти код - должен упасть на Vault, взять из env
python test_vault.py
```

## График Миграции

| Фаза | Описание | Срок | Ответственный |
|------|----------|------|---------------|
| ✅ 0 | Настройка Vault, encryption_key | ГОТОВО | Claude |
| ⚠️ 1 | Обновить placeholders (smtp, slack, pagerduty) | **Сегодня** | Ты |
| 2 | Критичные секреты (openai, rabbitmq, temporal) | 1-2 дня | Ты |
| 3 | Интеграции (twilio, qdrant, keycloak) | 3-5 дней | Ты |
| 4 | Инфраструктура (grafana, s3) | 5-7 дней | Ты |
| 5 | Обновить код для всех секретов | 7-10 дней | Claude + Ты |
| 6 | Удалить из .env, проверка | 10-14 дней | Ты |

## Rollback План

Если что-то пошло не так:

1. **Vault недоступен** - код автоматически использует env fallback
2. **Неправильный секрет** - обнови через `vault.update_secret()`
3. **Код сломался** - временно верни env переменную

```bash
# Emergency rollback - верни секрет в .env
export OPENAI_API_KEY=<backup-key>
```

## Безопасность После Миграции

### ✅ DO

- Регулярно ротируй encryption_key (каждые 90 дней)
- Аудит логов Vault (`vault.secrets` updated_at)
- Backup Vault секретов (зашифрованный export)
- Используй разные ключи для dev/staging/prod

### ❌ DON'T

- Не коммить `.env` с реальными секретами
- Не логировать `decrypted_secret` из Vault
- Не давать `service_role` key в frontend
- Не хранить Vault backups рядом с кодом

## Мониторинг

Проверяй здоровье Vault:

```sql
-- Сколько секретов в Vault
SELECT COUNT(*) FROM vault.secrets;

-- Последние изменения
SELECT
    name,
    description,
    updated_at
FROM vault.secrets
ORDER BY updated_at DESC
LIMIT 10;

-- Секреты без обновлений >90 дней (нужна ротация)
SELECT
    name,
    description,
    created_at,
    updated_at
FROM vault.secrets
WHERE updated_at < NOW() - INTERVAL '90 days'
   OR (updated_at IS NULL AND created_at < NOW() - INTERVAL '90 days');
```

## Следующие Шаги

**Сегодня:**
1. ✅ Обнови `smtp_password` в Vault
2. ✅ Обнови `slack_webhook_url` в Vault
3. ✅ Обнови `pagerduty_api_key` в Vault

**Эта неделя:**
4. Создай `openai_api_key` в Vault (если используешь OpenAI)
5. Создай `rabbitmq_password` в Vault
6. Создай `temporal_api_key` в Vault

**Следующая неделя:**
7. Мигрируй остальные интеграции (twilio, qdrant, etc)
8. Обнови код для чтения всех секретов из Vault
9. Удали секреты из .env файлов
10. Проведи security audit

---

**Документация:**
- Vault Usage Guide: `/infrastructure/security/VAULT_USAGE.md`
- Comprehensive ENV List: `/COMPREHENSIVE_.env.example`
- Encryption Guide: `/infrastructure/security/encryption.py`

**Контакты:**
- Vault Issues: Create issue в GitHub
- Security Questions: security@ai-platform-iso.org
