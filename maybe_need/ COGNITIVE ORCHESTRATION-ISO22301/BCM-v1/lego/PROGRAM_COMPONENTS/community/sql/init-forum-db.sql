-- BCM Community Forum Database Schema
-- Knowledge sharing and discussion platform for BCM professionals

-- Enable UUID and other extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For composite indices

-- User roles enum
CREATE TYPE user_role AS ENUM (
    'member', 'moderator', 'expert', 'admin', 'bcm_coordinator'
);

-- Post status enum
CREATE TYPE post_status AS ENUM (
    'draft', 'published', 'archived', 'deleted', 'moderated'
);

-- Forum category enum
CREATE TYPE forum_category AS ENUM (
    'general', 'bcm_policy', 'risk_management', 'business_impact',
    'continuity_planning', 'incident_response', 'exercises_testing',
    'compliance', 'technology', 'case_studies', 'announcements', 'q_and_a'
);

-- Reaction type enum
CREATE TYPE reaction_type AS ENUM (
    'like', 'helpful', 'insightful', 'agree', 'disagree'
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    company_id VARCHAR(100) NOT NULL,
    role user_role DEFAULT 'member',
    bio TEXT,
    avatar_url VARCHAR(500),
    reputation_score INTEGER DEFAULT 0,
    join_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    certifications JSONB DEFAULT '[]',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category_type forum_category NOT NULL,
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    icon VARCHAR(50),
    color VARCHAR(7), -- Hex color code
    sort_order INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    topic_count INTEGER DEFAULT 0,
    is_private BOOLEAN DEFAULT FALSE,
    allowed_roles user_role[] DEFAULT '{member}',
    moderators UUID[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Topics table
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(250) NOT NULL,
    description TEXT,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status post_status DEFAULT 'published',
    is_pinned BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    is_question BOOLEAN DEFAULT FALSE,
    has_accepted_solution BOOLEAN DEFAULT FALSE,
    tags TEXT[] DEFAULT '{}',
    post_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    reaction_counts JSONB DEFAULT '{}', -- {like: 5, helpful: 3}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_post_at TIMESTAMP WITH TIME ZONE,
    last_post_author_id UUID REFERENCES users(id),
    search_vector TSVECTOR
);

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    content_html TEXT NOT NULL,
    status post_status DEFAULT 'published',
    is_solution BOOLEAN DEFAULT FALSE,
    parent_post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    reply_count INTEGER DEFAULT 0,
    attachments JSONB DEFAULT '[]',
    reaction_counts JSONB DEFAULT '{}',
    mentions UUID[] DEFAULT '{}', -- User IDs mentioned in post
    hashtags TEXT[] DEFAULT '{}',
    edited_at TIMESTAMP WITH TIME ZONE,
    edited_by UUID REFERENCES users(id),
    edit_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    search_vector TSVECTOR
);

-- Reactions table
CREATE TABLE IF NOT EXISTS reactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_id UUID NOT NULL, -- Topic or Post ID
    target_type VARCHAR(10) NOT NULL CHECK (target_type IN ('topic', 'post')),
    reaction_type reaction_type NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, target_id, target_type, reaction_type)
);

-- Subscriptions table (for notifications)
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_id UUID NOT NULL, -- Topic or Category ID
    target_type VARCHAR(10) NOT NULL CHECK (target_type IN ('topic', 'category')),
    notification_types TEXT[] DEFAULT '{new_post,mention}', -- Types of notifications
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, target_id, target_type)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- mention, new_post, reaction, etc.
    title VARCHAR(200) NOT NULL,
    message TEXT,
    data JSONB DEFAULT '{}', -- Additional notification data
    is_read BOOLEAN DEFAULT FALSE,
    related_user_id UUID REFERENCES users(id), -- User who triggered notification
    related_topic_id UUID REFERENCES topics(id),
    related_post_id UUID REFERENCES posts(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User activity log
CREATE TABLE IF NOT EXISTS user_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL, -- login, post_created, reaction_added, etc.
    target_id UUID, -- Related object ID
    target_type VARCHAR(20), -- topic, post, user, etc.
    data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Moderation actions table
CREATE TABLE IF NOT EXISTS moderation_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    moderator_id UUID NOT NULL REFERENCES users(id),
    target_id UUID NOT NULL, -- Post, Topic, or User ID
    target_type VARCHAR(10) NOT NULL CHECK (target_type IN ('post', 'topic', 'user')),
    action VARCHAR(50) NOT NULL, -- delete, edit, lock, ban, warn
    reason TEXT,
    notes TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Forum statistics table
CREATE TABLE IF NOT EXISTS forum_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL UNIQUE,
    total_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0, -- Users active in last 30 days
    total_topics INTEGER DEFAULT 0,
    total_posts INTEGER DEFAULT 0,
    new_topics INTEGER DEFAULT 0,
    new_posts INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    top_category_id UUID REFERENCES categories(id),
    top_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Badges table for user achievements
CREATE TABLE IF NOT EXISTS badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(100),
    color VARCHAR(7),
    criteria JSONB NOT NULL, -- Criteria for earning the badge
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User badges (many-to-many)
CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, badge_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_company_id ON users(company_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_reputation ON users(reputation_score DESC);

CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(category_type);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);

CREATE INDEX IF NOT EXISTS idx_topics_category ON topics(category_id);
CREATE INDEX IF NOT EXISTS idx_topics_author ON topics(author_id);
CREATE INDEX IF NOT EXISTS idx_topics_status ON topics(status);
CREATE INDEX IF NOT EXISTS idx_topics_created_at ON topics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_topics_last_post ON topics(last_post_at DESC);
CREATE INDEX IF NOT EXISTS idx_topics_pinned ON topics(is_pinned DESC, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_topics_tags ON topics USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_topics_search ON topics USING gin(search_vector);

CREATE INDEX IF NOT EXISTS idx_posts_topic ON posts(topic_id);
CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id);
CREATE INDEX IF NOT EXISTS idx_posts_parent ON posts(parent_post_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);
CREATE INDEX IF NOT EXISTS idx_posts_solution ON posts(is_solution);
CREATE INDEX IF NOT EXISTS idx_posts_mentions ON posts USING gin(mentions);
CREATE INDEX IF NOT EXISTS idx_posts_hashtags ON posts USING gin(hashtags);
CREATE INDEX IF NOT EXISTS idx_posts_search ON posts USING gin(search_vector);

CREATE INDEX IF NOT EXISTS idx_reactions_user ON reactions(user_id);
CREATE INDEX IF NOT EXISTS idx_reactions_target ON reactions(target_id, target_type);
CREATE INDEX IF NOT EXISTS idx_reactions_type ON reactions(reaction_type);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_target ON subscriptions(target_id, target_type);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_activities_user ON user_activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_type ON user_activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_created ON user_activities(created_at DESC);

-- Functions and triggers

-- Function to update search vectors
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME = 'topics' THEN
        NEW.search_vector := to_tsvector('english', 
            COALESCE(NEW.title, '') || ' ' || 
            COALESCE(NEW.description, '') || ' ' ||
            array_to_string(NEW.tags, ' ')
        );
    ELSIF TG_TABLE_NAME = 'posts' THEN
        NEW.search_vector := to_tsvector('english', COALESCE(NEW.content, ''));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for search vector updates
CREATE TRIGGER topics_search_vector_update
    BEFORE INSERT OR UPDATE ON topics
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();

CREATE TRIGGER posts_search_vector_update
    BEFORE INSERT OR UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();

-- Function to update topic stats when posts are added/removed
CREATE OR REPLACE FUNCTION update_topic_stats()
RETURNS TRIGGER AS $$
DECLARE
    topic_id_val UUID;
BEGIN
    IF TG_OP = 'INSERT' THEN
        topic_id_val := NEW.topic_id;
        
        -- Update topic post count and last post info
        UPDATE topics SET 
            post_count = post_count + 1,
            last_post_at = NEW.created_at,
            last_post_author_id = NEW.author_id
        WHERE id = topic_id_val;
        
    ELSIF TG_OP = 'DELETE' THEN
        topic_id_val := OLD.topic_id;
        
        -- Update topic post count
        UPDATE topics SET 
            post_count = GREATEST(0, post_count - 1)
        WHERE id = topic_id_val;
        
        -- Update last post info if this was the last post
        UPDATE topics SET
            last_post_at = (
                SELECT created_at FROM posts 
                WHERE topic_id = topic_id_val 
                ORDER BY created_at DESC 
                LIMIT 1
            ),
            last_post_author_id = (
                SELECT author_id FROM posts 
                WHERE topic_id = topic_id_val 
                ORDER BY created_at DESC 
                LIMIT 1
            )
        WHERE id = topic_id_val;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger for topic stats
CREATE TRIGGER update_topic_stats_trigger
    AFTER INSERT OR DELETE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_topic_stats();

-- Function to update category stats
CREATE OR REPLACE FUNCTION update_category_stats()
RETURNS TRIGGER AS $$
DECLARE
    category_id_val UUID;
BEGIN
    IF TG_OP = 'INSERT' THEN
        category_id_val := NEW.category_id;
        UPDATE categories SET 
            topic_count = topic_count + 1,
            post_count = post_count + 1
        WHERE id = category_id_val;
    ELSIF TG_OP = 'DELETE' THEN
        category_id_val := OLD.category_id;
        UPDATE categories SET 
            topic_count = GREATEST(0, topic_count - 1),
            post_count = GREATEST(0, post_count - OLD.post_count)
        WHERE id = category_id_val;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger for category stats
CREATE TRIGGER update_category_stats_trigger
    AFTER INSERT OR DELETE ON topics
    FOR EACH ROW EXECUTE FUNCTION update_category_stats();

-- Function to update reaction counts
CREATE OR REPLACE FUNCTION update_reaction_counts()
RETURNS TRIGGER AS $$
DECLARE
    target_table TEXT;
    reaction_count INTEGER;
BEGIN
    IF TG_TABLE_NAME = 'reactions' THEN
        target_table := CASE 
            WHEN NEW.target_type = 'topic' THEN 'topics'
            WHEN NEW.target_type = 'post' THEN 'posts'
        END;
        
        IF TG_OP = 'INSERT' THEN
            -- Get current count for this reaction type
            EXECUTE format('
                SELECT COALESCE((reaction_counts->>%L)::INTEGER, 0) + 1
                FROM %I WHERE id = %L',
                NEW.reaction_type, target_table, NEW.target_id
            ) INTO reaction_count;
            
            -- Update the count
            EXECUTE format('
                UPDATE %I SET 
                reaction_counts = reaction_counts || jsonb_build_object(%L, %L)
                WHERE id = %L',
                target_table, NEW.reaction_type, reaction_count, NEW.target_id
            );
            
        ELSIF TG_OP = 'DELETE' THEN
            -- Get current count and decrement
            EXECUTE format('
                SELECT GREATEST(0, COALESCE((reaction_counts->>%L)::INTEGER, 0) - 1)
                FROM %I WHERE id = %L',
                OLD.reaction_type, target_table, OLD.target_id
            ) INTO reaction_count;
            
            -- Update the count
            EXECUTE format('
                UPDATE %I SET 
                reaction_counts = reaction_counts || jsonb_build_object(%L, %L)
                WHERE id = %L',
                target_table, OLD.reaction_type, reaction_count, OLD.target_id
            );
        END IF;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger for reaction counts
CREATE TRIGGER update_reaction_counts_trigger
    AFTER INSERT OR DELETE ON reactions
    FOR EACH ROW EXECUTE FUNCTION update_reaction_counts();

-- Function to update user reputation
CREATE OR REPLACE FUNCTION update_user_reputation()
RETURNS TRIGGER AS $$
DECLARE
    reputation_change INTEGER := 0;
BEGIN
    -- Calculate reputation change based on the action
    IF TG_TABLE_NAME = 'posts' AND TG_OP = 'INSERT' THEN
        reputation_change := 2; -- Points for creating a post
    ELSIF TG_TABLE_NAME = 'topics' AND TG_OP = 'INSERT' THEN
        reputation_change := 5; -- Points for creating a topic
    ELSIF TG_TABLE_NAME = 'reactions' AND TG_OP = 'INSERT' THEN
        IF NEW.reaction_type = 'helpful' THEN
            reputation_change := 5; -- Points for helpful reaction
        ELSIF NEW.reaction_type = 'like' THEN
            reputation_change := 1; -- Points for like reaction
        END IF;
        
        -- Update reputation of the content author, not the reactor
        IF NEW.target_type = 'post' THEN
            UPDATE users SET reputation_score = reputation_score + reputation_change
            WHERE id = (SELECT author_id FROM posts WHERE id = NEW.target_id);
        ELSIF NEW.target_type = 'topic' THEN
            UPDATE users SET reputation_score = reputation_score + reputation_change
            WHERE id = (SELECT author_id FROM topics WHERE id = NEW.target_id);
        END IF;
        RETURN NEW;
    END IF;
    
    -- Update author's reputation for posts and topics
    IF reputation_change > 0 THEN
        UPDATE users SET reputation_score = reputation_score + reputation_change
        WHERE id = NEW.author_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for reputation updates
CREATE TRIGGER update_reputation_posts
    AFTER INSERT ON posts
    FOR EACH ROW EXECUTE FUNCTION update_user_reputation();

CREATE TRIGGER update_reputation_topics
    AFTER INSERT ON topics
    FOR EACH ROW EXECUTE FUNCTION update_user_reputation();

CREATE TRIGGER update_reputation_reactions
    AFTER INSERT ON reactions
    FOR EACH ROW EXECUTE FUNCTION update_user_reputation();

-- Insert default categories
INSERT INTO categories (name, slug, description, category_type, icon, color, sort_order) VALUES
('General Discussion', 'general', 'General BCM topics and open discussions', 'general', 'forum', '#2196F3', 1),
('BCM Policy & Governance', 'bcm-policy', 'Business continuity policies, frameworks, and governance', 'bcm_policy', 'policy', '#4CAF50', 2),
('Risk Management', 'risk-management', 'Risk assessment, threat analysis, and mitigation strategies', 'risk_management', 'warning', '#FF9800', 3),
('Business Impact Analysis', 'business-impact', 'BIA methodologies, tools, and case studies', 'business_impact', 'analytics', '#9C27B0', 4),
('Continuity Planning', 'continuity-planning', 'Business continuity and recovery planning discussions', 'continuity_planning', 'plan', '#607D8B', 5),
('Incident Response', 'incident-response', 'Crisis management and incident response strategies', 'incident_response', 'emergency', '#F44336', 6),
('Exercises & Testing', 'exercises-testing', 'BCM exercises, drills, and testing methodologies', 'exercises_testing', 'test', '#795548', 7),
('Compliance & Auditing', 'compliance', 'ISO 22301, regulations, and audit discussions', 'compliance', 'compliance', '#3F51B5', 8),
('Technology & Tools', 'technology', 'BCM software, tools, and technology solutions', 'technology', 'tech', '#009688', 9),
('Case Studies', 'case-studies', 'Real-world BCM implementations and lessons learned', 'case_studies', 'case_study', '#E91E63', 10),
('Announcements', 'announcements', 'Important announcements and updates', 'announcements', 'announcement', '#FF5722', 11),
('Questions & Answers', 'q-and-a', 'Ask questions and get expert answers', 'q_and_a', 'question', '#8BC34A', 12)
ON CONFLICT (slug) DO NOTHING;

-- Insert default badges
INSERT INTO badges (name, description, icon, color, criteria) VALUES
('Welcome', 'Completed profile setup', 'welcome', '#4CAF50', '{"profile_completed": true}'),
('First Post', 'Created your first forum post', 'first_post', '#2196F3', '{"posts_created": 1}'),
('Active Contributor', 'Created 10+ posts', 'contributor', '#FF9800', '{"posts_created": 10}'),
('BCM Expert', 'High reputation score (1000+)', 'expert', '#FFD700', '{"reputation_score": 1000}'),
('Helpful Member', 'Received 25+ helpful reactions', 'helpful', '#9C27B0', '{"helpful_reactions": 25}'),
('Question Master', 'Asked 5+ well-received questions', 'question_master', '#607D8B', '{"questions_asked": 5, "avg_score": 5}'),
('Solution Provider', 'Provided 10+ accepted solutions', 'solution', '#4CAF50', '{"solutions_accepted": 10}'),
('Community Moderator', 'Active community moderation', 'moderator', '#F44336', '{"role": "moderator"}')
ON CONFLICT (name) DO NOTHING;

-- Create views for common queries

-- Popular topics view
CREATE OR REPLACE VIEW popular_topics AS
SELECT 
    t.*,
    u.username as author_username,
    u.reputation_score as author_reputation,
    c.name as category_name,
    c.color as category_color
FROM topics t
JOIN users u ON t.author_id = u.id
JOIN categories c ON t.category_id = c.id
WHERE t.status = 'published'
ORDER BY (t.view_count + t.post_count * 2) DESC;

-- Recent activity view
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    'topic' as type,
    t.id,
    t.title,
    t.author_id,
    u.username,
    t.created_at,
    c.name as category_name
FROM topics t
JOIN users u ON t.author_id = u.id
JOIN categories c ON t.category_id = c.id
WHERE t.status = 'published'

UNION ALL

SELECT 
    'post' as type,
    p.id,
    t.title,
    p.author_id,
    u.username,
    p.created_at,
    c.name as category_name
FROM posts p
JOIN topics t ON p.topic_id = t.id
JOIN users u ON p.author_id = u.id
JOIN categories c ON t.category_id = c.id
WHERE p.status = 'published'

ORDER BY created_at DESC;

-- User statistics view
CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    u.id,
    u.username,
    u.reputation_score,
    COUNT(DISTINCT t.id) as topics_created,
    COUNT(DISTINCT p.id) as posts_created,
    COUNT(DISTINCT CASE WHEN p.is_solution THEN p.id END) as solutions_provided,
    SUM(COALESCE((t.reaction_counts->>'helpful')::INTEGER, 0)) as topic_helpful_reactions,
    SUM(COALESCE((p.reaction_counts->>'helpful')::INTEGER, 0)) as post_helpful_reactions
FROM users u
LEFT JOIN topics t ON u.id = t.author_id AND t.status = 'published'
LEFT JOIN posts p ON u.id = p.author_id AND p.status = 'published'
GROUP BY u.id, u.username, u.reputation_score;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO forum_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO forum_user;
