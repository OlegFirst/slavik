"""
Scenario Service - Business Logic
Handles scenario marketplace operations and deployments
"""

from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Scenario, ScenarioReview
from integrations.validation_client import ValidationClient


class ScenarioService:
    """
    Scenario Marketplace business logic

    Responsibilities:
    - Scenario catalog browsing
    - Scenario deployment to exercises
    - Review and rating management
    """

    async def get_scenarios(
        self,
        db: AsyncSession,
        scenario_type: Optional[str] = None,
        industry: Optional[str] = None,
        threat_type: Optional[str] = None,
        published_only: bool = True,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Scenario], int]:
        """
        Get scenarios with filtering and pagination

        Args:
            db: Database session
            scenario_type: Filter by type
            industry: Filter by industry
            threat_type: Filter by threat type
            published_only: Only published scenarios
            page: Page number
            page_size: Results per page

        Returns:
            Tuple of (scenarios list, total count)
        """
        # Build query
        stmt = select(Scenario)

        # Apply filters
        filters = []

        if published_only:
            filters.append(Scenario.published == True)

        if scenario_type:
            filters.append(Scenario.scenario_type == scenario_type)

        if industry:
            filters.append(Scenario.industry == industry)

        if threat_type:
            filters.append(Scenario.threat_type == threat_type)

        if filters:
            stmt = stmt.where(and_(*filters))

        # Order by rating and deployment count
        stmt = stmt.order_by(
            Scenario.average_rating.desc(),
            Scenario.deployment_count.desc()
        )

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        # Execute
        result = await db.execute(stmt)
        scenarios = result.scalars().all()

        return scenarios, total

    async def get_scenario(
        self,
        db: AsyncSession,
        scenario_id: int
    ) -> Optional[Scenario]:
        """
        Get scenario by ID and increment view count

        Args:
            db: Database session
            scenario_id: Scenario ID

        Returns:
            Scenario or None if not found
        """
        result = await db.execute(
            select(Scenario).where(Scenario.id == scenario_id)
        )
        scenario = result.scalar_one_or_none()

        if scenario:
            # Increment view count
            await db.execute(
                update(Scenario)
                .where(Scenario.id == scenario_id)
                .values(view_count=Scenario.view_count + 1)
            )
            await db.commit()
            await db.refresh(scenario)

        return scenario

    async def deploy_scenario(
        self,
        db: AsyncSession,
        scenario_id: int,
        tenant_id: str,
        token: str,
        validation_client: ValidationClient,
        exercise_name_override: Optional[str] = None
    ) -> dict:
        """
        Deploy scenario as an exercise in Validation module

        Args:
            db: Database session
            scenario_id: Scenario ID
            tenant_id: Target tenant ID
            token: JWT token
            validation_client: Validation service client
            exercise_name_override: Override exercise name

        Returns:
            dict with exercise_id, exercise_code, etc.

        Raises:
            ValueError if scenario not found
        """
        # Get scenario
        scenario = await self.get_scenario(db, scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        # Prepare scenario data for deployment
        scenario_data = {
            'scenario_code': scenario.scenario_code,
            'scenario_name': exercise_name_override or scenario.scenario_name,
            'scenario_type': scenario.scenario_type,
            'full_scenario': scenario.full_scenario,
            'injects': scenario.injects,
            'learning_objectives': scenario.learning_objectives,
            'duration_minutes': scenario.duration_minutes,
        }

        # Deploy to Validation module
        exercise = await validation_client.deploy_scenario(
            scenario_id=scenario_id,
            scenario_data=scenario_data,
            tenant_id=tenant_id,
            token=token
        )

        # Increment deployment count
        await db.execute(
            update(Scenario)
            .where(Scenario.id == scenario_id)
            .values(deployment_count=Scenario.deployment_count + 1)
        )
        await db.commit()

        return exercise

    async def create_review(
        self,
        db: AsyncSession,
        scenario_id: int,
        user_id: str,
        tenant_id: str,
        rating: int,
        review_text: Optional[str] = None,
        exercise_id: Optional[int] = None
    ) -> ScenarioReview:
        """
        Create or update a scenario review

        Args:
            db: Database session
            scenario_id: Scenario ID
            user_id: User ID
            tenant_id: Tenant ID
            rating: Rating (1-5)
            review_text: Optional review text
            exercise_id: Optional exercise where scenario was used

        Returns:
            Created/updated ScenarioReview
        """
        # Check if review exists
        result = await db.execute(
            select(ScenarioReview).where(
                and_(
                    ScenarioReview.scenario_id == scenario_id,
                    ScenarioReview.user_id == user_id,
                    ScenarioReview.tenant_id == tenant_id
                )
            )
        )
        existing_review = result.scalar_one_or_none()

        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.review_text = review_text
            existing_review.exercise_id = exercise_id
            await db.commit()
            await db.refresh(existing_review)
            return existing_review
        else:
            # Create new review
            review = ScenarioReview(
                scenario_id=scenario_id,
                user_id=user_id,
                tenant_id=tenant_id,
                rating=rating,
                review_text=review_text,
                exercise_id=exercise_id
            )
            db.add(review)
            await db.commit()
            await db.refresh(review)
            return review

    async def get_scenario_reviews(
        self,
        db: AsyncSession,
        scenario_id: int,
        limit: int = 20
    ) -> List[ScenarioReview]:
        """
        Get reviews for a scenario

        Args:
            db: Database session
            scenario_id: Scenario ID
            limit: Maximum results

        Returns:
            List of reviews
        """
        result = await db.execute(
            select(ScenarioReview)
            .where(ScenarioReview.scenario_id == scenario_id)
            .order_by(ScenarioReview.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_popular_scenarios(
        self,
        db: AsyncSession,
        limit: int = 10
    ) -> List[Scenario]:
        """
        Get most popular scenarios by deployment count and rating

        Args:
            db: Database session
            limit: Maximum results

        Returns:
            List of popular scenarios
        """
        result = await db.execute(
            select(Scenario)
            .where(Scenario.published == True)
            .order_by(
                Scenario.deployment_count.desc(),
                Scenario.average_rating.desc()
            )
            .limit(limit)
        )
        return result.scalars().all()
