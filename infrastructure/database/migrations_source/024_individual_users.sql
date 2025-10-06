-- ============================================
-- BCM Platform - Unified Database
-- Migration 024: Individual Users (B2C)
-- ============================================
-- Creates individual_users table for B2C users
-- Based on PLATFORM/clients/app/models/individual.py
-- ============================================

CREATE TABLE public.individual_users (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign key to user profile
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,

    -- User type
    user_type VARCHAR(50) DEFAULT 'freelancer',
    -- Types: freelancer, student, researcher, solo_business, enthusiast

    -- Professional info
    profession VARCHAR(200),
    interests JSONB DEFAULT '[]'::jsonb,  -- ["BIA", "Risk Management", "Crisis Response"]

    -- Subscription
    subscription_tier VARCHAR(50) DEFAULT 'free',  -- free, basic, pro
    subscription_status VARCHAR(50) DEFAULT 'active',  -- active, cancelled, suspended
    subscription_start_date DATE,
    subscription_end_date DATE,

    -- Usage limits (based on tier)
    max_projects INTEGER DEFAULT 1,  -- Max projects allowed
    current_projects_count INTEGER DEFAULT 0,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Status
    is_active BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT individual_users_user_type_check
        CHECK (user_type IN ('freelancer', 'student', 'researcher', 'solo_business', 'enthusiast')),
    CONSTRAINT individual_users_subscription_tier_check
        CHECK (subscription_tier IN ('free', 'basic', 'pro')),
    CONSTRAINT individual_users_subscription_status_check
        CHECK (subscription_status IN ('active', 'cancelled', 'suspended', 'trial')),
    CONSTRAINT individual_users_projects_count_check
        CHECK (current_projects_count >= 0 AND current_projects_count <= max_projects)
);

-- Indexes
CREATE INDEX idx_individual_users_user_id ON public.individual_users(user_id);
CREATE INDEX idx_individual_users_type ON public.individual_users(user_type);
CREATE INDEX idx_individual_users_subscription ON public.individual_users(subscription_tier, subscription_status) WHERE is_active = true;
CREATE INDEX idx_individual_users_active ON public.individual_users(is_active) WHERE is_active = true;

-- Auto-update timestamp trigger
CREATE TRIGGER update_individual_users_updated_at
    BEFORE UPDATE ON public.individual_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE public.individual_users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own profile
CREATE POLICY "Individual users can view own profile"
    ON public.individual_users FOR SELECT
    USING ((SELECT auth.uid()) = user_id);

-- Policy: Users can update their own profile
CREATE POLICY "Individual users can update own profile"
    ON public.individual_users FOR UPDATE
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

-- Policy: Users can insert their own profile
CREATE POLICY "Individual users can insert own profile"
    ON public.individual_users FOR INSERT
    WITH CHECK ((SELECT auth.uid()) = user_id);

-- Comments
COMMENT ON TABLE public.individual_users IS 'Individual users (B2C) - students, researchers, solo practitioners';
COMMENT ON COLUMN public.individual_users.user_type IS 'Type of individual user: freelancer, student, researcher, solo_business, enthusiast';
COMMENT ON COLUMN public.individual_users.subscription_tier IS 'Subscription plan: free, basic, pro';
COMMENT ON COLUMN public.individual_users.max_projects IS 'Maximum number of projects allowed based on subscription tier';
COMMENT ON COLUMN public.individual_users.current_projects_count IS 'Current number of active projects';
