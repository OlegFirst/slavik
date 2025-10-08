-- Migration: Fix Security Definer View ERROR
-- Description: Remove SECURITY DEFINER from views (security vulnerability)
-- Lint: security_definer_view

-- Drop and recreate view without SECURITY DEFINER
DROP VIEW IF EXISTS public.v_mutual_relationships;

-- Recreate view without SECURITY DEFINER
CREATE OR REPLACE VIEW public.v_mutual_relationships AS
SELECT
    r1.id,
    r1.user_id,
    r1.related_user_id,
    r1.relationship_type,
    r1.created_at
FROM public.user_relationships r1
WHERE EXISTS (
    SELECT 1
    FROM public.user_relationships r2
    WHERE r2.user_id = r1.related_user_id
    AND r2.related_user_id = r1.user_id
    AND r2.relationship_type = r1.relationship_type
);

-- Add RLS policy if needed
ALTER VIEW public.v_mutual_relationships SET (security_invoker = true);

COMMENT ON VIEW public.v_mutual_relationships IS 'Shows mutual relationships between users (uses SECURITY INVOKER for proper RLS)';
