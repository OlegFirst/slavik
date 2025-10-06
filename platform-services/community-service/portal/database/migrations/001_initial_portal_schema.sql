-- ============================================================================
-- Portal Service - Initial Schema Migration
-- ============================================================================
-- Description: Creates portal schema with Knowledge Hub tables
-- Date: 2025-10-02
-- Tables: knowledge_articles, article_bookmarks, article_votes
-- ============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS portal;

-- Enable extensions for full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- ============================================================================
-- Table: knowledge_articles
-- ============================================================================

CREATE TABLE portal.knowledge_articles (
    id SERIAL PRIMARY KEY,

    -- Multi-tenancy
    tenant_id VARCHAR(255),  -- NULL = public article

    -- Content
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    summary VARCHAR(1000) NOT NULL,
    content TEXT NOT NULL,  -- Markdown
    content_html TEXT,  -- Cached HTML

    -- Categorization
    category VARCHAR(100) NOT NULL,
    tags JSONB DEFAULT '[]'::jsonb,
    iso_clause VARCHAR(20),

    -- Authorship
    author_id VARCHAR(255) NOT NULL,
    author_type VARCHAR(50) NOT NULL,  -- 'user', 'specialist', 'admin'

    -- Publishing
    published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,

    -- AI Generation
    ai_generated BOOLEAN DEFAULT FALSE,
    ai_confidence_score FLOAT,  -- 0.0 - 1.0
    source_exercise_id INTEGER,

    -- Expert Verification
    verification_status VARCHAR(20) DEFAULT 'pending',  -- pending, verified, rejected
    verified_by VARCHAR(255),
    verified_at TIMESTAMP,
    verification_notes TEXT,

    -- Engagement Metrics
    view_count INTEGER DEFAULT 0,
    usefulness_score FLOAT DEFAULT 0.0,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_articles_tenant ON portal.knowledge_articles(tenant_id);
CREATE INDEX idx_articles_published ON portal.knowledge_articles(published, published_at);
CREATE INDEX idx_articles_category ON portal.knowledge_articles(category);
CREATE INDEX idx_articles_verification ON portal.knowledge_articles(verification_status);
CREATE INDEX idx_articles_usefulness ON portal.knowledge_articles(usefulness_score DESC);
CREATE INDEX idx_articles_created ON portal.knowledge_articles(created_at DESC);

-- Full-text search index (GIN)
CREATE INDEX idx_articles_fts ON portal.knowledge_articles
    USING GIN (to_tsvector('english', title || ' ' || summary || ' ' || content));

-- GIN index for tags (JSONB)
CREATE INDEX idx_articles_tags ON portal.knowledge_articles USING GIN (tags);

-- Trigger: auto-update updated_at
CREATE OR REPLACE FUNCTION portal.update_articles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_articles_updated_at
    BEFORE UPDATE ON portal.knowledge_articles
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_articles_updated_at();

-- Trigger: auto-set published_at when published becomes true
CREATE OR REPLACE FUNCTION portal.set_article_published_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.published = TRUE AND OLD.published = FALSE THEN
        NEW.published_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_article_published_at
    BEFORE UPDATE ON portal.knowledge_articles
    FOR EACH ROW
    EXECUTE FUNCTION portal.set_article_published_at();

-- Row Level Security (RLS)
ALTER TABLE portal.knowledge_articles ENABLE ROW LEVEL SECURITY;

-- Policy: Read public articles or own tenant articles
CREATE POLICY articles_tenant_isolation ON portal.knowledge_articles
    FOR SELECT
    USING (
        tenant_id IS NULL  -- Public articles
        OR tenant_id = current_setting('app.current_tenant_id', TRUE)
    );

-- Policy: Write only to own tenant
CREATE POLICY articles_tenant_write ON portal.knowledge_articles
    FOR INSERT
    WITH CHECK (
        tenant_id IS NULL  -- Allow creating public articles
        OR tenant_id = current_setting('app.current_tenant_id', TRUE)
    );

-- ============================================================================
-- Table: article_bookmarks
-- ============================================================================

CREATE TABLE portal.article_bookmarks (
    id SERIAL PRIMARY KEY,

    user_id VARCHAR(255) NOT NULL,
    article_id INTEGER NOT NULL REFERENCES portal.knowledge_articles(id) ON DELETE CASCADE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    UNIQUE(user_id, article_id)
);

-- Indexes
CREATE INDEX idx_bookmarks_user ON portal.article_bookmarks(user_id);
CREATE INDEX idx_bookmarks_article ON portal.article_bookmarks(article_id);

-- ============================================================================
-- Table: article_votes
-- ============================================================================

CREATE TABLE portal.article_votes (
    id SERIAL PRIMARY KEY,

    user_id VARCHAR(255) NOT NULL,
    article_id INTEGER NOT NULL REFERENCES portal.knowledge_articles(id) ON DELETE CASCADE,

    vote INTEGER NOT NULL CHECK (vote IN (1, -1)),  -- 1 = upvote, -1 = downvote

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    UNIQUE(user_id, article_id)
);

-- Indexes
CREATE INDEX idx_votes_article ON portal.article_votes(article_id);
CREATE INDEX idx_votes_user ON portal.article_votes(user_id);

-- Trigger: auto-update updated_at
CREATE TRIGGER trigger_votes_updated_at
    BEFORE UPDATE ON portal.article_votes
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_articles_updated_at();

-- Trigger: Update article vote counts when vote is inserted/updated/deleted
CREATE OR REPLACE FUNCTION portal.update_article_vote_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE portal.knowledge_articles
        SET upvotes = upvotes + CASE WHEN NEW.vote = 1 THEN 1 ELSE 0 END,
            downvotes = downvotes + CASE WHEN NEW.vote = -1 THEN 1 ELSE 0 END
        WHERE id = NEW.article_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Remove old vote
        UPDATE portal.knowledge_articles
        SET upvotes = upvotes - CASE WHEN OLD.vote = 1 THEN 1 ELSE 0 END,
            downvotes = downvotes - CASE WHEN OLD.vote = -1 THEN 1 ELSE 0 END
        WHERE id = OLD.article_id;
        -- Add new vote
        UPDATE portal.knowledge_articles
        SET upvotes = upvotes + CASE WHEN NEW.vote = 1 THEN 1 ELSE 0 END,
            downvotes = downvotes + CASE WHEN NEW.vote = -1 THEN 1 ELSE 0 END
        WHERE id = NEW.article_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE portal.knowledge_articles
        SET upvotes = upvotes - CASE WHEN OLD.vote = 1 THEN 1 ELSE 0 END,
            downvotes = downvotes - CASE WHEN OLD.vote = -1 THEN 1 ELSE 0 END
        WHERE id = OLD.article_id;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_article_votes
    AFTER INSERT OR UPDATE OR DELETE ON portal.article_votes
    FOR EACH ROW
    EXECUTE FUNCTION portal.update_article_vote_counts();

-- Trigger: Recalculate usefulness_score when votes or views change
CREATE OR REPLACE FUNCTION portal.recalculate_usefulness_score()
RETURNS TRIGGER AS $$
BEGIN
    NEW.usefulness_score = (NEW.upvotes * 2.0 - NEW.downvotes) + (NEW.view_count / 100.0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_recalculate_usefulness
    BEFORE UPDATE OF upvotes, downvotes, view_count ON portal.knowledge_articles
    FOR EACH ROW
    EXECUTE FUNCTION portal.recalculate_usefulness_score();

-- ============================================================================
-- Sample Data (Optional - for testing)
-- ============================================================================

-- Public knowledge article example
INSERT INTO portal.knowledge_articles (
    tenant_id, title, slug, summary, content, category, tags,
    author_id, author_type, published, verification_status
) VALUES (
    NULL,  -- Public article
    'Understanding RTO and RPO in Business Continuity',
    'understanding-rto-rpo-business-continuity',
    'Learn the difference between Recovery Time Objective (RTO) and Recovery Point Objective (RPO) and how to set them effectively.',
    '# Understanding RTO and RPO

**Recovery Time Objective (RTO)** is the maximum acceptable time that a business process can be down after a disaster.

**Recovery Point Objective (RPO)** is the maximum acceptable amount of data loss measured in time.

## Best Practices:
1. Align RTO/RPO with business impact analysis
2. Consider cost vs criticality
3. Document and test regularly',
    'BIA',
    '["RTO", "RPO", "ISO 22301", "BIA"]'::jsonb,
    'admin-001',
    'admin',
    TRUE,
    'verified'
);

-- ============================================================================
-- Rollback Script (run manually if needed)
-- ============================================================================

/*
-- Drop triggers
DROP TRIGGER IF EXISTS trigger_recalculate_usefulness ON portal.knowledge_articles;
DROP TRIGGER IF EXISTS trigger_update_article_votes ON portal.article_votes;
DROP TRIGGER IF EXISTS trigger_votes_updated_at ON portal.article_votes;
DROP TRIGGER IF EXISTS trigger_article_published_at ON portal.knowledge_articles;
DROP TRIGGER IF EXISTS trigger_articles_updated_at ON portal.knowledge_articles;

-- Drop functions
DROP FUNCTION IF EXISTS portal.recalculate_usefulness_score();
DROP FUNCTION IF EXISTS portal.update_article_vote_counts();
DROP FUNCTION IF EXISTS portal.set_article_published_at();
DROP FUNCTION IF EXISTS portal.update_articles_updated_at();

-- Drop tables
DROP TABLE IF EXISTS portal.article_votes CASCADE;
DROP TABLE IF EXISTS portal.article_bookmarks CASCADE;
DROP TABLE IF EXISTS portal.knowledge_articles CASCADE;

-- Drop schema
DROP SCHEMA IF EXISTS portal CASCADE;
*/
