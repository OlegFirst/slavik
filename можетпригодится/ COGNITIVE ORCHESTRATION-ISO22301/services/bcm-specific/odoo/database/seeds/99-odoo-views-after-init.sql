-- =====================================================
-- BCM Views that depend on Odoo tables
-- Run after Odoo initialization
-- =====================================================

-- BCM Dashboard Summary View
CREATE OR REPLACE VIEW bcm_dashboard_summary AS
SELECT 
    c.name as company_name,
    COUNT(DISTINCT bp.id) as total_processes,
    COUNT(DISTINCT CASE WHEN bp.criticality = 'critical' THEN bp.id END) as critical_processes,
    COUNT(DISTINCT i.id) as total_incidents,
    COUNT(DISTINCT CASE WHEN i.status = 'open' THEN i.id END) as open_incidents,
    COUNT(DISTINCT e.id) as total_exercises,
    COUNT(DISTINCT CASE WHEN e.state = 'completed' THEN e.id END) as completed_exercises,
    COUNT(DISTINCT t.id) as total_trainings,
    COUNT(DISTINCT a.id) as total_audits,
    AVG(bp.optimized_rto_hours) as avg_rto_hours
FROM res_company c
LEFT JOIN bcm_business_process bp ON bp.company_id = c.id
LEFT JOIN bcm_incident i ON i.company_id = c.id
LEFT JOIN bcm_exercise e ON e.company_id = c.id
LEFT JOIN bcm_training t ON t.company_id = c.id
LEFT JOIN bcm_audit a ON a.company_id = c.id
GROUP BY c.id, c.name;

-- Comments
COMMENT ON VIEW bcm_dashboard_summary IS 'Summary view for BCM dashboard showing key metrics by company';