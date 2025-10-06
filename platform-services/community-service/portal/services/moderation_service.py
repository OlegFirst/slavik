"""
Moderation Service - Business Logic
Handles content moderation, flags, and moderation actions
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    ModerationFlag, ForumTopic, ForumPost, ModerationAction, TopicStatus
)


class ModerationService:
    """
    Content moderation business logic

    Responsibilities:
    - Flag management (reports)
    - Moderation queue
    - Content moderation actions
    """

    async def flag_topic(
        self,
        db: AsyncSession,
        topic_id: int,
        reporter_id: str,
        reason: str,
        description: Optional[str] = None
    ) -> ModerationFlag:
        """
        Flag a topic for moderation

        Args:
            db: Database session
            topic_id: Topic ID
            reporter_id: User reporting
            reason: Reason for flag
            description: Detailed description

        Returns:
            Created ModerationFlag
        """
        flag = ModerationFlag(
            topic_id=topic_id,
            reporter_id=reporter_id,
            reason=reason,
            description=description,
            status='pending'
        )

        db.add(flag)
        await db.commit()
        await db.refresh(flag)

        return flag

    async def flag_post(
        self,
        db: AsyncSession,
        post_id: int,
        reporter_id: str,
        reason: str,
        description: Optional[str] = None
    ) -> ModerationFlag:
        """
        Flag a post for moderation

        Args:
            db: Database session
            post_id: Post ID
            reporter_id: User reporting
            reason: Reason for flag
            description: Detailed description

        Returns:
            Created ModerationFlag
        """
        flag = ModerationFlag(
            post_id=post_id,
            reporter_id=reporter_id,
            reason=reason,
            description=description,
            status='pending'
        )

        db.add(flag)
        await db.commit()
        await db.refresh(flag)

        return flag

    async def get_moderation_queue(
        self,
        db: AsyncSession,
        status: str = 'pending',
        limit: int = 50
    ) -> List[ModerationFlag]:
        """
        Get moderation queue

        Args:
            db: Database session
            status: Filter by status (pending, reviewed, resolved)
            limit: Maximum results

        Returns:
            List of flags
        """
        stmt = select(ModerationFlag)

        if status:
            stmt = stmt.where(ModerationFlag.status == status)

        stmt = stmt.order_by(ModerationFlag.created_at).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def resolve_flag(
        self,
        db: AsyncSession,
        flag_id: int,
        moderator_id: str,
        action: ModerationAction,
        notes: Optional[str] = None
    ) -> Optional[ModerationFlag]:
        """
        Resolve a moderation flag

        Args:
            db: Database session
            flag_id: Flag ID
            moderator_id: Moderator user ID
            action: Moderation action taken
            notes: Moderator notes

        Returns:
            Updated flag or None
        """
        # Get flag
        result = await db.execute(
            select(ModerationFlag).where(ModerationFlag.id == flag_id)
        )
        flag = result.scalar_one_or_none()

        if not flag:
            return None

        # Update flag
        flag.status = 'resolved'
        flag.reviewed_by = moderator_id
        flag.reviewed_at = datetime.utcnow()
        flag.action_taken = action
        flag.moderator_notes = notes

        # Take action on content
        if flag.topic_id:
            await self._moderate_topic(db, flag.topic_id, action)
        elif flag.post_id:
            await self._moderate_post(db, flag.post_id, action)

        await db.commit()
        await db.refresh(flag)

        return flag

    async def _moderate_topic(
        self,
        db: AsyncSession,
        topic_id: int,
        action: ModerationAction
    ):
        """
        Apply moderation action to topic

        Args:
            db: Database session
            topic_id: Topic ID
            action: Moderation action
        """
        if action == ModerationAction.approved:
            # No action needed
            pass
        elif action == ModerationAction.rejected:
            # Close topic
            await db.execute(
                update(ForumTopic)
                .where(ForumTopic.id == topic_id)
                .values(
                    status=TopicStatus.closed,
                    is_locked=True
                )
            )
        elif action == ModerationAction.hidden:
            # Archive topic (hidden from public)
            await db.execute(
                update(ForumTopic)
                .where(ForumTopic.id == topic_id)
                .values(status=TopicStatus.archived)
            )
        elif action == ModerationAction.deleted:
            # Soft delete (mark as deleted)
            await db.execute(
                update(ForumTopic)
                .where(ForumTopic.id == topic_id)
                .values(status=TopicStatus.deleted)
            )

    async def _moderate_post(
        self,
        db: AsyncSession,
        post_id: int,
        action: ModerationAction
    ):
        """
        Apply moderation action to post

        Args:
            db: Database session
            post_id: Post ID
            action: Moderation action
        """
        if action == ModerationAction.approved:
            # No action needed
            pass
        elif action == ModerationAction.rejected or action == ModerationAction.hidden:
            # Hide post
            await db.execute(
                update(ForumPost)
                .where(ForumPost.id == post_id)
                .values(is_hidden=True)
            )
        elif action == ModerationAction.deleted:
            # Soft delete post
            await db.execute(
                update(ForumPost)
                .where(ForumPost.id == post_id)
                .values(is_deleted=True)
            )

    async def get_user_flags(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 20
    ) -> List[ModerationFlag]:
        """
        Get flags reported by user

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum results

        Returns:
            List of flags
        """
        result = await db.execute(
            select(ModerationFlag)
            .where(ModerationFlag.reporter_id == user_id)
            .order_by(ModerationFlag.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_content_flags(
        self,
        db: AsyncSession,
        topic_id: Optional[int] = None,
        post_id: Optional[int] = None
    ) -> List[ModerationFlag]:
        """
        Get flags for specific content

        Args:
            db: Database session
            topic_id: Filter by topic
            post_id: Filter by post

        Returns:
            List of flags
        """
        filters = []

        if topic_id:
            filters.append(ModerationFlag.topic_id == topic_id)
        if post_id:
            filters.append(ModerationFlag.post_id == post_id)

        stmt = select(ModerationFlag)

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(ModerationFlag.created_at.desc())

        result = await db.execute(stmt)
        return result.scalars().all()
