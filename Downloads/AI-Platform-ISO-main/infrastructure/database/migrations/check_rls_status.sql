-- ============================================
-- BCM Platform - RLS Status Check
-- ============================================
-- Purpose: Check Row Level Security status for all tables
-- Usage: psql -U postgres -d bcm_platform -f check_rls_status.sql
-- ============================================

\echo ''
\echo '================================================'
\echo 'RLS STATUS CHECK - BCM Platform'
\echo '================================================'
\echo ''

-- Summary statistics
\echo '1. SUMMARY STATISTICS'
\echo '----------------------------------------------'

SELECT
    'Total tables' AS metric,
    COUNT(*)::text AS value
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
UNION ALL
SELECT
    'Tables with RLS enabled',
    COUNT(*)::text
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
AND c.relrowsecurity = true
UNION ALL
SELECT
    'Tables with FORCE RLS',
    COUNT(*)::text
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
AND c.relrowsecurity = true
AND c.relforcerowsecurity = true
UNION ALL
SELECT
    'Tables WITHOUT RLS',
    COUNT(*)::text
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
AND c.relrowsecurity = false;

\echo ''
\echo '2. TABLES WITH RLS ENABLED (should be 122+)'
\echo '----------------------------------------------'

SELECT
    t.schemaname AS schema,
    t.tablename AS table_name,
    CASE
        WHEN c.relforcerowsecurity THEN 'FORCE RLS ✅'
        WHEN c.relrowsecurity THEN 'RLS ENABLED ⚠️'
        ELSE 'NO RLS ❌'
    END AS status,
    (SELECT COUNT(*) FROM pg_policies WHERE schemaname = t.schemaname AND tablename = t.tablename) AS policies_count
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
AND c.relrowsecurity = true
ORDER BY t.schemaname, t.tablename;

\echo ''
\echo '3. TABLES WITHOUT RLS (security risk!)'
\echo '----------------------------------------------'

SELECT
    t.schemaname AS schema,
    t.tablename AS table_name,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS size,
    'NO RLS ❌' AS warning
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema', 'auth')
AND c.relrowsecurity = false
AND t.tablename NOT LIKE 'pg_%'
ORDER BY pg_total_relation_size(c.oid) DESC;

\echo ''
\echo '4. RLS POLICIES BY SCHEMA'
\echo '----------------------------------------------'

SELECT
    schemaname,
    COUNT(DISTINCT tablename) AS tables_with_policies,
    COUNT(*) AS total_policies,
    string_agg(DISTINCT policyname, ', ' ORDER BY policyname) AS policy_names
FROM pg_policies
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
GROUP BY schemaname
ORDER BY schemaname;

\echo ''
\echo '5. DETAILED RLS POLICY INFORMATION'
\echo '----------------------------------------------'

SELECT
    schemaname AS schema,
    tablename AS table,
    policyname AS policy_name,
    cmd AS operation,
    CASE
        WHEN roles = '{public}' THEN 'PUBLIC'
        ELSE array_to_string(roles, ', ')
    END AS applies_to,
    CASE
        WHEN qual IS NOT NULL THEN 'Row filter defined'
        ELSE 'No row filter'
    END AS has_filter
FROM pg_policies
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename, policyname
LIMIT 50;

\echo ''
\echo '6. SECURITY RECOMMENDATIONS'
\echo '----------------------------------------------'

DO $$
DECLARE
    rls_count INTEGER;
    force_count INTEGER;
    no_rls_count INTEGER;
BEGIN
    -- Get counts
    SELECT COUNT(*) INTO rls_count
    FROM pg_tables t
    JOIN pg_class c ON c.relname = t.tablename
    WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
    AND c.relrowsecurity = true;

    SELECT COUNT(*) INTO force_count
    FROM pg_tables t
    JOIN pg_class c ON c.relname = t.tablename
    WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
    AND c.relrowsecurity = true
    AND c.relforcerowsecurity = true;

    SELECT COUNT(*) INTO no_rls_count
    FROM pg_tables t
    JOIN pg_class c ON c.relname = t.tablename
    WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema', 'auth')
    AND c.relrowsecurity = false
    AND t.tablename NOT LIKE 'pg_%';

    -- Print recommendations
    RAISE NOTICE '';
    IF force_count >= 122 THEN
        RAISE NOTICE '✅ EXCELLENT: All % tenant tables have FORCE RLS', force_count;
    ELSIF rls_count >= 122 THEN
        RAISE WARNING '⚠️  WARNING: % tables have RLS, but only % have FORCE RLS', rls_count, force_count;
        RAISE NOTICE 'ACTION REQUIRED: Run 999_force_rls_enforcement.sql';
    ELSE
        RAISE WARNING '❌ CRITICAL: Only % tables have RLS (expected 122+)', rls_count;
        RAISE NOTICE 'ACTION REQUIRED: Enable RLS on all tenant tables';
    END IF;

    IF no_rls_count > 0 THEN
        RAISE WARNING '⚠️  WARNING: % tables have NO RLS protection', no_rls_count;
        RAISE NOTICE 'Review these tables to determine if RLS is needed';
    END IF;

    RAISE NOTICE '';
    RAISE NOTICE 'ISO 22301 Compliance: Clause 5.2 requires data isolation';
    RAISE NOTICE 'GDPR Compliance: Article 32 requires security measures';
    RAISE NOTICE '';
END $$;

\echo ''
\echo '================================================'
\echo 'END OF RLS STATUS CHECK'
\echo '================================================'
\echo ''
