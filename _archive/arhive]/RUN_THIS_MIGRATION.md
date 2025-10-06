# 🚀 Быстрая Миграция - Создание Users Table

## Шаг 1: Открыть Supabase Dashboard

1. Открыть: **https://supabase.com/dashboard/project/tpdkhddtbhpoqzzgxfni**
2. Залогиниться если нужно
3. Слева в меню выбрать **SQL Editor**

## Шаг 2: Создать New Query

1. Нажать кнопку **"New query"**
2. Скопировать ВЕСЬ SQL код ниже
3. Вставить в SQL Editor
4. Нажать **Run** (или Ctrl+Enter)

## Шаг 3: SQL Migration Code

```sql
-- ============================================================================
-- Users Table for JWT Authentication
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS auth;

-- ============================================================================
-- USERS TABLE
-- ============================================================================

CREATE TABLE auth.users (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Tenant isolation
    tenant_id VARCHAR(255) NOT NULL,

    -- User identity
    user_id VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,

    -- Authentication
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    -- Profile
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    display_name VARCHAR(200),
    avatar_url TEXT,

    -- Roles (JSON array)
    roles JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- Permissions
    permissions JSONB DEFAULT '[]'::jsonb,

    -- Department/Organization
    department VARCHAR(100),
    job_title VARCHAR(100),
    manager_id VARCHAR(255),

    -- Security
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(50),
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,

    -- Password management
    password_changed_at TIMESTAMP,
    must_change_password BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255),
    deleted_at TIMESTAMP,

    -- Constraints
    CONSTRAINT users_email_unique UNIQUE (tenant_id, email),
    CONSTRAINT users_username_unique UNIQUE (tenant_id, username)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_users_tenant_id ON auth.users(tenant_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_user_id ON auth.users(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_username ON auth.users(tenant_id, username) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_email ON auth.users(tenant_id, email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_roles ON auth.users USING GIN(roles);
CREATE INDEX idx_users_active ON auth.users(tenant_id, is_active) WHERE deleted_at IS NULL;

-- ============================================================================
-- TRIGGER FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION auth.update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION auth.update_users_updated_at();

-- ============================================================================
-- SEED DATA - Demo Users
-- ALL PASSWORDS: "admin123"
-- ============================================================================

INSERT INTO auth.users (
    tenant_id,
    user_id,
    username,
    email,
    password_hash,
    is_active,
    is_verified,
    first_name,
    last_name,
    display_name,
    roles,
    department,
    job_title
) VALUES
-- Admin user
(
    'tenant_001',
    'admin_user_001',
    'admin',
    'admin@bcm-platform.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztWZdR0RZN8O',
    TRUE,
    TRUE,
    'System',
    'Administrator',
    'Admin User',
    '["admin", "bcm_manager"]'::jsonb,
    'IT',
    'System Administrator'
),
-- Manager user
(
    'tenant_001',
    'manager_user_001',
    'manager',
    'manager@bcm-platform.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztWZdR0RZN8O',
    TRUE,
    TRUE,
    'John',
    'Manager',
    'John Manager',
    '["manager", "bcm_manager"]'::jsonb,
    'BCM',
    'BCM Manager'
),
-- Regular user
(
    'tenant_001',
    'regular_user_001',
    'user',
    'user@bcm-platform.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztWZdR0RZN8O',
    TRUE,
    TRUE,
    'Jane',
    'Doe',
    'Jane Doe',
    '["user"]'::jsonb,
    'Operations',
    'Operations Specialist'
),
-- Resource Manager
(
    'tenant_001',
    'resource_mgr_001',
    'resourcemgr',
    'resourcemgr@bcm-platform.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztWZdR0RZN8O',
    TRUE,
    TRUE,
    'Bob',
    'Resources',
    'Bob Resources',
    '["resource_manager"]'::jsonb,
    'Facilities',
    'Resource Manager'
);

-- ============================================================================
-- VERIFY
-- ============================================================================

SELECT
    username,
    email,
    roles,
    is_active,
    created_at
FROM auth.users
ORDER BY username;
```

## Шаг 4: Проверка

После запуска должна появиться таблица с результатами:

```
username     | email                        | roles                        | is_active | created_at
-------------|------------------------------|------------------------------|-----------|------------------
admin        | admin@bcm-platform.com       | ["admin","bcm_manager"]      | true      | 2025-10-03...
manager      | manager@bcm-platform.com     | ["manager","bcm_manager"]    | true      | 2025-10-03...
resourcemgr  | resourcemgr@bcm-platform.com | ["resource_manager"]         | true      | 2025-10-03...
user         | user@bcm-platform.com        | ["user"]                     | true      | 2025-10-03...
```

✅ **Если видишь 4 users - миграция прошла успешно!**

## Troubleshooting

### Error: "relation auth.users already exists"
**Решение:** Таблица уже создана, всё ОК! Можно запускать сервисы.

### Error: "permission denied"
**Решение:** Нужны права admin в Supabase. Проверь что залогинен под правильным пользователем.

---

## После миграции:

Запустить сервисы:

```bash
# Terminal 1
cd /Users/MD/AI-Platform-ISO/platform-services/learning-service
python3 main.py

# Terminal 2
cd /Users/MD/AI-Platform-ISO/platform-services/governance-service
python3 main.py
```

Готово! 🚀
