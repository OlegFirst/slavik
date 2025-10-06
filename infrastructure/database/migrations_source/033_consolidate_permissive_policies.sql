-- Migration: Consolidate Multiple Permissive RLS Policies (PERFORMANCE)
-- Description: Merge multiple permissive policies into single policies using OR conditions
-- Lint: multiple_permissive_policies (WARN - PERFORMANCE)

-- Note: Multiple permissive policies cause ALL policies to execute for every query
-- Consolidating them into single policies with OR conditions improves performance

-- =========================================
-- BCM SCHEMA
-- =========================================

-- bcm.communication_plans
DROP POLICY IF EXISTS "Communication plans manageable by org admins" ON bcm.communication_plans;
DROP POLICY IF EXISTS "Communication plans visible to org members" ON bcm.communication_plans;
CREATE POLICY "communication_plans_access" ON bcm.communication_plans
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- bcm.documents
DROP POLICY IF EXISTS "Documents manageable by org admins" ON bcm.documents;
DROP POLICY IF EXISTS "Documents visible to org members" ON bcm.documents;
CREATE POLICY "documents_select" ON bcm.documents
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- bcm.plans
DROP POLICY IF EXISTS "Plans manageable by org admins" ON bcm.plans;
DROP POLICY IF EXISTS "Plans visible to org members" ON bcm.plans;
CREATE POLICY "plans_access" ON bcm.plans
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- bcm.procedures
DROP POLICY IF EXISTS "Procedures manageable by org admins" ON bcm.procedures;
DROP POLICY IF EXISTS "Procedures visible to org members" ON bcm.procedures;
CREATE POLICY "procedures_access" ON bcm.procedures
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- bcm.resources
DROP POLICY IF EXISTS "BCM resources manageable by org admins" ON bcm.resources;
DROP POLICY IF EXISTS "BCM resources visible to org members" ON bcm.resources;
CREATE POLICY "resources_access" ON bcm.resources
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- =========================================
-- BIA SCHEMA
-- =========================================

-- bia.dependencies
DROP POLICY IF EXISTS "Dependencies manageable by org admins" ON bia.dependencies;
DROP POLICY IF EXISTS "Dependencies visible to org members" ON bia.dependencies;
CREATE POLICY "dependencies_access" ON bia.dependencies
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- bia.impact_assessments
DROP POLICY IF EXISTS "Impact assessments manageable by org admins" ON bia.impact_assessments;
DROP POLICY IF EXISTS "Impact assessments visible to org members" ON bia.impact_assessments;
CREATE POLICY "impact_assessments_access" ON bia.impact_assessments
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- bia.processes
DROP POLICY IF EXISTS "BIA processes manageable by org admins" ON bia.processes;
DROP POLICY IF EXISTS "BIA processes visible to org members" ON bia.processes;
CREATE POLICY "processes_access" ON bia.processes
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- =========================================
-- COMMUNITY SCHEMA
-- =========================================

-- community.ai_digital_colleagues
DROP POLICY IF EXISTS "AI colleagues manageable by org admins" ON community.ai_digital_colleagues;
DROP POLICY IF EXISTS "AI colleagues visible to org members" ON community.ai_digital_colleagues;
CREATE POLICY "ai_digital_colleagues_access" ON community.ai_digital_colleagues
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- =========================================
-- COMPLIANCE SCHEMA
-- =========================================

-- compliance.requirements
DROP POLICY IF EXISTS "Compliance requirements manageable by org admins" ON compliance.requirements;
DROP POLICY IF EXISTS "Compliance requirements visible to org members" ON compliance.requirements;
CREATE POLICY "requirements_access" ON compliance.requirements
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- =========================================
-- GOVERNANCE SCHEMA
-- =========================================

-- governance.objectives
DROP POLICY IF EXISTS "Objectives manageable by org admins" ON governance.objectives;
DROP POLICY IF EXISTS "Objectives visible to org members" ON governance.objectives;
CREATE POLICY "objectives_access" ON governance.objectives
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- governance.policies
DROP POLICY IF EXISTS "Policies manageable by org admins" ON governance.policies;
DROP POLICY IF EXISTS "Policies visible to org members" ON governance.policies;
CREATE POLICY "policies_access" ON governance.policies
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- governance.roles
DROP POLICY IF EXISTS "Roles manageable by org admins" ON governance.roles;
DROP POLICY IF EXISTS "Roles visible to org members" ON governance.roles;
CREATE POLICY "roles_access" ON governance.roles
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- =========================================
-- INTELLIGENCE SCHEMA
-- =========================================

-- intelligence.digital_twins
DROP POLICY IF EXISTS "Digital twins manageable by org admins" ON intelligence.digital_twins;
DROP POLICY IF EXISTS "Digital twins visible to org members" ON intelligence.digital_twins;
CREATE POLICY "digital_twins_access" ON intelligence.digital_twins
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- =========================================
-- LEARNING SCHEMA
-- =========================================

-- learning.awareness_campaigns
DROP POLICY IF EXISTS "Awareness campaigns manageable by org admins" ON learning.awareness_campaigns;
DROP POLICY IF EXISTS "Awareness campaigns visible to org members" ON learning.awareness_campaigns;
CREATE POLICY "awareness_campaigns_access" ON learning.awareness_campaigns
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- learning.training_programs
DROP POLICY IF EXISTS "Training programs manageable by org admins" ON learning.training_programs;
DROP POLICY IF EXISTS "Training programs visible to org members" ON learning.training_programs;
CREATE POLICY "training_programs_access" ON learning.training_programs
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- =========================================
-- PUBLIC SCHEMA
-- =========================================

-- public.individual_users
DROP POLICY IF EXISTS "Individual users can view own profile" ON public.individual_users;
DROP POLICY IF EXISTS "Platform admins can view all individual users" ON public.individual_users;
CREATE POLICY "individual_users_select" ON public.individual_users
    FOR SELECT
    USING (
        auth_user_id = (SELECT auth.uid())
        OR EXISTS (
            SELECT 1 FROM public.platform_administrators
            WHERE auth_user_id = (SELECT auth.uid())
        )
    );

-- public.organization_users
DROP POLICY IF EXISTS "Org users manageable by admins" ON public.organization_users;
DROP POLICY IF EXISTS "Org users visible to org members" ON public.organization_users;
CREATE POLICY "organization_users_select" ON public.organization_users
    FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
    );

-- public.organizations
DROP POLICY IF EXISTS "Organizations visible to members" ON public.organizations;
DROP POLICY IF EXISTS "Platform admins can view all organizations" ON public.organizations;
CREATE POLICY "organizations_select" ON public.organizations
    FOR SELECT
    USING (
        id IN (
            SELECT organization_id
            FROM public.organization_users
            WHERE user_id = (SELECT auth.uid())
        )
        OR EXISTS (
            SELECT 1 FROM public.platform_administrators
            WHERE auth_user_id = (SELECT auth.uid())
        )
    );

-- public.platform_administrators
DROP POLICY IF EXISTS "Platform admins can view own profile" ON public.platform_administrators;
DROP POLICY IF EXISTS "Super admins can manage all admins" ON public.platform_administrators;
DROP POLICY IF EXISTS "Super admins can view all admins" ON public.platform_administrators;
CREATE POLICY "platform_administrators_select" ON public.platform_administrators
    FOR SELECT
    USING (
        auth_user_id = (SELECT auth.uid())
        OR EXISTS (
            SELECT 1 FROM public.platform_administrators
            WHERE auth_user_id = (SELECT auth.uid())
            AND role = 'super_admin'
        )
    );

COMMENT ON MIGRATION IS 'Consolidated multiple permissive RLS policies to improve query performance';
