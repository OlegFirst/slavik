"""
Forum Service - Business Logic
Handles forum topics, posts, and voting
"""

import markdown
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from database.models import (
    ForumCategory, ForumTopic, ForumPost, TopicVote, PostVote, TopicStatus
)
from schemas.forum import TopicCreate, TopicUpdate, PostCreate


class ForumService:
    """
    Forum business logic

    Responsibilities:
    - Topic CRUD operations
    - Post CRUD operations
    - Voting system
    - Topic/Post rendering
    """

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

    async def get_categories(
        self,
        db: AsyncSession,
        parent_id: Optional[int] = None
    ) -> List[ForumCategory]:
        """
        Get forum categories

        Args:
            db: Database session
            parent_id: Filter by parent category (None for top-level)

        Returns:
            List of categories
        """
        stmt = select(ForumCategory)

        if parent_id is None:
            stmt = stmt.where(ForumCategory.parent_id.is_(None))
        else:
            stmt = stmt.where(ForumCategory.parent_id == parent_id)

        stmt = stmt.order_by(ForumCategory.display_order, ForumCategory.name)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_topic(
        self,
        db: AsyncSession,
        topic_data: TopicCreate,
        author_id: str,
        author_type: str,
        tenant_id: Optional[str] = None
    ) -> ForumTopic:
        """
        Create a new forum topic

        Args:
            db: Database session
            topic_data: Topic creation data
            author_id: Author user ID
            author_type: Author type (user, specialist, admin)
            tenant_id: Tenant ID (None for public)

        Returns:
            Created ForumTopic
        """
        # Render Markdown to HTML
        content_html = self.render_markdown(topic_data.content)

        # Create topic
        topic = ForumTopic(
            category_id=topic_data.category_id,
            tenant_id=tenant_id,
            title=topic_data.title,
            content=topic_data.content,
            content_html=content_html,
            author_id=author_id,
            author_type=author_type,
            tags=topic_data.tags,
            linked_article_id=topic_data.linked_article_id,
            linked_scenario_id=topic_data.linked_scenario_id,
            status=TopicStatus.active
        )

        db.add(topic)
        await db.commit()
        await db.refresh(topic)

        return topic

    async def get_topics(
        self,
        db: AsyncSession,
        category_id: Optional[int] = None,
        tenant_id: Optional[str] = None,
        status: str = 'active',
        linked_article_id: Optional[int] = None,
        linked_scenario_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ForumTopic], int]:
        """
        Get forum topics with filtering and pagination

        Args:
            db: Database session
            category_id: Filter by category
            tenant_id: Filter by tenant (None for public only)
            status: Filter by status
            linked_article_id: Filter by linked article
            linked_scenario_id: Filter by linked scenario
            page: Page number
            page_size: Results per page

        Returns:
            Tuple of (topics list, total count)
        """
        stmt = select(ForumTopic)

        # Filters
        filters = []

        if category_id:
            filters.append(ForumTopic.category_id == category_id)

        if status:
            filters.append(ForumTopic.status == status)

        if linked_article_id:
            filters.append(ForumTopic.linked_article_id == linked_article_id)

        if linked_scenario_id:
            filters.append(ForumTopic.linked_scenario_id == linked_scenario_id)

        # Tenant visibility
        if tenant_id:
            filters.append(
                or_(
                    ForumTopic.tenant_id == tenant_id,
                    ForumTopic.tenant_id.is_(None)
                )
            )
        else:
            filters.append(ForumTopic.tenant_id.is_(None))

        if filters:
            stmt = stmt.where(and_(*filters))

        # Order: pinned first, then by activity
        stmt = stmt.order_by(
            ForumTopic.is_pinned.desc(),
            ForumTopic.last_post_at.desc()
        )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # Execute
        result = await db.execute(stmt)
        topics = result.scalars().all()

        return topics, total

    async def get_topic(
        self,
        db: AsyncSession,
        topic_id: int,
        increment_views: bool = True
    ) -> Optional[ForumTopic]:
        """
        Get topic by ID

        Args:
            db: Database session
            topic_id: Topic ID
            increment_views: Whether to increment view count

        Returns:
            ForumTopic or None
        """
        result = await db.execute(
            select(ForumTopic).where(ForumTopic.id == topic_id)
        )
        topic = result.scalar_one_or_none()

        if topic and increment_views:
            # Increment view count
            await db.execute(
                update(ForumTopic)
                .where(ForumTopic.id == topic_id)
                .values(view_count=ForumTopic.view_count + 1)
            )
            await db.commit()
            await db.refresh(topic)

        return topic

    async def update_topic(
        self,
        db: AsyncSession,
        topic_id: int,
        topic_data: TopicUpdate
    ) -> Optional[ForumTopic]:
        """
        Update a topic

        Args:
            db: Database session
            topic_id: Topic ID
            topic_data: Update data

        Returns:
            Updated topic or None
        """
        result = await db.execute(
            select(ForumTopic).where(ForumTopic.id == topic_id)
        )
        topic = result.scalar_one_or_none()

        if not topic:
            return None

        # Update fields
        update_data = topic_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(topic, field, value)

        # Re-render HTML if content changed
        if 'content' in update_data:
            topic.content_html = self.render_markdown(topic.content)

        await db.commit()
        await db.refresh(topic)

        return topic

    async def vote_topic(
        self,
        db: AsyncSession,
        topic_id: int,
        user_id: str,
        vote_value: int  # 1 or -1
    ) -> TopicVote:
        """
        Vote on a topic

        Args:
            db: Database session
            topic_id: Topic ID
            user_id: User ID
            vote_value: 1 for upvote, -1 for downvote

        Returns:
            TopicVote instance
        """
        # Check if vote exists
        result = await db.execute(
            select(TopicVote).where(
                and_(
                    TopicVote.topic_id == topic_id,
                    TopicVote.user_id == user_id
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
            vote = TopicVote(
                topic_id=topic_id,
                user_id=user_id,
                vote=vote_value
            )
            db.add(vote)
            await db.commit()
            await db.refresh(vote)
            return vote

    async def remove_topic_vote(
        self,
        db: AsyncSession,
        topic_id: int,
        user_id: str
    ) -> bool:
        """
        Remove vote from topic

        Args:
            db: Database session
            topic_id: Topic ID
            user_id: User ID

        Returns:
            True if removed, False if no vote existed
        """
        result = await db.execute(
            delete(TopicVote).where(
                and_(
                    TopicVote.topic_id == topic_id,
                    TopicVote.user_id == user_id
                )
            )
        )
        await db.commit()

        return result.rowcount > 0

    async def create_post(
        self,
        db: AsyncSession,
        topic_id: int,
        post_data: PostCreate,
        author_id: str,
        author_type: str
    ) -> ForumPost:
        """
        Create a forum post (reply to topic)

        Args:
            db: Database session
            topic_id: Topic ID
            post_data: Post creation data
            author_id: Author user ID
            author_type: Author type

        Returns:
            Created ForumPost
        """
        # Render Markdown to HTML
        content_html = self.render_markdown(post_data.content)

        # Create post
        post = ForumPost(
            topic_id=topic_id,
            parent_post_id=post_data.parent_post_id,
            content=post_data.content,
            content_html=content_html,
            author_id=author_id,
            author_type=author_type
        )

        db.add(post)
        await db.commit()
        await db.refresh(post)

        return post

    async def get_topic_posts(
        self,
        db: AsyncSession,
        topic_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[ForumPost], int]:
        """
        Get posts for a topic

        Args:
            db: Database session
            topic_id: Topic ID
            page: Page number
            page_size: Results per page

        Returns:
            Tuple of (posts list, total count)
        """
        stmt = select(ForumPost).where(
            and_(
                ForumPost.topic_id == topic_id,
                ForumPost.is_deleted == False
            )
        ).order_by(ForumPost.created_at)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # Execute
        result = await db.execute(stmt)
        posts = result.scalars().all()

        return posts, total

    async def update_post(
        self,
        db: AsyncSession,
        post_id: int,
        content: str
    ) -> Optional[ForumPost]:
        """
        Update a post

        Args:
            db: Database session
            post_id: Post ID
            content: New content

        Returns:
            Updated post or None
        """
        result = await db.execute(
            select(ForumPost).where(ForumPost.id == post_id)
        )
        post = result.scalar_one_or_none()

        if not post:
            return None

        post.content = content
        post.content_html = self.render_markdown(content)
        post.edited_at = datetime.utcnow()

        await db.commit()
        await db.refresh(post)

        return post

    async def vote_post(
        self,
        db: AsyncSession,
        post_id: int,
        user_id: str,
        vote_value: int
    ) -> PostVote:
        """
        Vote on a post

        Args:
            db: Database session
            post_id: Post ID
            user_id: User ID
            vote_value: 1 for upvote, -1 for downvote

        Returns:
            PostVote instance
        """
        # Check if vote exists
        result = await db.execute(
            select(PostVote).where(
                and_(
                    PostVote.post_id == post_id,
                    PostVote.user_id == user_id
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
            vote = PostVote(
                post_id=post_id,
                user_id=user_id,
                vote=vote_value
            )
            db.add(vote)
            await db.commit()
            await db.refresh(vote)
            return vote

    async def mark_solution(
        self,
        db: AsyncSession,
        topic_id: int,
        post_id: int
    ) -> bool:
        """
        Mark a post as solution for a topic

        Args:
            db: Database session
            topic_id: Topic ID
            post_id: Post ID

        Returns:
            True if successful
        """
        # Update topic
        await db.execute(
            update(ForumTopic)
            .where(ForumTopic.id == topic_id)
            .values(
                is_solved=True,
                solution_post_id=post_id
            )
        )

        # Update post
        await db.execute(
            update(ForumPost)
            .where(ForumPost.id == post_id)
            .values(is_solution=True)
        )

        await db.commit()
        return True

    async def get_user_topics(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 20
    ) -> List[ForumTopic]:
        """
        Get topics created by user

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum results

        Returns:
            List of topics
        """
        result = await db.execute(
            select(ForumTopic)
            .where(ForumTopic.author_id == user_id)
            .order_by(ForumTopic.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_posts(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 20
    ) -> List[ForumPost]:
        """
        Get posts created by user

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum results

        Returns:
            List of posts
        """
        result = await db.execute(
            select(ForumPost)
            .where(
                and_(
                    ForumPost.author_id == user_id,
                    ForumPost.is_deleted == False
                )
            )
            .order_by(ForumPost.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
