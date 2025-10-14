-- Migration: Fix Function Search Path Mutable (SECURITY)
-- Description: Set immutable search_path on functions to prevent SQL injection
-- Lint: function_search_path_mutable

-- Fix public schema functions
ALTER FUNCTION public.get_user_following_count(uuid)
    SET search_path = public, pg_temp;

ALTER FUNCTION public.get_user_followers_count(uuid)
    SET search_path = public, pg_temp;

-- Fix portal schema functions
ALTER FUNCTION portal.update_articles_updated_at()
    SET search_path = portal, public, pg_temp;

ALTER FUNCTION portal.set_article_published_at()
    SET search_path = portal, public, pg_temp;

ALTER FUNCTION portal.update_article_vote_counts()
    SET search_path = portal, public, pg_temp;

ALTER FUNCTION portal.recalculate_usefulness_score()
    SET search_path = portal, public, pg_temp;

-- Fix learning schema functions
ALTER FUNCTION learning.update_updated_at_column()
    SET search_path = learning, public, pg_temp;

COMMENT ON MIGRATION IS 'Fixed function search_path security vulnerability (0011_function_search_path_mutable)';
