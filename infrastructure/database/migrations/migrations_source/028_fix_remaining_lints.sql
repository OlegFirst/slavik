-- ============================================
-- BCM Platform - Unified Database
-- Migration 028: Fix Remaining Supabase Lints
-- ============================================
-- 1. Fix function search_path for 3 functions in public
-- 2. Move unaccent extension from public to extensions schema
-- 3. Enable RLS on schema_migrations table
-- ============================================

-- ============================================
-- Part 1: Fix function search_path
-- ============================================

-- Fix update_specialist_rating function
CREATE OR REPLACE FUNCTION public.update_specialist_rating()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = ''
AS $function$
BEGIN
    UPDATE community.specialists
    SET
        rating = (
            SELECT COALESCE(AVG(rating), 0)
            FROM community.specialist_reviews
            WHERE specialist_id = NEW.specialist_id
        ),
        review_count = (
            SELECT COUNT(*)
            FROM community.specialist_reviews
            WHERE specialist_id = NEW.specialist_id
        )
    WHERE id = NEW.specialist_id;

    RETURN NEW;
END;
$function$;

-- Fix update_project_proposal_count function
CREATE OR REPLACE FUNCTION public.update_project_proposal_count()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = ''
AS $function$
BEGIN
    UPDATE community.specialist_engagements
    SET
        proposal_count = (
            SELECT COUNT(*)
            FROM community.specialist_engagements
            WHERE project_id = NEW.project_id
            AND status IN ('pending', 'accepted')
        )
    WHERE id = NEW.project_id;

    RETURN NEW;
END;
$function$;

-- Fix update_specialist_completed_projects function
CREATE OR REPLACE FUNCTION public.update_specialist_completed_projects()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = ''
AS $function$
BEGIN
    IF NEW.status = 'completed' AND (OLD.status IS NULL OR OLD.status != 'completed') THEN
        UPDATE community.specialists
        SET
            completed_projects = completed_projects + 1,
            total_earned = total_earned + COALESCE(NEW.budget, 0)
        WHERE id = NEW.specialist_id;
    END IF;

    RETURN NEW;
END;
$function$;

-- ============================================
-- Part 2: Move unaccent extension
-- ============================================

-- Drop from public if exists
DROP EXTENSION IF EXISTS unaccent CASCADE;

-- Create in extensions schema
CREATE EXTENSION IF NOT EXISTS unaccent SCHEMA extensions;

-- ============================================
-- Part 3: Enable RLS on schema_migrations
-- ============================================

-- Enable RLS on schema_migrations table
ALTER TABLE IF EXISTS public.schema_migrations ENABLE ROW LEVEL SECURITY;

-- Policy: Only platform admins can view schema_migrations
CREATE POLICY "Platform admins can view schema_migrations"
    ON public.schema_migrations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.platform_administrators pa
            WHERE pa.user_id = (SELECT auth.uid()) AND pa.is_active = true
        )
    );

-- Policy: Only super admins can manage schema_migrations
CREATE POLICY "Super admins can manage schema_migrations"
    ON public.schema_migrations FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.platform_administrators pa
            WHERE pa.user_id = (SELECT auth.uid())
            AND pa.admin_level = 'super_admin'
            AND pa.is_active = true
        )
    );

-- Comments
COMMENT ON POLICY "Platform admins can view schema_migrations" ON public.schema_migrations
    IS 'Platform administrators can view migration history';
COMMENT ON POLICY "Super admins can manage schema_migrations" ON public.schema_migrations
    IS 'Only super admins can add/modify/delete migrations';
