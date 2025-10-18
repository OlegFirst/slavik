"""
Portal Service - Database Models
Knowledge Hub, Scenario Marketplace, and Forum models
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, Index, JSON, ForeignKey, Enum
)
from sqlalchemy.sql import func
from .connection import Base
import enum


class KnowledgeArticle(Base):
    """
    Knowledge Base Article Model

    Stores articles about BCM best practices, lessons learned, and expert insights.
    Supports AI generation from exercises, expert verification, and community engagement.
    """
    __tablename__ = "knowledge_articles"
    __table_args__ = (
        Index('idx_articles_tenant', 'tenant_id'),
        Index('idx_articles_published', 'published', 'published_at'),
        Index('idx_articles_category', 'category'),
        Index('idx_articles_verification', 'verification_status'),
        Index('idx_articles_usefulness', 'usefulness_score'),
        # Full-text search index (GIN)
        # Will be created in SQL migration
        {'schema': 'portal'}
    )

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), index=True, nullable=True)  # NULL = public article

    # Content
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False)
    summary = Column(String(1000), nullable=False)
    content = Column(Text, nullable=False)  # Markdown content
    content_html = Column(Text)  # Cached HTML rendering

    # Categorization
    category = Column(String(100), nullable=False)  # e.g., "Risk Management", "BIA"
    tags = Column(JSON, default=list)  # ["ISO 22301", "RTO", "Recovery"]
    iso_clause = Column(String(20))  # e.g., "8.4", "4.2"

    # Authorship
    author_id = Column(String(255), nullable=False)
    author_type = Column(String(50), nullable=False)  # "user", "specialist", "admin"

    # Publishing
    published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)

    # AI Generation
    ai_generated = Column(Boolean, default=False)
    ai_confidence_score = Column(Float, nullable=True)  # 0.0 - 1.0
    source_exercise_id = Column(Integer, nullable=True)  # Reference to Validation exercise

    # Expert Verification
    verification_status = Column(
        String(20),
        default='pending'
    )  # pending, verified, rejected
    verified_by = Column(String(255), nullable=True)  # Specialist ID
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)

    # Engagement Metrics
    view_count = Column(Integer, default=0)
    usefulness_score = Column(Float, default=0.0)  # Calculated: (upvotes*2 - downvotes) + view_count/100
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    # ==================== PHASE 4: Learning Service Integration ====================
    related_training_program_id = Column(Integer, nullable=True)  # FK to learning.training_programs.id
    required_competency_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced, expert

    # ==================== PHASE 4: Governance Service Integration ====================
    related_policy_id = Column(Integer, nullable=True)  # FK to governance.policies.id
    related_policy_references = Column(JSON, default=list)  # [{"policy_id": 1, "section": "5.2"}]

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<KnowledgeArticle(id={self.id}, title='{self.title}', published={self.published})>"


class ArticleBookmark(Base):
    """
    User bookmarks for knowledge articles
    Allows users to save articles for later reading
    """
    __tablename__ = "article_bookmarks"
    __table_args__ = (
        Index('idx_bookmarks_user', 'user_id'),
        Index('idx_bookmarks_article', 'article_id'),
        Index('idx_bookmarks_user_article', 'user_id', 'article_id', unique=True),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # References
    user_id = Column(String(255), nullable=False)
    article_id = Column(Integer, ForeignKey('portal.knowledge_articles.id', ondelete='CASCADE'), nullable=False)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ArticleBookmark(user_id='{self.user_id}', article_id={self.article_id})>"


class ArticleVote(Base):
    """
    User votes on knowledge articles
    Supports upvote/downvote system for community curation
    """
    __tablename__ = "article_votes"
    __table_args__ = (
        Index('idx_votes_article', 'article_id'),
        Index('idx_votes_user', 'user_id'),
        Index('idx_votes_user_article', 'user_id', 'article_id', unique=True),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # References
    user_id = Column(String(255), nullable=False)
    article_id = Column(Integer, ForeignKey('portal.knowledge_articles.id', ondelete='CASCADE'), nullable=False)

    # Vote value
    vote = Column(Integer, nullable=False)  # 1 = upvote, -1 = downvote

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        vote_type = "upvote" if self.vote == 1 else "downvote"
        return f"<ArticleVote(user_id='{self.user_id}', article_id={self.article_id}, vote={vote_type})>"


class Scenario(Base):
    """
    BCM Scenario Marketplace Model

    Stores pre-built exercise scenarios that can be deployed as exercises.
    Includes templates, injects, and learning objectives.
    """
    __tablename__ = "scenarios"
    __table_args__ = (
        Index('idx_scenarios_category', 'scenario_type'),
        Index('idx_scenarios_published', 'published'),
        Index('idx_scenarios_rating', 'average_rating'),
        {'schema': 'portal'}
    )

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic Info
    scenario_code = Column(String(50), unique=True, nullable=False)
    scenario_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Type & Category
    scenario_type = Column(String(50), nullable=False)  # "tabletop", "functional", "full_scale"
    industry = Column(String(100))  # "Finance", "Healthcare", "Manufacturing"
    threat_type = Column(String(100))  # "Cyber Attack", "Natural Disaster", "Pandemic"

    # Content
    full_scenario = Column(Text, nullable=False)  # Detailed scenario description
    injects = Column(JSON, nullable=False)  # List of injects/events
    learning_objectives = Column(JSON, nullable=False)  # List of objectives
    duration_minutes = Column(Integer, nullable=False)  # Estimated duration

    # ISO Mapping
    iso_clauses = Column(JSON, default=list)  # ["8.4", "8.5"]

    # ==================== PHASE 4: Governance Service Integration ====================
    related_policies = Column(JSON, default=list)  # [{"policy_id": 1, "test_coverage": "full"}]
    iso_clauses_covered = Column(JSON, default=list)  # ["8.4", "8.5", "7.2"]

    # Publishing
    published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)

    # Authorship
    created_by = Column(String(255), nullable=False)
    author_type = Column(String(50), nullable=False)  # "specialist", "admin"

    # Engagement
    view_count = Column(Integer, default=0)
    deployment_count = Column(Integer, default=0)  # How many times deployed
    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Scenario(code='{self.scenario_code}', name='{self.scenario_name}')>"


class ScenarioReview(Base):
    """
    User reviews and ratings for scenarios
    Helps community evaluate scenario quality
    """
    __tablename__ = "scenario_reviews"
    __table_args__ = (
        Index('idx_reviews_scenario', 'scenario_id'),
        Index('idx_reviews_user', 'user_id'),
        Index('idx_reviews_rating', 'rating'),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # References
    scenario_id = Column(Integer, ForeignKey('portal.scenarios.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), nullable=False)
    tenant_id = Column(String(255), nullable=False)  # To verify actual usage

    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text)

    # Usage context
    exercise_id = Column(Integer, nullable=True)  # Reference to exercise where scenario was used

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ScenarioReview(scenario_id={self.scenario_id}, rating={self.rating})>"


# ============================================================================
# FORUM MODELS
# ============================================================================

class TopicStatus(str, enum.Enum):
    """Forum topic status enum"""
    active = "active"
    closed = "closed"
    archived = "archived"
    deleted = "deleted"


class ModerationAction(str, enum.Enum):
    """Moderation action types"""
    approved = "approved"
    rejected = "rejected"
    hidden = "hidden"
    deleted = "deleted"


class ReputationLevel(str, enum.Enum):
    """User reputation levels"""
    newbie = "newbie"          # 0-99
    contributor = "contributor"  # 100-499
    expert = "expert"          # 500-999
    guru = "guru"              # 1000-2499
    legend = "legend"          # 2500+


class ForumCategory(Base):
    """
    Forum categories for organizing discussions
    Maps to ISO 22301 clauses and BCM topics
    """
    __tablename__ = "forum_categories"
    __table_args__ = (
        Index('idx_forum_categories_parent', 'parent_id'),
        Index('idx_forum_categories_order', 'display_order'),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Category info
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(50))  # Icon name/emoji

    # Hierarchy
    parent_id = Column(Integer, ForeignKey('portal.forum_categories.id'), nullable=True)
    display_order = Column(Integer, default=0)

    # ISO Mapping
    iso_clause = Column(String(20))  # e.g., "8.4"

    # Stats (denormalized)
    topic_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ForumCategory(id={self.id}, name='{self.name}')>"


class ForumTopic(Base):
    """
    Forum discussion topics
    Can be linked to articles or scenarios for discussions
    """
    __tablename__ = "forum_topics"
    __table_args__ = (
        Index('idx_forum_topics_category', 'category_id'),
        Index('idx_forum_topics_tenant', 'tenant_id'),
        Index('idx_forum_topics_status', 'status'),
        Index('idx_forum_topics_activity', 'last_post_at'),
        Index('idx_forum_topics_votes', 'vote_score'),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Organization
    category_id = Column(Integer, ForeignKey('portal.forum_categories.id'), nullable=False)
    tenant_id = Column(String(255), nullable=True)  # NULL = public discussion

    # Content
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)  # Markdown
    content_html = Column(Text)  # Cached HTML

    # Author
    author_id = Column(String(255), nullable=False)
    author_type = Column(String(50), nullable=False)  # user, specialist, admin

    # Status
    status = Column(Enum(TopicStatus), default=TopicStatus.active, nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_solved = Column(Boolean, default=False)  # For Q&A topics
    solution_post_id = Column(Integer, nullable=True)

    # Linking to content
    linked_article_id = Column(Integer, ForeignKey('portal.knowledge_articles.id'), nullable=True)
    linked_scenario_id = Column(Integer, ForeignKey('portal.scenarios.id'), nullable=True)

    # Engagement
    view_count = Column(Integer, default=0)
    post_count = Column(Integer, default=0)  # Reply count
    vote_score = Column(Integer, default=0)  # upvotes - downvotes

    # Tags
    tags = Column(JSON, default=list)

    # Activity tracking
    last_post_at = Column(DateTime, default=func.now(), nullable=False)
    last_post_by = Column(String(255))

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ForumTopic(id={self.id}, title='{self.title}')>"


class ForumPost(Base):
    """
    Forum posts (replies to topics)
    """
    __tablename__ = "forum_posts"
    __table_args__ = (
        Index('idx_forum_posts_topic', 'topic_id'),
        Index('idx_forum_posts_author', 'author_id'),
        Index('idx_forum_posts_parent', 'parent_post_id'),
        Index('idx_forum_posts_votes', 'vote_score'),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # References
    topic_id = Column(Integer, ForeignKey('portal.forum_topics.id', ondelete='CASCADE'), nullable=False)
    parent_post_id = Column(Integer, ForeignKey('portal.forum_posts.id'), nullable=True)  # For nested replies

    # Content
    content = Column(Text, nullable=False)  # Markdown
    content_html = Column(Text)  # Cached HTML

    # Author
    author_id = Column(String(255), nullable=False)
    author_type = Column(String(50), nullable=False)

    # Status
    is_deleted = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)  # Hidden by moderator

    # Engagement
    vote_score = Column(Integer, default=0)
    is_solution = Column(Boolean, default=False)  # Marked as solution by topic author

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    edited_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<ForumPost(id={self.id}, topic_id={self.topic_id})>"


class TopicVote(Base):
    """
    Voting on forum topics
    """
    __tablename__ = "topic_votes"
    __table_args__ = (
        Index('idx_topic_votes_topic', 'topic_id'),
        Index('idx_topic_votes_user', 'user_id'),
        Index('idx_topic_votes_user_topic', 'user_id', 'topic_id', unique=True),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    topic_id = Column(Integer, ForeignKey('portal.forum_topics.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), nullable=False)

    vote = Column(Integer, nullable=False)  # 1 = upvote, -1 = downvote

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        vote_type = "upvote" if self.vote == 1 else "downvote"
        return f"<TopicVote(topic_id={self.topic_id}, user_id='{self.user_id}', vote={vote_type})>"


class PostVote(Base):
    """
    Voting on forum posts
    """
    __tablename__ = "post_votes"
    __table_args__ = (
        Index('idx_post_votes_post', 'post_id'),
        Index('idx_post_votes_user', 'user_id'),
        Index('idx_post_votes_user_post', 'user_id', 'post_id', unique=True),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    post_id = Column(Integer, ForeignKey('portal.forum_posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(255), nullable=False)

    vote = Column(Integer, nullable=False)  # 1 = upvote, -1 = downvote

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        vote_type = "upvote" if self.vote == 1 else "downvote"
        return f"<PostVote(post_id={self.post_id}, user_id='{self.user_id}', vote={vote_type})>"


class ModerationFlag(Base):
    """
    User reports for moderation
    """
    __tablename__ = "moderation_flags"
    __table_args__ = (
        Index('idx_moderation_flags_status', 'status'),
        Index('idx_moderation_flags_topic', 'topic_id'),
        Index('idx_moderation_flags_post', 'post_id'),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    # What's being flagged
    topic_id = Column(Integer, ForeignKey('portal.forum_topics.id', ondelete='CASCADE'), nullable=True)
    post_id = Column(Integer, ForeignKey('portal.forum_posts.id', ondelete='CASCADE'), nullable=True)

    # Reporter
    reporter_id = Column(String(255), nullable=False)
    reason = Column(String(50), nullable=False)  # spam, inappropriate, offensive, other
    description = Column(Text)

    # Moderation
    status = Column(String(20), default='pending')  # pending, reviewed, resolved
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    action_taken = Column(Enum(ModerationAction), nullable=True)
    moderator_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ModerationFlag(id={self.id}, reason='{self.reason}', status='{self.status}')>"


class UserReputation(Base):
    """
    User reputation and gamification stats
    """
    __tablename__ = "user_reputation"
    __table_args__ = (
        Index('idx_user_reputation_user', 'user_id', unique=True),
        Index('idx_user_reputation_score', 'reputation_score'),
        Index('idx_user_reputation_level', 'reputation_level'),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(String(255), unique=True, nullable=False)

    # Reputation
    reputation_score = Column(Integer, default=0)
    reputation_level = Column(Enum(ReputationLevel), default=ReputationLevel.newbie, nullable=False)

    # Activity stats
    topics_created = Column(Integer, default=0)
    posts_created = Column(Integer, default=0)
    solutions_marked = Column(Integer, default=0)
    upvotes_received = Column(Integer, default=0)
    downvotes_received = Column(Integer, default=0)
    badges_earned = Column(Integer, default=0)

    # ==================== PHASE 4: Learning Service Integration ====================
    learning_competencies = Column(JSON, default=dict)  # {"bc_planning": {"level": "advanced", "score": 85}}
    certifications_count = Column(Integer, default=0)
    last_certification_date = Column(DateTime, nullable=True)

    # ==================== PHASE 4: Governance Service Integration ====================
    governance_roles = Column(JSON, default=list)  # [{"role_code": "bcm_manager", "assigned_date": "2025-01-01"}]
    is_moderator = Column(Boolean, default=False)
    moderator_since = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<UserReputation(user_id='{self.user_id}', score={self.reputation_score}, level='{self.reputation_level}')>"


class Badge(Base):
    """
    Achievement badges
    """
    __tablename__ = "badges"
    __table_args__ = (
        Index('idx_badges_code', 'badge_code', unique=True),
        Index('idx_badges_type', 'badge_type'),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    badge_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    badge_type = Column(String(50), nullable=False)  # certification, achievement, special
    tier = Column(String(20))  # bronze, silver, gold

    # Criteria
    criteria = Column(JSON)  # Conditions to earn badge
    points_value = Column(Integer, default=10)  # Reputation points awarded

    # Visual
    icon_url = Column(String(500))
    color = Column(String(20))

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Badge(code='{self.badge_code}', name='{self.name}')>"


class UserBadge(Base):
    """
    Badges earned by users
    """
    __tablename__ = "user_badges"
    __table_args__ = (
        Index('idx_user_badges_user', 'user_id'),
        Index('idx_user_badges_badge', 'badge_id'),
        Index('idx_user_badges_user_badge', 'user_id', 'badge_id', unique=True),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(String(255), nullable=False)
    badge_id = Column(Integer, ForeignKey('portal.badges.id', ondelete='CASCADE'), nullable=False)

    # Context
    earned_for = Column(String(500))  # Description of why/how earned

    # Metadata
    earned_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<UserBadge(user_id='{self.user_id}', badge_id={self.badge_id})>"


class ReputationEvent(Base):
    """
    Audit log of reputation changes
    """
    __tablename__ = "reputation_events"
    __table_args__ = (
        Index('idx_reputation_events_user', 'user_id'),
        Index('idx_reputation_events_type', 'event_type'),
        {'schema': 'portal'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(String(255), nullable=False)

    # Event details
    event_type = Column(String(50), nullable=False)  # topic_created, post_upvoted, solution_marked, etc.
    points_change = Column(Integer, nullable=False)  # Can be positive or negative

    # Context
    topic_id = Column(Integer, ForeignKey('portal.forum_topics.id', ondelete='SET NULL'), nullable=True)
    post_id = Column(Integer, ForeignKey('portal.forum_posts.id', ondelete='SET NULL'), nullable=True)
    badge_id = Column(Integer, ForeignKey('portal.badges.id', ondelete='SET NULL'), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ReputationEvent(user_id='{self.user_id}', type='{self.event_type}', points={self.points_change})>"


# ============================================================================
# PHASE 4: Junction Tables for Learning & Governance Integration
# ============================================================================

class ArticleCompetency(Base):
    """
    Links knowledge articles to competency areas from Learning Service

    Many-to-many: Articles <-> Competencies
    """
    __tablename__ = "article_competencies"
    __table_args__ = (
        Index('idx_article_comp_article', 'article_id'),
        Index('idx_article_comp_area', 'competency_area'),
        Index('idx_article_comp_level', 'required_level'),
        {'schema': 'portal'}
    )

    # Composite primary key
    article_id = Column(Integer, ForeignKey('portal.knowledge_articles.id', ondelete='CASCADE'), primary_key=True)
    competency_area = Column(String(100), primary_key=True)  # e.g., "bc_planning", "risk_assessment"

    # Relationship metadata
    relevance = Column(String(20), default='medium')  # low, medium, high, critical
    required_level = Column(String(20), nullable=True)  # beginner, intermediate, advanced, expert
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    created_by = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<ArticleCompetency(article_id={self.article_id}, area='{self.competency_area}', level='{self.required_level}')>"


class ScenarioPolicy(Base):
    """
    Links BCM scenarios to governance policies they test

    Many-to-many: Scenarios <-> Policies
    """
    __tablename__ = "scenario_policies"
    __table_args__ = (
        Index('idx_scenario_policy_scenario', 'scenario_id'),
        Index('idx_scenario_policy_policy', 'policy_id'),
        Index('idx_scenario_policy_coverage', 'test_coverage'),
        {'schema': 'portal'}
    )

    # Composite primary key
    scenario_id = Column(Integer, ForeignKey('portal.scenarios.id', ondelete='CASCADE'), primary_key=True)
    policy_id = Column(Integer, primary_key=True)  # Reference to governance.policies.id (different DB)

    # Testing metadata
    test_coverage = Column(String(20), default='partial')  # none, partial, full
    iso_clauses_tested = Column(JSON, default=list)  # ["8.4", "8.5"]
    last_tested_date = Column(DateTime, nullable=True)
    test_results = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ScenarioPolicy(scenario_id={self.scenario_id}, policy_id={self.policy_id}, coverage='{self.test_coverage}')>"
