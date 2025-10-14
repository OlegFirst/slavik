"""
📚 Living Documentation Database Models

Tables:
- documentation_pages - Content storage
- page_versions - Version history with A/B testing
- user_interactions - Tracking for learning
- knowledge_gaps - Auto-detected missing topics
- improvement_queue - Pages flagged for AI improvement
- user_profiles - Personalization data
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class DocumentationPage(Base):
    """
    Documentation page with versioning

    Each page can have multiple versions (A/B testing)
    """
    __tablename__ = "living_documentation_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(String(200), unique=True, nullable=False, index=True)

    # Current version
    current_version_id = Column(UUID(as_uuid=True), ForeignKey('living_documentation_versions.id'))

    # Metadata
    title = Column(String(500), nullable=False)
    topic = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    tags = Column(ARRAY(String), default=[])

    # Quality metrics
    avg_quality_score = Column(Float, default=0.0)
    total_views = Column(Integer, default=0)
    helpful_votes = Column(Integer, default=0)
    not_helpful_votes = Column(Integer, default=0)
    avg_time_on_page = Column(Float, default=0.0)

    # Status
    status = Column(String(50), default='active')  # active, needs_improvement, deprecated
    auto_generated = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_improved_at = Column(DateTime, nullable=True)

    # Relationships
    versions = relationship("PageVersion", back_populates="page", foreign_keys="PageVersion.page_id")
    interactions = relationship("UserInteraction", back_populates="page")

    __table_args__ = (
        Index('idx_page_topic_category', 'topic', 'category'),
        Index('idx_page_quality', 'avg_quality_score'),
    )


class PageVersion(Base):
    """
    Version of documentation page (for A/B testing)

    System creates new versions when improving content
    Runs A/B test to determine winner
    """
    __tablename__ = "living_documentation_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey('living_documentation_pages.id'), nullable=False)

    # Version info
    version_number = Column(Integer, nullable=False)
    version_type = Column(String(50), default='manual')  # manual, ai_improved, ab_test

    # Content
    content_markdown = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)

    # Structured content
    sections = Column(JSON, default=[])  # [{title, content, type}]
    examples = Column(JSON, default=[])  # [{title, content, code}]
    interactive_elements = Column(JSON, default=[])  # [{type, config}]

    # Personalization templates
    industry_variants = Column(JSON, default={})  # {healthcare: content, finance: content}
    level_variants = Column(JSON, default={})  # {beginner: content, expert: content}

    # A/B Testing
    is_active = Column(Boolean, default=False)
    ab_test_group = Column(String(50), nullable=True)  # A, B, C, etc.
    views_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)

    # Quality
    quality_score = Column(Float, nullable=True)
    ai_generated_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)

    # Metadata
    created_by = Column(String(100), default='system')
    improvement_reason = Column(Text, nullable=True)
    ai_prompt_used = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    deployed_at = Column(DateTime, nullable=True)
    deprecated_at = Column(DateTime, nullable=True)

    # Relationships
    page = relationship("DocumentationPage", back_populates="versions", foreign_keys=[page_id])

    __table_args__ = (
        Index('idx_version_page_active', 'page_id', 'is_active'),
    )


class UserInteraction(Base):
    """
    User interaction tracking for learning

    Every view, click, vote teaches the system
    """
    __tablename__ = "living_documentation_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    page_id = Column(UUID(as_uuid=True), ForeignKey('living_documentation_pages.id'), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey('living_documentation_versions.id'), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Interaction details
    event_type = Column(String(50), nullable=False)  # view, vote, search, question, exit

    # Engagement metrics
    time_on_page = Column(Float, default=0.0)  # seconds
    scroll_depth = Column(Float, default=0.0)  # 0-1
    clicked_examples = Column(ARRAY(String), default=[])
    clicked_tools = Column(ARRAY(String), default=[])

    # Feedback
    helpful_vote = Column(Boolean, nullable=True)
    feedback_text = Column(Text, nullable=True)
    question_asked = Column(Text, nullable=True)

    # Context
    user_industry = Column(String(100), nullable=True)
    user_level = Column(String(50), nullable=True)
    referrer_page = Column(String(200), nullable=True)
    search_query = Column(String(500), nullable=True)

    # Metadata
    session_id = Column(String(200), nullable=True)
    device_type = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    page = relationship("DocumentationPage", back_populates="interactions")

    __table_args__ = (
        Index('idx_interaction_user_created', 'user_id', 'created_at'),
        Index('idx_interaction_event_type', 'event_type'),
    )


class KnowledgeGap(Base):
    """
    Auto-detected knowledge gaps

    System detects missing topics from:
    - Searches with no results
    - Frequently asked questions
    - User confusion patterns
    """
    __tablename__ = "living_documentation_gaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Gap details
    topic = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False)

    # Evidence
    search_queries = Column(ARRAY(String), default=[])
    user_questions = Column(ARRAY(String), default=[])
    affected_user_count = Column(Integer, default=0)

    # Priority
    priority_score = Column(Float, default=0.0)  # 0-10
    urgency = Column(String(50), default='medium')  # low, medium, high, critical

    # Auto-generation
    auto_generation_scheduled = Column(Boolean, default=False)
    auto_generation_started_at = Column(DateTime, nullable=True)
    auto_generation_completed_at = Column(DateTime, nullable=True)
    generated_page_id = Column(UUID(as_uuid=True), nullable=True)

    # Status
    status = Column(String(50), default='detected')  # detected, scheduled, in_progress, completed

    # Timestamps
    first_detected_at = Column(DateTime, default=datetime.utcnow)
    last_search_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_gap_priority', 'priority_score'),
        Index('idx_gap_status', 'status'),
    )


class ImprovementQueue(Base):
    """
    Pages flagged for improvement

    AI automatically improves low-quality content
    """
    __tablename__ = "living_documentation_improvements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Target page
    page_id = Column(UUID(as_uuid=True), ForeignKey('living_documentation_pages.id'), nullable=False, index=True)

    # Issues detected
    issues = Column(ARRAY(String), default=[])  # too_short, no_examples, unclear, outdated

    # Analytics that triggered improvement
    avg_time_on_page = Column(Float, nullable=True)
    helpful_rate = Column(Float, nullable=True)
    bounce_rate = Column(Float, nullable=True)
    negative_feedback_count = Column(Integer, default=0)

    # Priority
    priority = Column(Integer, default=5)  # 1-10
    urgency = Column(String(50), default='medium')

    # AI improvement
    ai_improvement_status = Column(String(50), default='pending')  # pending, in_progress, completed, failed
    ai_started_at = Column(DateTime, nullable=True)
    ai_completed_at = Column(DateTime, nullable=True)
    new_version_id = Column(UUID(as_uuid=True), nullable=True)

    # A/B test results
    ab_test_started_at = Column(DateTime, nullable=True)
    ab_test_completed_at = Column(DateTime, nullable=True)
    ab_test_winner = Column(String(10), nullable=True)  # A (old), B (new)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_improvement_priority', 'priority'),
        Index('idx_improvement_status', 'ai_improvement_status'),
    )


class UserProfile(Base):
    """
    User profile for personalization

    Built from interactions over time
    """
    __tablename__ = "living_documentation_user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)

    # Context
    industry = Column(String(100), nullable=True)
    org_size = Column(String(50), nullable=True)
    org_type = Column(String(100), nullable=True)

    # Experience level
    experience_level = Column(String(50), default='beginner')  # beginner, intermediate, advanced, expert
    confidence_score = Column(Float, default=0.0)  # 0-1

    # Learning journey
    current_goal = Column(String(200), nullable=True)
    completed_journeys = Column(ARRAY(String), default=[])

    # Interests
    favorite_topics = Column(ARRAY(String), default=[])
    search_history = Column(ARRAY(String), default=[])

    # Engagement
    total_pages_viewed = Column(Integer, default=0)
    total_time_spent = Column(Float, default=0.0)  # minutes
    last_active_at = Column(DateTime, nullable=True)

    # Preferences
    preferred_format = Column(String(50), default='detailed')  # quick, detailed, visual, step_by_step
    preferred_examples = Column(String(100), default='industry_specific')

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_profile_industry_level', 'industry', 'experience_level'),
    )


class SearchQuery(Base):
    """
    Search queries for learning and gap detection
    """
    __tablename__ = "living_documentation_searches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    query = Column(String(500), nullable=False, index=True)

    # Results
    results_count = Column(Integer, default=0)
    clicked_result = Column(String(200), nullable=True)
    satisfied = Column(Boolean, nullable=True)

    # Context
    user_industry = Column(String(100), nullable=True)
    user_level = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_search_query_created', 'query', 'created_at'),
    )
