# HashiCorp Vault - Secrets Manager

Безопасное управление секретами, токенами, паролями и шифрованием для BCM Platform.

## 🚀 Возможности

- **KV Secrets** - статичное хранение секретов (пароли, API keys)
- **Dynamic Secrets** - временные credentials для БД
- **Encryption as a Service** - шифрование/расшифрование данных
- **Token Management** - управление access tokens
- **Audit Logging** - логирование всех операций
- **Versioning** - версионирование секретов
- **Auto-renewal** - автопродление leases

## 📦 Установка

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить Vault (Docker)
docker-compose up vault

# Или standalone
docker run -d \
  --name vault \
  -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=root-token \
  hashicorp/vault:1.15 server -dev
```

## 🔧 Использование

### 1. Инициализация

```python
from vault_manager import get_vault_manager

# Получить менеджер (singleton)
vault = get_vault_manager(
    url="http://localhost:8200",
    token="root-token"
)

# Или напрямую
from vault_manager import VaultManager

vault = VaultManager(
    url="http://localhost:8200",
    token="root-token",
    mount_point="secret"  # KV v2 mount point
)
```

### 2. KV Secrets (Статичные секреты)

```python
# Сохранить секрет
vault.write_secret("database/postgres", {
    "host": "localhost",
    "port": 5432,
    "username": "admin",
    "password": "super-secret-password",
    "ssl_mode": "require"
})

# Прочитать секрет
db_config = vault.read_secret("database/postgres")

print(f"DB Host: {db_config['host']}")
print(f"DB Password: {db_config['password']}")

# Прочитать конкретную версию
old_config = vault.read_secret("database/postgres", version=1)

# Список секретов в директории
secrets = vault.list_secrets("database")
# Returns: ["postgres", "mysql", "redis"]

# Удалить секрет (soft delete)
vault.delete_secret("database/old-db", versions=[1, 2])
```

### 3. Encryption as a Service

```python
# Создать ключ шифрования
vault.create_encryption_key(
    name="customer-data-key",
    key_type="aes256-gcm96"
)

# Зашифровать данные
plaintext = "John Doe, SSN: 123-45-6789"
ciphertext = vault.encrypt("customer-data-key", plaintext)

print(f"Encrypted: {ciphertext}")
# Output: vault:v1:8SDd3WHDOj...

# Сохранить в БД
await db.execute(
    "INSERT INTO customers (name, encrypted_data) VALUES ($1, $2)",
    "John Doe", ciphertext
)

# Прочитать из БД и расшифровать
row = await db.fetchrow("SELECT encrypted_data FROM customers WHERE id = $1", 123)
decrypted = vault.decrypt("customer-data-key", row["encrypted_data"])

print(f"Decrypted: {decrypted}")
# Output: John Doe, SSN: 123-45-6789
```

### 4. Dynamic Database Credentials

```python
# 1. Настроить подключение к БД
vault.configure_database(
    name="bcm-postgres",
    plugin_name="postgresql-database-plugin",
    connection_url="postgresql://{{username}}:{{password}}@localhost:5432/bcm_platform",
    allowed_roles=["readonly", "readwrite", "admin"],
    username="vault",
    password="vault-db-password"
)

# 2. Создать роль для readonly доступа
vault.create_database_role(
    name="readonly",
    db_name="bcm-postgres",
    creation_statements=[
        "CREATE USER '{{name}}' WITH PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
        "GRANT CONNECT ON DATABASE bcm_platform TO '{{name}}';",
        "GRANT SELECT ON ALL TABLES IN SCHEMA public TO '{{name}}';"
    ],
    default_ttl="1h",  # Credentials живут 1 час
    max_ttl="24h"      # Максимум 24 часа
)

# 3. Получить временные credentials
creds = vault.get_database_credentials("readonly")

print(f"Username: {creds['username']}")  # v-root-readonly-AbC123...
print(f"Password: {creds['password']}")  # XyZ789...

# 4. Использовать credentials
import asyncpg

conn = await asyncpg.connect(
    host="localhost",
    database="bcm_platform",
    user=creds['username'],
    password=creds['password']
)

# Через 1 час credentials автоматически удалятся из БД!
```

### 5. Token Management

```python
# Создать token для приложения
app_token = vault.create_token(
    policies=["app-read", "app-write"],
    ttl="24h",
    renewable=True,
    metadata={"app": "bcm-platform", "env": "production"}
)

print(f"App Token: {app_token['client_token']}")
print(f"Expires in: {app_token['lease_duration']}s")

# Продлить token
renewed = vault.renew_token(
    token=app_token['client_token'],
    increment="24h"
)

# Отозвать token
vault.revoke_token(app_token['client_token'])
```

## 🎯 Примеры использования в BCM Platform

### 1. Хранение API Keys

```python
# Сохранить API keys для внешних сервисов
vault.write_secret("api-keys/openai", {
    "api_key": "sk-...",
    "organization": "org-..."
})

vault.write_secret("api-keys/anthropic", {
    "api_key": "sk-ant-...",
    "model": "claude-3-5-sonnet-20250929"
})

vault.write_secret("api-keys/supabase", {
    "url": "https://tpdkhddtbhpoqzzgxfni.supabase.co",
    "anon_key": "eyJ...",
    "service_role_key": "eyJ..."
})

# Использовать в приложении
openai_config = vault.read_secret("api-keys/openai")

import openai
openai.api_key = openai_config["api_key"]
```

### 2. Шифрование персональных данных (GDPR)

```python
# Шифровать PII (Personally Identifiable Information)
vault.create_encryption_key("pii-encryption-key")

# При создании пользователя
async def create_user(email: str, phone: str, ssn: str):
    # Шифруем sensitive data
    encrypted_phone = vault.encrypt("pii-encryption-key", phone)
    encrypted_ssn = vault.encrypt("pii-encryption-key", ssn)

    # Сохраняем в БД
    await db.execute(
        "INSERT INTO users (email, encrypted_phone, encrypted_ssn) VALUES ($1, $2, $3)",
        email, encrypted_phone, encrypted_ssn
    )

# При чтении пользователя
async def get_user_info(user_id: int):
    row = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)

    return {
        "email": row["email"],
        "phone": vault.decrypt("pii-encryption-key", row["encrypted_phone"]),
        "ssn": vault.decrypt("pii-encryption-key", row["encrypted_ssn"])
    }
```

### 3. Временные credentials для background jobs

```python
# Background job runner
async def run_data_sync_job():
    # Получить временные credentials
    creds = vault.get_database_credentials("readwrite")

    # Подключиться к БД
    conn = await asyncpg.connect(
        host="localhost",
        database="bcm_platform",
        user=creds['username'],
        password=creds['password']
    )

    # Выполнить sync
    await sync_data(conn)

    # Закрыть подключение
    await conn.close()

    # Credentials автоматически истекут через 1 час
```

### 4. Миграция с .env файлов на Vault

```python
# Миграция секретов из .env в Vault
import os
from dotenv import load_dotenv

load_dotenv()

# Прочитать из .env
secrets = {
    "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    "JWT_SECRET": os.getenv("JWT_SECRET"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY")
}

# Сохранить в Vault
vault.write_secret("bcm-platform/production", secrets)

# Теперь в приложении:
config = vault.read_secret("bcm-platform/production")

DATABASE_URL = f"postgresql://user:{config['POSTGRES_PASSWORD']}@localhost/db"
JWT_SECRET = config['JWT_SECRET']
```

## 🔐 Production Deployment

### 1. Unseal Vault (Production mode)

```bash
# Инициализация Vault (только первый раз!)
vault operator init

# Сохрани 5 unseal keys и root token!

# Unseal (нужно 3 из 5 ключей)
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>
```

### 2. Enable Audit Logging

```bash
vault audit enable file file_path=/vault/logs/audit.log
```

### 3. Create Policies

```hcl
# app-read-policy.hcl
path "secret/data/bcm-platform/*" {
  capabilities = ["read", "list"]
}

path "transit/decrypt/customer-data-key" {
  capabilities = ["update"]
}

# app-write-policy.hcl
path "secret/data/bcm-platform/*" {
  capabilities = ["create", "update", "read", "list"]
}
```

```bash
vault policy write app-read app-read-policy.hcl
vault policy write app-write app-write-policy.hcl
```

### 4. Use AppRole Authentication

```python
# Вместо root token используй AppRole
import hvac

client = hvac.Client(url="https://vault.production.com")

# Authenticate with AppRole
role_id = "..."
secret_id = "..."

client.auth.approle.login(
    role_id=role_id,
    secret_id=secret_id
)

# Теперь client authenticated!
```

## 📊 Мониторинг

```python
# Health check
health = vault.health_check()

print(f"Initialized: {health['initialized']}")
print(f"Sealed: {health['sealed']}")
print(f"Version: {health['version']}")

# Check if sealed
if vault.is_sealed():
    print("⚠️  Vault is sealed! Run 'vault operator unseal'")
```

## 📚 Дополнительно

- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [HVAC Python Client](https://hvac.readthedocs.io/)
- [Vault Best Practices](https://www.vaultproject.io/docs/best-practices)
