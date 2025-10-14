# Community Service Migrations

Миграции базы данных для Community Service (Portal + Marketplace).

## Структура

```
migrations/
├── 001_community_schemas.sql    # Portal + Marketplace schemas (combined)
├── 002_add_scenarios.sql         # Scenario templates (portal)
├── 003_add_forum.sql            # Forum features (portal)
└── README.md
```

## Применение миграций

### Локально (development)

```bash
# Using psql
psql -h localhost -U postgres -d bcm_platform -f 001_community_schemas.sql

# Using Python script
python3 apply_migration.py 001_community_schemas.sql
```

### Supabase (production)

```bash
# Method 1: Via Supabase Dashboard
# 1. Open https://supabase.com/dashboard/project/[project-id]/sql
# 2. Paste migration SQL
# 3. Run

# Method 2: Via apply_migration.py script
cd /Users/MD/AI-Platform-ISO/platform-services/community-service
python3 migrations/apply_migration.py

# Method 3: Via Supabase CLI
supabase db push

# Method 4: Direct connection
export DATABASE_URL="postgresql://postgres.xxx:xxx@aws-1-eu-north-1.pooler.supabase.com:5432/postgres"
psql $DATABASE_URL < migrations/001_community_schemas.sql
```

## Schemas Overview

### Portal Schema

**Tables:**
1. `knowledge_articles` - База знаний (статьи, гайды, best practices)
2. `news_items` - Новости платформы
3. `event_items` - События и вебинары
4. `bcm_scenarios` - Сценарии BCM для reference
5. `forum_categories` - Категории форума
6. `forum_topics` - Топики форума
7. `forum_posts` - Посты форума

**Features:**
- Multi-tenant (tenant_id на всех таблицах)
- Полнотекстовый поиск (tsvector)
- Автоматические timestamps
- Audit trail (created_by, updated_by)

### Marketplace Schema

**Tables:**
1. `specialists` - Профили BCM-специалистов
2. `certifications` - Сертификаты специалистов
3. `portfolio_items` - Портфолио работ
4. `projects` - Проекты от клиентов
5. `proposals` - Предложения от специалистов
6. `reviews` - Отзывы о специалистах

**Features:**
- Multi-tenant (tenant_id)
- JSONB для гибких полей (skills, specializations)
- ENUMs для типов (service_type, status, etc.)
- Auto-calculation triggers (rating, proposal_count)
- Foreign keys to clients.users (commented out for now)

## Row Level Security (RLS)

RLS будет настроен после миграции:

```sql
-- Enable RLS on all tables
ALTER TABLE portal.knowledge_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace.specialists ENABLE ROW LEVEL SECURITY;
-- ... etc

-- Create policies
CREATE POLICY "Users see own tenant data"
ON portal.knowledge_articles
FOR SELECT
USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
```

## Migration Status

- ✅ `001_community_schemas.sql` - Combined portal + marketplace (ready)
- ⏳ `002_add_scenarios.sql` - Copy from portal/migrations
- ⏳ `003_add_forum.sql` - Copy from portal/migrations

## Notes

1. **Foreign Keys:** Marketplace foreign keys к `clients.users` закомментированы до интеграции с Clients service
2. **Supabase Session Pooler:** Используем `aws-1-eu-north-1.pooler.supabase.com` для IPv4 compatibility
3. **Schemas Naming:** `portal` и `marketplace` - отдельные schemas для логического разделения
4. **RLS:** Настраивается после создания tables для proper tenant isolation

## Testing Migrations

```bash
# Check schemas created
psql $DATABASE_URL -c "\dn"

# Check portal tables
psql $DATABASE_URL -c "\dt portal.*"

# Check marketplace tables
psql $DATABASE_URL -c "\dt marketplace.*"

# Check ENUMs
psql $DATABASE_URL -c "\dT marketplace.*"

# Verify triggers
psql $DATABASE_URL -c "SELECT tgname, tgrelid::regclass FROM pg_trigger WHERE tgrelid::regclass::text LIKE 'marketplace.%';"
```

## Rollback

```sql
-- Drop schemas (use with caution!)
DROP SCHEMA IF EXISTS portal CASCADE;
DROP SCHEMA IF EXISTS marketplace CASCADE;
```

## Related Documentation

- [Community Service README](../README.md)
- [Portal Database Models](../portal/database/models.py)
- [Marketplace Database Models](../marketplace/database/models.py)
- [Shared Database Connection](../shared/database/connection.py)
