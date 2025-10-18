-- ПРОСТОЕ РЕШЕНИЕ ДЛЯ DIGITAL TWIN
-- Выполните весь этот файл в Supabase SQL Editor

-- 1. СОЗДАЕМ ТАБЛИЦУ organization_profiles (НЕ ТРОГАЕМ organizations VIEW)
CREATE TABLE IF NOT EXISTS organization_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pgpx_subject_id UUID,
    org_code VARCHAR(255) UNIQUE NOT NULL,
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

-- 2. ОБНОВЛЯЕМ digital_twins чтобы работать с organization_profiles
ALTER TABLE digital_twins 
    ADD COLUMN IF NOT EXISTS organization_profile_id UUID;

-- 3. СОЗДАЕМ ИНДЕКСЫ
CREATE INDEX IF NOT EXISTS idx_org_prof_pgpx ON organization_profiles(pgpx_subject_id);
CREATE INDEX IF NOT EXISTS idx_org_prof_active ON organization_profiles(is_active);
CREATE INDEX IF NOT EXISTS idx_org_prof_code ON organization_profiles(org_code);
CREATE INDEX IF NOT EXISTS idx_twin_org_profile ON digital_twins(organization_profile_id);

-- 4. ДАЕМ ПРАВА ДОСТУПА
GRANT ALL ON organization_profiles TO authenticated;
GRANT ALL ON organization_profiles TO anon;

-- 5. ВКЛЮЧАЕМ RLS (Row Level Security)
ALTER TABLE organization_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE digital_twins ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;
ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- 6. СОЗДАЕМ ПОЛИТИКИ ДОСТУПА (пока разрешаем все для тестирования)
CREATE POLICY "Allow all for organization_profiles" ON organization_profiles
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for digital_twins" ON digital_twins
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for simulations" ON simulations
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for metrics" ON metrics
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for predictions" ON predictions
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for reports" ON reports
    FOR ALL USING (true) WITH CHECK (true);

-- 7. ПРОВЕРКА
SELECT 
    'ГОТОВО! Таблицы созданы:' as message
UNION ALL
SELECT 
    '- ' || table_name || ' (' || table_type || ')'
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('organization_profiles', 'digital_twins', 'simulations', 'metrics', 'predictions', 'reports')
ORDER BY 1;