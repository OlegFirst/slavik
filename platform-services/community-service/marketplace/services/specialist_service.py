"""
Specialist Service - Business Logic
Manages specialist profiles, certifications, and portfolios
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging

from database.models import Specialist, Certification, PortfolioItem
from schemas.specialist import (
    SpecialistCreate,
    SpecialistUpdate,
    CertificationCreate,
    PortfolioItemCreate,
    SpecialistSearchFilters
)
from shared.eventbus import get_eventbus

logger = logging.getLogger(__name__)


class SpecialistService:
    """Service for managing specialist profiles and related data"""

    # ========================================================================
    # Specialist Profile Management
    # ========================================================================

    async def create_specialist(
        self,
        db: AsyncSession,
        specialist_data: SpecialistCreate,
        user_id: str,
        tenant_id: str
    ) -> Specialist:
        """
        Create new specialist profile

        Args:
            db: Database session
            specialist_data: Specialist data
            user_id: User ID from auth
            tenant_id: Tenant ID from auth

        Returns:
            Created specialist

        Business Rules:
            - One active profile per user
            - Initial profile_completion calculated
            - Default availability_status = 'available'
            - is_verified = False (requires admin verification)
        """
        # Check if user already has active specialist profile
        result = await db.execute(
            select(Specialist).where(
                and_(
                    Specialist.user_id == user_id,
                    Specialist.tenant_id == tenant_id,
                    Specialist.active == True
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError("User already has an active specialist profile")

        # Calculate initial profile completion
        completion = self._calculate_profile_completion(specialist_data)

        # Create specialist
        specialist = Specialist(
            user_id=user_id,
            tenant_id=tenant_id,
            name=specialist_data.name,
            title=specialist_data.title,
            bio=specialist_data.bio,
            specializations=specialist_data.specializations or [],
            skills=specialist_data.skills or [],
            industries=specialist_data.industries or [],
            years_experience=specialist_data.years_experience,
            hourly_rate=specialist_data.hourly_rate,
            currency=specialist_data.currency or "USD",
            availability_status=specialist_data.availability_status or "available",
            country=specialist_data.country,
            city=specialist_data.city,
            timezone=specialist_data.timezone,
            languages=specialist_data.languages or [],
            profile_completion=completion,
            active=True,
            is_verified=False
        )

        db.add(specialist)
        await db.commit()
        await db.refresh(specialist)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.specialist.registered",
                {
                    "specialist_id": specialist.id,
                    "user_id": user_id,
                    "name": specialist.name,
                    "specializations": specialist.specializations
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish specialist.registered event: {e}")

        logger.info(f"Specialist profile created: {specialist.id}")
        return specialist

    async def get_specialist(
        self,
        db: AsyncSession,
        specialist_id: int,
        tenant_id: str
    ) -> Optional[Specialist]:
        """Get specialist by ID"""
        result = await db.execute(
            select(Specialist)
            .options(
                selectinload(Specialist.certifications),
                selectinload(Specialist.portfolio_items)
            )
            .where(
                and_(
                    Specialist.id == specialist_id,
                    Specialist.tenant_id == tenant_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_specialist_by_user(
        self,
        db: AsyncSession,
        user_id: str,
        tenant_id: str
    ) -> Optional[Specialist]:
        """Get specialist profile by user_id"""
        result = await db.execute(
            select(Specialist)
            .options(
                selectinload(Specialist.certifications),
                selectinload(Specialist.portfolio_items)
            )
            .where(
                and_(
                    Specialist.user_id == user_id,
                    Specialist.tenant_id == tenant_id,
                    Specialist.active == True
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_specialist(
        self,
        db: AsyncSession,
        specialist_id: int,
        specialist_data: SpecialistUpdate,
        tenant_id: str,
        user_id: str
    ) -> Specialist:
        """
        Update specialist profile

        Business Rules:
            - Recalculate profile_completion
            - Track updated_fields for event
            - Cannot change verification status (admin only)
        """
        specialist = await self.get_specialist(db, specialist_id, tenant_id)
        if not specialist:
            raise ValueError("Specialist not found")

        # Track what changed
        updated_fields = []

        update_data = specialist_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if getattr(specialist, field) != value:
                setattr(specialist, field, value)
                updated_fields.append(field)

        # Recalculate completion
        if updated_fields:
            specialist.profile_completion = self._calculate_profile_completion_model(specialist)
            specialist.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(specialist)

        # Publish event
        if updated_fields:
            try:
                eventbus = get_eventbus()
                await eventbus.publish(
                    "marketplace.specialist.profile_updated",
                    {
                        "specialist_id": specialist.id,
                        "user_id": user_id,
                        "updated_fields": updated_fields
                    },
                    tenant_id=tenant_id
                )
            except Exception as e:
                logger.warning(f"Failed to publish specialist.profile_updated event: {e}")

        logger.info(f"Specialist {specialist.id} updated: {updated_fields}")
        return specialist

    async def verify_specialist(
        self,
        db: AsyncSession,
        specialist_id: int,
        verified: bool,
        verified_by: str,
        verification_notes: Optional[str],
        tenant_id: str
    ) -> Specialist:
        """
        Verify or unverify specialist (admin only)

        Business Rules:
            - Only admins can verify
            - Track who verified and when
            - Emit verification event
        """
        specialist = await self.get_specialist(db, specialist_id, tenant_id)
        if not specialist:
            raise ValueError("Specialist not found")

        specialist.is_verified = verified
        specialist.verified_at = datetime.utcnow() if verified else None
        specialist.verified_by = verified_by if verified else None
        specialist.verification_notes = verification_notes
        specialist.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(specialist)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.specialist.verified",
                {
                    "specialist_id": specialist.id,
                    "verified": verified,
                    "verified_by": verified_by
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish specialist.verified event: {e}")

        logger.info(f"Specialist {specialist.id} verification changed to {verified}")
        return specialist

    async def search_specialists(
        self,
        db: AsyncSession,
        filters: SpecialistSearchFilters,
        tenant_id: str
    ) -> List[Specialist]:
        """
        Search specialists with filters

        Filters:
            - skills (JSONB array overlap)
            - specializations (JSONB array overlap)
            - industries (JSONB array overlap)
            - min_rating
            - verified_only
            - availability_status
            - min_hourly_rate, max_hourly_rate
            - country, city
            - search query (name, title, bio full-text)

        Returns:
            List of specialists sorted by rating DESC
        """
        query = select(Specialist).where(
            and_(
                Specialist.tenant_id == tenant_id,
                Specialist.active == True
            )
        )

        # Verified filter
        if filters.verified_only:
            query = query.where(Specialist.is_verified == True)

        # Skills filter (JSONB array overlap)
        if filters.skills:
            # Check if any skill in filters.skills exists in specialist.skills
            query = query.where(
                Specialist.skills.op('?|')(filters.skills)  # ?| is JSONB overlap operator
            )

        # Specializations filter
        if filters.specializations:
            query = query.where(
                Specialist.specializations.op('?|')(filters.specializations)
            )

        # Industries filter
        if filters.industries:
            query = query.where(
                Specialist.industries.op('?|')(filters.industries)
            )

        # Rating filter
        if filters.min_rating:
            query = query.where(Specialist.rating >= filters.min_rating)

        # Availability
        if filters.availability_status:
            query = query.where(Specialist.availability_status == filters.availability_status)

        # Hourly rate
        if filters.min_hourly_rate:
            query = query.where(Specialist.hourly_rate >= filters.min_hourly_rate)
        if filters.max_hourly_rate:
            query = query.where(Specialist.hourly_rate <= filters.max_hourly_rate)

        # Location
        if filters.country:
            query = query.where(Specialist.country == filters.country)
        if filters.city:
            query = query.where(Specialist.city == filters.city)

        # Text search (name, title, bio)
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.where(
                or_(
                    Specialist.name.ilike(search_pattern),
                    Specialist.title.ilike(search_pattern),
                    Specialist.bio.ilike(search_pattern)
                )
            )

        # Sort by rating DESC, then by total_reviews DESC
        query = query.order_by(
            Specialist.rating.desc(),
            Specialist.total_reviews.desc()
        )

        # Pagination
        if filters.offset:
            query = query.offset(filters.offset)
        if filters.limit:
            query = query.limit(filters.limit)

        result = await db.execute(query)
        return result.scalars().all()

    # ========================================================================
    # Certifications
    # ========================================================================

    async def add_certification(
        self,
        db: AsyncSession,
        specialist_id: int,
        cert_data: CertificationCreate,
        tenant_id: str
    ) -> Certification:
        """Add certification to specialist profile"""
        specialist = await self.get_specialist(db, specialist_id, tenant_id)
        if not specialist:
            raise ValueError("Specialist not found")

        certification = Certification(
            specialist_id=specialist_id,
            name=cert_data.name,
            issuing_organization=cert_data.issuing_organization,
            issue_date=cert_data.issue_date,
            expiry_date=cert_data.expiry_date,
            credential_id=cert_data.credential_id,
            credential_url=cert_data.credential_url,
            documents=cert_data.documents or [],
            is_verified=False
        )

        db.add(certification)

        # Update specialist profile completion
        specialist.profile_completion = self._calculate_profile_completion_model(specialist)

        await db.commit()
        await db.refresh(certification)

        logger.info(f"Certification added to specialist {specialist_id}")
        return certification

    async def delete_certification(
        self,
        db: AsyncSession,
        cert_id: int,
        specialist_id: int,
        tenant_id: str
    ):
        """Delete certification"""
        specialist = await self.get_specialist(db, specialist_id, tenant_id)
        if not specialist:
            raise ValueError("Specialist not found")

        await db.execute(
            delete(Certification).where(
                and_(
                    Certification.id == cert_id,
                    Certification.specialist_id == specialist_id
                )
            )
        )

        # Update profile completion
        specialist.profile_completion = self._calculate_profile_completion_model(specialist)

        await db.commit()
        logger.info(f"Certification {cert_id} deleted")

    # ========================================================================
    # Portfolio
    # ========================================================================

    async def add_portfolio_item(
        self,
        db: AsyncSession,
        specialist_id: int,
        portfolio_data: PortfolioItemCreate,
        tenant_id: str
    ) -> PortfolioItem:
        """Add portfolio item"""
        specialist = await self.get_specialist(db, specialist_id, tenant_id)
        if not specialist:
            raise ValueError("Specialist not found")

        portfolio = PortfolioItem(
            specialist_id=specialist_id,
            title=portfolio_data.title,
            description=portfolio_data.description,
            project_type=portfolio_data.project_type,
            industry=portfolio_data.industry,
            completion_date=portfolio_data.completion_date,
            client_name=portfolio_data.client_name,
            images=portfolio_data.images or [],
            documents=portfolio_data.documents or [],
            tags=portfolio_data.tags or []
        )

        db.add(portfolio)

        # Update profile completion
        specialist.profile_completion = self._calculate_profile_completion_model(specialist)

        await db.commit()
        await db.refresh(portfolio)

        logger.info(f"Portfolio item added to specialist {specialist_id}")
        return portfolio

    async def delete_portfolio_item(
        self,
        db: AsyncSession,
        portfolio_id: int,
        specialist_id: int,
        tenant_id: str
    ):
        """Delete portfolio item"""
        specialist = await self.get_specialist(db, specialist_id, tenant_id)
        if not specialist:
            raise ValueError("Specialist not found")

        await db.execute(
            delete(PortfolioItem).where(
                and_(
                    PortfolioItem.id == portfolio_id,
                    PortfolioItem.specialist_id == specialist_id
                )
            )
        )

        # Update profile completion
        specialist.profile_completion = self._calculate_profile_completion_model(specialist)

        await db.commit()
        logger.info(f"Portfolio item {portfolio_id} deleted")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _calculate_profile_completion(self, data: SpecialistCreate) -> int:
        """Calculate profile completion percentage"""
        score = 0

        if data.name:
            score += 10
        if data.title:
            score += 10
        if data.bio and len(data.bio) > 50:
            score += 15
        if data.hourly_rate:
            score += 10
        if data.specializations and len(data.specializations) > 0:
            score += 15
        if data.skills and len(data.skills) > 0:
            score += 10
        if data.country:
            score += 5
        if data.languages and len(data.languages) > 0:
            score += 5
        if data.years_experience:
            score += 10

        # Additional 10% if has certifications (will be added later)
        # Additional 10% if has portfolio (will be added later)

        return min(score, 100)

    def _calculate_profile_completion_model(self, specialist: Specialist) -> int:
        """Calculate profile completion from model"""
        score = 0

        if specialist.name:
            score += 10
        if specialist.title:
            score += 10
        if specialist.bio and len(specialist.bio) > 50:
            score += 15
        if specialist.hourly_rate:
            score += 10
        if specialist.specializations and len(specialist.specializations) > 0:
            score += 15
        if specialist.skills and len(specialist.skills) > 0:
            score += 10
        if specialist.country:
            score += 5
        if specialist.languages and len(specialist.languages) > 0:
            score += 5
        if specialist.years_experience:
            score += 10

        # Bonus for certifications and portfolio
        if len(specialist.certifications) > 0:
            score += 5
        if len(specialist.portfolio_items) > 0:
            score += 5

        return min(score, 100)


# Singleton instance
specialist_service = SpecialistService()
