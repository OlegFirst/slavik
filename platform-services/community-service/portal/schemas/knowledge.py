"""
Knowledge Hub - Pydantic Schemas
Request/Response models for knowledge articles
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Article Schemas
# ============================================================================

class ArticleCreate(BaseModel):
    """Request schema for creating a knowledge article"""

    title: str = Field(..., max_length=500, description="Article title")
    summary: str = Field(..., max_length=1000, description="Short summary")
    content: str = Field(..., description="Article content in Markdown")
    category: str = Field(..., max_length=100, description="Article category")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    iso_clause: Optional[str] = Field(None, max_length=20, description="ISO 22301 clause reference")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError("Maximum 10 tags allowed")
        return v


class ArticleUpdate(BaseModel):
    """Request schema for updating an article"""

    title: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = Field(None, max_length=1000)
    content: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    iso_clause: Optional[str] = Field(None, max_length=20)
    published: Optional[bool] = None


class ArticleResponse(BaseModel):
    """Response schema for knowledge article"""

    id: int
    tenant_id: Optional[str]
    title: str
    slug: str
    summary: str
    content: str  # Markdown
    content_html: Optional[str]  # Rendered HTML
    category: str
    tags: List[str]
    iso_clause: Optional[str]

    # Authorship
    author_id: str
    author_type: str

    # Publishing
    published: bool
    published_at: Optional[datetime]

    # AI Generation
    ai_generated: bool
    ai_confidence_score: Optional[float]
    source_exercise_id: Optional[int]

    # Verification
    verification_status: str
    verified_by: Optional[str]
    verified_at: Optional[datetime]

    # Engagement
    view_count: int
    usefulness_score: float
    upvotes: int
    downvotes: int

    # Metadata
    created_at: datetime
    updated_at: datetime

    # User-specific fields (added dynamically)
    is_bookmarked: Optional[bool] = None
    user_vote: Optional[int] = None  # 1, -1, or None

    class Config:
        from_attributes = True


class ArticleListItem(BaseModel):
    """Simplified article for list views"""

    id: int
    title: str
    slug: str
    summary: str
    category: str
    tags: List[str]
    author_id: str
    author_type: str
    published: bool
    published_at: Optional[datetime]
    verification_status: str
    view_count: int
    usefulness_score: float
    upvotes: int
    ai_generated: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Paginated list of articles"""

    articles: List[ArticleListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Voting Schemas
# ============================================================================

class ArticleVoteRequest(BaseModel):
    """Request schema for voting on an article"""

    vote: int = Field(..., description="Vote value: 1 for upvote, -1 for downvote")

    @field_validator('vote')
    @classmethod
    def validate_vote(cls, v):
        if v not in [1, -1]:
            raise ValueError("Vote must be 1 (upvote) or -1 (downvote)")
        return v


# ============================================================================
# Bookmark Schemas
# ============================================================================

class BookmarkResponse(BaseModel):
    """Response schema for bookmark"""

    id: int
    user_id: str
    article_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# AI Generation Schemas
# ============================================================================

class AIGenerateRequest(BaseModel):
    """Request schema for AI article generation"""

    exercise_id: int = Field(..., description="Source exercise ID from Validation module")
    category: Optional[str] = Field(None, description="Override category (auto-detected if not provided)")
    tags: Optional[List[str]] = Field(None, description="Override tags (auto-detected if not provided)")


class AIGenerateResponse(BaseModel):
    """Response schema for AI generation"""

    article_id: int
    title: str
    slug: str
    confidence_score: float
    verification_status: str = "pending"
    message: str = "Article generated successfully and pending expert verification"


# ============================================================================
# Search Schemas
# ============================================================================

class SearchRequest(BaseModel):
    """Request schema for searching articles"""

    query: str = Field(..., min_length=2, description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    verified_only: bool = Field(False, description="Only show verified articles")
    published_only: bool = Field(True, description="Only show published articles")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Results per page")


class SearchResultItem(BaseModel):
    """Single search result item"""

    id: int
    title: str
    slug: str
    summary: str
    category: str
    tags: List[str]
    relevance_score: float
    verification_status: str
    usefulness_score: float
    upvotes: int
    created_at: datetime

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """Response schema for search"""

    results: List[SearchResultItem]
    total: int
    query: str
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Verification Schemas
# ============================================================================

class VerifyArticleRequest(BaseModel):
    """Request schema for verifying an article"""

    status: str = Field(..., description="Verification status: verified or rejected")
    notes: Optional[str] = Field(None, description="Verification notes")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['verified', 'rejected']:
            raise ValueError("Status must be 'verified' or 'rejected'")
        return v


class VerifyArticleResponse(BaseModel):
    """Response schema for verification"""

    article_id: int
    verification_status: str
    verified_by: str
    verified_at: datetime
    message: str
