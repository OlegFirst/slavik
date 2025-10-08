# 🗄️ Process Analytics Schema - Application Guide

**Schema:** `process_analytics.*`
**Database:** Supabase PostgreSQL
**Status:** Ready to apply
**Version:** 1.0.0

---

## 📋 Quick Apply

```bash
# Apply schema to Supabase
PGPASSWORD='K@x3ta9V8GK5rnW' psql \
  -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.tpdkhddtbhpoqzzgxfni \
  -d postgres \
  -p 5432 \
  -f supabase_schema.sql
```

---

## ✅ Verification

```bash
# Verify schema created
PGPASSWORD='K@x3ta9V8GK5rnW' psql \
  -h aws-1-eu-north-1.pooler.supabase.com \
  -U postgres.tpdkhddtbhpoqzzgxfni \
  -d postgres \
  -p 5432 \
  -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'process_analytics';"
```

**Expected output:** 6 tables
- executions
- events
- patterns
- deviations
- bottlenecks
- performance_snapshots

---

## 📊 Schema Overview

### Tables (6)

1. **executions** - Process instances (workflow runs)
2. **events** - Individual steps/events within executions
3. **patterns** - Discovered process patterns (sequences, loops, parallels)
4. **deviations** - Detected deviations from expected behavior
5. **bottlenecks** - Identified bottlenecks causing delays
6. **performance_snapshots** - Aggregated metrics over time

### Views (3)

1. **active_executions** - Currently running processes
2. **recent_bottlenecks** - Bottlenecks from last 7 days
3. **process_health** - Health metrics for all processes (last 30 days)

### Functions (1)

1. **get_process_summary()** - Comprehensive process summary

### Triggers (2)

1. **update_execution_duration** - Auto-calculate duration on completion
2. **update_pattern_last_seen** - Update when pattern frequency increases

---

## 🔐 Security (RLS Policies)

- ✅ **service_role**: Full access (for backend services)
- ✅ **authenticated**: Read all + Insert executions/events
- ✅ **anon**: No access

---

## 🔄 Migration from Old Tables

If you have existing data in `public.process_executions`, etc.:

```sql
-- Migrate executions
INSERT INTO process_analytics.executions
SELECT * FROM public.process_executions;

-- Migrate events
INSERT INTO process_analytics.events
SELECT * FROM public.process_events;

-- Migrate patterns
INSERT INTO process_analytics.patterns
SELECT * FROM public.discovered_patterns;

-- Migrate deviations (if exists)
INSERT INTO process_analytics.deviations
SELECT * FROM public.process_deviations;
```

Then drop old tables:

```sql
DROP TABLE IF EXISTS public.process_deviations;
DROP TABLE IF EXISTS public.process_events;
DROP TABLE IF EXISTS public.discovered_patterns;
DROP TABLE IF EXISTS public.process_executions;
```

---

## 🔧 Update Application Code

### Before (old table names):

```python
class ProcessExecution(Base):
    __tablename__ = "process_executions"  # ❌ public schema
```

### After (new schema):

```python
class ProcessExecution(Base):
    __tablename__ = "executions"
    __table_args__ = {"schema": "process_analytics"}  # ✅ Isolated schema
```

**Apply to all models:**
- ProcessExecution → process_analytics.executions
- ProcessEvent → process_analytics.events
- ProcessPattern → process_analytics.patterns
- ProcessDeviation → process_analytics.deviations

---

## 📊 Sample Queries

### Get active processes

```sql
SELECT * FROM process_analytics.active_executions;
```

### Get process health

```sql
SELECT * FROM process_analytics.process_health
WHERE success_rate < 80;
```

### Get recent bottlenecks

```sql
SELECT * FROM process_analytics.recent_bottlenecks
WHERE impact_score > 7;
```

### Get process summary

```sql
SELECT * FROM process_analytics.get_process_summary('bia_workflow', 30);
```

---

## 🎯 Next Steps

1. **Apply schema** (command above)
2. **Update main.py** to use schema-qualified table names
3. **Test connection** with updated code
4. **Migrate data** (if old tables exist)
5. **Drop old tables** after verification

---

**Schema file:** `supabase_schema.sql`
**Applied:** TBD
**Version:** 1.0.0
