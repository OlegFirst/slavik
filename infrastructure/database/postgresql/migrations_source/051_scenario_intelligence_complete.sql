-- =====================================================
-- SCENARIO INTELLIGENCE - COMPLETE MIGRATION
-- Полная миграция с RLS, функциями, триггерами
-- =====================================================

-- Создать схему
CREATE SCHEMA IF NOT EXISTS scenario_intelligence;

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Функция для получения текущей организации (wrapper)
CREATE OR REPLACE FUNCTION scenario_intelligence.get_current_org_id()
RETURNS UUID AS $$
BEGIN
    RETURN public.current_org();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public, scenario_intelligence;

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION scenario_intelligence.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = scenario_intelligence, public;

-- Функция для обновления search vector
CREATE OR REPLACE FUNCTION scenario_intelligence.update_scenario_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    -- Extract title and description from JSONB content
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.content->>'title', '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.content->'description'->>'summary', '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.content->'description'->>'purpose', '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = scenario_intelligence, public;

-- =====================================================
-- MAIN TABLES
-- =====================================================

-- Основная таблица сценариев
CREATE TABLE IF NOT EXISTS scenario_intelligence.scenarios (
    -- Идентификация
    id TEXT PRIMARY KEY,
    version TEXT NOT NULL DEFAULT '1.0.0',

    -- Временные метки
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Классификация
    level INTEGER NOT NULL CHECK (level >= 1 AND level <= 4),
    type TEXT NOT NULL,
    pillar TEXT,

    -- Иерархия
    module TEXT,
    subsystem TEXT,

    -- Содержимое (полный JSONB сценарий)
    content JSONB NOT NULL,

    -- Статус
    status TEXT NOT NULL DEFAULT 'active',
    deprecated_at TIMESTAMPTZ,
    deprecated_reason TEXT,

    -- Compliance
    iso_clauses TEXT[],
    compliance_tags TEXT[],

    -- Full-text search
    search_vector tsvector,

    -- Multi-tenancy (NULL = platform scenario)
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE
);

-- Уникальность: один сценарий может иметь несколько версий
CREATE UNIQUE INDEX IF NOT EXISTS scenarios_unique_version
ON scenario_intelligence.scenarios(id, version);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_scenarios_level ON scenario_intelligence.scenarios(level);
CREATE INDEX IF NOT EXISTS idx_scenarios_type ON scenario_intelligence.scenarios(type);
CREATE INDEX IF NOT EXISTS idx_scenarios_status ON scenario_intelligence.scenarios(status);
CREATE INDEX IF NOT EXISTS idx_scenarios_module ON scenario_intelligence.scenarios(module) WHERE module IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_scenarios_subsystem ON scenario_intelligence.scenarios(subsystem) WHERE subsystem IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_scenarios_created ON scenario_intelligence.scenarios(created_at DESC);

-- GIN индекс для JSONB поиска
CREATE INDEX IF NOT EXISTS idx_scenarios_content ON scenario_intelligence.scenarios USING GIN(content);

-- Full-text search индекс
CREATE INDEX IF NOT EXISTS idx_scenarios_search ON scenario_intelligence.scenarios USING GIN(search_vector);

-- Триггеры
DROP TRIGGER IF EXISTS scenarios_update_timestamp ON scenario_intelligence.scenarios;
CREATE TRIGGER scenarios_update_timestamp
    BEFORE UPDATE ON scenario_intelligence.scenarios
    FOR EACH ROW
    EXECUTE FUNCTION scenario_intelligence.update_updated_at();

DROP TRIGGER IF EXISTS scenarios_update_search_vector ON scenario_intelligence.scenarios;
CREATE TRIGGER scenarios_update_search_vector
    BEFORE INSERT OR UPDATE ON scenario_intelligence.scenarios
    FOR EACH ROW
    EXECUTE FUNCTION scenario_intelligence.update_scenario_search_vector();

-- Таблица связей между сценариями
CREATE TABLE IF NOT EXISTS scenario_intelligence.scenario_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_scenario_id TEXT NOT NULL REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    child_scenario_id TEXT NOT NULL REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL, -- 'uses', 'depends_on', 'extends', 'part_of'

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_relation UNIQUE(parent_scenario_id, child_scenario_id, relation_type)
);

CREATE INDEX IF NOT EXISTS idx_scenario_relations_parent ON scenario_intelligence.scenario_relations(parent_scenario_id);
CREATE INDEX IF NOT EXISTS idx_scenario_relations_child ON scenario_intelligence.scenario_relations(child_scenario_id);

-- Таблица тегов
CREATE TABLE IF NOT EXISTS scenario_intelligence.scenario_tags (
    scenario_id TEXT NOT NULL REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,

    PRIMARY KEY (scenario_id, tag)
);

CREATE INDEX IF NOT EXISTS idx_scenario_tags_tag ON scenario_intelligence.scenario_tags(tag);

-- Таблица истории выполнения (уже существует с расширенной структурой)
-- Просто создадим дополнительные индексы если их нет

CREATE INDEX IF NOT EXISTS idx_executions_scenario ON scenario_intelligence.executions(scenario_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON scenario_intelligence.executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_executed_at ON scenario_intelligence.executions(executed_at DESC);

-- Таблица паттернов
CREATE TABLE IF NOT EXISTS scenario_intelligence.patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    pattern_data JSONB NOT NULL,
    confidence FLOAT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Таблица предсказаний
CREATE TABLE IF NOT EXISTS scenario_intelligence.predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    current_scenario_id TEXT REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    predicted_scenario_id TEXT REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    confidence FLOAT NOT NULL,
    reasoning JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Таблица статистики
CREATE TABLE IF NOT EXISTS scenario_intelligence.statistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id TEXT REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    metric_value FLOAT NOT NULL,
    metadata JSONB,

    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Таблица evidence vault
CREATE TABLE IF NOT EXISTS scenario_intelligence.evidence_vault (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id TEXT REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    evidence_type TEXT NOT NULL,
    evidence_data JSONB NOT NULL,
    source TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Включить RLS на всех таблицах
ALTER TABLE scenario_intelligence.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.scenario_relations ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.scenario_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.statistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.evidence_vault ENABLE ROW LEVEL SECURITY;

-- ===== SCENARIOS POLICIES =====

-- Platform scenarios (organization_id IS NULL) доступны всем
DROP POLICY IF EXISTS scenario_platform_read ON scenario_intelligence.scenarios;
CREATE POLICY scenario_platform_read ON scenario_intelligence.scenarios
    FOR SELECT
    USING (organization_id IS NULL);

-- Organization scenarios доступны только своей организации
DROP POLICY IF EXISTS scenario_org_read ON scenario_intelligence.scenarios;
CREATE POLICY scenario_org_read ON scenario_intelligence.scenarios
    FOR SELECT
    USING (
        organization_id IS NOT NULL
        AND organization_id = scenario_intelligence.get_current_org_id()
    );

-- Создание сценариев только для своей организации
DROP POLICY IF EXISTS scenario_org_insert ON scenario_intelligence.scenarios;
CREATE POLICY scenario_org_insert ON scenario_intelligence.scenarios
    FOR INSERT
    WITH CHECK (
        organization_id = scenario_intelligence.get_current_org_id()
        OR organization_id IS NULL  -- Разрешить создание platform scenarios
    );

-- Обновление только своих сценариев
DROP POLICY IF EXISTS scenario_org_update ON scenario_intelligence.scenarios;
CREATE POLICY scenario_org_update ON scenario_intelligence.scenarios
    FOR UPDATE
    USING (
        organization_id = scenario_intelligence.get_current_org_id()
        OR organization_id IS NULL  -- Разрешить обновление platform scenarios
    );

-- Удаление только своих сценариев
DROP POLICY IF EXISTS scenario_org_delete ON scenario_intelligence.scenarios;
CREATE POLICY scenario_org_delete ON scenario_intelligence.scenarios
    FOR DELETE
    USING (
        organization_id = scenario_intelligence.get_current_org_id()
        OR organization_id IS NULL  -- Разрешить удаление platform scenarios
    );

-- ===== RELATIONS POLICIES =====

DROP POLICY IF EXISTS scenario_relations_read ON scenario_intelligence.scenario_relations;
CREATE POLICY scenario_relations_read ON scenario_intelligence.scenario_relations
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM scenario_intelligence.scenarios s
            WHERE s.id = parent_scenario_id
            AND (s.organization_id IS NULL OR s.organization_id = scenario_intelligence.get_current_org_id())
        )
    );

DROP POLICY IF EXISTS scenario_relations_manage ON scenario_intelligence.scenario_relations;
CREATE POLICY scenario_relations_manage ON scenario_intelligence.scenario_relations
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM scenario_intelligence.scenarios s
            WHERE s.id = parent_scenario_id
            AND (s.organization_id IS NULL OR s.organization_id = scenario_intelligence.get_current_org_id())
        )
    );

-- ===== TAGS POLICIES =====

DROP POLICY IF EXISTS scenario_tags_read ON scenario_intelligence.scenario_tags;
CREATE POLICY scenario_tags_read ON scenario_intelligence.scenario_tags
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM scenario_intelligence.scenarios s
            WHERE s.id = scenario_id
            AND (s.organization_id IS NULL OR s.organization_id = scenario_intelligence.get_current_org_id())
        )
    );

DROP POLICY IF EXISTS scenario_tags_manage ON scenario_intelligence.scenario_tags;
CREATE POLICY scenario_tags_manage ON scenario_intelligence.scenario_tags
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM scenario_intelligence.scenarios s
            WHERE s.id = scenario_id
            AND (s.organization_id IS NULL OR s.organization_id = scenario_intelligence.get_current_org_id())
        )
    );

-- ===== EXECUTIONS POLICIES =====
-- Executions table уже имеет свою структуру, просто разрешим доступ всем

DROP POLICY IF EXISTS scenario_executions_all ON scenario_intelligence.executions;
CREATE POLICY scenario_executions_all ON scenario_intelligence.executions
    FOR ALL
    USING (true);

-- ===== OTHER TABLES POLICIES (patterns, predictions, statistics, evidence) =====
-- Эти таблицы доступны всем (они не привязаны к организациям)

DROP POLICY IF EXISTS patterns_all ON scenario_intelligence.patterns;
CREATE POLICY patterns_all ON scenario_intelligence.patterns FOR ALL USING (true);

DROP POLICY IF EXISTS predictions_all ON scenario_intelligence.predictions;
CREATE POLICY predictions_all ON scenario_intelligence.predictions FOR ALL USING (true);

DROP POLICY IF EXISTS statistics_all ON scenario_intelligence.statistics;
CREATE POLICY statistics_all ON scenario_intelligence.statistics FOR ALL USING (true);

DROP POLICY IF EXISTS evidence_vault_all ON scenario_intelligence.evidence_vault;
CREATE POLICY evidence_vault_all ON scenario_intelligence.evidence_vault FOR ALL USING (true);

-- =====================================================
-- BUSINESS FUNCTIONS
-- =====================================================

-- Функция для поиска сценариев
CREATE OR REPLACE FUNCTION scenario_intelligence.search_scenarios(
    p_query TEXT DEFAULT NULL,
    p_level INTEGER DEFAULT NULL,
    p_type TEXT DEFAULT NULL,
    p_module TEXT DEFAULT NULL,
    p_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    id TEXT,
    level INTEGER,
    type TEXT,
    module TEXT,
    created_at TIMESTAMPTZ,
    content JSONB,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.level,
        s.type,
        s.module,
        s.created_at,
        s.content,
        CASE
            WHEN p_query IS NOT NULL THEN
                ts_rank(s.search_vector, plainto_tsquery('english', p_query))
            ELSE 0
        END as rank
    FROM scenario_intelligence.scenarios s
    WHERE
        (p_query IS NULL OR s.search_vector @@ plainto_tsquery('english', p_query))
        AND (p_level IS NULL OR s.level = p_level)
        AND (p_type IS NULL OR s.type = p_type)
        AND (p_module IS NULL OR s.module = p_module)
        AND (s.organization_id IS NULL OR s.organization_id = scenario_intelligence.get_current_org_id())
        AND s.status = 'active'
    ORDER BY rank DESC, s.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = scenario_intelligence, public;

-- Функция для получения статистики
CREATE OR REPLACE FUNCTION scenario_intelligence.get_statistics()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    current_org UUID;
BEGIN
    current_org := scenario_intelligence.get_current_org_id();

    SELECT jsonb_build_object(
        'total_scenarios', COUNT(*),
        'by_level', (
            SELECT jsonb_object_agg(level::TEXT, count)
            FROM (
                SELECT level, COUNT(*) as count
                FROM scenario_intelligence.scenarios
                WHERE organization_id IS NULL OR organization_id = current_org
                GROUP BY level
            ) level_stats
        ),
        'by_type', (
            SELECT jsonb_object_agg(type, count)
            FROM (
                SELECT type, COUNT(*) as count
                FROM scenario_intelligence.scenarios
                WHERE organization_id IS NULL OR organization_id = current_org
                GROUP BY type
            ) type_stats
        ),
        'by_module', (
            SELECT jsonb_object_agg(module, count)
            FROM (
                SELECT module, COUNT(*) as count
                FROM scenario_intelligence.scenarios
                WHERE (organization_id IS NULL OR organization_id = current_org)
                AND module IS NOT NULL
                GROUP BY module
            ) module_stats
        )
    ) INTO result
    FROM scenario_intelligence.scenarios
    WHERE organization_id IS NULL OR organization_id = current_org;

    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = scenario_intelligence, public;

-- =====================================================
-- GRANTS
-- =====================================================

-- Доступ для authenticated users
GRANT USAGE ON SCHEMA scenario_intelligence TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA scenario_intelligence TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA scenario_intelligence TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA scenario_intelligence TO authenticated;

-- Доступ для service role (для генераторов и сервисов)
GRANT ALL ON SCHEMA scenario_intelligence TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA scenario_intelligence TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA scenario_intelligence TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA scenario_intelligence TO service_role;

-- Доступ для anon (только чтение platform scenarios)
GRANT USAGE ON SCHEMA scenario_intelligence TO anon;
GRANT SELECT ON scenario_intelligence.scenarios TO anon;
GRANT EXECUTE ON FUNCTION scenario_intelligence.search_scenarios TO anon;
GRANT EXECUTE ON FUNCTION scenario_intelligence.get_statistics TO anon;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON SCHEMA scenario_intelligence IS 'Scenario Intelligence: хранилище сценариев всех уровней (L1-L4) с полной поддержкой RLS';
COMMENT ON TABLE scenario_intelligence.scenarios IS 'Основная таблица сценариев с полным JSONB содержимым';
COMMENT ON TABLE scenario_intelligence.scenario_relations IS 'Связи между сценариями (иерархия, зависимости)';
COMMENT ON TABLE scenario_intelligence.scenario_tags IS 'Теги для категоризации сценариев';
COMMENT ON TABLE scenario_intelligence.executions IS 'История выполнения сценариев';
COMMENT ON TABLE scenario_intelligence.patterns IS 'Обнаруженные паттерны в сценариях';
COMMENT ON TABLE scenario_intelligence.predictions IS 'Предсказания следующих сценариев';
COMMENT ON TABLE scenario_intelligence.statistics IS 'Статистика по сценариям';
COMMENT ON TABLE scenario_intelligence.evidence_vault IS 'Хранилище доказательств выполнения';

COMMENT ON FUNCTION scenario_intelligence.get_current_org_id() IS 'Получить ID текущей организации из контекста';
COMMENT ON FUNCTION scenario_intelligence.search_scenarios IS 'Полнотекстовый поиск сценариев с фильтрацией';
COMMENT ON FUNCTION scenario_intelligence.get_statistics IS 'Получить статистику по сценариям для текущей организации';
