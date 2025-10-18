"""
Project Service - Business Logic
Manages client projects/requests and matching with specialists
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging

from database.models import Project, Proposal, Specialist
from schemas.project import ProjectCreate, ProjectUpdate, ProjectSearchFilters
from shared.eventbus import get_eventbus
from integrations.portal_client import portal_client

logger = logging.getLogger(__name__)


class ProjectService:
    """Service for managing client projects and requests"""

    # ========================================================================
    # Project Management
    # ========================================================================

    async def create_project(
        self,
        db: AsyncSession,
        project_data: ProjectCreate,
        client_id: str,
        tenant_id: str
    ) -> Project:
        """
        Create new project/request

        Args:
            db: Database session
            project_data: Project data
            client_id: Client user ID from auth
            tenant_id: Tenant ID from auth

        Returns:
            Created project

        Business Rules:
            - Status starts as 'draft'
            - Client can publish when ready
            - required_skills should be validated
            - budget_min <= budget_max
            - start_date < end_date if both provided
        """
        # Validate budget range
        if project_data.budget_min and project_data.budget_max:
            if project_data.budget_min > project_data.budget_max:
                raise ValueError("budget_min cannot be greater than budget_max")

        # Validate dates
        if project_data.start_date and project_data.end_date:
            if project_data.start_date > project_data.end_date:
                raise ValueError("start_date cannot be after end_date")

        # Create project
        project = Project(
            client_id=client_id,
            tenant_id=tenant_id,
            title=project_data.title,
            description=project_data.description,
            service_type=project_data.service_type,
            urgency=project_data.urgency or "medium",
            required_skills=project_data.required_skills or [],
            budget_type=project_data.budget_type,
            budget_min=project_data.budget_min,
            budget_max=project_data.budget_max,
            currency=project_data.currency or "USD",
            work_location=project_data.work_location or "remote",
            country=project_data.country,
            city=project_data.city,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            expected_duration_days=project_data.expected_duration_days,
            status="draft",
            view_count=0,
            proposal_count=0
        )

        db.add(project)
        await db.commit()
        await db.refresh(project)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.project.created",
                {
                    "project_id": project.id,
                    "client_id": client_id,
                    "title": project.title,
                    "service_type": project.service_type,
                    "budget_range": {
                        "min": float(project.budget_min) if project.budget_min else None,
                        "max": float(project.budget_max) if project.budget_max else None,
                        "currency": project.currency
                    }
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish project.created event: {e}")

        logger.info(f"Project created: {project.id}")
        return project

    async def get_project(
        self,
        db: AsyncSession,
        project_id: int,
        tenant_id: str,
        increment_view: bool = False
    ) -> Optional[Project]:
        """
        Get project by ID

        Args:
            db: Database session
            project_id: Project ID
            tenant_id: Tenant ID
            increment_view: Whether to increment view count

        Returns:
            Project or None
        """
        result = await db.execute(
            select(Project)
            .options(selectinload(Project.proposals))
            .where(
                and_(
                    Project.id == project_id,
                    Project.tenant_id == tenant_id
                )
            )
        )
        project = result.scalar_one_or_none()

        # Increment view count if requested
        if project and increment_view:
            project.view_count += 1
            await db.commit()

        return project

    async def update_project(
        self,
        db: AsyncSession,
        project_id: int,
        project_data: ProjectUpdate,
        tenant_id: str
    ) -> Project:
        """
        Update project

        Business Rules:
            - Can only update if status is 'draft' or 'open'
            - Cannot update if status is 'in_progress', 'completed', or 'cancelled'
            - If changing to 'open', call publish_project instead
        """
        project = await self.get_project(db, project_id, tenant_id)
        if not project:
            raise ValueError("Project not found")

        # Check if can be updated
        if project.status not in ["draft", "open"]:
            raise ValueError(f"Cannot update project with status '{project.status}'")

        # Update fields
        update_data = project_data.model_dump(exclude_unset=True)

        # Validate budget if being updated
        if "budget_min" in update_data or "budget_max" in update_data:
            budget_min = update_data.get("budget_min", project.budget_min)
            budget_max = update_data.get("budget_max", project.budget_max)
            if budget_min and budget_max and budget_min > budget_max:
                raise ValueError("budget_min cannot be greater than budget_max")

        # Validate dates if being updated
        if "start_date" in update_data or "end_date" in update_data:
            start_date = update_data.get("start_date", project.start_date)
            end_date = update_data.get("end_date", project.end_date)
            if start_date and end_date and start_date > end_date:
                raise ValueError("start_date cannot be after end_date")

        for field, value in update_data.items():
            setattr(project, field, value)

        project.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(project)

        logger.info(f"Project {project.id} updated")
        return project

    async def publish_project(
        self,
        db: AsyncSession,
        project_id: int,
        tenant_id: str,
        client_id: str
    ) -> Project:
        """
        Publish project (change status from 'draft' to 'open')

        Business Rules:
            - Can only publish from 'draft' status
            - Sets published_at timestamp
            - Emits project.published event
            - Triggers specialist matching (future)
        """
        project = await self.get_project(db, project_id, tenant_id)
        if not project:
            raise ValueError("Project not found")

        if project.status != "draft":
            raise ValueError(f"Can only publish projects with 'draft' status, current: '{project.status}'")

        # Validate project is complete enough to publish
        if not project.title or len(project.title) < 10:
            raise ValueError("Title must be at least 10 characters")
        if not project.description or len(project.description) < 50:
            raise ValueError("Description must be at least 50 characters")
        if not project.required_skills or len(project.required_skills) == 0:
            raise ValueError("At least one required skill must be specified")

        project.status = "open"
        project.published_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(project)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.project.published",
                {
                    "project_id": project.id,
                    "client_id": client_id,
                    "title": project.title
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish project.published event: {e}")

        # Get relevant Portal scenarios for this project type
        try:
            scenarios = await portal_client.search_scenarios(
                service_type=project.service_type,
                limit=3
            )
            logger.info(f"Found {len(scenarios)} relevant scenarios for project {project.id}")
        except Exception as e:
            logger.warning(f"Could not fetch scenarios: {e}")

        logger.info(f"Project {project.id} published")
        return project

    async def assign_specialist(
        self,
        db: AsyncSession,
        project_id: int,
        specialist_id: int,
        proposal_id: int,
        tenant_id: str,
        client_id: str
    ) -> Project:
        """
        Assign specialist to project

        Business Rules:
            - Can only assign to 'open' projects
            - Changes status to 'in_progress'
            - Sets selected_specialist_id and selected_proposal_id
            - Sets started_at timestamp
            - Emits project.assigned event
            - Usually called from proposal.accept()
        """
        project = await self.get_project(db, project_id, tenant_id)
        if not project:
            raise ValueError("Project not found")

        if project.status != "open":
            raise ValueError(f"Can only assign specialist to 'open' projects, current: '{project.status}'")

        project.status = "in_progress"
        project.selected_specialist_id = specialist_id
        project.selected_proposal_id = proposal_id
        project.started_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(project)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.project.assigned",
                {
                    "project_id": project.id,
                    "specialist_id": specialist_id,
                    "client_id": client_id
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish project.assigned event: {e}")

        logger.info(f"Project {project.id} assigned to specialist {specialist_id}")
        return project

    async def complete_project(
        self,
        db: AsyncSession,
        project_id: int,
        tenant_id: str,
        client_id: str
    ) -> Project:
        """
        Mark project as completed

        Business Rules:
            - Can only complete 'in_progress' projects
            - Sets completed_at timestamp
            - Changes status to 'completed'
            - Emits project.completed event
            - Should trigger review request (future)
        """
        project = await self.get_project(db, project_id, tenant_id)
        if not project:
            raise ValueError("Project not found")

        if project.status != "in_progress":
            raise ValueError(f"Can only complete 'in_progress' projects, current: '{project.status}'")

        if not project.selected_specialist_id:
            raise ValueError("Project has no assigned specialist")

        project.status = "completed"
        project.completed_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(project)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.project.completed",
                {
                    "project_id": project.id,
                    "specialist_id": project.selected_specialist_id,
                    "client_id": client_id
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish project.completed event: {e}")

        logger.info(f"Project {project.id} marked as completed")
        return project

    async def cancel_project(
        self,
        db: AsyncSession,
        project_id: int,
        tenant_id: str,
        reason: Optional[str] = None
    ) -> Project:
        """
        Cancel project

        Business Rules:
            - Can cancel from 'draft', 'open', or 'in_progress'
            - Cannot cancel 'completed' or already 'cancelled'
            - If cancelled while in_progress, may need refund logic (future)
        """
        project = await self.get_project(db, project_id, tenant_id)
        if not project:
            raise ValueError("Project not found")

        if project.status in ["completed", "cancelled"]:
            raise ValueError(f"Cannot cancel project with status '{project.status}'")

        project.status = "cancelled"
        project.updated_at = datetime.utcnow()
        # Could store cancellation reason in metadata or new field

        await db.commit()
        await db.refresh(project)

        logger.info(f"Project {project.id} cancelled: {reason}")
        return project

    # ========================================================================
    # Search & Filtering
    # ========================================================================

    async def search_projects(
        self,
        db: AsyncSession,
        filters: ProjectSearchFilters,
        tenant_id: str
    ) -> List[Project]:
        """
        Search projects with filters

        Filters:
            - service_type
            - status
            - urgency
            - budget_min, budget_max
            - required_skills (JSONB array overlap)
            - work_location
            - country, city
            - search query (title, description)

        Returns:
            List of projects sorted by published_at DESC
        """
        query = select(Project).where(Project.tenant_id == tenant_id)

        # Service type
        if filters.service_type:
            query = query.where(Project.service_type == filters.service_type)

        # Status
        if filters.status:
            query = query.where(Project.status == filters.status)
        else:
            # Default: only show 'open' projects
            query = query.where(Project.status == "open")

        # Urgency
        if filters.urgency:
            query = query.where(Project.urgency == filters.urgency)

        # Budget
        if filters.budget_min:
            query = query.where(Project.budget_max >= filters.budget_min)
        if filters.budget_max:
            query = query.where(Project.budget_min <= filters.budget_max)

        # Required skills (JSONB overlap)
        if filters.required_skills:
            query = query.where(
                Project.required_skills.op('?|')(filters.required_skills)
            )

        # Work location
        if filters.work_location:
            query = query.where(Project.work_location == filters.work_location)

        # Location
        if filters.country:
            query = query.where(Project.country == filters.country)
        if filters.city:
            query = query.where(Project.city == filters.city)

        # Text search
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.where(
                or_(
                    Project.title.ilike(search_pattern),
                    Project.description.ilike(search_pattern)
                )
            )

        # Sort by published_at DESC (newest first)
        query = query.order_by(Project.published_at.desc().nulls_last())

        # Pagination
        if filters.offset:
            query = query.offset(filters.offset)
        if filters.limit:
            query = query.limit(filters.limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_projects_by_client(
        self,
        db: AsyncSession,
        client_id: str,
        tenant_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Project]:
        """Get all projects for a specific client"""
        query = select(Project).where(
            and_(
                Project.client_id == client_id,
                Project.tenant_id == tenant_id
            )
        )

        if status:
            query = query.where(Project.status == status)

        query = query.order_by(Project.created_at.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_projects_for_specialist(
        self,
        db: AsyncSession,
        specialist_id: int,
        tenant_id: str,
        limit: int = 20
    ) -> List[Project]:
        """
        Get projects matching specialist's skills

        Business Logic:
            - Match specialist.skills with project.required_skills
            - Only show 'open' projects
            - Sort by match quality and urgency
        """
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
            raise ValueError("Specialist not found")

        # Find matching projects
        query = select(Project).where(
            and_(
                Project.tenant_id == tenant_id,
                Project.status == "open"
            )
        )

        # Filter by skills overlap
        if specialist.skills and len(specialist.skills) > 0:
            query = query.where(
                Project.required_skills.op('?|')(specialist.skills)
            )

        # Sort by urgency (high first) then published_at
        query = query.order_by(
            Project.urgency.desc(),
            Project.published_at.desc()
        ).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    # ========================================================================
    # Statistics
    # ========================================================================

    async def get_project_stats(
        self,
        db: AsyncSession,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get overall project statistics for tenant"""
        # Total projects by status
        result = await db.execute(
            select(
                Project.status,
                func.count(Project.id).label("count")
            )
            .where(Project.tenant_id == tenant_id)
            .group_by(Project.status)
        )
        status_counts = {row.status: row.count for row in result}

        # Average budget
        result = await db.execute(
            select(
                func.avg(Project.budget_min).label("avg_min"),
                func.avg(Project.budget_max).label("avg_max")
            )
            .where(Project.tenant_id == tenant_id)
        )
        budget_avg = result.first()

        return {
            "total_projects": sum(status_counts.values()),
            "by_status": status_counts,
            "average_budget": {
                "min": float(budget_avg.avg_min) if budget_avg.avg_min else 0,
                "max": float(budget_avg.avg_max) if budget_avg.avg_max else 0
            }
        }


# Singleton instance
project_service = ProjectService()
