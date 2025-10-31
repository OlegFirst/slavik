-- СОЗДАНИЕ ИНДЕКСОВ ДЛЯ DIGITAL TWIN ТАБЛИЦ
-- Выполните в Supabase SQL Editor

-- Индексы для organizations
CREATE INDEX idx_org_pgpx ON organizations(pgpx_subject_id);
CREATE INDEX idx_org_active ON organizations(is_active);

-- Индексы для digital_twins
CREATE INDEX idx_twin_org ON digital_twins(organization_id);
CREATE INDEX idx_twin_active ON digital_twins(is_active);

-- Индексы для simulations
CREATE INDEX idx_sim_twin ON simulations(twin_id);
CREATE INDEX idx_sim_status ON simulations(status);

-- Индексы для metrics
CREATE INDEX idx_metrics_twin ON metrics(twin_id);
CREATE INDEX idx_metrics_type ON metrics(metric_type);
CREATE INDEX idx_metrics_timestamp ON metrics(timestamp DESC);

-- Индексы для predictions
CREATE INDEX idx_pred_twin ON predictions(twin_id);
CREATE INDEX idx_pred_type ON predictions(prediction_type);

-- Индексы для reports
CREATE INDEX idx_reports_twin ON reports(twin_id);
CREATE INDEX idx_reports_type ON reports(report_type);

-- Проверка созданных индексов
SELECT 
    indexname,
    tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('organizations', 'digital_twins', 'simulations', 'metrics', 'predictions', 'reports')
ORDER BY tablename, indexname;