-- ============================================================================
-- Portal Service - Forum Migration
-- ============================================================================
-- Description: Adds Forum with categories, topics, posts, moderation, gamification
-- Date: 2025-10-02
-- Tables: forum_categories, forum_topics, forum_posts, votes, moderation, reputation, badges
-- ============================================================================

-- ============================================================================
-- Table: forum_categories
-- ============================================================================

CREATE TABLE portal.forum_categories (
    id SERIAL PRIMARY KEY,

    -- Category info
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),  -- Icon name or emoji

    -- Hierarchy
    parent_id INTEGER REFERENCES portal.forum_categories(id) ON DELETE SET NULL,
    display_order INTEGER DEFAULT 0,

    -- ISO Mapping
    iso_clause VARCHAR(20),

    -- Stats (denormalized for performance)
    topic_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_forum_categories_parent ON portal.forum_categories(parent_id);
CREATE INDEX idx_forum_categories_order ON portal.forum_categories(display_order);

-- ============================================================================
-- Table: forum_topics
-- ============================================================================

CREATE TYPE portal.topic_status AS ENUM ('active', 'closed', 'archived', 'deleted');

CREATE TABLE portal.forum_topics (
    id SERIAL PRIMARY KEY,

    -- Organization
    category_id INTEGER NOT NULL REFERENCES portal.forum_categories(id) ON DELETE CASCADE,
    tenant_id VARCHAR(255),  -- NULL = public discussion

    -- Content
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,  -- Markdown
    content_html TEXT,  -- Cached HTML

    -- Author
    author_id VARCHAR(255) NOT NULL,
    author_type VARCHAR(50) NOT NULL,  -- user, specialist, admin

    -- Status
    status portal.topic_status DEFAULT 'active' NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    is_solved BOOLEAN DEFAULT FALSE,
    solution_post_id INTEGER,

    -- Linking to content (for discussions)
    linked_article_id INTEGER REFERENCES portal.knowledge_articles(id) ON DELETE SET NULL,
    linked_scenario_id INTEGER REFERENCES portal.scenarios(id) ON DELETE SET NULL,

    -- Engagement
    view_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    vote_score INTEGER DEFAULT 0,

    -- Tags
    tags JSONB DEFAULT '[]'::jsonb,

    -- Activity tracking
    last_post_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_post_by VARCHAR(255),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_forum_topics_category ON portal.forum_topics(category_id);
CREATE INDEX idx_forum_topics_tenant ON portal.forum_topics(tenant_id);
CREATE INDEX idx_forum_topics_status ON portal.forum_topics(status);
CREATE INDEX idx_forum_topics_activity ON portal.forum_topics(last_post_at DESC);
CREATE INDEX idx_forum_topics_votes ON portal.forum_topics(vote_score DESC);
CREATE INDEX idx_forum_topics_article ON portal.forum_topics(linked_article_id);
CREATE INDEX idx_forum_topics_scenario ON portal.forum_topics(linked_scenario_id);
CREATE INDEX idx_forum_topics_tags ON portal.forum_topics USING GIN (tags);

-- ============================================================================
-- Table: forum_posts
-- ============================================================================

CREATE TABLE portal.forum_posts (
    id SERIAL PRIMARY KEY,

    -- References
    topic_id INTEGER NOT NULL REFERENCES portal.forum_topics(id) ON DELETE CASCADE,
    parent_post_id INTEGER REFERENCES portal.forum_posts(id) ON DELETE SET NULL,  -- For nested replies

    -- Content
    content TEXT NOT NULL,  -- Markdown
    content_html TEXT,  -- Cached HTML

    -- Author
    author_id VARCHAR(255) NOT NULL,
    author_type VARCHAR(50) NOT NULL,

    -- Status
    is_deleted BOOLEAN DEFAULT FALSE,
    is_hidden BOOLEAN DEFAULT FALSE,  -- Hidden by moderator

    -- Engagement
    vote_score INTEGER DEFAULT 0,
    is_solution BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    edited_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_forum_posts_topic ON portal.forum_posts(topic_id);
CREATE INDEX idx_forum_posts_author ON portal.forum_posts(author_id);
CREATE INDEX idx_forum_posts_parent ON portal.forum_posts(parent_post_id);
CREATE INDEX idx_forum_posts_votes ON portal.forum_posts(vote_score DESC);

-- ============================================================================
-- Table: topic_votes
-- ============================================================================

CREATE TABLE portal.topic_votes (
    id SERIAL PRIMARY KEY,

    topic_id INTEGER NOT NULL REFERENCES portal.forum_topics(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,

    vote INTEGER NOT NULL CHECK (vote IN (1, -1)),  -- 1 = upvote, -1 = downvote

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    UNIQUE(user_id, topic_id)
);

-- Indexes
CREATE INDEX idx_topic_votes_topic ON portal.topic_votes(topic_id);
CREATE INDEX idx_topic_votes_user ON portal.topic_votes(user_id);

-- ============================================================================
-- Table: post_votes
-- ============================================================================

CREATE TABLE portal.post_votes (
    id SERIAL PRIMARY KEY,

    post_id INTEGER NOT NULL REFERENCES portal.forum_posts(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,

    vote INTEGER NOT NULL CHECK (vote IN (1, -1)),  -- 1 = upvote, -1 = downvote

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    UNIQUE(user_id, post_id)
);

-- Indexes
CREATE INDEX idx_post_votes_post ON portal.post_votes(post_id);
CREATE INDEX idx_post_votes_user ON portal.post_votes(user_id);

-- ============================================================================
-- Table: moderation_flags
-- ============================================================================

CREATE TYPE portal.moderation_action AS ENUM ('approved', 'rejected', 'hidden', 'deleted');

CREATE TABLE portal.moderation_flags (
    id SERIAL PRIMARY KEY,

    -- What's being flagged
    topic_id INTEGER REFERENCES portal.forum_topics(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES portal.forum_posts(id) ON DELETE CASCADE,

    -- Reporter
    reporter_id VARCHAR(255) NOT NULL,
    reason VARCHAR(50) NOT NULL,  -- spam, inappropriate, offensive, other
    description TEXT,

    -- Moderation
    status VARCHAR(20) DEFAULT 'pending',  -- pending, reviewed, resolved
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMP,
    action_taken portal.moderation_action,
    moderator_notes TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_moderation_flags_status ON portal.moderation_flags(status);
CREATE INDEX idx_moderation_flags_topic ON portal.moderation_flags(topic_id);
CREATE INDEX idx_moderation_flags_post ON portal.moderation_flags(post_id);

-- ============================================================================
-- Table: user_reputation
-- ============================================================================

CREATE TYPE portal.reputation_level AS ENUM ('newbie', 'contributor', 'expert', 'guru', 'legend');

CREATE TABLE portal.user_reputation (
    id SERIAL PRIMARY KEY,

    user_id VARCHAR(255) UNIQUE NOT NULL,

    -- Reputation
    reputation_score INTEGER DEFAULT 0,
    reputation_level portal.reputation_level DEFAULT 'newbie' NOT NULL,

    -- Activity stats
    topics_created INTEGER DEFAULT 0,
    posts_created INTEGER DEFAULT 0,
    solutions_marked INTEGER DEFAULT 0,
    upvotes_received INTEGER DEFAULT 0,
    downvotes_received INTEGER DEFAULT 0,
    badges_earned INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_user_reputation_score ON portal.user_reputation(reputation_score DESC);
CREATE INDEX idx_user_reputation_level ON portal.user_reputation(reputation_level);

-- ============================================================================
-- Table: badges
-- ============================================================================

CREATE TABLE portal.badges (
    id SERIAL PRIMARY KEY,

    badge_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    badge_type VARCHAR(50) NOT NULL,  -- certification, achievement, special
    tier VARCHAR(20),  -- bronze, silver, gold

    -- Criteria
    criteria JSONB,  -- Conditions to earn badge
    points_value INTEGER DEFAULT 10,  -- Reputation points awarded

    -- Visual
    icon_url VARCHAR(500),
    color VARCHAR(20),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_badges_type ON portal.badges(badge_type);

-- ============================================================================
-- Table: user_badges
-- ============================================================================

CREATE TABLE portal.user_badges (
    id SERIAL PRIMARY KEY,

    user_id VARCHAR(255) NOT NULL,
    badge_id INTEGER NOT NULL REFERENCES portal.badges(id) ON DELETE CASCADE,

    -- Context
    earned_for VARCHAR(500),  -- Description of why/how earned

    -- Metadata
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    UNIQUE(user_id, badge_id)
);

-- Indexes
CREATE INDEX idx_user_badges_user ON portal.user_badges(user_id);
CREATE INDEX idx_user_badges_badge ON portal.user_badges(badge_id);

-- ============================================================================
-- Table: reputation_events
-- ============================================================================

CREATE TABLE portal.reputation_events (
    id SERIAL PRIMARY KEY,

    user_id VARCHAR(255) NOT NULL,

    -- Event details
    event_type VARCHAR(50) NOT NULL,  -- topic_created, post_upvoted, solution_marked, etc.
    points_change INTEGER NOT NULL,  -- Can be positive or negative

    -- Context
    topic_id INTEGER REFERENCES portal.forum_topics(id) ON DELETE SET NULL,
    post_id INTEGER REFERENCES portal.forum_posts(id) ON DELETE SET NULL,
    badge_id INTEGER REFERENCES portal.badges(id) ON DELETE SET NULL,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_reputation_events_user ON portal.reputation_events(user_id);
CREATE INDEX idx_reputation_events_type ON portal.reputation_events(event_type);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Update topic.post_count when post is created/deleted
CREATE OR REPLACE FUNCTION portal.update_topic_post_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE portal.forum_topics
        SET post_count = post_count + 1,
            last_post_at = NEW.created_at,
            last_post_by = NEW.author_id
        WHERE id = NEW.topic_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE portal.forum_topics
        SET post_count = post_count - 1
        WHERE id = OLD.topic_id;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_topic_post_count
    AFTER INSERT OR DELETE ON portal.forum_posts
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_topic_post_count();

-- Trigger: Update category stats when topic is created/deleted
CREATE OR REPLACE FUNCTION portal.update_category_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE portal.forum_categories
        SET topic_count = topic_count + 1
        WHERE id = NEW.category_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE portal.forum_categories
        SET topic_count = topic_count - 1
        WHERE id = OLD.category_id;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_category_stats
    AFTER INSERT OR DELETE ON portal.forum_topics
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_category_stats();

-- Trigger: Update topic vote_score when vote changes
CREATE OR REPLACE FUNCTION portal.update_topic_vote_score()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE portal.forum_topics
        SET vote_score = vote_score + NEW.vote
        WHERE id = NEW.topic_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE portal.forum_topics
        SET vote_score = vote_score - OLD.vote + NEW.vote
        WHERE id = NEW.topic_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE portal.forum_topics
        SET vote_score = vote_score - OLD.vote
        WHERE id = OLD.topic_id;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_topic_vote_score
    AFTER INSERT OR UPDATE OR DELETE ON portal.topic_votes
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_topic_vote_score();

-- Trigger: Update post vote_score when vote changes
CREATE OR REPLACE FUNCTION portal.update_post_vote_score()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE portal.forum_posts
        SET vote_score = vote_score + NEW.vote
        WHERE id = NEW.post_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE portal.forum_posts
        SET vote_score = vote_score - OLD.vote + NEW.vote
        WHERE id = NEW.post_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE portal.forum_posts
        SET vote_score = vote_score - OLD.vote
        WHERE id = OLD.post_id;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_post_vote_score
    AFTER INSERT OR UPDATE OR DELETE ON portal.post_votes
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_post_vote_score();

-- Trigger: Auto-update reputation level when score changes
CREATE OR REPLACE FUNCTION portal.update_reputation_level()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.reputation_score >= 2500 THEN
        NEW.reputation_level = 'legend';
    ELSIF NEW.reputation_score >= 1000 THEN
        NEW.reputation_level = 'guru';
    ELSIF NEW.reputation_score >= 500 THEN
        NEW.reputation_level = 'expert';
    ELSIF NEW.reputation_score >= 100 THEN
        NEW.reputation_level = 'contributor';
    ELSE
        NEW.reputation_level = 'newbie';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_reputation_level
    BEFORE INSERT OR UPDATE OF reputation_score ON portal.user_reputation
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_reputation_level();

-- ============================================================================
-- SAMPLE DATA - Forum Categories
-- ============================================================================

INSERT INTO portal.forum_categories (name, slug, description, icon, iso_clause, display_order) VALUES
('General Discussion', 'general', 'General BCM topics and questions', '💬', NULL, 1),
('ISO 22301 Implementation', 'iso-22301', 'Discussions about implementing ISO 22301', '📋', NULL, 2),
('Business Impact Analysis', 'bia', 'BIA methodologies and best practices', '📊', '8.2', 3),
('Risk Assessment', 'risk', 'Risk identification and treatment', '⚠️', '8.2', 4),
('Business Continuity Plans', 'bc-plans', 'Plan development and maintenance', '📝', '8.3', 5),
('Incident Response', 'incident-response', 'Incident management and response', '🚨', '8.4', 6),
('Testing & Exercises', 'exercises', 'Exercise planning and execution', '🎯', '8.5', 7),
('Case Studies', 'case-studies', 'Real-world BCM experiences', '📚', NULL, 8),
('Tools & Technology', 'tools', 'BCM software and tools discussion', '🔧', NULL, 9),
('Announcements', 'announcements', 'Platform updates and news', '📢', NULL, 0);

-- ============================================================================
-- SAMPLE DATA - Badges
-- ============================================================================

INSERT INTO portal.badges (badge_code, name, description, badge_type, tier, criteria, points_value, color) VALUES
-- Certification Badges (Gold)
('iso22301-lead-implementer', 'ISO 22301 Lead Implementer', 'Certified ISO 22301 Lead Implementer', 'certification', 'gold', '{"certification": "ISO 22301 Lead Implementer"}'::jsonb, 50, '#FFD700'),
('iso22301-lead-auditor', 'ISO 22301 Lead Auditor', 'Certified ISO 22301 Lead Auditor', 'certification', 'gold', '{"certification": "ISO 22301 Lead Auditor"}'::jsonb, 50, '#FFD700'),
('bci-certified', 'BCI Certified Professional', 'Business Continuity Institute Certification', 'certification', 'gold', '{"certification": "BCI"}'::jsonb, 50, '#FFD700'),

-- Achievement Badges
('first-post', 'First Post', 'Created your first forum post', 'achievement', 'bronze', '{"posts_created": 1}'::jsonb, 10, '#CD7F32'),
('helpful', 'Helpful', 'Received 50+ upvotes on posts', 'achievement', 'silver', '{"upvotes_received": 50}'::jsonb, 25, '#C0C0C0'),
('expert-contributor', 'Expert Contributor', 'Created 100+ posts', 'achievement', 'gold', '{"posts_created": 100}'::jsonb, 50, '#FFD700'),
('problem-solver', 'Problem Solver', 'Had 10 posts marked as solutions', 'achievement', 'gold', '{"solutions_marked": 10}'::jsonb, 50, '#FFD700'),

-- Reputation Badges
('rising-star', 'Rising Star', 'Reached 100 reputation points', 'achievement', 'bronze', '{"reputation_score": 100}'::jsonb, 10, '#CD7F32'),
('community-leader', 'Community Leader', 'Reached 1000 reputation points', 'achievement', 'silver', '{"reputation_score": 1000}'::jsonb, 25, '#C0C0C0'),
('guru', 'BCM Guru', 'Reached 2500 reputation points', 'achievement', 'gold', '{"reputation_score": 2500}'::jsonb, 50, '#FFD700');

-- ============================================================================
-- Rollback Script
-- ============================================================================

/*
-- Drop triggers
DROP TRIGGER IF EXISTS trigger_update_reputation_level ON portal.user_reputation;
DROP TRIGGER IF EXISTS trigger_update_post_vote_score ON portal.post_votes;
DROP TRIGGER IF EXISTS trigger_update_topic_vote_score ON portal.topic_votes;
DROP TRIGGER IF EXISTS trigger_update_category_stats ON portal.forum_topics;
DROP TRIGGER IF EXISTS trigger_update_topic_post_count ON portal.forum_posts;

-- Drop functions
DROP FUNCTION IF EXISTS portal.update_reputation_level();
DROP FUNCTION IF EXISTS portal.update_post_vote_score();
DROP FUNCTION IF EXISTS portal.update_topic_vote_score();
DROP FUNCTION IF EXISTS portal.update_category_stats();
DROP FUNCTION IF EXISTS portal.update_topic_post_count();

-- Drop tables
DROP TABLE IF EXISTS portal.reputation_events CASCADE;
DROP TABLE IF EXISTS portal.user_badges CASCADE;
DROP TABLE IF EXISTS portal.badges CASCADE;
DROP TABLE IF EXISTS portal.user_reputation CASCADE;
DROP TABLE IF EXISTS portal.moderation_flags CASCADE;
DROP TABLE IF EXISTS portal.post_votes CASCADE;
DROP TABLE IF EXISTS portal.topic_votes CASCADE;
DROP TABLE IF EXISTS portal.forum_posts CASCADE;
DROP TABLE IF EXISTS portal.forum_topics CASCADE;
DROP TABLE IF EXISTS portal.forum_categories CASCADE;

-- Drop types
DROP TYPE IF EXISTS portal.reputation_level;
DROP TYPE IF EXISTS portal.moderation_action;
DROP TYPE IF EXISTS portal.topic_status;
*/
