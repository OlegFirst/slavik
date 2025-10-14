-- Migration: Add Missing Foreign Key Indexes (PERFORMANCE)
-- Description: Create indexes on foreign key columns to improve JOIN performance
-- Lint: unindexed_foreign_keys (INFO - PERFORMANCE)

-- audit schema indexes
CREATE INDEX IF NOT EXISTS idx_domain_events_organization_id ON audit.domain_events(organization_id);
CREATE INDEX IF NOT EXISTS idx_logs_organization_id ON audit.logs(organization_id);

-- bia schema indexes
CREATE INDEX IF NOT EXISTS idx_dependencies_organization_id ON bia.dependencies(organization_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_process_id ON bia.dependencies(process_id);
CREATE INDEX IF NOT EXISTS idx_exports_generated_by ON bia.exports(generated_by);
CREATE INDEX IF NOT EXISTS idx_exports_organization_id ON bia.exports(organization_id);
CREATE INDEX IF NOT EXISTS idx_impact_assessments_organization_id ON bia.impact_assessments(organization_id);
CREATE INDEX IF NOT EXISTS idx_impact_assessments_process_id ON bia.impact_assessments(process_id);
CREATE INDEX IF NOT EXISTS idx_processes_organization_id ON bia.processes(organization_id);
CREATE INDEX IF NOT EXISTS idx_processes_process_owner_id ON bia.processes(process_owner_id);
CREATE INDEX IF NOT EXISTS idx_supplier_disruptions_organization_id ON bia.supplier_disruptions(organization_id);
CREATE INDEX IF NOT EXISTS idx_supplier_disruptions_supplier_id ON bia.supplier_disruptions(supplier_id);
CREATE INDEX IF NOT EXISTS idx_templates_organization_id ON bia.templates(organization_id);
CREATE INDEX IF NOT EXISTS idx_workflow_logs_actor_id ON bia.workflow_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_workflow_logs_organization_id ON bia.workflow_logs(organization_id);
CREATE INDEX IF NOT EXISTS idx_workflow_logs_process_id ON bia.workflow_logs(process_id);

-- community schema indexes
CREATE INDEX IF NOT EXISTS idx_ai_digital_colleagues_organization_id ON community.ai_digital_colleagues(organization_id);
CREATE INDEX IF NOT EXISTS idx_specialist_certifications_specialist_id ON community.specialist_certifications(specialist_id);
CREATE INDEX IF NOT EXISTS idx_specialist_engagements_organization_id ON community.specialist_engagements(organization_id);
CREATE INDEX IF NOT EXISTS idx_specialist_engagements_specialist_id ON community.specialist_engagements(specialist_id);
CREATE INDEX IF NOT EXISTS idx_specialist_portfolio_specialist_id ON community.specialist_portfolio(specialist_id);
CREATE INDEX IF NOT EXISTS idx_specialist_reviews_organization_id ON community.specialist_reviews(organization_id);
CREATE INDEX IF NOT EXISTS idx_specialist_reviews_specialist_id ON community.specialist_reviews(specialist_id);
CREATE INDEX IF NOT EXISTS idx_specialist_services_specialist_id ON community.specialist_services(specialist_id);

-- compliance schema indexes
CREATE INDEX IF NOT EXISTS idx_assessments_organization_id ON compliance.assessments(organization_id);
CREATE INDEX IF NOT EXISTS idx_assessments_requirement_id ON compliance.assessments(requirement_id);
CREATE INDEX IF NOT EXISTS idx_evidence_organization_id ON compliance.evidence(organization_id);
CREATE INDEX IF NOT EXISTS idx_evidence_requirement_id ON compliance.evidence(requirement_id);
CREATE INDEX IF NOT EXISTS idx_gaps_organization_id ON compliance.gaps(organization_id);
CREATE INDEX IF NOT EXISTS idx_gaps_requirement_id ON compliance.gaps(requirement_id);

-- governance schema indexes
CREATE INDEX IF NOT EXISTS idx_context_analysis_organization_id ON governance.context_analysis(organization_id);
CREATE INDEX IF NOT EXISTS idx_objectives_organization_id ON governance.objectives(organization_id);
CREATE INDEX IF NOT EXISTS idx_objectives_owner_id ON governance.objectives(owner_id);
CREATE INDEX IF NOT EXISTS idx_policies_organization_id ON governance.policies(organization_id);
CREATE INDEX IF NOT EXISTS idx_policy_versions_organization_id ON governance.policy_versions(organization_id);
CREATE INDEX IF NOT EXISTS idx_policy_versions_policy_id ON governance.policy_versions(policy_id);
CREATE INDEX IF NOT EXISTS idx_roles_assigned_to_team_id ON governance.roles(assigned_to_team_id);
CREATE INDEX IF NOT EXISTS idx_roles_assigned_to_user_id ON governance.roles(assigned_to_user_id);
CREATE INDEX IF NOT EXISTS idx_roles_organization_id ON governance.roles(organization_id);
CREATE INDEX IF NOT EXISTS idx_stakeholders_organization_id ON governance.stakeholders(organization_id);

-- intelligence schema indexes
CREATE INDEX IF NOT EXISTS idx_digital_twins_organization_id ON intelligence.digital_twins(organization_id);
CREATE INDEX IF NOT EXISTS idx_simulations_digital_twin_id ON intelligence.simulations(digital_twin_id);

-- learning schema indexes
CREATE INDEX IF NOT EXISTS idx_competency_assessments_organization_id ON learning.competency_assessments(organization_id);
CREATE INDEX IF NOT EXISTS idx_competency_assessments_user_id ON learning.competency_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_organization_id ON learning.enrollments(organization_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_program_id ON learning.enrollments(program_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON learning.enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_training_templates_organization_id ON learning.training_templates(organization_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_organization_id ON learning.user_achievements(organization_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON learning.user_achievements(user_id);

-- planning schema indexes
CREATE INDEX IF NOT EXISTS idx_action_items_organization_id ON planning.action_items(organization_id);
CREATE INDEX IF NOT EXISTS idx_action_items_plan_id ON planning.action_items(plan_id);
CREATE INDEX IF NOT EXISTS idx_action_items_assigned_to ON planning.action_items(assigned_to);
CREATE INDEX IF NOT EXISTS idx_strategic_plans_organization_id ON planning.strategic_plans(organization_id);

-- response schema indexes
CREATE INDEX IF NOT EXISTS idx_activations_organization_id ON response.activations(organization_id);
CREATE INDEX IF NOT EXISTS idx_activations_plan_id ON response.activations(plan_id);
CREATE INDEX IF NOT EXISTS idx_activations_incident_id ON response.activations(incident_id);
CREATE INDEX IF NOT EXISTS idx_incidents_organization_id ON response.incidents(organization_id);
CREATE INDEX IF NOT EXISTS idx_incident_logs_organization_id ON response.incident_logs(organization_id);
CREATE INDEX IF NOT EXISTS idx_incident_logs_incident_id ON response.incident_logs(incident_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON response.notifications(user_id);

-- risk schema indexes
CREATE INDEX IF NOT EXISTS idx_controls_organization_id ON risk.controls(organization_id);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_organization_id ON risk.risk_assessments(organization_id);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_risk_id ON risk.risk_assessments(risk_id);
CREATE INDEX IF NOT EXISTS idx_risks_organization_id ON risk.risks(organization_id);
CREATE INDEX IF NOT EXISTS idx_risks_owner_id ON risk.risks(owner_id);

-- validation schema indexes
CREATE INDEX IF NOT EXISTS idx_exercises_organization_id ON validation.exercises(organization_id);
CREATE INDEX IF NOT EXISTS idx_kpi_alerts_organization_id ON validation.kpi_alerts(organization_id);
CREATE INDEX IF NOT EXISTS idx_kpi_alerts_kpi_id ON validation.kpi_alerts(kpi_id);
CREATE INDEX IF NOT EXISTS idx_kpis_organization_id ON validation.kpis(organization_id);

COMMENT ON MIGRATION IS 'Added missing foreign key indexes to improve JOIN query performance';
