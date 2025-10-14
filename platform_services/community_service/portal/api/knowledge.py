"""
Knowledge Hub API
Endpoints for knowledge articles, search, voting, and bookmarks
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.models import KnowledgeArticle, ArticleBookmark, ArticleVote
from schemas.knowledge import (
    ArticleCreate, ArticleUpdate, ArticleResponse, ArticleListResponse,
    ArticleListItem, ArticleVoteRequest, BookmarkResponse,
    AIGenerateRequest, AIGenerateResponse,
    SearchRequest, SearchResponse, SearchResultItem,
    VerifyArticleRequest, VerifyArticleResponse
)
from services.knowledge_service import KnowledgeService
from services.search_service import SearchService
from api.dependencies import (
    get_current_user, get_current_user_optional, get_token,
    require_specialist, get_validation_client, get_ai_client
)
from integrations.validation_client import ValidationClient
from integrations.ai_client import AIClient

router = APIRouter(prefix="/api/portal/knowledge", tags=["Knowledge Hub"])
knowledge_service = KnowledgeService()
search_service = SearchService()


# ============================================================================
# Article CRUD
# ============================================================================

@router.post("/articles", response_model=ArticleResponse, status_code=201)
async def create_article(
    article_data: ArticleCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new knowledge article

    - **title**: Article title (max 500 chars)
    - **summary**: Short summary (max 1000 chars)
    - **content**: Full article content in Markdown
    - **category**: Article category
    - **tags**: List of tags (max 10)
    - **iso_clause**: Optional ISO 22301 clause reference

    Article is created as draft (not published) by default.
    """
    article = await knowledge_service.create_article(
        db=db,
        article_data=article_data,
        author_id=current_user['user_id'],
        author_type=current_user.get('user_type', 'user'),
        tenant_id=current_user.get('tenant_id')
    )

    return article


@router.get("/articles", response_model=ArticleListResponse)
async def get_articles(
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    verified_only: bool = Query(False, description="Only verified articles"),
    published_only: bool = Query(True, description="Only published articles"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of knowledge articles with filtering and pagination

    Supports filtering by:
    - Category
    - Tags (comma-separated list)
    - Verification status
    - Published status

    Returns articles visible to the current user (public + tenant articles).
    """
    # Build query
    stmt = select(KnowledgeArticle)

    # Filters
    filters = []

    if published_only:
        filters.append(KnowledgeArticle.published == True)

    if verified_only:
        filters.append(KnowledgeArticle.verification_status == 'verified')

    if category:
        filters.append(KnowledgeArticle.category == category)

    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        for tag in tag_list:
            filters.append(
                KnowledgeArticle.tags.op('@>')(f'["{tag}"]')
            )

    # Tenant visibility
    tenant_id = current_user.get('tenant_id') if current_user else None
    if tenant_id:
        filters.append(
            (KnowledgeArticle.tenant_id == tenant_id) |
            (KnowledgeArticle.tenant_id.is_(None))
        )
    else:
        filters.append(KnowledgeArticle.tenant_id.is_(None))

    if filters:
        stmt = stmt.where(and_(*filters))

    # Order by usefulness score
    stmt = stmt.order_by(KnowledgeArticle.usefulness_score.desc())

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    # Execute
    result = await db.execute(stmt)
    articles = result.scalars().all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    return ArticleListResponse(
        articles=[ArticleListItem.model_validate(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get article by ID

    Increments view count automatically.
    Returns user-specific fields (bookmarked, user_vote) if authenticated.
    """
    # Get article
    result = await db.execute(
        select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check visibility
    tenant_id = current_user.get('tenant_id') if current_user else None
    if article.tenant_id and article.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Increment view count
    await knowledge_service.increment_view_count(db, article_id)

    # Get user-specific data if authenticated
    response = ArticleResponse.model_validate(article)

    if current_user:
        user_id = current_user['user_id']

        # Check if bookmarked
        bookmark_result = await db.execute(
            select(ArticleBookmark).where(
                and_(
                    ArticleBookmark.article_id == article_id,
                    ArticleBookmark.user_id == user_id
                )
            )
        )
        response.is_bookmarked = bookmark_result.scalar_one_or_none() is not None

        # Get user vote
        vote_result = await db.execute(
            select(ArticleVote).where(
                and_(
                    ArticleVote.article_id == article_id,
                    ArticleVote.user_id == user_id
                )
            )
        )
        vote = vote_result.scalar_one_or_none()
        response.user_vote = vote.vote if vote else None

    return response


@router.patch("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an article

    Only the article author or admin can update.
    """
    # Get article
    result = await db.execute(
        select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check permissions
    user_id = current_user['user_id']
    user_type = current_user.get('user_type')

    if article.author_id != user_id and user_type != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Only article author or admin can update"
        )

    # Update
    updated_article = await knowledge_service.update_article(
        db, article_id, article_data
    )

    return updated_article


# ============================================================================
# Voting
# ============================================================================

@router.post("/articles/{article_id}/vote")
async def vote_article(
    article_id: int,
    vote_data: ArticleVoteRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vote on an article

    - **vote**: 1 for upvote, -1 for downvote

    If user already voted, updates the vote.
    """
    user_id = current_user['user_id']

    # Check if article exists
    result = await db.execute(
        select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Vote
    await knowledge_service.vote_article(
        db, article_id, user_id, vote_data.vote
    )

    return {"message": "Vote recorded successfully", "vote": vote_data.vote}


@router.delete("/articles/{article_id}/vote")
async def remove_vote(
    article_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove user's vote from an article"""

    user_id = current_user['user_id']

    removed = await knowledge_service.remove_vote(db, article_id, user_id)

    if not removed:
        raise HTTPException(status_code=404, detail="No vote found to remove")

    return {"message": "Vote removed successfully"}


# ============================================================================
# Bookmarks
# ============================================================================

@router.post("/articles/{article_id}/bookmark", response_model=BookmarkResponse)
async def bookmark_article(
    article_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bookmark an article for later reading"""

    user_id = current_user['user_id']

    # Check if article exists
    result = await db.execute(
        select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    bookmark = await knowledge_service.bookmark_article(db, article_id, user_id)

    return bookmark


@router.delete("/articles/{article_id}/bookmark")
async def remove_bookmark(
    article_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove bookmark from an article"""

    user_id = current_user['user_id']

    removed = await knowledge_service.remove_bookmark(db, article_id, user_id)

    if not removed:
        raise HTTPException(status_code=404, detail="No bookmark found to remove")

    return {"message": "Bookmark removed successfully"}


@router.get("/bookmarks", response_model=ArticleListResponse)
async def get_my_bookmarks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's bookmarked articles"""

    user_id = current_user['user_id']

    # Build query
    stmt = select(KnowledgeArticle).join(ArticleBookmark).where(
        ArticleBookmark.user_id == user_id
    ).order_by(ArticleBookmark.created_at.desc())

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    # Execute
    result = await db.execute(stmt)
    articles = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return ArticleListResponse(
        articles=[ArticleListItem.model_validate(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ============================================================================
# Search
# ============================================================================

@router.get("/search", response_model=SearchResponse)
async def search_articles(
    query: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    verified_only: bool = Query(False),
    published_only: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Full-text search for articles

    Uses PostgreSQL ts_rank for relevance scoring.
    Results are sorted by relevance.
    """
    tenant_id = current_user.get('tenant_id') if current_user else None
    tag_list = [t.strip() for t in tags.split(',')] if tags else None

    results, total = await search_service.search_articles(
        db=db,
        query=query,
        category=category,
        tags=tag_list,
        verified_only=verified_only,
        published_only=published_only,
        tenant_id=tenant_id,
        page=page,
        page_size=page_size
    )

    total_pages = (total + page_size - 1) // page_size

    # Format results
    search_results = []
    for item in results:
        article = item['article']
        search_results.append(SearchResultItem(
            id=article.id,
            title=article.title,
            slug=article.slug,
            summary=article.summary,
            category=article.category,
            tags=article.tags,
            relevance_score=item['relevance_score'],
            verification_status=article.verification_status,
            usefulness_score=article.usefulness_score,
            upvotes=article.upvotes,
            created_at=article.created_at
        ))

    return SearchResponse(
        results=search_results,
        total=total,
        query=query,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


# ============================================================================
# AI Generation
# ============================================================================

@router.post("/ai-generate", response_model=AIGenerateResponse, status_code=201)
async def generate_article_from_exercise(
    generate_request: AIGenerateRequest,
    current_user: dict = Depends(get_current_user),
    token: str = Depends(get_token),
    validation_client: ValidationClient = Depends(get_validation_client),
    ai_client: AIClient = Depends(get_ai_client),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate knowledge article from exercise using AI

    Requires:
    - **exercise_id**: Exercise ID from Validation module

    Optional:
    - **category**: Override auto-detected category
    - **tags**: Override auto-detected tags

    Generated article is created as draft with 'pending' verification status.
    Requires expert verification before publishing.
    """
    article = await knowledge_service.generate_article_from_exercise(
        db=db,
        exercise_id=generate_request.exercise_id,
        author_id=current_user['user_id'],
        tenant_id=current_user['tenant_id'],
        token=token,
        validation_client=validation_client,
        ai_client=ai_client,
        category_override=generate_request.category,
        tags_override=generate_request.tags
    )

    return AIGenerateResponse(
        article_id=article.id,
        title=article.title,
        slug=article.slug,
        confidence_score=article.ai_confidence_score or 0.0,
        verification_status=article.verification_status
    )


# ============================================================================
# Verification (Specialist/Admin only)
# ============================================================================

@router.post("/articles/{article_id}/verify", response_model=VerifyArticleResponse)
async def verify_article(
    article_id: int,
    verify_request: VerifyArticleRequest,
    current_user: dict = Depends(require_specialist),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify or reject an article (Specialist/Admin only)

    - **status**: 'verified' or 'rejected'
    - **notes**: Optional verification notes

    Only specialists and admins can verify articles.
    Typically used for AI-generated content.
    """
    article = await knowledge_service.verify_article(
        db=db,
        article_id=article_id,
        verifier_id=current_user['user_id'],
        status=verify_request.status,
        notes=verify_request.notes
    )

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return VerifyArticleResponse(
        article_id=article.id,
        verification_status=article.verification_status,
        verified_by=article.verified_by,
        verified_at=article.verified_at,
        message=f"Article {verify_request.status} successfully"
    )


# ============================================================================
# Article Discussions (Forum Integration)
# ============================================================================

@router.post("/articles/{article_id}/discuss")
async def create_article_discussion(
    article_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a forum topic to discuss an article

    Automatically creates a topic in the "Knowledge Hub" category
    linked to this article.

    Returns the created topic.
    """
    # Import here to avoid circular dependency
    from services.forum_service import ForumService
    from schemas.forum import TopicCreate

    forum_service = ForumService()

    # Check if article exists
    result = await db.execute(
        select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check if discussion already exists
    result = await db.execute(
        select(ForumTopic).where(ForumTopic.linked_article_id == article_id)
    )
    existing_topic = result.scalar_one_or_none()

    if existing_topic:
        return {
            "message": "Discussion already exists",
            "topic_id": existing_topic.id,
            "topic_url": f"/forum/topics/{existing_topic.id}"
        }

    # Create topic
    # Note: category_id=2 assumes "Knowledge Hub" category exists (from migration)
    topic_data = TopicCreate(
        category_id=2,  # "Knowledge Hub" category
        title=f"Discussion: {article.title}",
        content=f"Let's discuss this article: [{article.title}](/knowledge/articles/{article.slug})\n\n{article.summary}",
        tags=article.tags,
        linked_article_id=article_id
    )

    topic = await forum_service.create_topic(
        db=db,
        topic_data=topic_data,
        author_id=current_user['user_id'],
        author_type=current_user.get('user_type', 'user'),
        tenant_id=current_user.get('tenant_id')
    )

    return {
        "message": "Discussion topic created",
        "topic_id": topic.id,
        "topic_url": f"/forum/topics/{topic.id}"
    }


@router.get("/articles/{article_id}/discussion")
async def get_article_discussion(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get forum discussion for an article

    Returns the linked forum topic if it exists.
    """
    from database.models import ForumTopic

    result = await db.execute(
        select(ForumTopic).where(ForumTopic.linked_article_id == article_id)
    )
    topic = result.scalar_one_or_none()

    if not topic:
        return {
            "has_discussion": False,
            "message": "No discussion exists for this article"
        }

    return {
        "has_discussion": True,
        "topic_id": topic.id,
        "topic_title": topic.title,
        "post_count": topic.post_count,
        "last_post_at": topic.last_post_at,
        "topic_url": f"/forum/topics/{topic.id}"
    }
