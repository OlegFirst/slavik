# База Данных - Полное Руководство по Настройке
## BCM Platform Database Setup & Migration Guide

**Дата**: 2025-10-10
**Статус**: ✅ ГОТОВО К ИСПОЛЬЗОВАНИЮ

---

## 📋 ОБЗОР

Платформа BCM использует **PostgreSQL** (через Supabase или локальную установку) с полной поддержкой:
- **46 миграций** для создания всех схем и таблиц
- **29 схем** для различных модулей (ISO 22301, Intelligence, Community)
- **Автоматический migration tracking** для отслеживания применённых миграций
- **RLS (Row Level Security)** для multi-tenancy и безопасности

---

## 🚀 БЫСТРЫЙ СТАРТ

### Вариант 1: Используя Python скрипт (рекомендуется)

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/database

# Убедитесь что DATABASE_URL настроен
export DATABASE_URL="postgresql://user:password@localhost:5432/bcm_platform"

# Или создайте .env файл в корне проекта
echo "DATABASE_URL=postgresql://user:password@localhost:5432/bcm_platform" > ../../.env

# Запустите скрипт
python3 setup_database.py
```

### Вариант 2: Используя Bash скрипт

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/database

# Настройте .env или export DATABASE_URL
./setup_database.sh
```

### Вариант 3: Ручное применение (для отладки)

```bash
# Применить конкретную миграцию
psql $DATABASE_URL -f migrations_source/001_schemas_and_extensions.sql

# Применить все миграции по порядку
for f in migrations_source/*.sql; do
    echo "Applying $f..."
    psql $DATABASE_URL -f "$f"
done
```

---

## 🔧 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### 1. PostgreSQL / Supabase

**Option A: Локальный PostgreSQL**
```bash
# macOS:
brew install postgresql@14
brew services start postgresql@14

# Создать базу данных
createdb bcm_platform

# Создать пользователя
psql postgres -c "CREATE USER bcm WITH PASSWORD 'bcm_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE bcm_platform TO bcm;"
```

**Option B: Supabase (рекомендуется для production)**
1. Зайдите на https://supabase.com
2. Создайте новый проект: `bcm-platform`
3. Получите Connection String из Settings → Database
4. Настройте environment variables:
   ```bash
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJhbG...
   DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@[HOST]:5432/postgres
   ```

### 2. Python зависимости (для Python скрипта)

```bash
pip install psycopg2-binary python-dotenv
```

### 3. Environment Variables

Создайте файл `/Users/MD/AI-Platform-ISO/.env`:

```bash
# Database Connection
DATABASE_URL=postgresql://bcm:bcm_password@localhost:5432/bcm_platform

# OR Supabase
SUPABASE_URL=https://tpdkhddtbhpoqzzgxfni.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres.tpdkhddtbhpoqzzgxfni:[PASSWORD]@aws-1-eu-north-1.pooler.supabase.com:5432/postgres

# Redis (опционально, для некоторых сервисов)
REDIS_URL=redis://localhost:6379/0

# RabbitMQ / EventBus (опционально)
EVENTBUS_URL=amqp://guest:guest@localhost:5672

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
```

---

## 📊 СТРУКТУРА МИГРАЦИЙ

### Миграции расположены в двух местах:

1. **`/infrastructure/database/migrations_source/`** (основные)
   - 001-044: Полный набор миграций для всей платформы
   - Применяются последовательно по номерам

2. **`/infrastructure/database/postgresql/migrations_source/`** (дополнительные)
   - PostgreSQL-специфичные расширения
   - Применяются после основных

### Основные миграции (001-044):

```
001-009: Базовые схемы и таблицы
├── 001: Schemas and Extensions (29 schemas)
├── 002: RLS Functions (security helpers)
├── 003: Core Tables (organizations, users, teams)
├── 004: Community Schema (portal, marketplace)
├── 005: Intelligence Schema (AI, digital twins)
├── 006: BIA & Risk Schemas (ISO 22301:2019 Clause 8.2.2, 8.2.3)
├── 007: Governance & Audit (ISO 22301 Clauses 5, 6, 7)
├── 008: Documents Schema (ISO 22301 Clause 7.5)
└── 009: Response Schema (incident management)

010-018: Расширения и улучшения
├── 010: Validation Schema (KPIs, metrics)
├── 011: BIA & Risk Extensions (advanced features)
├── 012: Governance & Compliance (enhanced tracking)
├── 013: Learning & Planning (training, exercises)
├── 014: Supply Chain Extension (dependencies)
├── 015: Compliance Improvements (gap analysis)
├── 016: Governance Context & Stakeholders
├── 017: Governance Domain Intelligence
└── 018: Validation KPI & Alerts

019-030: Безопасность и производительность
├── 019: RLS Security Hardening
├── 020: Community Specialists
├── 021: Performance & Security Fixes
├── 022-023: Auth RLS & Policy Consolidation
├── 024-027: User Management & Admin Policies
└── 028-030: Linting & Security Fixes

031-044: Расширенные функции
├── 031-037: Policy Optimization & Cleanup
├── 038: Gateway State Management
├── 040-041: Community Intelligence & Collective Agents
├── 042: Predictive Service
├── 043: Learning System Enhancements
└── 044: Outbox Events (guaranteed event delivery)
```

---

## 🔍 ПРОВЕРКА СТАТУСА МИГРАЦИЙ

### Проверка применённых миграций

```bash
# Подключитесь к базе
psql $DATABASE_URL

# Проверьте таблицу миграций
SELECT migration_number, migration_name, applied_at, execution_time_ms
FROM public.schema_migrations
ORDER BY migration_number;

# Количество применённых миграций
SELECT COUNT(*) as total_migrations FROM public.schema_migrations;

# Последняя применённая миграция
SELECT * FROM public.schema_migrations
ORDER BY applied_at DESC
LIMIT 1;
```

### Проверка схем и таблиц

```bash
# Список всех схем
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
ORDER BY schema_name;

# Количество таблиц по схемам
SELECT table_schema, COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
GROUP BY table_schema
ORDER BY table_count DESC;

# Общая статистика
SELECT
    (SELECT COUNT(*) FROM information_schema.schemata
     WHERE schema_name NOT IN ('pg_catalog', 'information_schema')) as total_schemas,
    (SELECT COUNT(*) FROM information_schema.tables
     WHERE table_schema NOT IN ('pg_catalog', 'information_schema')) as total_tables,
    (SELECT COUNT(*) FROM public.schema_migrations) as total_migrations;
```

---

## 📦 СХЕМЫ БАЗЫ ДАННЫХ

### Core Platform (6 схем)

| Схема | Назначение | Сервисы |
|-------|-----------|---------|
| **public** | Core shared: organizations, users, teams | All |
| **core** | Core platform functionality | Platform |
| **core_auth** | Authentication tables | Auth Service |
| **auth** | Supabase Auth (system) | Supabase |
| **extensions** | PostgreSQL extensions | System |
| **audit** | Audit logs, event sourcing | All |

### BCM Business Modules (6 схем)

| Схема | Назначение | Сервис | ISO Clause |
|-------|-----------|---------|------------|
| **bcm** | BCM shared resources | All BCM | - |
| **bia** | Business Impact Analysis | bia-service (8012) | 8.2.2 |
| **risk** | Risk Management | risk-service (8040) | 8.2.3 |
| **governance** | Governance & compliance | governance-service (8013) | 5, 6, 7 |
| **compliance** | Compliance tracking | compliance-service (8014) | 9.1, 9.2, 9.3 |
| **validation** | Validation & KPIs | validation-service (8022) | 10 |

### Intelligent Core (6 схем)

| Схема | Назначение | Сервис |
|-------|-----------|---------|
| **intelligence** | AI memory, digital twins | intelligent-core |
| **workflow_intelligence** | Workflow orchestration | workflow-intelligence |
| **domain_intelligence** | Domain-specific AI | expertise-center |
| **learning** | Learning system | learning-service (8021) |
| **workflow** | Workflow engine | workflow services |
| **community** | Community contributions | community-service |

### Additional Services (5 схем)

| Схема | Назначение | Сервис |
|-------|-----------|---------|
| **response** | Incident response | response-service (8041) |
| **simulation** | Digital twin simulations | simulation |
| **portal** | User portal | portal (8033) |
| **marketplace** | Template marketplace | marketplace (8032) |
| **seh** | Social Enterprise Hub | WHO programs |

---

## 🔐 ROW LEVEL SECURITY (RLS)

Все таблицы используют RLS для multi-tenancy и безопасности:

### Автоматическая изоляция по tenant_id

```sql
-- Пример политики для таблицы BIA
CREATE POLICY bia_tenant_isolation ON bia.bia_processes
    FOR ALL
    USING (
        tenant_id = current_setting('app.current_tenant_id', TRUE)
    );

-- Установка tenant_id для сессии
SET app.current_tenant_id = 'org-123';

-- Теперь все запросы автоматически фильтруются по tenant
SELECT * FROM bia.bia_processes;  -- Видит только данные org-123
```

### Service Role (административный доступ)

```sql
-- Service role видит все данные
CREATE POLICY bia_service_role ON bia.bia_processes
    FOR ALL
    USING (auth.role() = 'service_role');
```

---

## 🛠️ TROUBLESHOOTING

### Проблема: Migration уже применена

**Ошибка**: `duplicate key value violates unique constraint "schema_migrations_migration_number_key"`

**Решение**: Миграция уже применена, скрипт пропустит её автоматически.

```bash
# Проверьте применённую миграцию
psql $DATABASE_URL -c "SELECT * FROM public.schema_migrations WHERE migration_number = '001';"
```

### Проблема: Схема уже существует

**Ошибка**: `schema "bia" already exists`

**Решение**: Это нормально, миграция продолжится. Команда `CREATE SCHEMA IF NOT EXISTS` безопасна.

### Проблема: Нет подключения к базе

**Ошибка**: `FATAL: password authentication failed`

**Решение**:
1. Проверьте `DATABASE_URL` в .env
2. Проверьте доступность PostgreSQL: `psql $DATABASE_URL -c "SELECT 1;"`
3. Для Supabase проверьте Connection Pooler (port 5432), не Direct Connection (port 6543)

```bash
# Правильный Supabase URL (Pooler):
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@[REGION].pooler.supabase.com:5432/postgres

# НЕ используйте Direct Connection (если не знаете зачем):
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@[REGION].supabase.co:6543/postgres
```

### Проблема: Миграция завершилась с ошибкой

**Решение**:
1. Посмотрите детали ошибки
2. Проверьте конфликты (дубликаты таблиц/схем)
3. Примените миграцию вручную с verbose output:

```bash
psql $DATABASE_URL -f migrations_source/XXX_migration_name.sql -v ON_ERROR_STOP=1 --echo-all
```

4. Если миграция частично применена, может потребоваться rollback:

```sql
-- Начните транзакцию
BEGIN;

-- Примените миграцию
\i migrations_source/XXX_migration_name.sql

-- Если ошибка - откатите:
ROLLBACK;

-- Если успешно - подтвердите:
COMMIT;
```

---

## 📈 МОНИТОРИНГ БАЗЫ ДАННЫХ

### Размер базы данных

```sql
SELECT
    pg_size_pretty(pg_database_size(current_database())) as database_size;
```

### Размер по схемам

```sql
SELECT
    schemaname,
    pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))::bigint) as size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
GROUP BY schemaname
ORDER BY SUM(pg_total_relation_size(schemaname||'.'||tablename)) DESC;
```

### Активные подключения

```sql
SELECT
    count(*) as connections,
    datname as database
FROM pg_stat_activity
GROUP BY datname;
```

### Медленные запросы (если pg_stat_statements включен)

```sql
SELECT
    query,
    mean_exec_time,
    calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 🔄 ОБНОВЛЕНИЕ И ОТКАТ

### Применение новой миграции

```bash
# 1. Создайте новую миграцию
cat > migrations_source/045_new_feature.sql << 'EOF'
-- Migration: New Feature
-- Purpose: Add new functionality

CREATE TABLE IF NOT EXISTS public.new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
EOF

# 2. Примените её
python3 setup_database.py
# ИЛИ вручную:
psql $DATABASE_URL -f migrations_source/045_new_feature.sql
```

### Откат миграции (если нужен)

```sql
-- Создайте DOWN миграцию (rollback)
-- migrations_source/045_new_feature_down.sql

DROP TABLE IF EXISTS public.new_table;

-- Примените её
psql $DATABASE_URL -f migrations_source/045_new_feature_down.sql

-- Удалите запись из tracking table
DELETE FROM public.schema_migrations WHERE migration_number = '045';
```

---

## 📝 РЕКОМЕНДАЦИИ

### ✅ DO (Делайте)

1. **Всегда используйте миграции** - не изменяйте схему вручную
2. **Тестируйте на dev базе** перед production
3. **Делайте бэкапы** перед применением миграций:
   ```bash
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
   ```
4. **Используйте транзакции** для сложных миграций
5. **Документируйте изменения** в comments к миграциям

### ❌ DON'T (Не делайте)

1. **Не изменяйте применённые миграции** - создайте новую
2. **Не удаляйте migration tracking table** - потеряете историю
3. **Не применяйте миграции в production без тестирования**
4. **Не используйте CASCADE DROP** без необходимости
5. **Не пропускайте миграции** - применяйте последовательно

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

После успешной настройки базы данных:

1. ✅ **Настройте сервисы** в `/platform-services`
2. ✅ **Примените critical fixes** из `CRITICAL_FIXES_REQUIRED.md`
3. ✅ **Настройте .env** для всех сервисов
4. ✅ **Запустите health checks**: `bash check_services.sh`
5. ✅ **Проверьте интеграции** между сервисами

---

## 📞 ПОМОЩЬ

### Логи миграций

```bash
# Посмотреть последние применённые миграции
psql $DATABASE_URL -c "
SELECT
    migration_number,
    migration_name,
    applied_at,
    execution_time_ms || 'ms' as exec_time
FROM public.schema_migrations
ORDER BY applied_at DESC
LIMIT 10;
"
```

### Проверка целостности

```bash
# Проверить отсутствующие миграции
python3 << 'EOF'
import psycopg2
from pathlib import Path
import os

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Получить применённые миграции
cursor.execute("SELECT migration_number FROM public.schema_migrations")
applied = {row[0] for row in cursor.fetchall()}

# Получить доступные миграции
migrations_dir = Path("/Users/MD/AI-Platform-ISO/infrastructure/database/migrations_source")
available = {f.name[:3] for f in migrations_dir.glob("*.sql")}

# Найти отсутствующие
missing = available - applied

print(f"Available: {len(available)}")
print(f"Applied: {len(applied)}")
print(f"Missing: {len(missing)}")

if missing:
    print("\nMissing migrations:")
    for num in sorted(missing):
        print(f"  {num}")
EOF
```

---

**Статус**: ✅ ГОТОВО
**Последнее обновление**: 2025-10-10
**Следующий документ**: `STARTUP_GUIDE.md` - запуск всех сервисов платформы
