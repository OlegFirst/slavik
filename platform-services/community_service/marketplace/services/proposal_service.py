"""
Proposal Service - Business Logic
Manages specialist proposals to client projects
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging

from database.models import Proposal, Project, Specialist
from schemas.proposal import ProposalCreate, ProposalUpdate
from shared.eventbus import get_eventbus

logger = logging.getLogger(__name__)


class ProposalService:
    """Service for managing proposals between specialists and clients"""

    # ========================================================================
    # Proposal Management
    # ========================================================================

    async def create_proposal(
        self,
        db: AsyncSession,
        proposal_data: ProposalCreate,
        specialist_id: int,
        tenant_id: str,
        user_id: str
    ) -> Proposal:
        """
        Create new proposal

        Args:
            db: Database session
            proposal_data: Proposal data
            specialist_id: Specialist ID from auth
            tenant_id: Tenant ID from auth
            user_id: User ID for event

        Returns:
            Created proposal

        Business Rules:
            - Can only propose to 'open' projects
            - Specialist must be verified
            - One proposal per specialist per project
            - Proposed budget should be within project budget range
            - Estimated duration should match project timeline
            - Status starts as 'pending'
        """
        # Get project
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == proposal_data.project_id,
                    Project.tenant_id == tenant_id
                )
            )
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError("Project not found")

        if project.status != "open":
            raise ValueError(f"Cannot submit proposal to project with status '{project.status}'")

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

        if not specialist.is_verified:
            raise ValueError("Only verified specialists can submit proposals")

        if not specialist.active:
            raise ValueError("Specialist profile is inactive")

        # Check for existing proposal
        result = await db.execute(
            select(Proposal).where(
                and_(
                    Proposal.project_id == proposal_data.project_id,
                    Proposal.specialist_id == specialist_id
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError("You have already submitted a proposal for this project")

        # Validate budget if project has budget constraints
        if project.budget_max and proposal_data.proposed_budget:
            if proposal_data.proposed_budget > project.budget_max:
                logger.warning(
                    f"Proposed budget {proposal_data.proposed_budget} exceeds project max {project.budget_max}"
                )
                # Don't reject, but log for client visibility

        # Create proposal
        proposal = Proposal(
            project_id=proposal_data.project_id,
            specialist_id=specialist_id,
            tenant_id=tenant_id,
            cover_letter=proposal_data.cover_letter,
            proposed_budget=proposal_data.proposed_budget,
            currency=proposal_data.currency or project.currency,
            estimated_duration_days=proposal_data.estimated_duration_days,
            proposed_start_date=proposal_data.proposed_start_date,
            availability=proposal_data.availability,
            attachments=proposal_data.attachments or [],
            status="pending"
        )

        db.add(proposal)

        # Increment project proposal count
        project.proposal_count += 1

        await db.commit()
        await db.refresh(proposal)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.proposal.submitted",
                {
                    "proposal_id": proposal.id,
                    "project_id": project.id,
                    "specialist_id": specialist_id,
                    "user_id": user_id,
                    "proposed_budget": float(proposal.proposed_budget) if proposal.proposed_budget else 0
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish proposal.submitted event: {e}")

        logger.info(f"Proposal {proposal.id} created for project {project.id}")
        return proposal

    async def get_proposal(
        self,
        db: AsyncSession,
        proposal_id: int,
        tenant_id: str
    ) -> Optional[Proposal]:
        """Get proposal by ID with related data"""
        result = await db.execute(
            select(Proposal)
            .options(
                selectinload(Proposal.project),
                selectinload(Proposal.specialist)
            )
            .where(
                and_(
                    Proposal.id == proposal_id,
                    Proposal.tenant_id == tenant_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_proposal(
        self,
        db: AsyncSession,
        proposal_id: int,
        proposal_data: ProposalUpdate,
        tenant_id: str
    ) -> Proposal:
        """
        Update proposal

        Business Rules:
            - Can only update 'pending' proposals
            - Cannot update 'accepted', 'rejected', or 'withdrawn'
            - Updates increment response_count (if client requested changes)
        """
        proposal = await self.get_proposal(db, proposal_id, tenant_id)
        if not proposal:
            raise ValueError("Proposal not found")

        if proposal.status != "pending":
            raise ValueError(f"Cannot update proposal with status '{proposal.status}'")

        # Update fields
        update_data = proposal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(proposal, field, value)

        proposal.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(proposal)

        logger.info(f"Proposal {proposal.id} updated")
        return proposal

    async def accept_proposal(
        self,
        db: AsyncSession,
        proposal_id: int,
        tenant_id: str,
        client_id: str
    ) -> Proposal:
        """
        Accept proposal (client action)

        Business Rules:
            - Can only accept 'pending' proposals
            - Changes proposal status to 'accepted'
            - Rejects all other proposals for same project
            - Assigns specialist to project (status: open → in_progress)
            - Emits proposal.accepted event
            - Should trigger contract creation (future)

        This is a critical business transaction - should be atomic
        """
        proposal = await self.get_proposal(db, proposal_id, tenant_id)
        if not proposal:
            raise ValueError("Proposal not found")

        if proposal.status != "pending":
            raise ValueError(f"Can only accept 'pending' proposals, current: '{proposal.status}'")

        project = proposal.project
        if project.status != "open":
            raise ValueError(f"Cannot accept proposal for project with status '{project.status}'")

        # Accept this proposal
        proposal.status = "accepted"
        proposal.accepted_at = datetime.utcnow()
        proposal.response_notes = "Accepted by client"
        proposal.updated_at = datetime.utcnow()

        # Reject all other pending proposals for this project
        await db.execute(
            update(Proposal)
            .where(
                and_(
                    Proposal.project_id == project.id,
                    Proposal.id != proposal_id,
                    Proposal.status == "pending"
                )
            )
            .values(
                status="rejected",
                response_notes="Another proposal was accepted",
                updated_at=datetime.utcnow()
            )
        )

        # Assign specialist to project
        project.status = "in_progress"
        project.selected_specialist_id = proposal.specialist_id
        project.selected_proposal_id = proposal.id
        project.started_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(proposal)

        # Publish events
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.proposal.accepted",
                {
                    "proposal_id": proposal.id,
                    "project_id": project.id,
                    "specialist_id": proposal.specialist_id,
                    "client_id": client_id
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish proposal.accepted event: {e}")

        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.project.assigned",
                {
                    "project_id": project.id,
                    "specialist_id": proposal.specialist_id,
                    "client_id": client_id
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish project.assigned event: {e}")

        logger.info(f"Proposal {proposal.id} accepted, project {project.id} assigned to specialist {proposal.specialist_id}")
        return proposal

    async def reject_proposal(
        self,
        db: AsyncSession,
        proposal_id: int,
        tenant_id: str,
        client_id: str,
        reason: Optional[str] = None
    ) -> Proposal:
        """
        Reject proposal (client action)

        Business Rules:
            - Can only reject 'pending' proposals
            - Changes status to 'rejected'
            - Optional reason for rejection (feedback)
            - Emits proposal.rejected event
        """
        proposal = await self.get_proposal(db, proposal_id, tenant_id)
        if not proposal:
            raise ValueError("Proposal not found")

        if proposal.status != "pending":
            raise ValueError(f"Can only reject 'pending' proposals, current: '{proposal.status}'")

        proposal.status = "rejected"
        proposal.response_notes = reason or "Rejected by client"
        proposal.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(proposal)

        # Publish event
        try:
            eventbus = get_eventbus()
            await eventbus.publish(
                "marketplace.proposal.rejected",
                {
                    "proposal_id": proposal.id,
                    "project_id": proposal.project_id,
                    "client_id": client_id,
                    "reason": reason
                },
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to publish proposal.rejected event: {e}")

        logger.info(f"Proposal {proposal.id} rejected: {reason}")
        return proposal

    async def withdraw_proposal(
        self,
        db: AsyncSession,
        proposal_id: int,
        tenant_id: str,
        reason: Optional[str] = None
    ) -> Proposal:
        """
        Withdraw proposal (specialist action)

        Business Rules:
            - Can only withdraw 'pending' proposals
            - Changes status to 'withdrawn'
            - Decrements project proposal_count
        """
        proposal = await self.get_proposal(db, proposal_id, tenant_id)
        if not proposal:
            raise ValueError("Proposal not found")

        if proposal.status != "pending":
            raise ValueError(f"Can only withdraw 'pending' proposals, current: '{proposal.status}'")

        proposal.status = "withdrawn"
        proposal.response_notes = reason or "Withdrawn by specialist"
        proposal.updated_at = datetime.utcnow()

        # Decrement project proposal count
        project = proposal.project
        if project.proposal_count > 0:
            project.proposal_count -= 1

        await db.commit()
        await db.refresh(proposal)

        logger.info(f"Proposal {proposal.id} withdrawn: {reason}")
        return proposal

    # ========================================================================
    # Queries
    # ========================================================================

    async def get_proposals_by_project(
        self,
        db: AsyncSession,
        project_id: int,
        tenant_id: str,
        status: Optional[str] = None
    ) -> List[Proposal]:
        """
        Get all proposals for a project

        Used by:
            - Client to review proposals
            - Project detail page
        """
        query = select(Proposal).options(
            selectinload(Proposal.specialist)
        ).where(
            and_(
                Proposal.project_id == project_id,
                Proposal.tenant_id == tenant_id
            )
        )

        if status:
            query = query.where(Proposal.status == status)

        # Sort by created_at DESC (newest first)
        query = query.order_by(Proposal.created_at.desc())

        result = await db.execute(query)
        return result.scalars().all()

    async def get_proposals_by_specialist(
        self,
        db: AsyncSession,
        specialist_id: int,
        tenant_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Proposal]:
        """
        Get all proposals by a specialist

        Used by:
            - Specialist dashboard
            - My proposals page
        """
        query = select(Proposal).options(
            selectinload(Proposal.project)
        ).where(
            and_(
                Proposal.specialist_id == specialist_id,
                Proposal.tenant_id == tenant_id
            )
        )

        if status:
            query = query.where(Proposal.status == status)

        query = query.order_by(Proposal.created_at.desc()).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_pending_proposals_by_specialist(
        self,
        db: AsyncSession,
        specialist_id: int,
        tenant_id: str
    ) -> List[Proposal]:
        """Get all pending proposals for specialist"""
        return await self.get_proposals_by_specialist(
            db, specialist_id, tenant_id, status="pending"
        )

    # ========================================================================
    # Statistics
    # ========================================================================

    async def get_proposal_stats(
        self,
        db: AsyncSession,
        specialist_id: int,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get proposal statistics for a specialist"""
        # Count by status
        result = await db.execute(
            select(
                Proposal.status,
                func.count(Proposal.id).label("count")
            )
            .where(
                and_(
                    Proposal.specialist_id == specialist_id,
                    Proposal.tenant_id == tenant_id
                )
            )
            .group_by(Proposal.status)
        )
        status_counts = {row.status: row.count for row in result}

        total_proposals = sum(status_counts.values())
        accepted = status_counts.get("accepted", 0)
        rejected = status_counts.get("rejected", 0)
        pending = status_counts.get("pending", 0)
        withdrawn = status_counts.get("withdrawn", 0)

        # Calculate acceptance rate
        acceptance_rate = 0
        if (accepted + rejected) > 0:
            acceptance_rate = (accepted / (accepted + rejected)) * 100

        return {
            "total_proposals": total_proposals,
            "by_status": status_counts,
            "acceptance_rate": round(acceptance_rate, 2),
            "pending": pending,
            "accepted": accepted,
            "rejected": rejected,
            "withdrawn": withdrawn
        }

    async def calculate_specialist_metrics(
        self,
        db: AsyncSession,
        specialist_id: int,
        tenant_id: str
    ):
        """
        Calculate and update specialist metrics based on proposals

        Updates:
            - acceptance_rate
            - completed_projects (from accepted proposals with completed projects)

        Called periodically or after proposal status changes
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
            return

        # Get stats
        stats = await self.get_proposal_stats(db, specialist_id, tenant_id)

        # Update acceptance rate
        specialist.acceptance_rate = stats["acceptance_rate"]

        # Count completed projects
        result = await db.execute(
            select(func.count(Proposal.id))
            .join(Project)
            .where(
                and_(
                    Proposal.specialist_id == specialist_id,
                    Proposal.status == "accepted",
                    Project.status == "completed"
                )
            )
        )
        completed = result.scalar()
        specialist.completed_projects = completed

        await db.commit()
        logger.info(f"Updated metrics for specialist {specialist_id}: acceptance_rate={stats['acceptance_rate']}%, completed={completed}")


# Singleton instance
proposal_service = ProposalService()
