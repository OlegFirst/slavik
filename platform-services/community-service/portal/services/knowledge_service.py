"""
Knowledge Service - Business Logic
Handles knowledge article operations, voting, bookmarks, and AI generation
"""

import markdown
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from database.models import KnowledgeArticle, ArticleBookmark, ArticleVote
from schemas.knowledge import ArticleCreate, ArticleUpdate
from integrations.validation_client import ValidationClient
from integrations.ai_client import AIClient


class KnowledgeService:
    """
    Knowledge Hub business logic

    Responsibilities:
    - Article CRUD operations
    - Usefulness score calculation
    - Voting and bookmarks
    - AI content generation
    - Verification workflow
    """

    @staticmethod
    def calculate_usefulness_score(article: KnowledgeArticle) -> float:
        """
        Calculate usefulness score for an article

        Formula: (upvotes * 2 - downvotes) + (view_count / 100)

        Args:
            article: KnowledgeArticle instance

        Returns:
            Calculated usefulness score
        """
        vote_score = (article.upvotes * 2) - article.downvotes
        view_score = article.view_count / 100.0
        return vote_score + view_score

    @staticmethod
    def render_markdown(content: str) -> str:
        """
        Render Markdown content to HTML

        Args:
            content: Markdown text

        Returns:
            Rendered HTML
        """
        return markdown.markdown(
            content,
            extensions=['extra', 'codehilite', 'tables', 'fenced_code']
        )

    @staticmethod
    def generate_slug(title: str, article_id: Optional[int] = None) -> str:
        """
        Generate URL-safe slug from title

        Args:
            title: Article title
            article_id: Optional article ID to append for uniqueness

        Returns:
            URL-safe slug
        """
        base_slug = slugify(title, max_length=100)
        if article_id:
            return f"{base_slug}-{article_id}"
        return base_slug

    async def create_article(
        self,
        db: AsyncSession,
        article_data: ArticleCreate,
        author_id: str,
        author_type: str,
        tenant_id: Optional[str] = None
    ) -> KnowledgeArticle:
        """
        Create a new knowledge article

        Args:
            db: Database session
            article_data: Article creation data
            author_id: Author user/specialist ID
            author_type: Type of author (user, specialist, admin)
            tenant_id: Tenant ID (None for public article)

        Returns:
            Created KnowledgeArticle
        """
        # Generate initial slug
        temp_slug = self.generate_slug(article_data.title)

        # Render Markdown to HTML
        content_html = self.render_markdown(article_data.content)

        # Create article
        article = KnowledgeArticle(
            tenant_id=tenant_id,
            title=article_data.title,
            slug=temp_slug,  # Will be updated after insert
            summary=article_data.summary,
            content=article_data.content,
            content_html=content_html,
            category=article_data.category,
            tags=article_data.tags,
            iso_clause=article_data.iso_clause,
            author_id=author_id,
            author_type=author_type,
            published=False,  # Draft by default
            verification_status='pending'
        )

        db.add(article)
        await db.flush()  # Get ID

        # Update slug with ID for uniqueness
        article.slug = self.generate_slug(article_data.title, article.id)
        await db.commit()
        await db.refresh(article)

        return article

    async def update_article(
        self,
        db: AsyncSession,
        article_id: int,
        article_data: ArticleUpdate
    ) -> Optional[KnowledgeArticle]:
        """
        Update an existing article

        Args:
            db: Database session
            article_id: Article ID
            article_data: Update data

        Returns:
            Updated article or None if not found
        """
        # Get article
        result = await db.execute(
            select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
        )
        article = result.scalar_one_or_none()

        if not article:
            return None

        # Update fields
        update_data = article_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(article, field, value)

        # If content changed, re-render HTML
        if 'content' in update_data:
            article.content_html = self.render_markdown(article.content)

        # If title changed, regenerate slug
        if 'title' in update_data:
            article.slug = self.generate_slug(article.title, article.id)

        await db.commit()
        await db.refresh(article)

        return article

    async def publish_article(
        self,
        db: AsyncSession,
        article_id: int
    ) -> Optional[KnowledgeArticle]:
        """
        Publish an article (make it visible)

        Args:
            db: Database session
            article_id: Article ID

        Returns:
            Published article or None if not found
        """
        result = await db.execute(
            select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
        )
        article = result.scalar_one_or_none()

        if not article:
            return None

        article.published = True
        article.published_at = datetime.utcnow()

        await db.commit()
        await db.refresh(article)

        return article

    async def increment_view_count(
        self,
        db: AsyncSession,
        article_id: int
    ):
        """
        Increment article view count

        Args:
            db: Database session
            article_id: Article ID
        """
        await db.execute(
            update(KnowledgeArticle)
            .where(KnowledgeArticle.id == article_id)
            .values(view_count=KnowledgeArticle.view_count + 1)
        )
        await db.commit()

    async def vote_article(
        self,
        db: AsyncSession,
        article_id: int,
        user_id: str,
        vote_value: int  # 1 or -1
    ) -> ArticleVote:
        """
        Vote on an article (upvote or downvote)

        Args:
            db: Database session
            article_id: Article ID
            user_id: User ID
            vote_value: 1 for upvote, -1 for downvote

        Returns:
            ArticleVote instance
        """
        # Check if vote exists
        result = await db.execute(
            select(ArticleVote).where(
                and_(
                    ArticleVote.article_id == article_id,
                    ArticleVote.user_id == user_id
                )
            )
        )
        existing_vote = result.scalar_one_or_none()

        if existing_vote:
            # Update existing vote
            existing_vote.vote = vote_value
            await db.commit()
            await db.refresh(existing_vote)
            return existing_vote
        else:
            # Create new vote
            vote = ArticleVote(
                article_id=article_id,
                user_id=user_id,
                vote=vote_value
            )
            db.add(vote)
            await db.commit()
            await db.refresh(vote)
            return vote

    async def remove_vote(
        self,
        db: AsyncSession,
        article_id: int,
        user_id: str
    ) -> bool:
        """
        Remove user's vote from an article

        Args:
            db: Database session
            article_id: Article ID
            user_id: User ID

        Returns:
            True if vote was removed, False if no vote existed
        """
        result = await db.execute(
            delete(ArticleVote).where(
                and_(
                    ArticleVote.article_id == article_id,
                    ArticleVote.user_id == user_id
                )
            )
        )
        await db.commit()

        return result.rowcount > 0

    async def bookmark_article(
        self,
        db: AsyncSession,
        article_id: int,
        user_id: str
    ) -> ArticleBookmark:
        """
        Bookmark an article for later reading

        Args:
            db: Database session
            article_id: Article ID
            user_id: User ID

        Returns:
            ArticleBookmark instance
        """
        # Check if already bookmarked
        result = await db.execute(
            select(ArticleBookmark).where(
                and_(
                    ArticleBookmark.article_id == article_id,
                    ArticleBookmark.user_id == user_id
                )
            )
        )
        existing_bookmark = result.scalar_one_or_none()

        if existing_bookmark:
            return existing_bookmark

        # Create bookmark
        bookmark = ArticleBookmark(
            article_id=article_id,
            user_id=user_id
        )
        db.add(bookmark)
        await db.commit()
        await db.refresh(bookmark)

        return bookmark

    async def remove_bookmark(
        self,
        db: AsyncSession,
        article_id: int,
        user_id: str
    ) -> bool:
        """
        Remove bookmark from an article

        Args:
            db: Database session
            article_id: Article ID
            user_id: User ID

        Returns:
            True if bookmark was removed, False if didn't exist
        """
        result = await db.execute(
            delete(ArticleBookmark).where(
                and_(
                    ArticleBookmark.article_id == article_id,
                    ArticleBookmark.user_id == user_id
                )
            )
        )
        await db.commit()

        return result.rowcount > 0

    async def get_user_bookmarks(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> List[KnowledgeArticle]:
        """
        Get user's bookmarked articles

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of results

        Returns:
            List of bookmarked articles
        """
        result = await db.execute(
            select(KnowledgeArticle)
            .join(ArticleBookmark)
            .where(ArticleBookmark.user_id == user_id)
            .order_by(ArticleBookmark.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def verify_article(
        self,
        db: AsyncSession,
        article_id: int,
        verifier_id: str,
        status: str,  # 'verified' or 'rejected'
        notes: Optional[str] = None
    ) -> Optional[KnowledgeArticle]:
        """
        Verify or reject an article (specialist/admin only)

        Args:
            db: Database session
            article_id: Article ID
            verifier_id: Verifier user ID
            status: Verification status
            notes: Optional verification notes

        Returns:
            Updated article or None if not found
        """
        result = await db.execute(
            select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
        )
        article = result.scalar_one_or_none()

        if not article:
            return None

        article.verification_status = status
        article.verified_by = verifier_id
        article.verified_at = datetime.utcnow()
        article.verification_notes = notes

        await db.commit()
        await db.refresh(article)

        return article

    async def generate_article_from_exercise(
        self,
        db: AsyncSession,
        exercise_id: int,
        author_id: str,
        tenant_id: str,
        token: str,
        validation_client: ValidationClient,
        ai_client: AIClient,
        category_override: Optional[str] = None,
        tags_override: Optional[List[str]] = None
    ) -> KnowledgeArticle:
        """
        Generate knowledge article from exercise using AI

        Args:
            db: Database session
            exercise_id: Source exercise ID
            author_id: Author ID
            tenant_id: Tenant ID
            token: JWT token
            validation_client: Validation service client
            ai_client: AI Orchestrator client
            category_override: Override category
            tags_override: Override tags

        Returns:
            Generated KnowledgeArticle

        Raises:
            ValueError if exercise not found or insights unavailable
        """
        # Get exercise data
        exercise = await validation_client.get_exercise(exercise_id, token)
        if not exercise:
            raise ValueError(f"Exercise {exercise_id} not found")

        # Get exercise insights
        insights = await validation_client.get_exercise_insights(exercise_id, token)
        if not insights:
            raise ValueError(f"Exercise {exercise_id} has no insights available")

        # Generate article with AI
        ai_result = await ai_client.generate_article_from_exercise(
            exercise_data=exercise,
            insights_data=insights,
            token=token
        )

        # Render Markdown to HTML
        content_html = self.render_markdown(ai_result['content'])

        # Create article
        article = KnowledgeArticle(
            tenant_id=tenant_id,
            title=ai_result['title'],
            slug=self.generate_slug(ai_result['title']),
            summary=ai_result['summary'],
            content=ai_result['content'],
            content_html=content_html,
            category=category_override or ai_result.get('suggested_category', 'General'),
            tags=tags_override or ai_result.get('suggested_tags', []),
            iso_clause=ai_result.get('iso_clause'),
            author_id=author_id,
            author_type='ai',  # Mark as AI-generated
            published=False,  # Draft by default
            ai_generated=True,
            ai_confidence_score=ai_result.get('confidence_score', 0.0),
            source_exercise_id=exercise_id,
            verification_status='pending'  # Requires expert verification
        )

        db.add(article)
        await db.flush()

        # Update slug with ID
        article.slug = self.generate_slug(ai_result['title'], article.id)
        await db.commit()
        await db.refresh(article)

        return article
