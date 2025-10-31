-- ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С ORGANIZATIONS VIEW
-- Выполните по шагам в Supabase SQL Editor

-- =============================================
-- ШАГ 1: ПРОВЕРКА ЧТО ЭТО ЗА VIEW
-- =============================================
-- Посмотрим определение view organizations:

SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'organizations';

-- Посмотрим определение view:
SELECT pg_get_viewdef('organizations', true);

-- =============================================
-- ШАГ 2: УДАЛЯЕМ VIEW И СОЗДАЕМ ТАБЛИЦУ
-- =============================================
-- ВНИМАНИЕ: Это удалит view organizations!
-- Убедитесь что это не повредит другим частям системы

-- Сначала удаляем view
DROP VIEW IF EXISTS organizations CASCADE;

-- Теперь создаем ТАБЛИЦУ organizations
CREATE TABLE organizations (
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

-- Даем права доступа
GRANT ALL ON organizations TO authenticated;

-- =============================================
-- ШАГ 3: АЛЬТЕРНАТИВНЫЙ ВАРИАНТ
-- =============================================
-- Если не хотите удалять view, создайте таблицу с другим именем:

CREATE TABLE IF NOT EXISTS organization_profiles (
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

-- И обновляем digital_twins чтобы ссылаться на новую таблицу:
ALTER TABLE digital_twins 
    RENAME COLUMN organization_id TO organization_profile_id;

-- =============================================
-- ШАГ 4: ПРОВЕРКА РЕЗУЛЬТАТА
-- =============================================

SELECT 
    table_name,
    table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('organizations', 'organization_profiles', 'digital_twins')
ORDER BY table_name;