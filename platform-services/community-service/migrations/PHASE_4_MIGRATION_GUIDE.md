# Community Service - Phase 4 Migration Guide

**Database Extensions for Learning & Governance Integration**

This guide covers migrations 007 and 008 which add integration columns and junction tables to enable Community Service integration with Learning and Governance services.

---

## 📋 Migration Overview

| Migration | Version | Description | Tables Affected |
|-----------|---------|-------------|-----------------|
| **007_integration_columns.sql** | 007 | Add integration columns | Portal: 3 tables<br>Marketplace: 3 tables |
| **008_junction_tables.sql** | 008 | Create junction tables | Portal: 2 new tables<br>Marketplace: 3 new tables |

---

## 🎯 What These Migrations Do

### Migration 007: Integration Columns

**Portal Service:**
- `knowledge_articles`: Links to Learning programs and Governance policies
- `scenarios`: Links to Governance policies and ISO clauses
- `user_reputation`: Adds Learning competencies and Governance roles for moderation

**Marketplace Service:**
- `specialists`: Adds Learning certifications, competency scores, and Governance verification
- `projects`: Adds Learning/Governance requirements for matching
- `proposals`: Adds competency match scoring

**Created Objects:**
- 3 views (v_articles_with_training, v_verified_specialists, v_projects_with_requirements)
- 1 function (calculate_competency_match)

### Migration 008: Junction Tables

**Portal Service:**
- `article_competencies`: Many-to-many between articles and competency areas
- `scenario_policies`: Many-to-many between scenarios and policies

**Marketplace Service:**
- `specialist_competencies`: Detailed competency records per specialist
- `project_competency_requirements`: Competency requirements per project
- `specialist_certifications_normalized`: Alternative to JSONB certification storage

**Created Objects:**
- 1 view (v_specialist_full_profile)
- 1 function (find_matching_specialists)
- 1 trigger (update_specialist_cert_count)

---

## 🔧 How to Run Migrations

### Prerequisites

1. **Database Access**
   - Supabase project URL
   - Service role key (from Supabase dashboard → Settings → API)
   - PostgreSQL client installed (psql)

2. **Existing Schemas**
   - `portal` schema must exist (created by migration 001)
   - `marketplace` schema must exist (created by migration 001)

### Option 1: Via Supabase Dashboard (Recommended)

1. **Login to Supabase Dashboard**
   ```
   https://app.supabase.com/project/YOUR_PROJECT_ID
   ```

2. **Navigate to SQL Editor**
   - Left sidebar → "SQL Editor"
   - Click "+ New query"

3. **Run Migration 007**
   ```sql
   -- Copy and paste entire content of 007_integration_columns.sql
   -- Click "Run" or press Ctrl+Enter
   ```

4. **Verify Migration 007**
   ```sql
   -- Check migration history
   SELECT * FROM portal.migration_history WHERE version = '007';

   -- Verify new columns exist
   SELECT column_name, data_type
   FROM information_schema.columns
   WHERE table_schema = 'portal'
     AND table_name = 'knowledge_articles'
     AND column_name IN ('related_training_program_id', 'related_policy_id');
   ```

5. **Run Migration 008**
   ```sql
   -- Copy and paste entire content of 008_junction_tables.sql
   -- Click "Run" or press Ctrl+Enter
   ```

6. **Verify Migration 008**
   ```sql
   -- Check migration history
   SELECT * FROM portal.migration_history WHERE version = '008';

   -- Verify junction tables exist
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'portal'
     AND table_name IN ('article_competencies', 'scenario_policies');

   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'marketplace'
     AND table_name IN ('specialist_competencies', 'project_competency_requirements', 'specialist_certifications_normalized');
   ```

### Option 2: Via psql Command Line

1. **Set Environment Variables**
   ```bash
   export SUPABASE_HOST="db.YOUR_PROJECT_REF.supabase.co"
   export SUPABASE_PASSWORD="your-database-password"
   ```

2. **Run Migration 007**
   ```bash
   psql "postgresql://postgres:$SUPABASE_PASSWORD@$SUPABASE_HOST:5432/postgres" \
     -f migrations/007_integration_columns.sql
   ```

3. **Run Migration 008**
   ```bash
   psql "postgresql://postgres:$SUPABASE_PASSWORD@$SUPABASE_HOST:5432/postgres" \
     -f migrations/008_junction_tables.sql
   ```

4. **Verify Migrations**
   ```bash
   psql "postgresql://postgres:$SUPABASE_PASSWORD@$SUPABASE_HOST:5432/postgres" \
     -c "SELECT version, description, applied_at FROM portal.migration_history ORDER BY applied_at DESC LIMIT 5;"
   ```

### Option 3: Via Python Script

Create a migration runner script:

```python
import asyncpg
import asyncio
import os

async def run_migrations():
    conn = await asyncpg.connect(
        host=os.getenv("SUPABASE_HOST"),
        port=5432,
        user="postgres",
        password=os.getenv("SUPABASE_PASSWORD"),
        database="postgres"
    )

    # Read and execute migration 007
    with open("migrations/007_integration_columns.sql", "r") as f:
        await conn.execute(f.read())
    print("✅ Migration 007 complete")

    # Read and execute migration 008
    with open("migrations/008_junction_tables.sql", "r") as f:
        await conn.execute(f.read())
    print("✅ Migration 008 complete")

    # Verify
    result = await conn.fetch(
        "SELECT version, description, applied_at FROM portal.migration_history ORDER BY applied_at DESC LIMIT 2"
    )
    print("\nRecent migrations:")
    for row in result:
        print(f"  - {row['version']}: {row['description']} ({row['applied_at']})")

    await conn.close()

asyncio.run(run_migrations())
```

---

## ✅ Validation Checklist

After running both migrations, verify the following:

### Migration 007 Validation

**Portal Schema:**
- [ ] `knowledge_articles` has 4 new columns (related_training_program_id, required_competency_level, related_policy_id, related_policy_references)
- [ ] `scenarios` has 2 new columns (related_policies, iso_clauses_covered)
- [ ] `user_reputation` has 6 new columns (learning_competencies, certifications_count, last_certification_date, governance_roles, is_moderator, moderator_since)
- [ ] View `portal.v_articles_with_training` exists
- [ ] View `portal.v_projects_with_requirements` exists (in marketplace schema)

**Marketplace Schema:**
- [ ] `specialists` has 7 new columns (certifications, competency_scores, last_training_date, training_programs_completed, verified_by_role_id, verification_source, governance_competencies)
- [ ] `projects` has 3 new columns (required_certifications, required_competencies, related_policies)
- [ ] `proposals` has 2 new columns (competency_match_score, matching_details)
- [ ] View `marketplace.v_verified_specialists` exists
- [ ] Function `marketplace.calculate_competency_match` exists

### Migration 008 Validation

**Portal Schema:**
- [ ] Table `portal.article_competencies` exists with composite primary key (article_id, competency_area)
- [ ] Table `portal.scenario_policies` exists with composite primary key (scenario_id, policy_id)
- [ ] 6 indexes created on junction tables

**Marketplace Schema:**
- [ ] Table `marketplace.specialist_competencies` exists with composite primary key (specialist_id, competency_area)
- [ ] Table `marketplace.project_competency_requirements` exists with composite primary key (project_id, competency_area)
- [ ] Table `marketplace.specialist_certifications_normalized` exists with serial primary key
- [ ] View `marketplace.v_specialist_full_profile` exists
- [ ] Function `marketplace.find_matching_specialists` exists
- [ ] Trigger `trigger_update_cert_count` exists on specialist_certifications_normalized

**SQL Validation Queries:**
```sql
-- Check all new columns
SELECT
    table_schema,
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema IN ('portal', 'marketplace')
  AND (
    column_name LIKE '%competenc%' OR
    column_name LIKE '%certification%' OR
    column_name LIKE '%policy%' OR
    column_name LIKE '%governance%' OR
    column_name = 'verification_source' OR
    column_name = 'is_moderator'
  )
ORDER BY table_schema, table_name, column_name;

-- Check all junction tables
SELECT table_schema, table_name,
       (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_schema = t.table_schema AND c.table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema IN ('portal', 'marketplace')
  AND (
    table_name LIKE '%competenc%' OR
    table_name LIKE '%_policies' OR
    table_name LIKE '%certification%'
  )
ORDER BY table_schema, table_name;

-- Check functions
SELECT routine_schema, routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema IN ('portal', 'marketplace')
  AND (routine_name LIKE '%competency%' OR routine_name LIKE '%specialist%')
ORDER BY routine_schema, routine_name;

-- Check views
SELECT table_schema, table_name
FROM information_schema.views
WHERE table_schema IN ('portal', 'marketplace')
ORDER BY table_schema, table_name;
```

---

## 🔄 Rollback (If Needed)

If you need to rollback these migrations:

### Rollback Migration 008
```sql
-- Drop junction tables
DROP TABLE IF EXISTS portal.article_competencies CASCADE;
DROP TABLE IF EXISTS portal.scenario_policies CASCADE;
DROP TABLE IF EXISTS marketplace.specialist_competencies CASCADE;
DROP TABLE IF EXISTS marketplace.project_competency_requirements CASCADE;
DROP TABLE IF EXISTS marketplace.specialist_certifications_normalized CASCADE;

-- Drop views
DROP VIEW IF EXISTS marketplace.v_specialist_full_profile;

-- Drop functions
DROP FUNCTION IF EXISTS marketplace.find_matching_specialists;
DROP FUNCTION IF EXISTS marketplace.update_specialist_cert_count;

-- Remove migration record
DELETE FROM portal.migration_history WHERE version = '008';
```

### Rollback Migration 007
```sql
-- Portal: Remove integration columns
ALTER TABLE portal.knowledge_articles
DROP COLUMN IF EXISTS related_training_program_id,
DROP COLUMN IF EXISTS required_competency_level,
DROP COLUMN IF EXISTS related_policy_id,
DROP COLUMN IF EXISTS related_policy_references;

ALTER TABLE portal.scenarios
DROP COLUMN IF EXISTS related_policies,
DROP COLUMN IF EXISTS iso_clauses_covered;

ALTER TABLE portal.user_reputation
DROP COLUMN IF EXISTS learning_competencies,
DROP COLUMN IF EXISTS certifications_count,
DROP COLUMN IF EXISTS last_certification_date,
DROP COLUMN IF EXISTS governance_roles,
DROP COLUMN IF EXISTS is_moderator,
DROP COLUMN IF EXISTS moderator_since;

-- Marketplace: Remove integration columns
ALTER TABLE marketplace.specialists
DROP COLUMN IF EXISTS certifications,
DROP COLUMN IF EXISTS competency_scores,
DROP COLUMN IF EXISTS last_training_date,
DROP COLUMN IF EXISTS training_programs_completed,
DROP COLUMN IF EXISTS verified_by_role_id,
DROP COLUMN IF EXISTS verification_source,
DROP COLUMN IF EXISTS governance_competencies;

ALTER TABLE marketplace.projects
DROP COLUMN IF EXISTS required_certifications,
DROP COLUMN IF EXISTS required_competencies,
DROP COLUMN IF EXISTS related_policies;

ALTER TABLE marketplace.proposals
DROP COLUMN IF EXISTS competency_match_score,
DROP COLUMN IF EXISTS matching_details;

-- Drop views
DROP VIEW IF EXISTS portal.v_articles_with_training;
DROP VIEW IF EXISTS marketplace.v_verified_specialists;
DROP VIEW IF EXISTS marketplace.v_projects_with_requirements;

-- Drop functions
DROP FUNCTION IF EXISTS marketplace.calculate_competency_match;

-- Remove migration record
DELETE FROM portal.migration_history WHERE version = '007';
```

---

## 📊 Migration Impact

### Database Size Impact

**Estimated additional space:**
- Migration 007: ~500 bytes per existing row (JSONB columns with empty defaults)
- Migration 008: Minimal (empty junction tables)

**Index overhead:**
- Migration 007: ~15 new indexes
- Migration 008: ~12 new indexes

### Performance Impact

**Query Performance:**
- ✅ **Improved**: Competency matching via indexed junction tables
- ✅ **Improved**: Specialist search by certification via normalized table
- ⚠️ **Neutral**: JSONB columns have GIN indexes for performance

**Write Performance:**
- ⚠️ **Minor impact**: Additional indexes increase insert/update time by ~5-10%
- ⚠️ **Trigger overhead**: specialist_certifications_normalized has update trigger

---

## 🚀 Next Steps: SQLAlchemy Models

After running SQL migrations, Python models have been updated:

### Portal Models ✅
- `KnowledgeArticle` - added 4 columns
- `Scenario` - added 2 columns
- `UserReputation` - added 6 columns
- `ArticleCompetency` - new junction model
- `ScenarioPolicy` - new junction model

### Marketplace Models ✅
- `Specialist` - added 7 columns
- `Project` - added 3 columns
- `Proposal` - added 2 columns
- `SpecialistCompetency` - new junction model
- `ProjectCompetencyRequirement` - new junction model
- `SpecialistCertificationNormalized` - new junction model

**File paths:**
- `/Users/MD/AI-Platform-ISO/platform-services/community-service/portal/database/models.py`
- `/Users/MD/AI-Platform-ISO/platform-services/community-service/marketplace/database/models.py`

---

## 📝 Migration History

All migrations are tracked in `portal.migration_history`:

```sql
SELECT version, description, applied_at
FROM portal.migration_history
ORDER BY version;
```

**Expected output:**
```
version | description                                           | applied_at
--------|-------------------------------------------------------|-------------------
001     | Create Community Service schemas                      | 2025-10-03 ...
007     | Add Learning & Governance integration columns         | 2025-10-03 ...
008     | Create junction tables for Learning/Governance        | 2025-10-03 ...
```

---

## ⚠️ Important Notes

1. **No Foreign Keys to Other Databases**
   - `related_training_program_id`, `related_policy_id`, and `policy_id` columns do NOT have foreign key constraints
   - This is intentional: Learning and Governance services use separate databases
   - Referential integrity is maintained at the application layer

2. **JSONB vs Normalized Tables**
   - `specialists.certifications` stores full certification JSON from Learning Service
   - `specialist_certifications_normalized` provides queryable/indexed alternative
   - Both can coexist (use JSONB for full data, normalized for queries)

3. **Competency Scoring Algorithm**
   - Implemented in `marketplace.calculate_competency_match()` SQL function
   - Also implemented in `marketplace/integrations/learning_client.py` Python code
   - Keep both implementations in sync

4. **Migration Safety**
   - All new columns have default values (no null constraints)
   - All migrations use `IF NOT EXISTS` or `ON CONFLICT DO NOTHING`
   - Safe to run multiple times (idempotent)

---

## 🔍 Troubleshooting

### Error: "schema 'portal' does not exist"
**Solution:** Run migration 001 first to create base schemas.

### Error: "relation 'portal.knowledge_articles' does not exist"
**Solution:** Run base Portal migration first (001_community_schemas.sql).

### Error: "permission denied for schema portal"
**Solution:** Use service role key or ensure user has schema usage permissions:
```sql
GRANT USAGE ON SCHEMA portal TO authenticated;
GRANT USAGE ON SCHEMA marketplace TO authenticated;
```

### Error: "duplicate key value violates unique constraint"
**Solution:** Migration already applied. Check migration history:
```sql
SELECT * FROM portal.migration_history WHERE version IN ('007', '008');
```

---

## 📧 Support

For issues or questions:
- Review integration plan: `/Users/MD/AI-Platform-ISO/INTEGRATION_PLAN.md`
- Check Phase 3 completion: `/Users/MD/AI-Platform-ISO/platform-services/community-service/PHASE_3_COMPLETE.md`

---

**Created:** 2025-10-03
**Phase:** 4 - Database Extensions
**Status:** Ready to run
