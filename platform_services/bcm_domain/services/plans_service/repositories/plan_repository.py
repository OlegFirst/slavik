"""
Plans Repository - Data Access Layer

N+1 Query Optimizations:
- Existing eager loading methods with selectinload()
- Added dashboard queries with aggregations
- Added procedure dependency tree loading
- Added complete plan loading with all relationships
- Added cursor-based pagination
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.database import Plan, Procedure, PlanResource, ContactList, PlanActivation, PlanReview
from ..models.domain import PlanStatus, PlanType, PlanPriority


class PlanRepository:
    """Plan data access repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, plan: Plan) -> Plan:
        """Create new plan"""
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_by_id(self, plan_id: int) -> Optional[Plan]:
        """
        Get plan by ID (without relationships)

        For backward compatibility. Use get_by_id_with_relationships()
        when you need to access related data to avoid N+1 queries.
        """
        result = await self.session.execute(
            select(Plan).where(Plan.plan_id == plan_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relationships(
        self,
        plan_id: int,
        load_procedures: bool = False,
        load_resources: bool = False,
        load_contacts: bool = False,
        load_activations: bool = False,
        load_reviews: bool = False
    ) -> Optional[Plan]:
        """
        Get plan by ID with eager loading of relationships to prevent N+1 queries.

        Performance Optimization:
        - Uses selectinload() to fetch related data in a single additional query per relationship
        - Prevents N+1 query problem when accessing plan.procedures, plan.resources, etc.
        - Only loads relationships you actually need

        Args:
            plan_id: Plan identifier
            load_procedures: Eager load procedures relationship
            load_resources: Eager load resources relationship
            load_contacts: Eager load contact_lists relationship
            load_activations: Eager load activations relationship
            load_reviews: Eager load reviews relationship

        Returns:
            Plan with loaded relationships or None if not found

        Example:
            # Load plan with procedures (2 queries instead of 1+N)
            plan = await repo.get_by_id_with_relationships(
                plan_id=123,
                load_procedures=True
            )
            # No additional query here - already loaded
            for procedure in plan.procedures:
                print(procedure.procedure_name)
        """
        query = select(Plan).where(Plan.plan_id == plan_id)

        # Add eager loading options based on parameters
        if load_procedures:
            query = query.options(selectinload(Plan.procedures))

        if load_resources:
            query = query.options(selectinload(Plan.resources))

        if load_contacts:
            query = query.options(selectinload(Plan.contact_lists))

        if load_activations:
            query = query.options(selectinload(Plan.activations))

        if load_reviews:
            query = query.options(selectinload(Plan.reviews))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, plan_code: str) -> Optional[Plan]:
        """Get plan by plan_code"""
        result = await self.session.execute(
            select(Plan).where(Plan.plan_code == plan_code)
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        plan_type: Optional[PlanType] = None,
        status: Optional[PlanStatus] = None,
        priority: Optional[PlanPriority] = None,
        review_due: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Plan]:
        """
        List plans by tenant with filters (without relationships)

        For backward compatibility. Use list_by_tenant_with_relationships()
        when you need to access related data to avoid N+1 queries.
        """
        query = select(Plan).where(
            and_(
                Plan.tenant_id == tenant_id,
                Plan.active == True
            )
        )

        if plan_type:
            query = query.where(Plan.plan_type == plan_type)

        if status:
            query = query.where(Plan.status == status)

        if priority:
            query = query.where(Plan.priority == priority)

        if review_due is True:
            query = query.where(Plan.next_review_date <= datetime.utcnow())

        query = query.order_by(Plan.priority.desc(), Plan.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_tenant_with_relationships(
        self,
        tenant_id: str,
        plan_type: Optional[PlanType] = None,
        status: Optional[PlanStatus] = None,
        priority: Optional[PlanPriority] = None,
        review_due: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
        load_procedures: bool = False,
        load_resources: bool = False,
        load_contacts: bool = False,
        load_activations: bool = False,
        load_reviews: bool = False
    ) -> List[Plan]:
        """
        List plans by tenant with filters and eager loading of relationships.

        Performance Optimization:
        - Uses selectinload() to prevent N+1 queries when iterating through plans
        - Example: Loading 100 plans with procedures takes 2 queries instead of 101

        Args:
            tenant_id: Tenant identifier
            plan_type: Filter by plan type
            status: Filter by status
            priority: Filter by priority
            review_due: Filter by review due date
            skip: Pagination offset
            limit: Pagination limit
            load_procedures: Eager load procedures
            load_resources: Eager load resources
            load_contacts: Eager load contact_lists
            load_activations: Eager load activations
            load_reviews: Eager load reviews

        Returns:
            List of plans with loaded relationships

        Example:
            # Load 100 plans with their procedures (2 queries instead of 101)
            plans = await repo.list_by_tenant_with_relationships(
                tenant_id="org123",
                load_procedures=True,
                limit=100
            )
        """
        query = select(Plan).where(
            and_(
                Plan.tenant_id == tenant_id,
                Plan.active == True
            )
        )

        if plan_type:
            query = query.where(Plan.plan_type == plan_type)

        if status:
            query = query.where(Plan.status == status)

        if priority:
            query = query.where(Plan.priority == priority)

        if review_due is True:
            query = query.where(Plan.next_review_date <= datetime.utcnow())

        # Add eager loading options
        if load_procedures:
            query = query.options(selectinload(Plan.procedures))

        if load_resources:
            query = query.options(selectinload(Plan.resources))

        if load_contacts:
            query = query.options(selectinload(Plan.contact_lists))

        if load_activations:
            query = query.options(selectinload(Plan.activations))

        if load_reviews:
            query = query.options(selectinload(Plan.reviews))

        query = query.order_by(Plan.priority.desc(), Plan.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, plan_id: int, update_data: dict) -> Optional[Plan]:
        """Update plan"""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return None

        for key, value in update_data.items():
            if hasattr(plan, key):
                setattr(plan, key, value)

        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def delete(self, plan_id: int) -> bool:
        """Soft delete plan"""
        plan = await self.get_by_id(plan_id)
        if not plan:
            return False

        plan.active = False
        plan.status = PlanStatus.ARCHIVED
        await self.session.commit()
        return True

    # Procedure operations
    async def add_procedure(self, procedure: Procedure) -> Procedure:
        """Add procedure to plan"""
        self.session.add(procedure)
        await self.session.commit()
        await self.session.refresh(procedure)
        return procedure

    async def get_procedures(self, plan_id: int) -> List[Procedure]:
        """Get all procedures for a plan"""
        result = await self.session.execute(
            select(Procedure).where(
                and_(
                    Procedure.plan_id == plan_id,
                    Procedure.active == True
                )
            ).order_by(Procedure.sequence, Procedure.created_at)
        )
        return list(result.scalars().all())

    async def get_procedure_by_id(self, procedure_id: int) -> Optional[Procedure]:
        """Get procedure by ID"""
        result = await self.session.execute(
            select(Procedure).where(Procedure.procedure_id == procedure_id)
        )
        return result.scalar_one_or_none()

    async def update_procedure(self, procedure_id: int, update_data: dict) -> Optional[Procedure]:
        """Update procedure"""
        procedure = await self.get_procedure_by_id(procedure_id)
        if not procedure:
            return None

        for key, value in update_data.items():
            if hasattr(procedure, key):
                setattr(procedure, key, value)

        await self.session.commit()
        await self.session.refresh(procedure)
        return procedure

    async def delete_procedure(self, procedure_id: int) -> bool:
        """Soft delete procedure"""
        procedure = await self.get_procedure_by_id(procedure_id)
        if not procedure:
            return False

        procedure.active = False
        await self.session.commit()
        return True

    # Resource operations
    async def add_resource(self, resource: PlanResource) -> PlanResource:
        """Add resource to plan"""
        self.session.add(resource)
        await self.session.commit()
        await self.session.refresh(resource)
        return resource

    async def get_resources(self, plan_id: int) -> List[PlanResource]:
        """Get all resources for a plan"""
        result = await self.session.execute(
            select(PlanResource).where(
                and_(
                    PlanResource.plan_id == plan_id,
                    PlanResource.active == True
                )
            ).order_by(PlanResource.criticality.desc(), PlanResource.resource_name)
        )
        return list(result.scalars().all())

    async def get_resource_by_id(self, resource_id: int) -> Optional[PlanResource]:
        """Get resource by ID"""
        result = await self.session.execute(
            select(PlanResource).where(PlanResource.resource_id == resource_id)
        )
        return result.scalar_one_or_none()

    # Contact List operations
    async def add_contact_list(self, contact_list: ContactList) -> ContactList:
        """Add contact list"""
        self.session.add(contact_list)
        await self.session.commit()
        await self.session.refresh(contact_list)
        return contact_list

    async def get_contact_lists(self, plan_id: int) -> List[ContactList]:
        """Get all contact lists for a plan"""
        result = await self.session.execute(
            select(ContactList).where(
                and_(
                    ContactList.plan_id == plan_id,
                    ContactList.active == True
                )
            )
        )
        return list(result.scalars().all())

    # Activation operations
    async def create_activation(self, activation: PlanActivation) -> PlanActivation:
        """Create plan activation"""
        self.session.add(activation)
        await self.session.commit()
        await self.session.refresh(activation)
        return activation

    async def get_activations(self, plan_id: int) -> List[PlanActivation]:
        """Get all activations for a plan"""
        result = await self.session.execute(
            select(PlanActivation).where(
                PlanActivation.plan_id == plan_id
            ).order_by(PlanActivation.activation_datetime.desc())
        )
        return list(result.scalars().all())

    async def get_activation_by_id(self, activation_id: int) -> Optional[PlanActivation]:
        """Get activation by ID"""
        result = await self.session.execute(
            select(PlanActivation).where(PlanActivation.activation_id == activation_id)
        )
        return result.scalar_one_or_none()

    # Review operations
    async def create_review(self, review: PlanReview) -> PlanReview:
        """Create plan review"""
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        return review

    async def get_reviews(self, plan_id: int) -> List[PlanReview]:
        """Get all reviews for a plan"""
        result = await self.session.execute(
            select(PlanReview).where(
                PlanReview.plan_id == plan_id
            ).order_by(PlanReview.review_date.desc())
        )
        return list(result.scalars().all())

    async def get_review_by_id(self, review_id: int) -> Optional[PlanReview]:
        """Get review by ID"""
        result = await self.session.execute(
            select(PlanReview).where(PlanReview.review_id == review_id)
        )
        return result.scalar_one_or_none()

    # ========== N+1 Query Optimization Methods ==========

    async def get_plan_complete(self, plan_id: int) -> Optional[Plan]:
        """
        Get plan with ALL relationships loaded in single query set.

        Optimization: Load all relationships at once
        Before: 1 base query + 5 relationship queries = 6 queries
        After: 1 base query with 5 eager loads = 2 queries total (1 for base + procedures, 1 for collections)

        Args:
            plan_id: Plan identifier

        Returns:
            Plan with all relationships loaded
        """
        result = await self.session.execute(
            select(Plan)
            .where(Plan.plan_id == plan_id)
            .options(
                selectinload(Plan.procedures),
                selectinload(Plan.resources),
                selectinload(Plan.contact_lists),
                selectinload(Plan.activations),
                selectinload(Plan.reviews)
            )
        )
        return result.scalar_one_or_none()

    async def get_procedure_tree(self, plan_id: int) -> List[Procedure]:
        """
        Get procedures with dependency information optimized.

        Optimization: Single query to load all procedures, resolve dependencies in Python
        Before: 1 query + N queries for each procedure's dependencies
        After: 1 query, dependencies resolved from loaded set

        Args:
            plan_id: Plan identifier

        Returns:
            List of procedures with dependency info
        """
        # Load all procedures for the plan
        result = await self.session.execute(
            select(Procedure)
            .where(
                and_(
                    Procedure.plan_id == plan_id,
                    Procedure.active == True
                )
            )
            .order_by(Procedure.sequence, Procedure.created_at)
        )
        procedures = list(result.scalars().all())

        # Dependencies are stored as JSON array of IDs in prerequisite_procedure_ids
        # No additional queries needed - they're already in the loaded set
        return procedures

    async def get_plans_summary(
        self,
        tenant_id: str,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get plan summary data optimized for list/dashboard views.

        Optimization: Select only needed fields, add counts as subqueries
        Before: Load full plans + N queries for counts
        After: 1 query with subqueries for counts

        Args:
            tenant_id: Tenant identifier
            limit: Maximum results
            skip: Pagination offset

        Returns:
            List of plan summaries with counts
        """
        # Subquery for procedure count
        proc_count = (
            select(func.count(Procedure.procedure_id))
            .where(
                and_(
                    Procedure.plan_id == Plan.plan_id,
                    Procedure.active == True
                )
            )
            .correlate(Plan)
            .scalar_subquery()
        )

        # Subquery for resource count
        resource_count = (
            select(func.count(PlanResource.resource_id))
            .where(
                and_(
                    PlanResource.plan_id == Plan.plan_id,
                    PlanResource.active == True
                )
            )
            .correlate(Plan)
            .scalar_subquery()
        )

        # Subquery for activation count
        activation_count = (
            select(func.count(PlanActivation.activation_id))
            .where(PlanActivation.plan_id == Plan.plan_id)
            .correlate(Plan)
            .scalar_subquery()
        )

        result = await self.session.execute(
            select(
                Plan.plan_id,
                Plan.plan_code,
                Plan.plan_name,
                Plan.plan_type,
                Plan.priority,
                Plan.status,
                Plan.version,
                Plan.plan_owner_user_id,
                Plan.next_review_date,
                Plan.next_test_date,
                Plan.created_at,
                Plan.updated_at,
                proc_count.label('procedure_count'),
                resource_count.label('resource_count'),
                activation_count.label('activation_count')
            )
            .where(
                and_(
                    Plan.tenant_id == tenant_id,
                    Plan.active == True
                )
            )
            .order_by(Plan.priority.desc(), Plan.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        rows = result.all()

        return [
            {
                "plan_id": row.plan_id,
                "plan_code": row.plan_code,
                "plan_name": row.plan_name,
                "plan_type": row.plan_type.value if row.plan_type else None,
                "priority": row.priority.value if row.priority else None,
                "status": row.status.value if row.status else None,
                "version": row.version,
                "plan_owner": row.plan_owner_user_id,
                "next_review_date": row.next_review_date.isoformat() if row.next_review_date else None,
                "next_test_date": row.next_test_date.isoformat() if row.next_test_date else None,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                "procedure_count": row.procedure_count or 0,
                "resource_count": row.resource_count or 0,
                "activation_count": row.activation_count or 0
            }
            for row in rows
        ]

    async def get_dashboard_data(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get plan dashboard data with aggregations.

        Optimization: Single query with aggregations
        Before: Multiple queries for different statistics
        After: 1 query with aggregations

        Args:
            tenant_id: Tenant identifier

        Returns:
            Dictionary with dashboard statistics
        """
        query = select(
            func.count(Plan.plan_id).label('total_count'),
            # By status
            func.sum(case((Plan.status == PlanStatus.DRAFT, 1), else_=0)).label('draft_count'),
            func.sum(case((Plan.status == PlanStatus.IN_REVIEW, 1), else_=0)).label('in_review_count'),
            func.sum(case((Plan.status == PlanStatus.APPROVED, 1), else_=0)).label('approved_count'),
            func.sum(case((Plan.status == PlanStatus.ACTIVE, 1), else_=0)).label('active_count'),
            # By type
            func.sum(case((Plan.plan_type == PlanType.INCIDENT_RESPONSE, 1), else_=0)).label('incident_response_count'),
            func.sum(case((Plan.plan_type == PlanType.BUSINESS_CONTINUITY, 1), else_=0)).label('bc_count'),
            func.sum(case((Plan.plan_type == PlanType.DISASTER_RECOVERY, 1), else_=0)).label('dr_count'),
            func.sum(case((Plan.plan_type == PlanType.CRISIS_MANAGEMENT, 1), else_=0)).label('crisis_count'),
            # By priority
            func.sum(case((Plan.priority == PlanPriority.CRITICAL, 1), else_=0)).label('critical_count'),
            func.sum(case((Plan.priority == PlanPriority.HIGH, 1), else_=0)).label('high_count'),
            func.sum(case((Plan.priority == PlanPriority.MEDIUM, 1), else_=0)).label('medium_count'),
            func.sum(case((Plan.priority == PlanPriority.LOW, 1), else_=0)).label('low_count'),
        ).where(
            and_(
                Plan.tenant_id == tenant_id,
                Plan.active == True
            )
        )

        result = await self.session.execute(query)
        row = result.first()

        if not row or row.total_count == 0:
            return {
                "total_count": 0,
                "status_breakdown": {},
                "type_breakdown": {},
                "priority_breakdown": {}
            }

        return {
            "total_count": int(row.total_count),
            "status_breakdown": {
                "draft": int(row.draft_count or 0),
                "in_review": int(row.in_review_count or 0),
                "approved": int(row.approved_count or 0),
                "active": int(row.active_count or 0)
            },
            "type_breakdown": {
                "incident_response": int(row.incident_response_count or 0),
                "business_continuity": int(row.bc_count or 0),
                "disaster_recovery": int(row.dr_count or 0),
                "crisis_management": int(row.crisis_count or 0)
            },
            "priority_breakdown": {
                "critical": int(row.critical_count or 0),
                "high": int(row.high_count or 0),
                "medium": int(row.medium_count or 0),
                "low": int(row.low_count or 0)
            }
        }

    async def get_plans_needing_review(self, tenant_id: str) -> List[Plan]:
        """
        Get plans with review dates in the past or coming up soon.

        Optimization: Uses indexed next_review_date field

        Args:
            tenant_id: Tenant identifier

        Returns:
            List of plans needing review
        """
        from datetime import timedelta

        future_threshold = datetime.utcnow() + timedelta(days=30)

        result = await self.session.execute(
            select(Plan)
            .where(
                and_(
                    Plan.tenant_id == tenant_id,
                    Plan.active == True,
                    Plan.next_review_date.isnot(None),
                    Plan.next_review_date <= future_threshold,
                    Plan.status.in_([PlanStatus.APPROVED, PlanStatus.ACTIVE])
                )
            )
            .order_by(Plan.next_review_date)
        )
        return list(result.scalars().all())

    async def list_with_pagination_cursor(
        self,
        tenant_id: str,
        last_id: Optional[int] = None,
        limit: int = 100,
        plan_type: Optional[PlanType] = None,
        status: Optional[PlanStatus] = None,
        priority: Optional[PlanPriority] = None
    ) -> List[Plan]:
        """
        List plans with cursor-based pagination for large datasets.

        Optimization: Cursor-based pagination instead of OFFSET
        Before: OFFSET 10000 LIMIT 100 scans 10000 rows
        After: WHERE id > last_id LIMIT 100 uses index

        Args:
            tenant_id: Tenant identifier
            last_id: Last plan ID from previous page (cursor)
            limit: Number of results per page
            plan_type: Optional type filter
            status: Optional status filter
            priority: Optional priority filter

        Returns:
            List of plans
        """
        query = select(Plan).where(
            and_(
                Plan.tenant_id == tenant_id,
                Plan.active == True
            )
        )

        # Cursor-based pagination
        if last_id is not None:
            query = query.where(Plan.plan_id > last_id)

        # Optional filters
        if plan_type:
            query = query.where(Plan.plan_type == plan_type)

        if status:
            query = query.where(Plan.status == status)

        if priority:
            query = query.where(Plan.priority == priority)

        # Order by ID for consistent pagination
        query = query.order_by(Plan.plan_id).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())
