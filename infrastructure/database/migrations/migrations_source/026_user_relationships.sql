-- ============================================
-- BCM Platform - Unified Database
-- Migration 026: User Relationships
-- ============================================
-- Creates user_relationships table for connections between users
-- Based on PLATFORM/clients/app/models/relationship.py
-- ============================================

CREATE TABLE public.user_relationships (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Users involved
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,  -- Source user
    related_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,  -- Target user

    -- Relationship type
    relationship_type VARCHAR(50) NOT NULL,
    -- Types: colleague, mentor, mentee, follows, blocked

    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    -- Status: pending, accepted, rejected, blocked

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT user_relationships_different_users
        CHECK (user_id != related_user_id),
    CONSTRAINT user_relationships_type_check
        CHECK (relationship_type IN ('colleague', 'mentor', 'mentee', 'follows', 'blocked', 'friend')),
    CONSTRAINT user_relationships_status_check
        CHECK (status IN ('pending', 'accepted', 'rejected', 'blocked')),
    CONSTRAINT user_relationships_unique_pair
        UNIQUE (user_id, related_user_id, relationship_type)
);

-- Indexes
CREATE INDEX idx_user_relationships_user_id ON public.user_relationships(user_id);
CREATE INDEX idx_user_relationships_related_user_id ON public.user_relationships(related_user_id);
CREATE INDEX idx_user_relationships_type ON public.user_relationships(relationship_type);
CREATE INDEX idx_user_relationships_status ON public.user_relationships(status);
CREATE INDEX idx_user_relationships_user_type ON public.user_relationships(user_id, relationship_type);
CREATE INDEX idx_user_relationships_both_users ON public.user_relationships(user_id, related_user_id);

-- Auto-update timestamp trigger
CREATE TRIGGER update_user_relationships_updated_at
    BEFORE UPDATE ON public.user_relationships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE public.user_relationships ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own relationships
CREATE POLICY "Users can view own relationships"
    ON public.user_relationships FOR SELECT
    USING (
        (SELECT auth.uid()) = user_id
        OR (SELECT auth.uid()) = related_user_id
    );

-- Policy: Users can create relationships
CREATE POLICY "Users can create relationships"
    ON public.user_relationships FOR INSERT
    WITH CHECK ((SELECT auth.uid()) = user_id);

-- Policy: Users can update their own relationships
CREATE POLICY "Users can update own relationships"
    ON public.user_relationships FOR UPDATE
    USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

-- Policy: Users can delete their own relationships
CREATE POLICY "Users can delete own relationships"
    ON public.user_relationships FOR DELETE
    USING ((SELECT auth.uid()) = user_id);

-- Policy: Target users can update relationship status
CREATE POLICY "Target users can update relationship status"
    ON public.user_relationships FOR UPDATE
    USING ((SELECT auth.uid()) = related_user_id)
    WITH CHECK ((SELECT auth.uid()) = related_user_id);

-- Create view for mutual relationships (both users follow each other)
CREATE OR REPLACE VIEW public.v_mutual_relationships AS
SELECT
    r1.id,
    r1.user_id,
    r1.related_user_id,
    r1.relationship_type,
    r1.created_at
FROM public.user_relationships r1
WHERE r1.status = 'accepted'
AND EXISTS (
    SELECT 1 FROM public.user_relationships r2
    WHERE r2.user_id = r1.related_user_id
    AND r2.related_user_id = r1.user_id
    AND r2.relationship_type = r1.relationship_type
    AND r2.status = 'accepted'
);

-- Create function to get user followers count
CREATE OR REPLACE FUNCTION public.get_user_followers_count(target_user_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)::INTEGER
        FROM public.user_relationships
        WHERE related_user_id = target_user_id
        AND relationship_type = 'follows'
        AND status = 'accepted'
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Create function to get user following count
CREATE OR REPLACE FUNCTION public.get_user_following_count(target_user_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)::INTEGER
        FROM public.user_relationships
        WHERE user_id = target_user_id
        AND relationship_type = 'follows'
        AND status = 'accepted'
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Comments
COMMENT ON TABLE public.user_relationships IS 'Relationships between users - colleague, mentor, follows, blocked';
COMMENT ON COLUMN public.user_relationships.relationship_type IS 'Type of relationship: colleague, mentor, mentee, follows, blocked, friend';
COMMENT ON COLUMN public.user_relationships.status IS 'Status: pending, accepted, rejected, blocked';
COMMENT ON VIEW public.v_mutual_relationships IS 'View showing mutual relationships where both users follow each other';
COMMENT ON FUNCTION public.get_user_followers_count IS 'Get count of users following the target user';
COMMENT ON FUNCTION public.get_user_following_count IS 'Get count of users the target user is following';
