-- СОЗДАНИЕ ТАБЛИЦЫ organization_profiles (ВМЕСТО organizations)
-- Выполните весь скрипт в Supabase SQL Editor

-- 1. Создаем таблицу organization_profiles
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

-- 2. Обновляем digital_twins чтобы использовать organization_profiles
ALTER TABLE digital_twins 
    ADD COLUMN organization_profile_id UUID;

-- 3. Создаем индексы для organization_profiles
CREATE INDEX idx_org_prof_pgpx ON organization_profiles(pgpx_subject_id);
CREATE INDEX idx_org_prof_active ON organization_profiles(is_active);
CREATE INDEX idx_org_prof_code ON organization_profiles(org_code);

-- 4. Обновляем индекс для digital_twins
CREATE INDEX idx_twin_org_profile ON digital_twins(organization_profile_id);

-- 5. Даем права доступа
GRANT ALL ON organization_profiles TO authenticated;

-- 6. Проверка результата
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('organization_profiles', 'digital_twins')
ORDER BY table_name;