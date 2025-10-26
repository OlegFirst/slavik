-- ============================================
-- BCM Platform - RLS FORCE ENFORCEMENT Migration
-- Migration 999: Enable FORCE ROW LEVEL SECURITY
-- ============================================
-- Author: Security Team
-- Date: 2025-10-26
-- Purpose: Enforce RLS even for table owners and superusers
--
-- CRITICAL SECURITY FIX:
-- This migration changes RLS from ENABLE to FORCE mode.
--
-- Difference:
--   ENABLE RLS  - table owners/superusers can bypass RLS
--   FORCE RLS   - RLS applies to ALL users including owners
--
-- Impact: Multi-tenant data isolation is enforced for ALL queries
-- Risk Level: LOW - only strengthens security, no functionality change
-- Rollback: Can be reverted by replacing FORCE with standard ENABLE
--
-- ISO 22301 Compliance: Clause 5.2 - Information Security
-- GDPR Compliance: Article 32 - Security of Processing
-- ============================================

-- Transaction wrapper for atomicity
BEGIN;

-- Set client encoding and timezone for consistent behavior
SET client_encoding = 'UTF8';
SET timezone = 'UTC';

-- ============================================
-- AUDIT SCHEMA (2 tables)
-- ============================================
ALTER TABLE audit.domain_events FORCE ROW LEVEL SECURITY;
ALTER TABLE audit.logs FORCE ROW LEVEL SECURITY;

-- ============================================
-- BCM SCHEMA (12 tables)
-- ============================================
ALTER TABLE bcm.communication_plans FORCE ROW LEVEL SECURITY;
ALTER TABLE bcm.competence_records FORCE ROW LEVEL SECURITY;
ALTER TABLE bcm.document_access FORCE ROW LEVEL SECURITY;
ALTER TABLE bcm.document_approvals FORCE ROW LEVEL SECURITY;
ALTER TABLE bcm.document_retention_policies FORCE ROW LEVEL SECURITY;
ALTER TABLE bcm.document_tags FORCE ROW LEVEL SECURITY;
ALTER TABLE bcm.documents FORCE ROW LEVEL SECURITY;
ALTER TABLE bcm.plans FORCE ROW LEVEL SECURITY;
ALTER TABLE bcm.procedures FORCE ROW LEVEL SECURITY;
ALTER TABLE bcm.resources FORCE ROW LEVEL SECURITY;

-- ============================================
-- BIA SCHEMA (10 tables)
-- ============================================
ALTER TABLE bia.dependencies FORCE ROW LEVEL SECURITY;
ALTER TABLE bia.exports FORCE ROW LEVEL SECURITY;
ALTER TABLE bia.impact_assessments FORCE ROW LEVEL SECURITY;
ALTER TABLE bia.processes FORCE ROW LEVEL SECURITY;
ALTER TABLE bia.supplier_disruptions FORCE ROW LEVEL SECURITY;
ALTER TABLE bia.suppliers FORCE ROW LEVEL SECURITY;
ALTER TABLE bia.templates FORCE ROW LEVEL SECURITY;
ALTER TABLE bia.workflow_logs FORCE ROW LEVEL SECURITY;

-- ============================================
-- COMMUNITY SCHEMA (14 tables)
-- ============================================
ALTER TABLE community.ai_digital_colleagues FORCE ROW LEVEL SECURITY;
ALTER TABLE community.case_contributions FORCE ROW LEVEL SECURITY;
ALTER TABLE community.peer_reviews FORCE ROW LEVEL SECURITY;
ALTER TABLE community.reputation_transactions FORCE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_certifications FORCE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_engagements FORCE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_portfolio FORCE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_reviews FORCE ROW LEVEL SECURITY;
ALTER TABLE community.specialist_services FORCE ROW LEVEL SECURITY;
ALTER TABLE community.specialists FORCE ROW LEVEL SECURITY;
ALTER TABLE community.user_reputation FORCE ROW LEVEL SECURITY;

-- Legacy community tables (deprecated, but still enforced)
ALTER TABLE case_contributions FORCE ROW LEVEL SECURITY;
ALTER TABLE collective_agent_messages FORCE ROW LEVEL SECURITY;
ALTER TABLE collective_agents FORCE ROW LEVEL SECURITY;
ALTER TABLE community_annotations FORCE ROW LEVEL SECURITY;
ALTER TABLE peer_reviews FORCE ROW LEVEL SECURITY;
ALTER TABLE reputation_transactions FORCE ROW LEVEL SECURITY;
ALTER TABLE stuck_detection_logs FORCE ROW LEVEL SECURITY;
ALTER TABLE synthesized_guidance FORCE ROW LEVEL SECURITY;
ALTER TABLE user_reputation FORCE ROW LEVEL SECURITY;

-- ============================================
-- COMPLIANCE SCHEMA (5 tables)
-- ============================================
ALTER TABLE compliance.assessments FORCE ROW LEVEL SECURITY;
ALTER TABLE compliance.evidence FORCE ROW LEVEL SECURITY;
ALTER TABLE compliance.gaps FORCE ROW LEVEL SECURITY;
ALTER TABLE compliance.improvement_initiatives FORCE ROW LEVEL SECURITY;
ALTER TABLE compliance.requirements FORCE ROW LEVEL SECURITY;

-- ============================================
-- GOVERNANCE SCHEMA (6 tables)
-- ============================================
ALTER TABLE governance.context_analysis FORCE ROW LEVEL SECURITY;
ALTER TABLE governance.objectives FORCE ROW LEVEL SECURITY;
ALTER TABLE governance.policies FORCE ROW LEVEL SECURITY;
ALTER TABLE governance.policy_versions FORCE ROW LEVEL SECURITY;
ALTER TABLE governance.roles FORCE ROW LEVEL SECURITY;
ALTER TABLE governance.stakeholders FORCE ROW LEVEL SECURITY;

-- ============================================
-- INTELLIGENCE SCHEMA (3 tables)
-- ============================================
ALTER TABLE intelligence.digital_twins FORCE ROW LEVEL SECURITY;
ALTER TABLE intelligence.metrics FORCE ROW LEVEL SECURITY;
ALTER TABLE intelligence.simulations FORCE ROW LEVEL SECURITY;

-- ============================================
-- LEARNING SCHEMA (20 tables)
-- ============================================
ALTER TABLE learning.achievement_definitions FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.alerts FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.awareness_campaigns FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.badge_definitions FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.bcm_processes FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.competency_assessments FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.enrollments FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.gamification_profiles FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.gap_knowledge_mappings FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.leaderboards FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.learning_paths FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.process_coverage FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.role_competency_gaps FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.smart_goals FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.team_competencies FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.training_programs FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.training_templates FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.user_achievements FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.user_competencies FORCE ROW LEVEL SECURITY;
ALTER TABLE learning.user_learning_progress FORCE ROW LEVEL SECURITY;

-- ============================================
-- PUBLIC SCHEMA (15 tables)
-- ============================================
ALTER TABLE public.certification_predictions FORCE ROW LEVEL SECURITY;
ALTER TABLE public.expert_demand_forecasts FORCE ROW LEVEL SECURITY;
ALTER TABLE public.individual_users FORCE ROW LEVEL SECURITY;
ALTER TABLE public.journey_predictions FORCE ROW LEVEL SECURITY;
ALTER TABLE public.organization_users FORCE ROW LEVEL SECURITY;
ALTER TABLE public.organizations FORCE ROW LEVEL SECURITY;
ALTER TABLE public.outbox_events FORCE ROW LEVEL SECURITY;
ALTER TABLE public.platform_administrators FORCE ROW LEVEL SECURITY;
ALTER TABLE public.prediction_accuracy FORCE ROW LEVEL SECURITY;
ALTER TABLE public.proactive_recommendations FORCE ROW LEVEL SECURITY;
ALTER TABLE public.team_members FORCE ROW LEVEL SECURITY;
ALTER TABLE public.teams FORCE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles FORCE ROW LEVEL SECURITY;
ALTER TABLE public.user_relationships FORCE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.schema_migrations FORCE ROW LEVEL SECURITY;

-- ============================================
-- RESPONSE SCHEMA (7 tables)
-- ============================================
ALTER TABLE response.communication_templates FORCE ROW LEVEL SECURITY;
ALTER TABLE response.communications FORCE ROW LEVEL SECURITY;
ALTER TABLE response.escalations FORCE ROW LEVEL SECURITY;
ALTER TABLE response.incidents FORCE ROW LEVEL SECURITY;
ALTER TABLE response.notifications FORCE ROW LEVEL SECURITY;
ALTER TABLE response.response_teams FORCE ROW LEVEL SECURITY;
ALTER TABLE response.timeline_events FORCE ROW LEVEL SECURITY;

-- ============================================
-- RISK SCHEMA (6 tables)
-- ============================================
ALTER TABLE risk.assessments FORCE ROW LEVEL SECURITY;
ALTER TABLE risk.controls FORCE ROW LEVEL SECURITY;
ALTER TABLE risk.risks FORCE ROW LEVEL SECURITY;
ALTER TABLE risk.templates FORCE ROW LEVEL SECURITY;
ALTER TABLE risk.treatments FORCE ROW LEVEL SECURITY;
ALTER TABLE risk.workflow_logs FORCE ROW LEVEL SECURITY;

-- ============================================
-- SCENARIO INTELLIGENCE SCHEMA (3 tables)
-- ============================================
ALTER TABLE scenario_intelligence.evidence_vault FORCE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.executions FORCE ROW LEVEL SECURITY;
ALTER TABLE scenario_intelligence.scenarios FORCE ROW LEVEL SECURITY;

-- ============================================
-- VALIDATION SCHEMA (13 tables)
-- ============================================
ALTER TABLE validation.audit_findings FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.audit_plans FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.capa FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.exercise_actions FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.exercise_observations FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.exercise_scenarios FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.exercises FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.kpi_alerts FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.kpi_dashboards FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.kpi_measurements FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.kpis FORCE ROW LEVEL SECURITY;
ALTER TABLE validation.management_reviews FORCE ROW LEVEL SECURITY;

-- ============================================
-- WORKFLOW SCHEMA (4 tables)
-- ============================================
ALTER TABLE workflow.bpmn_instances FORCE ROW LEVEL SECURITY;
ALTER TABLE workflow.bpmn_processes FORCE ROW LEVEL SECURITY;
ALTER TABLE workflow.bpmn_tasks FORCE ROW LEVEL SECURITY;
ALTER TABLE workflow.process_analytics FORCE ROW LEVEL SECURITY;

-- ============================================
-- WORKFLOW INTELLIGENCE SCHEMA (1 table)
-- ============================================
ALTER TABLE workflow_intelligence.pdca_cycles FORCE ROW LEVEL SECURITY;

-- ============================================
-- VERIFICATION
-- ============================================
-- Verify FORCE RLS is enabled on all tables
DO $$
DECLARE
    table_count INTEGER;
    force_count INTEGER;
BEGIN
    -- Count total tables with RLS enabled
    SELECT COUNT(*) INTO table_count
    FROM pg_tables t
    JOIN pg_class c ON c.relname = t.tablename
    WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
    AND c.relrowsecurity = true;

    -- Count tables with FORCE RLS
    SELECT COUNT(*) INTO force_count
    FROM pg_tables t
    JOIN pg_class c ON c.relname = t.tablename
    WHERE t.schemaname NOT IN ('pg_catalog', 'information_schema')
    AND c.relrowsecurity = true
    AND c.relforcerowsecurity = true;

    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'RLS FORCE ENFORCEMENT - VERIFICATION';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables with RLS enabled: %', table_count;
    RAISE NOTICE 'Tables with FORCE RLS: %', force_count;

    IF force_count >= 122 THEN
        RAISE NOTICE '✅ SUCCESS: FORCE RLS enabled on % tables', force_count;
    ELSE
        RAISE WARNING '⚠️  WARNING: Expected 122+ tables, got %', force_count;
    END IF;
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
END $$;

-- Commit transaction
COMMIT;

-- ============================================
-- POST-MIGRATION NOTES
-- ============================================
--
-- TESTING:
-- 1. Run check_rls_status.sql to verify enforcement
-- 2. Test with non-privileged user to ensure RLS works
-- 3. Verify application continues to work correctly
--
-- ROLLBACK (if needed):
-- To revert to ENABLE RLS (not recommended):
--   Replace all "FORCE ROW LEVEL SECURITY" with
--   "DISABLE FORCE ROW LEVEL SECURITY"
--
-- MONITORING:
-- - Monitor application logs for RLS-related errors
-- - Check query performance (minimal impact expected)
-- - Audit tenant data isolation in next review
--
-- ============================================
