-- МИНИМАЛЬНЫЕ ИСПРАВЛЕНИЯ БЕЗОПАСНОСТИ (БЕЗ ПРЕДПОЛОЖЕНИЙ)

-- 1. ТОЛЬКО ВКЛЮЧАЕМ RLS НА КРИТИЧЕСКИХ ТАБЛИЦАХ
-- Без политик = только service role доступ (самый безопасный)

-- API ключи (КРИТИЧНО)
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- Workflow schedules (если существует)
DO $$
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'workflow_schedules') THEN
    ALTER TABLE public.workflow_schedules ENABLE ROW LEVEL SECURITY;
    -- Без политик = полная защита, только service role
  END IF;
END $$;

-- 2. ПРОВЕРЯЕМ КАКИЕ СТОЛБЦЫ ЕСТЬ В ТАБЛИЦАХ
CREATE OR REPLACE FUNCTION public.check_table_columns(table_name_param TEXT)
RETURNS TABLE(column_name TEXT, data_type TEXT) AS $$
BEGIN
  RETURN QUERY
  SELECT c.column_name::TEXT, c.data_type::TEXT
  FROM information_schema.columns c
  WHERE c.table_schema = 'public'
    AND c.table_name = table_name_param
  ORDER BY c.ordinal_position;
END;
$$ LANGUAGE plpgsql;

-- 3. БЕЗОПАСНЫЕ БАЗОВЫЕ ПРАВА
-- Убираем все права у публичных ролей
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon;

-- Minimal права для authenticated (только на безопасные таблицы)
GRANT SELECT, INSERT, UPDATE, DELETE ON public.bcm_users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_activities TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.ai_conversations TO authenticated;

-- НЕ даем права на api_keys и workflow_schedules!

-- 4. ФУНКЦИЯ ПРОВЕРКИ БЕЗОПАСНОСТИ
CREATE OR REPLACE FUNCTION public.security_audit()
RETURNS TABLE(
  table_name TEXT,
  rls_enabled BOOLEAN,
  anon_grants TEXT[],
  auth_grants TEXT[]
) AS $$
BEGIN
  RETURN QUERY
  WITH table_privileges AS (
    SELECT
      grantee,
      table_name,
      array_agg(privilege_type) as privileges
    FROM information_schema.table_privileges
    WHERE table_schema = 'public'
      AND grantee IN ('anon', 'authenticated')
    GROUP BY grantee, table_name
  )
  SELECT
    t.tablename::TEXT,
    t.rowsecurity AS rls_enabled,
    COALESCE(anon_priv.privileges, '{}') AS anon_grants,
    COALESCE(auth_priv.privileges, '{}') AS auth_grants
  FROM pg_tables t
  LEFT JOIN table_privileges anon_priv ON anon_priv.table_name = t.tablename AND anon_priv.grantee = 'anon'
  LEFT JOIN table_privileges auth_priv ON auth_priv.table_name = t.tablename AND auth_priv.grantee = 'authenticated'
  WHERE t.schemaname = 'public'
  ORDER BY t.tablename;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. ЗАПУСТИТЕ ДЛЯ ДИАГНОСТИКИ:
-- SELECT * FROM security_audit();
-- SELECT * FROM check_table_columns('workflow_schedules');
-- SELECT * FROM check_table_columns('api_keys');

-- ВЫВОДЫ:
-- 1. RLS включена на критических таблицах
-- 2. БЕЗ политик = максимальная безопасность
-- 3. Только service role может получить доступ
-- 4. Функции диагностики для проверки структуры