"""
Portal Service - Schemas Package
Pydantic models for request/response validation
"""

from .knowledge import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
    ArticleVoteRequest,
    BookmarkResponse,
    AIGenerateRequest,
    AIGenerateResponse,
    SearchRequest,
    SearchResponse,
)

from .scenarios import (
    ScenarioResponse,
    ScenarioListResponse,
    ScenarioDeployRequest,
    ScenarioDeployResponse,
    ScenarioReviewCreate,
    ScenarioReviewResponse,
)

from .forum import (
    CategoryResponse,
    TopicCreate,
    TopicUpdate,
    TopicResponse,
    TopicListItem,
    TopicListResponse,
    PostCreate,
    PostUpdate,
    PostResponse,
    VoteRequest,
    FlagRequest,
    FlagResponse,
    ResolveFlagRequest,
    ReputationResponse,
    LeaderboardEntry,
    LeaderboardResponse,
    BadgeResponse,
    UserBadgeResponse,
    ReputationEventResponse,
    ForumStatsResponse,
)

__all__ = [
    # Knowledge
    "ArticleCreate",
    "ArticleUpdate",
    "ArticleResponse",
    "ArticleListResponse",
    "ArticleVoteRequest",
    "BookmarkResponse",
    "AIGenerateRequest",
    "AIGenerateResponse",
    "SearchRequest",
    "SearchResponse",
    # Scenarios
    "ScenarioResponse",
    "ScenarioListResponse",
    "ScenarioDeployRequest",
    "ScenarioDeployResponse",
    "ScenarioReviewCreate",
    "ScenarioReviewResponse",
    # Forum
    "CategoryResponse",
    "TopicCreate",
    "TopicUpdate",
    "TopicResponse",
    "TopicListItem",
    "TopicListResponse",
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    "VoteRequest",
    "FlagRequest",
    "FlagResponse",
    "ResolveFlagRequest",
    "ReputationResponse",
    "LeaderboardEntry",
    "LeaderboardResponse",
    "BadgeResponse",
    "UserBadgeResponse",
    "ReputationEventResponse",
    "ForumStatsResponse",
]
