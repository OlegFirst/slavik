-- СОЗДАНИЕ ТАБЛИЦ ДЛЯ DIGITAL TWIN - РАБОЧАЯ ВЕРСИЯ
-- Выполняйте ВСЕ СРАЗУ в Supabase SQL Editor

-- =============================================
-- СОЗДАЕМ ВСЕ ТАБЛИЦЫ БЕЗ FOREIGN KEYS
-- =============================================

-- 1. Таблица organizations
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pgpx_subject_id UUID,
    organization_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    mission TEXT,
    description TEXT,
    size INTEGER,
    annual_budget DECIMAL(15, 2),
    website VARCHAR(255),
    contact_info JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID,
    is_active BOOLEAN DEFAULT true
);

-- 2. Таблица digital_twins (БЕЗ FOREIGN KEY)
CREATE TABLE IF NOT EXISTS digital_twins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id VARCHAR(255) UNIQUE NOT NULL,
    organization_id UUID,  -- Без REFERENCES
    name VARCHAR(255) NOT NULL,
    configuration JSONB DEFAULT '{}',
    state JSONB DEFAULT '{}',
    health_score DECIMAL(3, 2) DEFAULT 0.5,
    efficiency_score DECIMAL(3, 2) DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- 3. Таблица simulations (БЕЗ FOREIGN KEY)
CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id VARCHAR(255) UNIQUE NOT NULL,
    twin_id UUID,  -- Без REFERENCES
    scenario VARCHAR(100) NOT NULL,
    parameters JSONB DEFAULT '{}',
    results JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Таблица metrics (БЕЗ FOREIGN KEY)
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID,  -- Без REFERENCES
    metric_type VARCHAR(100) NOT NULL,
    value DECIMAL(15, 4) NOT NULL,
    unit VARCHAR(50),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Таблица predictions (БЕЗ FOREIGN KEY)
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID,  -- Без REFERENCES
    prediction_type VARCHAR(100) NOT NULL,
    predicted_value DECIMAL(15, 4),
    confidence_score DECIMAL(3, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Таблица reports (БЕЗ FOREIGN KEY)
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    twin_id UUID,  -- Без REFERENCES
    report_type VARCHAR(100) NOT NULL,
    title VARCHAR(255),
    content JSONB NOT NULL,
    format VARCHAR(20) DEFAULT 'json',
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    is_public BOOLEAN DEFAULT false
);

-- =============================================
-- СОЗДАЕМ ИНДЕКСЫ
-- =============================================

CREATE INDEX IF NOT EXISTS idx_org_pgpx ON organizations(pgpx_subject_id);
CREATE INDEX IF NOT EXISTS idx_org_active ON organizations(is_active);
CREATE INDEX IF NOT EXISTS idx_twin_org ON digital_twins(organization_id);
CREATE INDEX IF NOT EXISTS idx_twin_active ON digital_twins(is_active);
CREATE INDEX IF NOT EXISTS idx_sim_twin ON simulations(twin_id);
CREATE INDEX IF NOT EXISTS idx_metrics_twin ON metrics(twin_id);
CREATE INDEX IF NOT EXISTS idx_pred_twin ON predictions(twin_id);
CREATE INDEX IF NOT EXISTS idx_reports_twin ON reports(twin_id);

-- =============================================
-- ДОБАВЛЯЕМ FOREIGN KEYS (если нужно)
-- =============================================
-- Раскомментируйте если хотите добавить связи:
/*
ALTER TABLE digital_twins 
    ADD CONSTRAINT fk_twin_org 
    FOREIGN KEY (organization_id) 
    REFERENCES organizations(id) 
    ON DELETE CASCADE;

ALTER TABLE simulations 
    ADD CONSTRAINT fk_sim_twin 
    FOREIGN KEY (twin_id) 
    REFERENCES digital_twins(id) 
    ON DELETE CASCADE;

ALTER TABLE metrics 
    ADD CONSTRAINT fk_metrics_twin 
    FOREIGN KEY (twin_id) 
    REFERENCES digital_twins(id) 
    ON DELETE CASCADE;

ALTER TABLE predictions 
    ADD CONSTRAINT fk_pred_twin 
    FOREIGN KEY (twin_id) 
    REFERENCES digital_twins(id) 
    ON DELETE CASCADE;

ALTER TABLE reports 
    ADD CONSTRAINT fk_reports_twin 
    FOREIGN KEY (twin_id) 
    REFERENCES digital_twins(id) 
    ON DELETE CASCADE;
*/

-- =============================================
-- GRANT PERMISSIONS
-- =============================================

GRANT ALL ON organizations TO authenticated;
GRANT ALL ON digital_twins TO authenticated;
GRANT ALL ON simulations TO authenticated;
GRANT ALL ON metrics TO authenticated;
GRANT ALL ON predictions TO authenticated;
GRANT ALL ON reports TO authenticated;

-- =============================================
-- ПРОВЕРКА РЕЗУЛЬТАТА
-- =============================================

SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('organizations', 'digital_twins', 'simulations', 'metrics', 'predictions', 'reports')
ORDER BY table_name;