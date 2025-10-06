"""
Review Service - Business Logic
Manages client reviews of specialists and specialist responses
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
from decimal import Decimal
import logging

from database.models import Review, Project, Specialist
from schemas.review import ReviewCreate, SpecialistResponseCreate
from shared.eventbus import get_eventbus

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for managing specialist reviews and ratings"""

    # ========================================================================
    # Review Management
    # ========================================================================

    async def create_review(
        self,
        db: AsyncSession,
        review_data: ReviewCreate,
        reviewer_id: str,
        tenant_id: str
    ) -> Review:
        """
        Create new review for specialist

        Args:
            db: Database session
            review_data: Review data
            reviewer_id: Client user ID from auth
            tenant_id: Tenant ID from auth

        Returns:
            Created review

        Business Rules:
            - Can only review after project completion
            - One review per project-specialist pair
            - Reviewer must be project client
            - Rating 1-5 required
            - All category ratings optional but must be 1-5
            - Updates specialist overall rating after creation
        """
        # Get project
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == review_data.project_id,
                    Project.tenant_id == tenant_id
                )
            )
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError("Project not found")

        # Verify reviewer is project client
        if str(project.client_id) != str(reviewer_id):
            raise ValueError("Only the project client can write a review")

        # Verify project is completed
        if project.status != "completed":
            raise ValueError("Can only review completed projects")

        # Verify specialist matches
        if project.selected_specialist_id != review_data.specialist_id:
            raise ValueError("Specialist ID does not match project specialist")

        # Check for existing review
        result = await db.execute(
            select(Review).where(
                and_(
                    Review.project_id == review_data.project_id,
                    Review.specialist_id == review_data.specialist_id,
                    Review.reviewer_id == reviewer_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError("You have already reviewed this specialist for this project")

        # Create review
        review = Review(
            project_id=review_data.project_id,
            specialist_id=review_data.specialist_id,
            reviewer_id=reviewer_id,
            tenant_id=tenant_id,
            rating=review_data.rating,
            title=review_data.title,
            review_text=review_data.review_text,
            communication_rating=review_data.communication_rating,
            quality_rating=review_data.quality_rating,
            professionalism_rating=review_data.professionalism_rating,
            timeliness_rating=review_data.timeliness_rating,
            is_public=True,  # Default to public
            is_verified=True  # Auto-verify since client must own project
        )

        db.add(review)
        await db.commit()
        await db.refresh(review)

        # Update specialist rating
        await self.update_specialist_rating(db, review_data.specialist_id, tenant_id)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.review.created",
                {
                    "review_id": review.id,
                    "project_id": project.id,
                    "specialist_id": review_data.specialist_id,
                    "reviewer_id": reviewer_id,
                    "rating": review_data.rating,
                    "title": review_data.title
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish review.created event: {e}")

        logger.info(f"Review {review.id} created for specialist {review_data.specialist_id}")
        return review

    async def get_review(
        self,
        db: AsyncSession,
        review_id: int,
        tenant_id: str
    ) -> Optional[Review]:
        """Get review by ID"""
        result = await db.execute(
            select(Review)
            .options(
                selectinload(Review.project),
                selectinload(Review.specialist)
            )
            .where(
                and_(
                    Review.id == review_id,
                    Review.tenant_id == tenant_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def respond_to_review(
        self,
        db: AsyncSession,
        review_id: int,
        response_data: SpecialistResponseCreate,
        specialist_id: int,
        tenant_id: str,
        user_id: str
    ) -> Review:
        """
        Specialist responds to review

        Business Rules:
            - Only the reviewed specialist can respond
            - Can respond only once
            - Sets responded_at timestamp
            - Emits review.responded event
        """
        review = await self.get_review(db, review_id, tenant_id)
        if not review:
            raise ValueError("Review not found")

        # Verify specialist
        if review.specialist_id != specialist_id:
            raise ValueError("Only the reviewed specialist can respond")

        # Check if already responded
        if review.specialist_response:
            raise ValueError("You have already responded to this review")

        review.specialist_response = response_data.specialist_response
        review.responded_at = datetime.utcnow()
        review.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(review)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.review.responded",
                {
                    "review_id": review.id,
                    "specialist_id": specialist_id,
                    "user_id": user_id,
                    "response_text": response_data.specialist_response
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish review.responded event: {e}")

        logger.info(f"Review {review.id} response added by specialist {specialist_id}")
        return review

    # ========================================================================
    # Queries
    # ========================================================================

    async def get_reviews_by_specialist(
        self,
        db: AsyncSession,
        specialist_id: int,
        tenant_id: str,
        public_only: bool = True,
        limit: int = 50
    ) -> List[Review]:
        """
        Get all reviews for a specialist

        Used by:
            - Specialist profile page
            - Specialist dashboard
        """
        query = select(Review).options(
            selectinload(Review.project)
        ).where(
            and_(
                Review.specialist_id == specialist_id,
                Review.tenant_id == tenant_id
            )
        )

        if public_only:
            query = query.where(Review.is_public == True)

        # Sort by created_at DESC (newest first)
        query = query.order_by(Review.created_at.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_reviews_by_project(
        self,
        db: AsyncSession,
        project_id: int,
        tenant_id: str
    ) -> List[Review]:
        """Get all reviews for a project"""
        result = await db.execute(
            select(Review)
            .options(selectinload(Review.specialist))
            .where(
                and_(
                    Review.project_id == project_id,
                    Review.tenant_id == tenant_id
                )
            )
            .order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def get_reviews_by_client(
        self,
        db: AsyncSession,
        client_id: str,
        tenant_id: str,
        limit: int = 50
    ) -> List[Review]:
        """Get all reviews written by a client"""
        result = await db.execute(
            select(Review)
            .options(
                selectinload(Review.specialist),
                selectinload(Review.project)
            )
            .where(
                and_(
                    Review.reviewer_id == client_id,
                    Review.tenant_id == tenant_id
                )
            )
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    # ========================================================================
    # Rating Calculations
    # ========================================================================

    async def update_specialist_rating(
        self,
        db: AsyncSession,
        specialist_id: int,
        tenant_id: str
    ):
        """
        Recalculate and update specialist's overall rating

        Calculates:
            - Average overall rating
            - Total review count
            - Updates specialist.rating and specialist.total_reviews

        Called after:
            - New review created
            - Review updated
            - Review deleted
        """
        # Calculate average rating
        result = await db.execute(
            select(
                func.avg(Review.rating).label("avg_rating"),
                func.count(Review.id).label("total_reviews")
            )
            .where(
                and_(
                    Review.specialist_id == specialist_id,
                    Review.tenant_id == tenant_id,
                    Review.is_public == True
                )
            )
        )
        stats = result.first()

        # Get specialist
        result = await db.execute(
            select(Specialist).where(
                and_(
                    Specialist.id == specialist_id,
                    Specialist.tenant_id == tenant_id
                )
            )
        )
        specialist = result.scalar_one_or_none()

        if not specialist:
            logger.warning(f"Specialist {specialist_id} not found for rating update")
            return

        # Update specialist
        if stats.avg_rating:
            specialist.rating = Decimal(str(round(float(stats.avg_rating), 2)))
        else:
            specialist.rating = Decimal("0.00")

        specialist.total_reviews = stats.total_reviews or 0
        specialist.updated_at = datetime.utcnow()

        await db.commit()

        logger.info(
            f"Updated specialist {specialist_id} rating: {specialist.rating} "
            f"({specialist.total_reviews} reviews)"
        )

    async def get_review_statistics(
        self,
        db: AsyncSession,
        specialist_id: int,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed review statistics for specialist

        Returns:
            - Overall rating and count
            - Rating distribution (5 stars, 4 stars, etc.)
            - Category averages (communication, quality, etc.)
            - Response rate
        """
        # Get all reviews
        reviews = await self.get_reviews_by_specialist(
            db, specialist_id, tenant_id, public_only=True
        )

        if not reviews:
            return {
                "overall_rating": 0.0,
                "total_reviews": 0,
                "rating_distribution": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
                "category_averages": {},
                "response_rate": 0.0
            }

        # Overall
        total_reviews = len(reviews)
        overall_rating = sum(r.rating for r in reviews) / total_reviews

        # Rating distribution
        distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for review in reviews:
            distribution[review.rating] += 1

        # Category averages
        categories = {
            "communication": [],
            "quality": [],
            "professionalism": [],
            "timeliness": []
        }

        for review in reviews:
            if review.communication_rating:
                categories["communication"].append(review.communication_rating)
            if review.quality_rating:
                categories["quality"].append(review.quality_rating)
            if review.professionalism_rating:
                categories["professionalism"].append(review.professionalism_rating)
            if review.timeliness_rating:
                categories["timeliness"].append(review.timeliness_rating)

        category_averages = {}
        for category, ratings in categories.items():
            if ratings:
                category_averages[category] = round(sum(ratings) / len(ratings), 2)
            else:
                category_averages[category] = None

        # Response rate
        responded = sum(1 for r in reviews if r.specialist_response)
        response_rate = (responded / total_reviews * 100) if total_reviews > 0 else 0

        return {
            "overall_rating": round(overall_rating, 2),
            "total_reviews": total_reviews,
            "rating_distribution": distribution,
            "category_averages": category_averages,
            "response_rate": round(response_rate, 2),
            "responded_count": responded
        }

    async def get_recent_reviews(
        self,
        db: AsyncSession,
        tenant_id: str,
        limit: int = 10
    ) -> List[Review]:
        """
        Get recent reviews across all specialists in tenant

        Used for:
            - Homepage/dashboard
            - Activity feed
            - Marketplace overview
        """
        result = await db.execute(
            select(Review)
            .options(
                selectinload(Review.specialist),
                selectinload(Review.project)
            )
            .where(
                and_(
                    Review.tenant_id == tenant_id,
                    Review.is_public == True
                )
            )
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    # ========================================================================
    # Moderation
    # ========================================================================

    async def hide_review(
        self,
        db: AsyncSession,
        review_id: int,
        tenant_id: str,
        admin_id: str,
        reason: str
    ) -> Review:
        """
        Hide review (admin action)

        Business Rules:
            - Only admins can hide reviews
            - Sets is_public = False
            - Does NOT delete - keeps for records
            - Recalculates specialist rating
        """
        review = await self.get_review(db, review_id, tenant_id)
        if not review:
            raise ValueError("Review not found")

        review.is_public = False
        review.updated_at = datetime.utcnow()
        # Could store moderation reason in metadata

        await db.commit()

        # Recalculate rating without this review
        await self.update_specialist_rating(db, review.specialist_id, tenant_id)

        logger.info(f"Review {review_id} hidden by admin {admin_id}: {reason}")
        return review

    async def verify_review(
        self,
        db: AsyncSession,
        review_id: int,
        tenant_id: str,
        verified: bool
    ) -> Review:
        """
        Verify review (admin action)

        Used for:
            - Marking legitimate reviews as verified
            - Flagging suspicious reviews
        """
        review = await self.get_review(db, review_id, tenant_id)
        if not review:
            raise ValueError("Review not found")

        review.is_verified = verified
        review.updated_at = datetime.utcnow()

        await db.commit()
        logger.info(f"Review {review_id} verification set to {verified}")
        return review


# Singleton instance
review_service = ReviewService()
