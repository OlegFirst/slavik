"""
Forum API
Endpoints for forum topics, posts, moderation, and gamification
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import ForumTopic, ForumPost, TopicVote, PostVote
from schemas.forum import (
    CategoryResponse, TopicCreate, TopicUpdate, TopicResponse,
    TopicListItem, TopicListResponse, PostCreate, PostUpdate, PostResponse,
    VoteRequest, FlagRequest, FlagResponse, ResolveFlagRequest,
    ReputationResponse, LeaderboardResponse, LeaderboardEntry,
    BadgeResponse, UserBadgeResponse, ForumStatsResponse
)
from services.forum_service import ForumService
from services.moderation_service import ModerationService
from services.reputation_service import ReputationService
from api.dependencies import (
    get_current_user, get_current_user_optional, require_specialist
)

router = APIRouter(prefix="/api/portal/forum", tags=["Forum"])
forum_service = ForumService()
moderation_service = ModerationService()
reputation_service = ReputationService()


# ============================================================================
# Categories
# ============================================================================

@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(
    parent_id: Optional[int] = Query(None, description="Filter by parent category"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get forum categories

    Returns top-level categories by default.
    Use parent_id to get subcategories.
    """
    categories = await forum_service.get_categories(db, parent_id)
    return categories


# ============================================================================
# Topics
# ============================================================================

@router.post("/topics", response_model=TopicResponse, status_code=201)
async def create_topic(
    topic_data: TopicCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new forum topic

    - **category_id**: Forum category
    - **title**: Topic title
    - **content**: Topic content (Markdown)
    - **tags**: Optional tags
    - **linked_article_id**: Optional link to knowledge article (for discussions)
    - **linked_scenario_id**: Optional link to scenario (for discussions)
    """
    topic = await forum_service.create_topic(
        db=db,
        topic_data=topic_data,
        author_id=current_user['user_id'],
        author_type=current_user.get('user_type', 'user'),
        tenant_id=current_user.get('tenant_id')
    )

    # Award reputation points
    await reputation_service.award_points(
        db=db,
        user_id=current_user['user_id'],
        event_type='topic_created',
        topic_id=topic.id
    )

    return topic


@router.get("/topics", response_model=TopicListResponse)
async def get_topics(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    status: str = Query('active', description="Filter by status"),
    linked_article_id: Optional[int] = Query(None, description="Filter by linked article"),
    linked_scenario_id: Optional[int] = Query(None, description="Filter by linked scenario"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of forum topics

    Supports filtering by category, status, and linked content.
    Pinned topics appear first.
    """
    tenant_id = current_user.get('tenant_id') if current_user else None

    topics, total = await forum_service.get_topics(
        db=db,
        category_id=category_id,
        tenant_id=tenant_id,
        status=status,
        linked_article_id=linked_article_id,
        linked_scenario_id=linked_scenario_id,
        page=page,
        page_size=page_size
    )

    total_pages = (total + page_size - 1) // page_size

    return TopicListResponse(
        topics=[TopicListItem.model_validate(t) for t in topics],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get topic details

    Automatically increments view count.
    Returns user-specific data (user_vote) if authenticated.
    """
    topic = await forum_service.get_topic(db, topic_id, increment_views=True)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Check visibility
    tenant_id = current_user.get('tenant_id') if current_user else None
    if topic.tenant_id and topic.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get user vote if authenticated
    response = TopicResponse.model_validate(topic)

    if current_user:
        user_id = current_user['user_id']
        vote_result = await db.execute(
            select(TopicVote).where(
                and_(
                    TopicVote.topic_id == topic_id,
                    TopicVote.user_id == user_id
                )
            )
        )
        vote = vote_result.scalar_one_or_none()
        response.user_vote = vote.vote if vote else None

    return response


@router.patch("/topics/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a topic

    Only topic author or admin can update.
    """
    # Get topic
    topic = await forum_service.get_topic(db, topic_id, increment_views=False)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Check permissions
    user_id = current_user['user_id']
    user_type = current_user.get('user_type')

    if topic.author_id != user_id and user_type != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Only topic author or admin can update"
        )

    # Update
    updated_topic = await forum_service.update_topic(db, topic_id, topic_data)

    return updated_topic


# ============================================================================
# Posts
# ============================================================================

@router.post("/topics/{topic_id}/posts", response_model=PostResponse, status_code=201)
async def create_post(
    topic_id: int,
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a post (reply to topic)

    - **content**: Post content (Markdown)
    - **parent_post_id**: Optional, for nested replies
    """
    # Check if topic exists and is not locked
    topic = await forum_service.get_topic(db, topic_id, increment_views=False)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    if topic.is_locked:
        raise HTTPException(status_code=403, detail="Topic is locked")

    # Create post
    post = await forum_service.create_post(
        db=db,
        topic_id=topic_id,
        post_data=post_data,
        author_id=current_user['user_id'],
        author_type=current_user.get('user_type', 'user')
    )

    # Award reputation points
    await reputation_service.award_points(
        db=db,
        user_id=current_user['user_id'],
        event_type='post_created',
        post_id=post.id,
        topic_id=topic_id
    )

    return post


@router.get("/topics/{topic_id}/posts", response_model=list[PostResponse])
async def get_topic_posts(
    topic_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get posts for a topic

    Returns posts in chronological order.
    """
    posts, total = await forum_service.get_topic_posts(
        db, topic_id, page, page_size
    )

    # Add user votes if authenticated
    responses = []
    for post in posts:
        response = PostResponse.model_validate(post)

        if current_user:
            user_id = current_user['user_id']
            vote_result = await db.execute(
                select(PostVote).where(
                    and_(
                        PostVote.post_id == post.id,
                        PostVote.user_id == user_id
                    )
                )
            )
            vote = vote_result.scalar_one_or_none()
            response.user_vote = vote.vote if vote else None

        responses.append(response)

    return responses


@router.patch("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a post

    Only post author can update.
    """
    # Get post
    result = await db.execute(
        select(ForumPost).where(ForumPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check permissions
    if post.author_id != current_user['user_id']:
        raise HTTPException(
            status_code=403,
            detail="Only post author can update"
        )

    # Update
    updated_post = await forum_service.update_post(db, post_id, post_data.content)

    return updated_post


# ============================================================================
# Voting
# ============================================================================

@router.post("/topics/{topic_id}/vote")
async def vote_topic(
    topic_id: int,
    vote_data: VoteRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vote on a topic

    - **vote**: 1 for upvote, -1 for downvote

    Updates existing vote if already voted.
    """
    user_id = current_user['user_id']

    # Check if topic exists
    topic = await forum_service.get_topic(db, topic_id, increment_views=False)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get topic author for reputation
    topic_author = topic.author_id

    # Vote
    await forum_service.vote_topic(db, topic_id, user_id, vote_data.vote)

    # Award/deduct reputation to topic author
    if vote_data.vote == 1:
        await reputation_service.award_points(
            db=db,
            user_id=topic_author,
            event_type='topic_upvoted',
            topic_id=topic_id
        )
    else:
        await reputation_service.award_points(
            db=db,
            user_id=topic_author,
            event_type='topic_downvoted',
            topic_id=topic_id
        )

    return {"message": "Vote recorded", "vote": vote_data.vote}


@router.post("/posts/{post_id}/vote")
async def vote_post(
    post_id: int,
    vote_data: VoteRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vote on a post

    - **vote**: 1 for upvote, -1 for downvote
    """
    user_id = current_user['user_id']

    # Get post to find author
    result = await db.execute(
        select(ForumPost).where(ForumPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_author = post.author_id

    # Vote
    await forum_service.vote_post(db, post_id, user_id, vote_data.vote)

    # Award/deduct reputation
    if vote_data.vote == 1:
        await reputation_service.award_points(
            db=db,
            user_id=post_author,
            event_type='post_upvoted',
            post_id=post_id
        )
    else:
        await reputation_service.award_points(
            db=db,
            user_id=post_author,
            event_type='post_downvoted',
            post_id=post_id
        )

    return {"message": "Vote recorded", "vote": vote_data.vote}


@router.post("/posts/{post_id}/mark-solution")
async def mark_solution(
    post_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a post as solution

    Only topic author can mark solution.
    """
    # Get post and topic
    result = await db.execute(
        select(ForumPost).where(ForumPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    topic = await forum_service.get_topic(db, post.topic_id, increment_views=False)

    # Check permissions (only topic author can mark solution)
    if topic.author_id != current_user['user_id']:
        raise HTTPException(
            status_code=403,
            detail="Only topic author can mark solution"
        )

    # Mark solution
    await forum_service.mark_solution(db, post.topic_id, post_id)

    # Award reputation to post author
    await reputation_service.award_points(
        db=db,
        user_id=post.author_id,
        event_type='solution_marked',
        post_id=post_id,
        topic_id=post.topic_id
    )

    return {"message": "Post marked as solution"}


# ============================================================================
# Moderation
# ============================================================================

@router.post("/topics/{topic_id}/flag", response_model=FlagResponse)
async def flag_topic(
    topic_id: int,
    flag_data: FlagRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Report a topic for moderation

    - **reason**: spam, inappropriate, offensive, other
    - **description**: Detailed description
    """
    flag = await moderation_service.flag_topic(
        db=db,
        topic_id=topic_id,
        reporter_id=current_user['user_id'],
        reason=flag_data.reason,
        description=flag_data.description
    )

    return flag


@router.post("/posts/{post_id}/flag", response_model=FlagResponse)
async def flag_post(
    post_id: int,
    flag_data: FlagRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Report a post for moderation"""

    flag = await moderation_service.flag_post(
        db=db,
        post_id=post_id,
        reporter_id=current_user['user_id'],
        reason=flag_data.reason,
        description=flag_data.description
    )

    return flag


@router.get("/moderation/queue", response_model=list[FlagResponse])
async def get_moderation_queue(
    status: str = Query('pending', description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db)
):
    """
    Get moderation queue (Specialist/Admin only)

    Returns flags that need review.
    """
    flags = await moderation_service.get_moderation_queue(db, status, limit)
    return flags


@router.post("/moderation/flags/{flag_id}/resolve", response_model=FlagResponse)
async def resolve_flag(
    flag_id: int,
    resolve_data: ResolveFlagRequest,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db)
):
    """
    Resolve a moderation flag (Specialist/Admin only)

    - **action**: approved, rejected, hidden, deleted
    - **notes**: Moderator notes
    """
    flag = await moderation_service.resolve_flag(
        db=db,
        flag_id=flag_id,
        moderator_id=current_user['user_id'],
        action=resolve_data.action,
        notes=resolve_data.notes
    )

    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    return flag


# ============================================================================
# Reputation & Gamification
# ============================================================================

@router.get("/reputation/{user_id}", response_model=ReputationResponse)
async def get_user_reputation(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user's reputation details"""

    reputation = await reputation_service.get_or_create_reputation(db, user_id)
    return reputation


@router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete user profile with Learning competencies and Governance roles

    PHASE 5: Integration feature - fetches data from Learning & Governance services

    Returns:
    - Basic reputation data
    - Learning competencies (from Learning Service)
    - Certifications (from Learning Service)
    - Governance roles (from Governance Service)
    - Is moderator status
    """
    from integrations.learning_client import get_learning_client
    from integrations.governance_client import get_governance_client

    # Get base reputation data
    reputation = await reputation_service.get_or_create_reputation(db, user_id)

    # Get JWT token from current_user
    token = current_user.get('token', '')

    # Fetch Learning Service data
    learning_client = get_learning_client()
    competencies = await learning_client.get_person_competencies(user_id, token)
    certifications = await learning_client.get_person_certifications(user_id, token)

    # Fetch Governance Service data
    governance_client = get_governance_client()
    roles = await governance_client.get_person_roles(user_id, token)

    # Check if user is moderator based on governance roles
    moderator_roles = ['bcm_manager', 'moderator', 'admin']
    is_moderator = any(role.get('role_code') in moderator_roles for role in roles)

    # Update user_reputation with latest data (Phase 4 columns)
    reputation.learning_competencies = {
        comp.get('competency_area', ''): {
            'level': comp.get('proficiency_level'),
            'score': comp.get('score', 0)
        }
        for comp in competencies
    }
    reputation.certifications_count = len(certifications)
    reputation.governance_roles = [
        {
            'role_code': role.get('role_code'),
            'role_name': role.get('role_name'),
            'assigned_date': role.get('assigned_date')
        }
        for role in roles
    ]
    reputation.is_moderator = is_moderator

    if certifications:
        # Find latest certification date
        cert_dates = [cert.get('issued_date') for cert in certifications if cert.get('issued_date')]
        if cert_dates:
            reputation.last_certification_date = max(cert_dates)

    await db.commit()
    await db.refresh(reputation)

    return {
        "user_id": user_id,
        "reputation": {
            "score": reputation.reputation_score,
            "level": reputation.reputation_level.value,
            "topics_created": reputation.topics_created,
            "posts_created": reputation.posts_created,
            "solutions_marked": reputation.solutions_marked,
            "badges_earned": reputation.badges_earned
        },
        "competencies": competencies,
        "certifications": certifications,
        "certifications_count": len(certifications),
        "governance_roles": roles,
        "is_moderator": is_moderator
    }


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    period: str = Query('all_time', description="all_time, monthly, weekly"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reputation leaderboard

    Shows top users by reputation score.
    """
    leaderboard = await reputation_service.get_leaderboard(db, period, limit)

    entries = [
        LeaderboardEntry(
            rank=rank,
            user_id=rep.user_id,
            reputation_score=rep.reputation_score,
            reputation_level=rep.reputation_level.value,
            topics_created=rep.topics_created,
            posts_created=rep.posts_created,
            badges_earned=rep.badges_earned
        )
        for rank, rep in leaderboard
    ]

    return LeaderboardResponse(
        period=period,
        entries=entries,
        total_users=len(entries)
    )


@router.get("/badges", response_model=list[BadgeResponse])
async def get_badges(
    badge_type: Optional[str] = Query(None, description="Filter by type"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all available badges

    - **badge_type**: certification, achievement, special
    """
    badges = await reputation_service.get_all_badges(db, badge_type)
    return badges


@router.get("/users/{user_id}/badges", response_model=list[UserBadgeResponse])
async def get_user_badges(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get badges earned by user"""

    user_badges = await reputation_service.get_user_badges(db, user_id)
    return user_badges


@router.get("/stats", response_model=ForumStatsResponse)
async def get_forum_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get overall forum statistics"""

    stats = await reputation_service.get_forum_stats(db)

    return ForumStatsResponse(
        total_categories=10,  # TODO: query from DB
        total_topics=stats['total_topics'],
        total_posts=stats['total_posts'],
        total_users=stats['total_users'],
        most_active_category=None,  # TODO
        recent_topics_count=stats['recent_topics_count'],
        recent_posts_count=stats['recent_posts_count']
    )
