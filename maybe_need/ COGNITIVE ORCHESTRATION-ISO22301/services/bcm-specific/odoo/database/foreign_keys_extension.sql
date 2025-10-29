-- =============================================
-- BCM Centralized Architecture - Additional Foreign Keys
-- Дополнительные внешние ключи между сервисами
-- =============================================

-- Service-to-Service Foreign Keys
-- Связи между сервисами

-- 1. Event Registry to Service Registry
-- Связь событий с сервисами
ALTER TABLE bcm_event_registry
ADD CONSTRAINT fk_event_source_service
FOREIGN KEY (source_service) REFERENCES bcm_service_registry(service_name)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 2. CRM Projects to Odoo Partners
-- Связь проектов BCM с партнерами Odoo
ALTER TABLE bcm_crm_projects
ADD CONSTRAINT fk_crm_project_partner
FOREIGN KEY (partner_id) REFERENCES res_partner(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- 3. Workspaces to CRM Projects
-- Связь рабочих пространств с проектами
ALTER TABLE bcm_workspaces
ADD CONSTRAINT fk_workspace_crm_project
FOREIGN KEY (crm_project_id) REFERENCES bcm_crm_projects(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 4. Contexts to Workspaces
-- Связь контекстов с рабочими пространствами
ALTER TABLE bcm_contexts
ADD CONSTRAINT fk_context_workspace
FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 5. All BCM modules to Workspaces
-- Связь всех модулей BCM с рабочими пространствами

-- Audits to Workspaces
ALTER TABLE bcm_audits
ADD CONSTRAINT fk_audit_workspace
FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- Incidents to Workspaces
ALTER TABLE bcm_incidents
ADD CONSTRAINT fk_incident_workspace
FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- Plans to Workspaces
ALTER TABLE bcm_plans
ADD CONSTRAINT fk_plan_workspace
FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- Training to Workspaces
ALTER TABLE bcm_training
ADD CONSTRAINT fk_training_workspace
FOREIGN KEY (workspace_id) REFERENCES bcm_workspaces(id)
ON DELETE CASCADE ON UPDATE CASCADE;

-- 6. Cross-module relationships
-- Взаимосвязи между модулями

-- Incidents to Plans (incident response plans)
ALTER TABLE bcm_incidents
ADD CONSTRAINT fk_incident_response_plan
FOREIGN KEY (response_plan_id) REFERENCES bcm_plans(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- Training to Plans (training plans)
ALTER TABLE bcm_training
ADD CONSTRAINT fk_training_plan
FOREIGN KEY (plan_id) REFERENCES bcm_plans(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- Audits to Plans (audit findings implementation)
ALTER TABLE bcm_audits
ADD CONSTRAINT fk_audit_improvement_plan
FOREIGN KEY (improvement_plan_id) REFERENCES bcm_plans(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- 7. User Management Foreign Keys
-- Внешние ключи для управления пользователями

-- Workspace users to Odoo users
ALTER TABLE bcm_workspaces
ADD CONSTRAINT fk_workspace_responsible_user
FOREIGN KEY (responsible_user_id) REFERENCES res_users(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- Audits to users
ALTER TABLE bcm_audits
ADD CONSTRAINT fk_audit_auditor
FOREIGN KEY (auditor_id) REFERENCES res_users(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- Incidents to users
ALTER TABLE bcm_incidents
ADD CONSTRAINT fk_incident_reporter
FOREIGN KEY (reporter_id) REFERENCES res_users(id)
ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE bcm_incidents
ADD CONSTRAINT fk_incident_assignee
FOREIGN KEY (assigned_to) REFERENCES res_users(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- Plans to users
ALTER TABLE bcm_plans
ADD CONSTRAINT fk_plan_owner
FOREIGN KEY (owner_id) REFERENCES res_users(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- Training to users
ALTER TABLE bcm_training
ADD CONSTRAINT fk_training_instructor
FOREIGN KEY (instructor_id) REFERENCES res_users(id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- 8. Service Health to Service Registry
-- Здоровье сервисов связано с реестром сервисов
ALTER TABLE bcm_service_health
ADD CONSTRAINT fk_health_service
FOREIGN KEY (service_name) REFERENCES bcm_service_registry(service_name)
ON DELETE CASCADE ON UPDATE CASCADE;

-- =============================================
-- Cross-Service Data Integrity Views
-- Представления для контроля целостности данных
-- =============================================

-- View: Complete Project Overview
-- Полный обзор проектов со всеми связанными данными
CREATE OR REPLACE VIEW v_bcm_project_overview AS
SELECT
    p.id as project_id,
    p.name as project_name,
    p.stage as project_stage,
    p.partner_id,
    pt.name as partner_name,
    w.id as workspace_id,
    w.name as workspace_name,
    w.status as workspace_status,
    -- Counts from related modules
    (SELECT COUNT(*) FROM bcm_audits WHERE workspace_id = w.id) as audit_count,
    (SELECT COUNT(*) FROM bcm_incidents WHERE workspace_id = w.id) as incident_count,
    (SELECT COUNT(*) FROM bcm_plans WHERE workspace_id = w.id) as plan_count,
    (SELECT COUNT(*) FROM bcm_training WHERE workspace_id = w.id) as training_count,
    -- Latest activity
    GREATEST(
        COALESCE((SELECT MAX(created_at) FROM bcm_audits WHERE workspace_id = w.id), '1970-01-01'::timestamp),
        COALESCE((SELECT MAX(created_at) FROM bcm_incidents WHERE workspace_id = w.id), '1970-01-01'::timestamp),
        COALESCE((SELECT MAX(created_at) FROM bcm_plans WHERE workspace_id = w.id), '1970-01-01'::timestamp),
        COALESCE((SELECT MAX(created_at) FROM bcm_training WHERE workspace_id = w.id), '1970-01-01'::timestamp)
    ) as last_activity
FROM bcm_crm_projects p
LEFT JOIN res_partner pt ON p.partner_id = pt.id
LEFT JOIN bcm_workspaces w ON p.id = w.crm_project_id
ORDER BY p.created_at DESC;

-- View: Service Dependencies
-- Зависимости между сервисами
CREATE OR REPLACE VIEW v_service_dependencies AS
SELECT
    sr.service_name,
    sr.description,
    sr.status,
    sh.health_status,
    sh.response_time_ms,
    sh.last_check,
    -- Count of events from this service
    (SELECT COUNT(*) FROM bcm_event_registry WHERE source_service = sr.service_name) as events_count,
    -- Count of related workspaces
    CASE
        WHEN sr.service_name = 'crm_bridge' THEN (SELECT COUNT(*) FROM bcm_workspaces)
        WHEN sr.service_name LIKE 'bcm_%' THEN (
            SELECT COUNT(*) FROM bcm_workspaces w
            WHERE EXISTS (
                SELECT 1 FROM bcm_audits WHERE workspace_id = w.id AND sr.service_name = 'bcm_audit'
            ) OR EXISTS (
                SELECT 1 FROM bcm_incidents WHERE workspace_id = w.id AND sr.service_name = 'bcm_incident'
            ) OR EXISTS (
                SELECT 1 FROM bcm_plans WHERE workspace_id = w.id AND sr.service_name = 'bcm_plans'
            ) OR EXISTS (
                SELECT 1 FROM bcm_training WHERE workspace_id = w.id AND sr.service_name = 'bcm_training'
            )
        )
        ELSE 0
    END as affected_workspaces
FROM bcm_service_registry sr
LEFT JOIN bcm_service_health sh ON sr.service_name = sh.service_name;

-- =============================================
-- Data Consistency Triggers
-- Триггеры для поддержания согласованности данных
-- =============================================

-- Trigger: Update workspace status based on project stage
-- Обновление статуса рабочего пространства при изменении этапа проекта
CREATE OR REPLACE FUNCTION update_workspace_status()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE bcm_workspaces
    SET status = CASE
        WHEN NEW.stage = 'won' THEN 'active'
        WHEN NEW.stage = 'lost' THEN 'archived'
        WHEN NEW.stage = 'cancelled' THEN 'archived'
        ELSE 'draft'
    END,
    updated_at = CURRENT_TIMESTAMP
    WHERE crm_project_id = NEW.id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_project_stage_workspace_status
    AFTER UPDATE OF stage ON bcm_crm_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_workspace_status();

-- Trigger: Log service health changes
-- Логирование изменений состояния сервисов
CREATE OR REPLACE FUNCTION log_service_health_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert into monitoring logs if health status changed
    IF OLD.health_status IS DISTINCT FROM NEW.health_status THEN
        INSERT INTO bcm_monitoring_logs (
            service_name,
            level,
            message,
            metadata,
            created_at
        ) VALUES (
            NEW.service_name,
            CASE NEW.health_status
                WHEN 'healthy' THEN 'info'
                WHEN 'degraded' THEN 'warning'
                WHEN 'unhealthy' THEN 'error'
                ELSE 'info'
            END,
            format('Service health changed from %s to %s', OLD.health_status, NEW.health_status),
            jsonb_build_object(
                'old_status', OLD.health_status,
                'new_status', NEW.health_status,
                'response_time_ms', NEW.response_time_ms
            ),
            CURRENT_TIMESTAMP
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_service_health_change
    AFTER UPDATE OF health_status ON bcm_service_health
    FOR EACH ROW
    EXECUTE FUNCTION log_service_health_change();

-- =============================================
-- Cross-Service Indexes for Performance
-- Индексы для производительности межсервисных запросов
-- =============================================

-- Project and workspace relationship indexes
CREATE INDEX IF NOT EXISTS idx_workspace_crm_project ON bcm_workspaces(crm_project_id);
CREATE INDEX IF NOT EXISTS idx_workspace_status ON bcm_workspaces(status);

-- Module to workspace relationship indexes
CREATE INDEX IF NOT EXISTS idx_audit_workspace ON bcm_audits(workspace_id);
CREATE INDEX IF NOT EXISTS idx_incident_workspace ON bcm_incidents(workspace_id);
CREATE INDEX IF NOT EXISTS idx_plan_workspace ON bcm_plans(workspace_id);
CREATE INDEX IF NOT EXISTS idx_training_workspace ON bcm_training(workspace_id);

-- User relationship indexes
CREATE INDEX IF NOT EXISTS idx_workspace_responsible_user ON bcm_workspaces(responsible_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_auditor ON bcm_audits(auditor_id);
CREATE INDEX IF NOT EXISTS idx_incident_reporter ON bcm_incidents(reporter_id);
CREATE INDEX IF NOT EXISTS idx_incident_assignee ON bcm_incidents(assigned_to);

-- Service and event relationship indexes
CREATE INDEX IF NOT EXISTS idx_event_source_service ON bcm_event_registry(source_service);
CREATE INDEX IF NOT EXISTS idx_service_health_name ON bcm_service_health(service_name);

-- Cross-module relationship indexes
CREATE INDEX IF NOT EXISTS idx_incident_response_plan ON bcm_incidents(response_plan_id);
CREATE INDEX IF NOT EXISTS idx_training_plan ON bcm_training(plan_id);
CREATE INDEX IF NOT EXISTS idx_audit_improvement_plan ON bcm_audits(improvement_plan_id);

-- Performance indexes for common queries
CREATE INDEX IF NOT EXISTS idx_monitoring_logs_service_time ON bcm_monitoring_logs(service_name, created_at);
CREATE INDEX IF NOT EXISTS idx_event_registry_type_time ON bcm_event_registry(event_type, created_at);

-- =============================================
-- Data Validation Functions
-- Функции для валидации данных
-- =============================================

-- Function: Validate workspace consistency
-- Проверка согласованности рабочего пространства
CREATE OR REPLACE FUNCTION validate_workspace_consistency(workspace_id_param INTEGER)
RETURNS TABLE(
    issue_type TEXT,
    issue_description TEXT,
    severity TEXT
) AS $$
BEGIN
    -- Check if workspace has a valid CRM project
    IF NOT EXISTS (
        SELECT 1 FROM bcm_workspaces w
        JOIN bcm_crm_projects p ON w.crm_project_id = p.id
        WHERE w.id = workspace_id_param
    ) THEN
        RETURN QUERY SELECT
            'missing_crm_project'::TEXT,
            'Workspace has no valid CRM project'::TEXT,
            'critical'::TEXT;
    END IF;

    -- Check if workspace has any BCM modules
    IF NOT EXISTS (
        SELECT 1 FROM (
            SELECT workspace_id FROM bcm_audits WHERE workspace_id = workspace_id_param
            UNION
            SELECT workspace_id FROM bcm_incidents WHERE workspace_id = workspace_id_param
            UNION
            SELECT workspace_id FROM bcm_plans WHERE workspace_id = workspace_id_param
            UNION
            SELECT workspace_id FROM bcm_training WHERE workspace_id = workspace_id_param
        ) modules
    ) THEN
        RETURN QUERY SELECT
            'no_bcm_modules'::TEXT,
            'Workspace has no BCM modules configured'::TEXT,
            'warning'::TEXT;
    END IF;

    -- Check if workspace has responsible user
    IF NOT EXISTS (
        SELECT 1 FROM bcm_workspaces
        WHERE id = workspace_id_param AND responsible_user_id IS NOT NULL
    ) THEN
        RETURN QUERY SELECT
            'no_responsible_user'::TEXT,
            'Workspace has no responsible user assigned'::TEXT,
            'medium'::TEXT;
    END IF;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Function: Get service impact analysis
-- Анализ влияния сервиса на систему
CREATE OR REPLACE FUNCTION get_service_impact(service_name_param TEXT)
RETURNS TABLE(
    impact_area TEXT,
    affected_count INTEGER,
    impact_level TEXT
) AS $$
BEGIN
    -- Events generated by this service
    RETURN QUERY SELECT
        'events'::TEXT as impact_area,
        COUNT(*)::INTEGER as affected_count,
        CASE
            WHEN COUNT(*) > 1000 THEN 'high'
            WHEN COUNT(*) > 100 THEN 'medium'
            ELSE 'low'
        END::TEXT as impact_level
    FROM bcm_event_registry
    WHERE source_service = service_name_param;

    -- If it's CRM bridge, show workspace impact
    IF service_name_param = 'crm_bridge' THEN
        RETURN QUERY SELECT
            'workspaces'::TEXT as impact_area,
            COUNT(*)::INTEGER as affected_count,
            CASE
                WHEN COUNT(*) > 50 THEN 'high'
                WHEN COUNT(*) > 10 THEN 'medium'
                ELSE 'low'
            END::TEXT as impact_level
        FROM bcm_workspaces;
    END IF;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- Cleanup and Maintenance Functions
-- Функции очистки и обслуживания
-- =============================================

-- Function: Clean orphaned records
-- Очистка осиротевших записей
CREATE OR REPLACE FUNCTION cleanup_orphaned_records()
RETURNS INTEGER AS $$
DECLARE
    cleaned_count INTEGER := 0;
BEGIN
    -- Clean orphaned monitoring logs (older than 30 days)
    DELETE FROM bcm_monitoring_logs
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
    GET DIAGNOSTICS cleaned_count = ROW_COUNT;

    -- Clean orphaned event registry (older than 90 days)
    DELETE FROM bcm_event_registry
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '90 days';
    GET DIAGNOSTICS cleaned_count = cleaned_count + ROW_COUNT;

    -- Clean orphaned service health records (services no longer in registry)
    DELETE FROM bcm_service_health
    WHERE service_name NOT IN (SELECT service_name FROM bcm_service_registry);
    GET DIAGNOSTICS cleaned_count = cleaned_count + ROW_COUNT;

    RETURN cleaned_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- Security and Access Control
-- Безопасность и контроль доступа
-- =============================================

-- Row Level Security for workspace isolation
-- Изоляция рабочих пространств на уровне строк

-- Enable RLS on workspace-related tables
ALTER TABLE bcm_workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_audits ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE bcm_training ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access workspaces they are responsible for or part of
CREATE POLICY workspace_access_policy ON bcm_workspaces
    FOR ALL
    USING (
        responsible_user_id = current_setting('bcm.current_user_id')::INTEGER
        OR EXISTS (
            SELECT 1 FROM res_users u
            WHERE u.id = current_setting('bcm.current_user_id')::INTEGER
            AND u.groups_id && ARRAY[
                (SELECT id FROM res_groups WHERE name = 'BCM / Manager'),
                (SELECT id FROM res_groups WHERE name = 'BCM / Admin')
            ]
        )
    );

-- Policies for BCM modules (inherit workspace access)
CREATE POLICY audit_workspace_policy ON bcm_audits
    FOR ALL
    USING (
        workspace_id IN (
            SELECT id FROM bcm_workspaces
            WHERE responsible_user_id = current_setting('bcm.current_user_id')::INTEGER
        )
    );

CREATE POLICY incident_workspace_policy ON bcm_incidents
    FOR ALL
    USING (
        workspace_id IN (
            SELECT id FROM bcm_workspaces
            WHERE responsible_user_id = current_setting('bcm.current_user_id')::INTEGER
        )
    );

CREATE POLICY plan_workspace_policy ON bcm_plans
    FOR ALL
    USING (
        workspace_id IN (
            SELECT id FROM bcm_workspaces
            WHERE responsible_user_id = current_setting('bcm.current_user_id')::INTEGER
        )
    );

CREATE POLICY training_workspace_policy ON bcm_training
    FOR ALL
    USING (
        workspace_id IN (
            SELECT id FROM bcm_workspaces
            WHERE responsible_user_id = current_setting('bcm.current_user_id')::INTEGER
        )
    );

-- Function to set user context for RLS
-- Установка пользовательского контекста для RLS
CREATE OR REPLACE FUNCTION set_bcm_user_context(user_id INTEGER)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('bcm.current_user_id', user_id::TEXT, true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON SCHEMA public IS 'BCM Centralized Architecture - Foreign Keys Extension Applied';