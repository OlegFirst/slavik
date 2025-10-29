-- КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ БЕЗОПАСНОСТИ
-- Исправляет RLS проблемы для BCM Platform

-- 1. ИСПРАВЛЕНИЕ api_keys таблицы
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

-- API ключи должны быть только server-side (РЕКОМЕНДУЕТСЯ)
-- Без политик = только service role может получить доступ
-- Это самый безопасный вариант для секретов

-- Альтернатива если нужен клиентский доступ:
-- CREATE POLICY "User own API keys" ON public.api_keys
--   FOR ALL TO authenticated
--   USING (user_id = auth.uid())
--   WITH CHECK (user_id = auth.uid());

-- 2. ИСПРАВЛЕНИЕ workflow_schedules (если существует)
DO $$
BEGIN
  IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'workflow_schedules') THEN
    ALTER TABLE public.workflow_schedules ENABLE ROW LEVEL SECURITY;

    -- User-ownership модель
    CREATE POLICY "User workflow schedules" ON public.workflow_schedules
      FOR ALL TO authenticated
      USING (user_id = auth.uid())
      WITH CHECK (user_id = auth.uid());

    -- Индекс для производительности
    CREATE INDEX IF NOT EXISTS idx_workflow_schedules_user_id
    ON public.workflow_schedules (user_id);
  END IF;
END $$;

-- 3. ДОПОЛНИТЕЛЬНЫЕ БЕЗОПАСНЫЕ ТАБЛИЦЫ
CREATE TABLE IF NOT EXISTS public.user_preferences (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,

  preferences JSONB DEFAULT '{}',
  ui_settings JSONB DEFAULT '{}',

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

CREATE POLICY "User own preferences" ON public.user_preferences
  FOR ALL TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id
ON public.user_preferences (user_id);

-- 4. ФУНКЦИЯ ДЛЯ ПРОВЕРКИ БЕЗОПАСНОСТИ
CREATE OR REPLACE FUNCTION public.check_rls_enabled()
RETURNS TABLE(
  table_name TEXT,
  rls_enabled BOOLEAN,
  policies_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    t.tablename::TEXT,
    t.rowsecurity AS rls_enabled,
    COUNT(p.policyname) AS policies_count
  FROM pg_tables t
  LEFT JOIN pg_policies p ON p.tablename = t.tablename AND p.schemaname = t.schemaname
  WHERE t.schemaname = 'public'
    AND t.tablename NOT LIKE 'pg_%'
    AND t.tablename NOT LIKE 'information_schema%'
  GROUP BY t.tablename, t.rowsecurity
  ORDER BY t.tablename;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. ПРОВЕРКА ВСЕХ ТАБЛИЦ НА RLS
-- Запустите эту функцию чтобы увидеть статус RLS всех таблиц:
-- SELECT * FROM check_rls_enabled();

-- 6. БЕЗОПАСНЫЕ РОЛИ
-- Убедитесь что anon роль имеет минимальные права
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM anon;

-- Authenticated роль должна иметь только необходимые права
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM authenticated;

-- Дайте права только на нужные таблицы:
GRANT SELECT, INSERT, UPDATE, DELETE ON public.bcm_users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_activities TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.ai_conversations TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_preferences TO authenticated;

-- НЕ давайте права на api_keys - только service role!
-- GRANT ... ON public.api_keys TO authenticated; -- НЕ ДЕЛАЙТЕ ЭТО!

-- 7. AUDIT LOG ФУНКЦИЯ
CREATE OR REPLACE FUNCTION public.audit_rls_access()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_activities (user_id, action, resource, resource_id, details)
  VALUES (
    auth.uid(),
    TG_OP,
    TG_TABLE_NAME,
    COALESCE(NEW.id::TEXT, OLD.id::TEXT),
    jsonb_build_object(
      'table', TG_TABLE_NAME,
      'operation', TG_OP,
      'timestamp', NOW()
    )
  );

  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Применить audit trigger на критические таблицы
CREATE TRIGGER audit_api_keys
  AFTER INSERT OR UPDATE OR DELETE ON public.api_keys
  FOR EACH ROW EXECUTE FUNCTION public.audit_rls_access();