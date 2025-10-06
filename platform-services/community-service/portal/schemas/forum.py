"""
Forum - Pydantic Schemas
Request/Response models for forum topics, posts, moderation, and gamification
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Category Schemas
# ============================================================================

class CategoryResponse(BaseModel):
    """Forum category response"""
    id: int
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    parent_id: Optional[int]
    display_order: int
    iso_clause: Optional[str]
    topic_count: int
    post_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Topic Schemas
# ============================================================================

class TopicCreate(BaseModel):
    """Create a new topic"""
    category_id: int = Field(..., description="Forum category ID")
    title: str = Field(..., max_length=500, description="Topic title")
    content: str = Field(..., description="Topic content in Markdown")
    tags: List[str] = Field(default_factory=list, description="Topic tags")
    linked_article_id: Optional[int] = Field(None, description="Link to knowledge article")
    linked_scenario_id: Optional[int] = Field(None, description="Link to scenario")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return v


class TopicUpdate(BaseModel):
    """Update a topic"""
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None
    status: Optional[str] = None  # active, closed, archived


class TopicResponse(BaseModel):
    """Forum topic response"""
    id: int
    category_id: int
    tenant_id: Optional[str]
    title: str
    content: str
    content_html: Optional[str]
    author_id: str
    author_type: str
    status: str
    is_pinned: bool
    is_locked: bool
    is_solved: bool
    solution_post_id: Optional[int]
    linked_article_id: Optional[int]
    linked_scenario_id: Optional[int]
    view_count: int
    post_count: int
    vote_score: int
    tags: List[str]
    last_post_at: datetime
    last_post_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    # User-specific (added dynamically)
    user_vote: Optional[int] = None

    class Config:
        from_attributes = True


class TopicListItem(BaseModel):
    """Simplified topic for list views"""
    id: int
    category_id: int
    title: str
    author_id: str
    author_type: str
    status: str
    is_pinned: bool
    is_solved: bool
    view_count: int
    post_count: int
    vote_score: int
    tags: List[str]
    last_post_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TopicListResponse(BaseModel):
    """Paginated list of topics"""
    topics: List[TopicListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Post Schemas
# ============================================================================

class PostCreate(BaseModel):
    """Create a forum post"""
    content: str = Field(..., description="Post content in Markdown")
    parent_post_id: Optional[int] = Field(None, description="Reply to specific post")


class PostUpdate(BaseModel):
    """Update a forum post"""
    content: str = Field(..., description="Updated content")


class PostResponse(BaseModel):
    """Forum post response"""
    id: int
    topic_id: int
    parent_post_id: Optional[int]
    content: str
    content_html: Optional[str]
    author_id: str
    author_type: str
    is_deleted: bool
    is_hidden: bool
    vote_score: int
    is_solution: bool
    created_at: datetime
    updated_at: datetime
    edited_at: Optional[datetime]

    # User-specific
    user_vote: Optional[int] = None

    class Config:
        from_attributes = True


# ============================================================================
# Voting Schemas
# ============================================================================

class VoteRequest(BaseModel):
    """Vote on topic or post"""
    vote: int = Field(..., description="1 for upvote, -1 for downvote")

    @field_validator('vote')
    @classmethod
    def validate_vote(cls, v):
        if v not in [1, -1]:
            raise ValueError("Vote must be 1 (upvote) or -1 (downvote)")
        return v


# ============================================================================
# Moderation Schemas
# ============================================================================

class FlagRequest(BaseModel):
    """Report topic or post for moderation"""
    reason: str = Field(..., description="spam, inappropriate, offensive, other")
    description: Optional[str] = Field(None, description="Detailed description")

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        valid_reasons = ['spam', 'inappropriate', 'offensive', 'other']
        if v not in valid_reasons:
            raise ValueError(f"Reason must be one of: {', '.join(valid_reasons)}")
        return v


class FlagResponse(BaseModel):
    """Moderation flag response"""
    id: int
    topic_id: Optional[int]
    post_id: Optional[int]
    reporter_id: str
    reason: str
    description: Optional[str]
    status: str
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    action_taken: Optional[str]
    moderator_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ResolveFlagRequest(BaseModel):
    """Resolve a moderation flag"""
    action: str = Field(..., description="approved, rejected, hidden, deleted")
    notes: Optional[str] = Field(None, description="Moderator notes")

    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        valid_actions = ['approved', 'rejected', 'hidden', 'deleted']
        if v not in valid_actions:
            raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")
        return v


# ============================================================================
# Reputation & Gamification Schemas
# ============================================================================

class ReputationResponse(BaseModel):
    """User reputation details"""
    user_id: str
    reputation_score: int
    reputation_level: str  # newbie, contributor, expert, guru, legend
    topics_created: int
    posts_created: int
    solutions_marked: int
    upvotes_received: int
    downvotes_received: int
    badges_earned: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: str
    reputation_score: int
    reputation_level: str
    topics_created: int
    posts_created: int
    badges_earned: int


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    period: str  # all_time, monthly, weekly
    entries: List[LeaderboardEntry]
    total_users: int


class BadgeResponse(BaseModel):
    """Badge details"""
    id: int
    badge_code: str
    name: str
    description: Optional[str]
    badge_type: str  # certification, achievement, special
    tier: Optional[str]  # bronze, silver, gold
    criteria: Optional[dict]
    points_value: int
    icon_url: Optional[str]
    color: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserBadgeResponse(BaseModel):
    """User badge with details"""
    id: int
    user_id: str
    badge: BadgeResponse
    earned_for: Optional[str]
    earned_at: datetime

    class Config:
        from_attributes = True


class ReputationEventResponse(BaseModel):
    """Reputation change event"""
    id: int
    user_id: str
    event_type: str
    points_change: int
    topic_id: Optional[int]
    post_id: Optional[int]
    badge_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Statistics Schemas
# ============================================================================

class ForumStatsResponse(BaseModel):
    """Overall forum statistics"""
    total_categories: int
    total_topics: int
    total_posts: int
    total_users: int
    most_active_category: Optional[str]
    recent_topics_count: int  # Last 24h
    recent_posts_count: int  # Last 24h
