-- Migration 024: Drop Unused Indexes
-- Generated from Supabase performance linter analysis
-- Total indexes to drop: 355

-- Drop unused indexes to improve write performance and save disk space

-- Schema: audit

-- Table: domain_events, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_events_aggregate;

-- Table: domain_events, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_events_time;

-- Table: domain_events, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_events_unprocessed;

-- Table: domain_events, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_events_org;

-- Table: logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_audit_org_time;

-- Table: logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_audit_actor;

-- Table: logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_audit_resource;

-- Table: logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_audit_event_type;

-- Table: logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_audit_security;

-- Table: logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS audit.idx_audit_severity;

-- Schema: bcm

-- Table: communication_plans, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_comm_plans_code;

-- Table: communication_plans, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_comm_plans_type;

-- Table: communication_plans, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_comm_plans_status;

-- Table: communication_plans, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_comm_plans_active;

-- Table: competence_records, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_competence_records_area;

-- Table: competence_records, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_competence_records_status;

-- Table: competence_records, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_competence_records_expiring;

-- Table: document_access, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_document_access_type;

-- Table: document_tags, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_document_tags_category;

-- Table: documents, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_documents_code;

-- Table: documents, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_documents_type;

-- Table: documents, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_documents_status;

-- Table: documents, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_documents_version;

-- Table: documents, Size: 16 kB, Scans: 0
DROP INDEX IF EXISTS bcm.idx_documents_search;

-- Table: documents, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_documents_iso_clause;

-- Table: documents, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_documents_review_date;

-- Table: plans, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_plans_code;

-- Table: plans, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_plans_type;

-- Table: plans, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_plans_status;

-- Table: plans, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_plans_current;

-- Table: plans, Size: 16 kB, Scans: 0
DROP INDEX IF EXISTS bcm.idx_plans_search;

-- Table: plans, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_plans_review_due;

-- Table: procedures, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_procedures_type;

-- Table: procedures, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_procedures_active;

-- Table: resources, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_bcm_resources_code;

-- Table: resources, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_bcm_resources_type;

-- Table: resources, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_bcm_resources_critical;

-- Table: resources, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS bcm.idx_bcm_resources_spof;

-- Schema: bia

-- Table: dependencies, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_dependencies_process;

-- Table: dependencies, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_dependencies_org;

-- Table: dependencies, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_dependencies_type;

-- Table: dependencies, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_dependencies_criticality;

-- Table: dependencies, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_dependencies_spof;

-- Table: exports, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_exports_org;

-- Table: exports, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_exports_status;

-- Table: exports, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_exports_generated_by;

-- Table: impact_assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_impact_assessments_process;

-- Table: impact_assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_impact_assessments_org;

-- Table: impact_assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_impact_assessments_timeframe;

-- Table: impact_assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_impact_assessments_critical;

-- Table: processes, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_processes_org;

-- Table: processes, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_processes_criticality;

-- Table: processes, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_processes_owner;

-- Table: supplier_disruptions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_supplier_disruptions_tenant;

-- Table: supplier_disruptions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_supplier_disruptions_org;

-- Table: supplier_disruptions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_supplier_disruptions_supplier;

-- Table: supplier_disruptions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_supplier_disruptions_date;

-- Table: supplier_disruptions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_supplier_disruptions_type;

-- Table: supplier_disruptions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_supplier_disruptions_severity;

-- Table: supplier_disruptions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_supplier_disruptions_resolved;

-- Table: supplier_disruptions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_supplier_disruptions_unresolved;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_tenant;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_org;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_criticality;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_spof;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_status;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_code;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_country;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_bcm_cert;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_fin_stability;

-- Table: suppliers, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_suppliers_created_at;

-- Table: templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_templates_org;

-- Table: templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_templates_industry;

-- Table: workflow_logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_workflow_logs_process;

-- Table: workflow_logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_workflow_logs_org;

-- Table: workflow_logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_workflow_logs_event;

-- Table: workflow_logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS bia.idx_bia_workflow_logs_actor;

-- Schema: community

-- Table: ai_digital_colleagues, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_ai_colleagues_org;

-- Table: specialist_certifications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_certifications_specialist;

-- Table: specialist_certifications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_certifications_verified;

-- Table: specialist_engagements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_engagements_specialist;

-- Table: specialist_engagements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_engagements_organization;

-- Table: specialist_engagements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_engagements_status;

-- Table: specialist_engagements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_engagements_dates;

-- Table: specialist_portfolio, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_portfolio_specialist;

-- Table: specialist_portfolio, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_portfolio_featured;

-- Table: specialist_reviews, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_reviews_specialist;

-- Table: specialist_reviews, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_reviews_organization;

-- Table: specialist_reviews, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_reviews_engagement;

-- Table: specialist_services, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_services_specialist;

-- Table: specialist_services, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_services_active;

-- Table: specialists, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_specialists_user;

-- Table: specialists, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_specialists_rating;

-- Table: specialists, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_specialists_verified;

-- Table: specialists, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_specialists_availability;

-- Table: specialists, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_specialists_country;

-- Table: specialists, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_specialists_specializations;

-- Table: specialists, Size: unknown, Scans: 0
DROP INDEX IF EXISTS community.idx_specialists_skills;

-- Schema: compliance

-- Table: assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_assessments_requirement;

-- Table: assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_assessments_org;

-- Table: assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_assessments_status;

-- Table: assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_assessments_date;

-- Table: evidence, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_evidence_requirement;

-- Table: evidence, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_evidence_org;

-- Table: evidence, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_evidence_type;

-- Table: evidence, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_evidence_current;

-- Table: evidence, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_evidence_expiring;

-- Table: gaps, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_gaps_requirement;

-- Table: gaps, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_gaps_org;

-- Table: gaps, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_gaps_severity;

-- Table: gaps, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_gaps_status;

-- Table: gaps, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_gaps_open;

-- Table: gaps, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_gaps_overdue;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_tenant;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_organization;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_code;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_type;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_source;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_status;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_priority;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_owner;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_planned_end;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_created;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_verification;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_effectiveness;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_tenant_status;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_tenant_priority;

-- Table: improvement_initiatives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_improvements_org_status;

-- Table: requirements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_requirements_org;

-- Table: requirements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_requirements_code;

-- Table: requirements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_requirements_framework;

-- Table: requirements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_requirements_status;

-- Table: requirements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_requirements_search;

-- Table: requirements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS compliance.idx_compliance_requirements_non_compliant;

-- Schema: domain_intelligence

-- Table: domain_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_template_industry;

-- Table: domain_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_template_subdomain;

-- Table: domain_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_template_type;

-- Table: domain_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_template_code;

-- Table: domain_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_template_active;

-- Table: domain_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_template_rating;

-- Table: domain_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_template_industry_type;

-- Table: industry_benchmarks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_benchmark_industry;

-- Table: industry_benchmarks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_benchmark_metric;

-- Table: industry_benchmarks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_benchmark_active;

-- Table: industry_benchmarks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_benchmark_period;

-- Table: industry_benchmarks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_benchmark_industry_metric;

-- Table: industry_knowledge, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_knowledge_industry;

-- Table: industry_knowledge, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_knowledge_subdomain;

-- Table: industry_knowledge, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_knowledge_type;

-- Table: industry_knowledge, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_knowledge_active;

-- Table: industry_knowledge, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_knowledge_industry_type;

-- Table: industry_knowledge, Size: unknown, Scans: 0
DROP INDEX IF EXISTS domain_intelligence.idx_knowledge_tags;

-- Schema: governance

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_tenant;

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_organization;

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_type;

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_status;

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_priority;

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_created;

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_next_review;

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_next_review_due;

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_org_status;

-- Table: context_analysis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_context_tenant_type;

-- Table: objectives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_objectives_org;

-- Table: objectives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_objectives_status;

-- Table: objectives, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_objectives_owner;

-- Table: policies, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_policies_org;

-- Table: policies, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_policies_status;

-- Table: policies, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_policies_type;

-- Table: policy_versions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_policy_versions_policy;

-- Table: policy_versions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_policy_versions_org;

-- Table: policy_versions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_policy_versions_status;

-- Table: roles, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_roles_org;

-- Table: roles, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_roles_assigned_user;

-- Table: roles, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_roles_assigned_team;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_tenant;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_organization;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_type;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_status;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_created;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_influence;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_interest;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_influence_interest;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_org_status;

-- Table: stakeholders, Size: unknown, Scans: 0
DROP INDEX IF EXISTS governance.idx_stakeholders_tenant_type;

-- Schema: intelligence

-- Table: digital_twins, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.idx_twins_org;

-- Table: metrics_2025_q1, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.metrics_2025_q1_metric_name_recorded_at_idx;

-- Table: metrics_2025_q1, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.metrics_2025_q1_digital_twin_id_recorded_at_idx;

-- Table: metrics_2025_q2, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.metrics_2025_q2_metric_name_recorded_at_idx;

-- Table: metrics_2025_q2, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.metrics_2025_q2_digital_twin_id_recorded_at_idx;

-- Table: metrics_2025_q3, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.metrics_2025_q3_digital_twin_id_recorded_at_idx;

-- Table: metrics_2025_q3, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.metrics_2025_q3_metric_name_recorded_at_idx;

-- Table: metrics_2025_q4, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.metrics_2025_q4_digital_twin_id_recorded_at_idx;

-- Table: metrics_2025_q4, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.metrics_2025_q4_metric_name_recorded_at_idx;

-- Table: simulations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.idx_simulations_twin;

-- Table: simulations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS intelligence.idx_simulations_status;

-- Schema: learning

-- Table: awareness_campaigns, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_awareness_campaigns_org;

-- Table: awareness_campaigns, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_awareness_campaigns_code;

-- Table: awareness_campaigns, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_awareness_campaigns_type;

-- Table: awareness_campaigns, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_awareness_campaigns_status;

-- Table: awareness_campaigns, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_awareness_campaigns_active;

-- Table: competency_assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_competency_assessments_org;

-- Table: competency_assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_competency_assessments_user;

-- Table: competency_assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_competency_assessments_area;

-- Table: competency_assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_competency_assessments_date;

-- Table: enrollments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_enrollments_overdue;

-- Table: enrollments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_enrollments_expiring_cert;

-- Table: enrollments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_enrollments_program;

-- Table: enrollments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_enrollments_org;

-- Table: enrollments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_enrollments_user;

-- Table: enrollments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_enrollments_status;

-- Table: training_programs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_training_programs_org;

-- Table: training_programs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_training_programs_code;

-- Table: training_programs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_training_programs_type;

-- Table: training_programs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_training_programs_active;

-- Table: training_programs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_training_programs_search;

-- Table: training_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_training_templates_org;

-- Table: training_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_training_templates_type;

-- Table: training_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_training_templates_active;

-- Table: user_achievements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_user_achievements_org;

-- Table: user_achievements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_user_achievements_user;

-- Table: user_achievements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS learning.idx_user_achievements_type;

-- Schema: public

-- Table: organizations, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_organizations_tenant_id;

-- Table: organizations, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_organizations_slug;

-- Table: organizations, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_organizations_type;

-- Table: organizations, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_organizations_subscription;

-- Table: organizations, Size: 16 kB, Scans: 0
DROP INDEX IF EXISTS public.idx_organizations_search;

-- Table: organizations, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_orgs_org_type;

-- Table: organizations, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_orgs_industry;

-- Table: organizations, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_orgs_subdomain;

-- Table: organizations, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_orgs_company_size;

-- Table: teams, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_teams_type;

-- Table: user_profiles, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_user_profiles_email;

-- Table: user_profiles, Size: 8192 bytes, Scans: 0
DROP INDEX IF EXISTS public.idx_user_profiles_role;

-- Table: user_profiles, Size: 16 kB, Scans: 0
DROP INDEX IF EXISTS public.idx_user_profiles_search;

-- Schema: response

-- Table: communication_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_comm_templates_org;

-- Table: communication_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_comm_templates_type;

-- Table: communication_templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_comm_templates_active;

-- Table: communications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_communications_incident;

-- Table: communications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_communications_org;

-- Table: communications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_communications_status;

-- Table: communications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_communications_sent;

-- Table: communications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_communications_scheduled;

-- Table: escalations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_escalations_incident;

-- Table: escalations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_escalations_org;

-- Table: escalations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_escalations_level;

-- Table: escalations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_escalations_pending;

-- Table: incidents, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_incidents_type;

-- Table: incidents, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_incidents_detected;

-- Table: incidents, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_incidents_search;

-- Table: incidents, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_incidents_active;

-- Table: incidents, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_incidents_org;

-- Table: incidents, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_incidents_code;

-- Table: incidents, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_incidents_status;

-- Table: incidents, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_incidents_severity;

-- Table: notifications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_notifications_incident;

-- Table: notifications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_notifications_user;

-- Table: notifications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_notifications_status;

-- Table: notifications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_notifications_unread;

-- Table: notifications, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_notifications_pending_retry;

-- Table: response_teams, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_response_teams_org;

-- Table: response_teams, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_response_teams_type;

-- Table: response_teams, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_response_teams_active;

-- Table: timeline_events, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_timeline_incident;

-- Table: timeline_events, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_timeline_org;

-- Table: timeline_events, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_timeline_type;

-- Table: timeline_events, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_timeline_public;

-- Table: timeline_events, Size: unknown, Scans: 0
DROP INDEX IF EXISTS response.idx_timeline_milestones;

-- Schema: risk

-- Table: assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_assessments_risk;

-- Table: assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_assessments_org;

-- Table: assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_assessments_level;

-- Table: assessments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_assessments_date;

-- Table: controls, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_controls_risk;

-- Table: controls, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_controls_org;

-- Table: controls, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_controls_status;

-- Table: risks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risks_org;

-- Table: risks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risks_score;

-- Table: risks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risks_status;

-- Table: risks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risks_category;

-- Table: risks, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risks_owner;

-- Table: templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_templates_org;

-- Table: templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_templates_type;

-- Table: templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_templates_category;

-- Table: templates, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_templates_active;

-- Table: treatments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_treatments_risk;

-- Table: treatments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_treatments_org;

-- Table: treatments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_treatments_owner;

-- Table: treatments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_treatments_status;

-- Table: treatments, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_treatments_overdue;

-- Table: workflow_logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_workflow_logs_risk;

-- Table: workflow_logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_workflow_logs_org;

-- Table: workflow_logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_workflow_logs_event;

-- Table: workflow_logs, Size: unknown, Scans: 0
DROP INDEX IF EXISTS risk.idx_risk_workflow_logs_actor;

-- Schema: validation

-- Table: audit_findings, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_findings_plan;

-- Table: audit_findings, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_findings_org;

-- Table: audit_findings, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_findings_severity;

-- Table: audit_findings, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_findings_status;

-- Table: audit_findings, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_findings_open;

-- Table: audit_plans, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_plans_org;

-- Table: audit_plans, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_plans_code;

-- Table: audit_plans, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_plans_status;

-- Table: audit_plans, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_plans_type;

-- Table: audit_plans, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_audit_plans_dates;

-- Table: capa, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_capa_org;

-- Table: capa, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_capa_code;

-- Table: capa, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_capa_type;

-- Table: capa, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_capa_status;

-- Table: capa, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_capa_priority;

-- Table: capa, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_capa_assigned;

-- Table: capa, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_capa_overdue;

-- Table: exercise_actions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercise_actions_exercise;

-- Table: exercise_actions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercise_actions_org;

-- Table: exercise_actions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercise_actions_assigned;

-- Table: exercise_actions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercise_actions_status;

-- Table: exercise_actions, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercise_actions_overdue;

-- Table: exercise_observations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_observations_exercise;

-- Table: exercise_observations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_observations_org;

-- Table: exercise_observations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_observations_type;

-- Table: exercise_observations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_observations_severity;

-- Table: exercise_observations, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_observations_status;

-- Table: exercise_scenarios, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_scenarios_org;

-- Table: exercise_scenarios, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_scenarios_type;

-- Table: exercise_scenarios, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_scenarios_active;

-- Table: exercises, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercises_org;

-- Table: exercises, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercises_code;

-- Table: exercises, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercises_status;

-- Table: exercises, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercises_type;

-- Table: exercises, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercises_scheduled;

-- Table: exercises, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_exercises_search;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_kpi_status;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_notification;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_escalation;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_tenant;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_organization;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_kpi;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_status;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_severity;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_triggered;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_active;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_tenant_status;

-- Table: kpi_alerts, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_alerts_org_status;

-- Table: kpi_dashboards, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_dashboards_org;

-- Table: kpi_dashboards, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_dashboards_active;

-- Table: kpi_measurements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_measurements_kpi;

-- Table: kpi_measurements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_measurements_org;

-- Table: kpi_measurements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_measurements_period;

-- Table: kpi_measurements, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpi_measurements_status;

-- Table: kpis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpis_org;

-- Table: kpis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpis_code;

-- Table: kpis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpis_category;

-- Table: kpis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpis_status;

-- Table: kpis, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_kpis_active;

-- Table: management_reviews, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_mgmt_reviews_org;

-- Table: management_reviews, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_mgmt_reviews_code;

-- Table: management_reviews, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_mgmt_reviews_status;

-- Table: management_reviews, Size: unknown, Scans: 0
DROP INDEX IF EXISTS validation.idx_mgmt_reviews_date;
