-- =====================================================
-- SCENARIO INTELLIGENCE SCHEMA
-- Хранилище сценариев всех уровней (L1-L4)
-- =====================================================

-- Создать схему
CREATE SCHEMA IF NOT EXISTS scenario_intelligence;

-- Основная таблица сценариев
CREATE TABLE IF NOT EXISTS scenario_intelligence.scenarios (
    -- Идентификация
    id TEXT PRIMARY KEY,
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 4),
    type TEXT NOT NULL,

    -- Метаданные
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version TEXT NOT NULL DEFAULT '1.0.0',

    -- Ownership
    module TEXT,
    service TEXT,
    subsystem TEXT,

    -- Content
    title TEXT NOT NULL,
    description TEXT,
    data JSONB NOT NULL,

    -- RLS
    organization_id UUID REFERENCES auth.organizations(id) ON DELETE CASCADE,

    -- Индексы для быстрого поиска
    CONSTRAINT valid_level CHECK (level IN (1, 2, 3, 4))
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_scenarios_level ON scenario_intelligence.scenarios(level);
CREATE INDEX IF NOT EXISTS idx_scenarios_type ON scenario_intelligence.scenarios(type);
CREATE INDEX IF NOT EXISTS idx_scenarios_module ON scenario_intelligence.scenarios(module);
CREATE INDEX IF NOT EXISTS idx_scenarios_service ON scenario_intelligence.scenarios(service);
CREATE INDEX IF NOT EXISTS idx_scenarios_subsystem ON scenario_intelligence.scenarios(subsystem);
CREATE INDEX IF NOT EXISTS idx_scenarios_org ON scenario_intelligence.scenarios(organization_id);
CREATE INDEX IF NOT EXISTS idx_scenarios_created ON scenario_intelligence.scenarios(created_at DESC);

-- GIN индекс для JSONB поиска
CREATE INDEX IF NOT EXISTS idx_scenarios_data_gin ON scenario_intelligence.scenarios USING GIN(data);

-- Full-text search индекс
CREATE INDEX IF NOT EXISTS idx_scenarios_title_search ON scenario_intelligence.scenarios USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_scenarios_description_search ON scenario_intelligence.scenarios USING GIN(to_tsvector('english', COALESCE(description, '')));

-- Таблица для связей между сценариями
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

-- Таблица для tags
CREATE TABLE IF NOT EXISTS scenario_intelligence.scenario_tags (
    scenario_id TEXT NOT NULL REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,

    PRIMARY KEY (scenario_id, tag)
);

CREATE INDEX IF NOT EXISTS idx_scenario_tags_tag ON scenario_intelligence.scenario_tags(tag);

-- Таблица для execution истории
CREATE TABLE IF NOT EXISTS scenario_intelligence.scenario_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id TEXT NOT NULL REFERENCES scenario_intelligence.scenarios(id) ON DELETE CASCADE,

    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL, -- 'running', 'success', 'failed', 'timeout'

    result JSONB,
    error_message TEXT,

    organization_id UUID REFERENCES auth.organizations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_scenario_executions_scenario ON scenario_intelligence.scenario_executions(scenario_id);
CREATE INDEX IF NOT EXISTS idx_scenario_executions_status ON scenario_intelligence.scenario_executions(status);
CREATE INDEX IF NOT EXISTS idx_scenario_executions_started ON scenario_intelligence.scenario_executions(started_at DESC);

-- =====================================================
-- RLS POLICIES
-- =====================================================

-- Включить RLS
ALTER TABLE scenario_intelligence.scenarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.scenario_relations ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.scenario_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.scenario_executions ENABLE ROW LEVEL SECURITY;

-- Политика: Platform scenarios (без organization_id) доступны всем
CREATE POLICY scenario_platform_read ON scenario_intelligence.scenarios
    FOR SELECT
    USING (organization_id IS NULL);

-- Политика: Organization scenarios доступны только своей организации
CREATE POLICY scenario_org_read ON scenario_intelligence.scenarios
    FOR SELECT
    USING (
        organization_id IS NOT NULL
        AND organization_id = auth.get_current_org_id()
    );

-- Политика: Создание сценариев только для своей организации
CREATE POLICY scenario_org_insert ON scenario_intelligence.scenarios
    FOR INSERT
    WITH CHECK (
        organization_id = auth.get_current_org_id()
    );

-- Политика: Обновление только своих сценариев
CREATE POLICY scenario_org_update ON scenario_intelligence.scenarios
    FOR UPDATE
    USING (
        organization_id = auth.get_current_org_id()
    );

-- Политика: Удаление только своих сценариев
CREATE POLICY scenario_org_delete ON scenario_intelligence.scenarios
    FOR DELETE
    USING (
        organization_id = auth.get_current_org_id()
    );

-- Relations: доступ через parent scenario
CREATE POLICY scenario_relations_read ON scenario_intelligence.scenario_relations
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM scenario_intelligence.scenarios s
            WHERE s.id = parent_scenario_id
            AND (s.organization_id IS NULL OR s.organization_id = auth.get_current_org_id())
        )
    );

-- Tags: доступ через scenario
CREATE POLICY scenario_tags_read ON scenario_intelligence.scenario_tags
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM scenario_intelligence.scenarios s
            WHERE s.id = scenario_id
            AND (s.organization_id IS NULL OR s.organization_id = auth.get_current_org_id())
        )
    );

-- Executions: только своя организация
CREATE POLICY scenario_executions_read ON scenario_intelligence.scenario_executions
    FOR SELECT
    USING (organization_id = auth.get_current_org_id());

CREATE POLICY scenario_executions_insert ON scenario_intelligence.scenario_executions
    FOR INSERT
    WITH CHECK (organization_id = auth.get_current_org_id());

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION scenario_intelligence.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = scenario_intelligence, public;

-- Триггер для updated_at
CREATE TRIGGER scenarios_updated_at
    BEFORE UPDATE ON scenario_intelligence.scenarios
    FOR EACH ROW
    EXECUTE FUNCTION scenario_intelligence.update_updated_at();

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
    title TEXT,
    description TEXT,
    module TEXT,
    created_at TIMESTAMPTZ,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.level,
        s.type,
        s.title,
        s.description,
        s.module,
        s.created_at,
        CASE
            WHEN p_query IS NOT NULL THEN
                ts_rank(
                    to_tsvector('english', s.title || ' ' || COALESCE(s.description, '')),
                    plainto_tsquery('english', p_query)
                )
            ELSE 0
        END as rank
    FROM scenario_intelligence.scenarios s
    WHERE
        (p_query IS NULL OR (
            to_tsvector('english', s.title || ' ' || COALESCE(s.description, '')) @@ plainto_tsquery('english', p_query)
        ))
        AND (p_level IS NULL OR s.level = p_level)
        AND (p_type IS NULL OR s.type = p_type)
        AND (p_module IS NULL OR s.module = p_module)
        AND (s.organization_id IS NULL OR s.organization_id = auth.get_current_org_id())
    ORDER BY rank DESC, s.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = scenario_intelligence, auth, public;

-- Функция для статистики
CREATE OR REPLACE FUNCTION scenario_intelligence.get_statistics()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_scenarios', COUNT(*),
        'by_level', (
            SELECT jsonb_object_agg(level::TEXT, count)
            FROM (
                SELECT level, COUNT(*) as count
                FROM scenario_intelligence.scenarios
                WHERE organization_id IS NULL OR organization_id = auth.get_current_org_id()
                GROUP BY level
            ) level_stats
        ),
        'by_type', (
            SELECT jsonb_object_agg(type, count)
            FROM (
                SELECT type, COUNT(*) as count
                FROM scenario_intelligence.scenarios
                WHERE organization_id IS NULL OR organization_id = auth.get_current_org_id()
                GROUP BY type
            ) type_stats
        ),
        'by_module', (
            SELECT jsonb_object_agg(module, count)
            FROM (
                SELECT module, COUNT(*) as count
                FROM scenario_intelligence.scenarios
                WHERE organization_id IS NULL OR organization_id = auth.get_current_org_id()
                AND module IS NOT NULL
                GROUP BY module
            ) module_stats
        )
    ) INTO result
    FROM scenario_intelligence.scenarios
    WHERE organization_id IS NULL OR organization_id = auth.get_current_org_id();

    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER
SET search_path = scenario_intelligence, auth, public;

-- =====================================================
-- GRANTS
-- =====================================================

-- Доступ для authenticated users
GRANT USAGE ON SCHEMA scenario_intelligence TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA scenario_intelligence TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA scenario_intelligence TO authenticated;

-- Доступ для service role (для генераторов)
GRANT ALL ON SCHEMA scenario_intelligence TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA scenario_intelligence TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA scenario_intelligence TO service_role;

COMMENT ON SCHEMA scenario_intelligence IS 'Scenario Intelligence: хранилище сценариев всех уровней (L1-L4)';
COMMENT ON TABLE scenario_intelligence.scenarios IS 'Основная таблица сценариев с полным JSONB содержимым';
COMMENT ON TABLE scenario_intelligence.scenario_relations IS 'Связи между сценариями (иерархия, зависимости)';
COMMENT ON TABLE scenario_intelligence.scenario_tags IS 'Теги для категоризации сценариев';
COMMENT ON TABLE scenario_intelligence.scenario_executions IS 'История выполнения сценариев';
