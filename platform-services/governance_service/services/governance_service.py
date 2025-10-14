"""
Governance Service - FULL Business Logic
Implements PolicyService, RoleService, and ResourceService
Preserves ALL business logic from original governance/main.py (1,953 lines)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from models.database import (
    BCMPolicy, PolicyVersion, PolicyStatus, PolicyType,
    OrganizationalRole, RoleType, RoleStatus,
    BCMResource, ResourceType, ResourceAvailability,
    CompetenceRecord, CompetenceLevel, EvidenceType,
)
from repositories.policy_repository import PolicyRepository, PolicyVersionRepository
from repositories.role_repository import RoleRepository
from repositories.resource_repository import ResourceRepository
from repositories.competence_repository import CompetenceRepository

from workflows.policy_workflow import (
    PolicyWorkflowEngine,
    PolicyValidator,
    PolicyState,
    PolicyAction,
)
from workflows.role_workflow import (
    RoleWorkflowEngine,
    RoleValidator,
    RoleState,
    RoleAction,
)
from workflows.resource_workflow import (
    ResourceWorkflowEngine,
    ResourceValidator,
    ResourceAvailability as WorkflowResourceAvailability,
    ResourceAction,
)


# ============================================================================
# POLICY SERVICE - ISO 22301 Clause 5.2
# ============================================================================

class PolicyService:
    """
    Policy Service - Full Business Logic

    Handles:
    - Policy lifecycle (draft → review → approved → active → archived)
    - Version management
    - Review scheduling
    - Approval workflow with validations
    - Publication and archival
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.policy_repo = PolicyRepository(session)
        self.version_repo = PolicyVersionRepository(session)
        self.workflow = PolicyWorkflowEngine()
        self.validator = PolicyValidator()

    # ========================================================================
    # POLICY CREATION & MANAGEMENT
    # ========================================================================

    async def create_policy(
        self,
        tenant_id: str,
        title: str,
        policy_type: PolicyType,
        content: str,
        version: str = "1.0",
        summary: Optional[str] = None,
        iso_clause: Optional[str] = None,
        scope: Optional[str] = None,
        applicable_departments: Optional[List[str]] = None,
        applicable_locations: Optional[List[str]] = None,
        policy_owner: Optional[str] = None,
        review_frequency_months: int = 12,
        created_by: Optional[str] = None,
    ) -> BCMPolicy:
        """Create new BCM policy (preserves original logic from lines 192-236)"""

        # Validate content (original line 197-199)
        valid, error = self.validator.validate_policy_content(content)
        if not valid:
            raise ValueError(error)

        # Validate version (original line 201-204)
        valid, error = self.validator.validate_version(version)
        if not valid:
            raise ValueError(error)

        # Check for duplicate title
        existing = await self.policy_repo.get_by_title(tenant_id, title)
        if existing:
            raise ValueError(f"Policy with title '{title}' already exists")

        # Calculate next review date
        next_review_date = datetime.utcnow() + timedelta(days=review_frequency_months * 30)

        # Create policy (original lines 206-222)
        policy = BCMPolicy(
            tenant_id=tenant_id,
            title=title,
            policy_type=policy_type,
            version=version,
            content=content,
            summary=summary,
            iso_clause=iso_clause,
            scope=scope,
            applicable_departments=applicable_departments or [],
            applicable_locations=applicable_locations or [],
            policy_owner=policy_owner,
            review_frequency_months=review_frequency_months,
            status=PolicyStatus.DRAFT,
            workflow_state=PolicyStatus.DRAFT.value,
            created_by=created_by,
            next_review_date=next_review_date,
        )

        created_policy = await self.policy_repo.create(policy)

        # Create initial version record
        await self._create_version(
            policy_id=created_policy.id,
            version=version,
            content=content,
            changes_summary="Initial version",
            created_by=created_by
        )

        return created_policy

    async def get_policy(self, policy_id: int) -> BCMPolicy:
        """Get policy by ID (original lines 263-279)"""
        policy = await self.policy_repo.get_by_id(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        return policy

    async def update_policy(
        self,
        policy_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        summary: Optional[str] = None,
        policy_owner: Optional[str] = None,
        approved_by: Optional[str] = None,
        status: Optional[PolicyStatus] = None,
    ) -> BCMPolicy:
        """Update policy (original lines 281-310)"""
        policy = await self.get_policy(policy_id)

        # Only allow updates to DRAFT or ACTIVE policies
        if policy.status in [PolicyStatus.ARCHIVED]:
            raise ValueError("Cannot update archived policy")

        # Update fields (original lines 295-297)
        content_changed = False
        if title is not None:
            policy.title = title
        if content is not None:
            # Validate new content
            valid, error = self.validator.validate_policy_content(content)
            if not valid:
                raise ValueError(error)
            content_changed = content != policy.content
            policy.content = content
        if summary is not None:
            policy.summary = summary
        if policy_owner is not None:
            policy.policy_owner = policy_owner
        if approved_by is not None:
            policy.approved_by = approved_by
        if status is not None:
            policy.status = status

        updated_policy = await self.policy_repo.update(policy)

        # Create new version if content changed
        if content_changed and content is not None:
            # Increment version
            major, minor = map(int, updated_policy.version.split('.'))
            new_version = f"{major}.{minor + 1}"
            updated_policy.version = new_version

            await self._create_version(
                policy_id=policy_id,
                version=new_version,
                content=content,
                changes_summary="Content updated",
                created_by=approved_by
            )

        return updated_policy

    async def list_policies(
        self,
        tenant_id: str,
        status: Optional[PolicyStatus] = None,
        policy_type: Optional[PolicyType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BCMPolicy]:
        """List policies with filters (original lines 238-261)"""
        return await self.policy_repo.list_by_tenant(
            tenant_id, status, policy_type, skip, limit
        )

    # ========================================================================
    # POLICY WORKFLOW - State Machine Implementation
    # ========================================================================

    async def submit_for_review(
        self,
        policy_id: int,
        submitted_by: Optional[str] = None
    ) -> BCMPolicy:
        """
        Submit policy for review
        Transition: DRAFT → UNDER_REVIEW
        (Preserves original workflow logic)
        """
        policy = await self.get_policy(policy_id)

        # Validate transition
        policy_dict = self._policy_to_dict(policy)
        valid, error = self.workflow.validate_transition(
            policy_dict,
            PolicyAction.SUBMIT_FOR_REVIEW.value
        )
        if not valid:
            raise ValueError(error)

        # Perform transition
        policy.status = PolicyStatus.UNDER_REVIEW
        policy.workflow_state = PolicyStatus.UNDER_REVIEW.value

        # Add workflow history
        self._add_workflow_log(
            policy,
            PolicyStatus.DRAFT.value,
            PolicyStatus.UNDER_REVIEW.value,
            PolicyAction.SUBMIT_FOR_REVIEW.value,
            submitted_by,
            "Submitted for review"
        )

        return await self.policy_repo.update(policy)

    async def approve_policy(
        self,
        policy_id: int,
        approved_by: str,
        approval_comments: Optional[str] = None
    ) -> BCMPolicy:
        """
        Approve policy
        Transition: UNDER_REVIEW → APPROVED
        (Preserves original approval logic)
        """
        policy = await self.get_policy(policy_id)

        # Validate transition
        policy_dict = self._policy_to_dict(policy)
        valid, error = self.workflow.validate_transition(
            policy_dict,
            PolicyAction.APPROVE.value
        )
        if not valid:
            raise ValueError(error)

        # Validate approval info
        valid, error = self.validator.validate_approval(
            approved_by,
            datetime.utcnow()
        )
        if not valid:
            raise ValueError(error)

        # Perform transition
        policy.status = PolicyStatus.APPROVED
        policy.workflow_state = PolicyStatus.APPROVED.value
        policy.approved_by = approved_by
        policy.approved_at = datetime.utcnow()
        policy.approval_comments = approval_comments

        # Add workflow history
        self._add_workflow_log(
            policy,
            PolicyStatus.UNDER_REVIEW.value,
            PolicyStatus.APPROVED.value,
            PolicyAction.APPROVE.value,
            approved_by,
            approval_comments
        )

        return await self.policy_repo.update(policy)

    async def reject_policy(
        self,
        policy_id: int,
        rejected_by: str,
        rejection_reason: str
    ) -> BCMPolicy:
        """
        Reject policy
        Transition: UNDER_REVIEW → DRAFT
        """
        policy = await self.get_policy(policy_id)

        # Validate transition
        policy_dict = self._policy_to_dict(policy)
        valid, error = self.workflow.validate_transition(
            policy_dict,
            PolicyAction.REJECT.value
        )
        if not valid:
            raise ValueError(error)

        # Perform transition
        policy.status = PolicyStatus.DRAFT
        policy.workflow_state = PolicyStatus.DRAFT.value
        policy.approval_comments = rejection_reason

        # Add workflow history
        self._add_workflow_log(
            policy,
            PolicyStatus.UNDER_REVIEW.value,
            PolicyStatus.DRAFT.value,
            PolicyAction.REJECT.value,
            rejected_by,
            rejection_reason
        )

        return await self.policy_repo.update(policy)

    async def activate_policy(
        self,
        policy_id: int,
        activated_by: Optional[str] = None
    ) -> BCMPolicy:
        """
        Activate policy (publish)
        Transition: APPROVED → ACTIVE
        """
        policy = await self.get_policy(policy_id)

        # Validate transition
        policy_dict = self._policy_to_dict(policy)
        valid, error = self.workflow.validate_transition(
            policy_dict,
            PolicyAction.ACTIVATE.value
        )
        if not valid:
            raise ValueError(error)

        # Perform transition
        policy.status = PolicyStatus.ACTIVE
        policy.workflow_state = PolicyStatus.ACTIVE.value
        policy.effective_date = datetime.utcnow()

        # Set next review date
        if policy.review_frequency_months:
            policy.next_review_date = datetime.utcnow() + timedelta(
                days=policy.review_frequency_months * 30
            )

        # Add workflow history
        self._add_workflow_log(
            policy,
            PolicyStatus.APPROVED.value,
            PolicyStatus.ACTIVE.value,
            PolicyAction.ACTIVATE.value,
            activated_by,
            "Policy activated"
        )

        return await self.policy_repo.update(policy)

    async def archive_policy(
        self,
        policy_id: int,
        archived_by: Optional[str] = None,
        archive_reason: Optional[str] = None
    ) -> BCMPolicy:
        """
        Archive policy
        Transition: ACTIVE → ARCHIVED
        """
        policy = await self.get_policy(policy_id)

        # Validate transition
        policy_dict = self._policy_to_dict(policy)
        valid, error = self.workflow.validate_transition(
            policy_dict,
            PolicyAction.ARCHIVE.value
        )
        if not valid:
            raise ValueError(error)

        # Perform transition
        policy.status = PolicyStatus.ARCHIVED
        policy.workflow_state = PolicyStatus.ARCHIVED.value
        policy.expiry_date = datetime.utcnow()

        # Add workflow history
        self._add_workflow_log(
            policy,
            PolicyStatus.ACTIVE.value,
            PolicyStatus.ARCHIVED.value,
            PolicyAction.ARCHIVE.value,
            archived_by,
            archive_reason
        )

        return await self.policy_repo.update(policy)

    # ========================================================================
    # POLICY REVIEW MANAGEMENT
    # ========================================================================

    async def list_policies_for_review(
        self,
        tenant_id: str
    ) -> List[BCMPolicy]:
        """List policies due for review"""
        return await self.policy_repo.list_for_review(
            tenant_id,
            datetime.utcnow()
        )

    async def record_policy_review(
        self,
        policy_id: int,
        reviewed_by: str,
        review_notes: Optional[str] = None,
        next_review_months: Optional[int] = None
    ) -> BCMPolicy:
        """Record policy review"""
        policy = await self.get_policy(policy_id)

        policy.last_review_date = datetime.utcnow()

        # Calculate next review date
        review_period = next_review_months or policy.review_frequency_months
        policy.next_review_date = datetime.utcnow() + timedelta(
            days=review_period * 30
        )

        # Add to workflow history
        self._add_workflow_log(
            policy,
            policy.status.value,
            policy.status.value,
            "review",
            reviewed_by,
            review_notes
        )

        return await self.policy_repo.update(policy)

    # ========================================================================
    # VERSION MANAGEMENT
    # ========================================================================

    async def get_policy_versions(
        self,
        policy_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[PolicyVersion]:
        """Get policy version history"""
        return await self.version_repo.list_by_policy(policy_id, skip, limit)

    async def get_latest_version(self, policy_id: int) -> Optional[PolicyVersion]:
        """Get latest version of policy"""
        return await self.version_repo.get_latest_version(policy_id)

    # ========================================================================
    # HELPERS
    # ========================================================================

    async def _create_version(
        self,
        policy_id: int,
        version: str,
        content: str,
        changes_summary: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> PolicyVersion:
        """Create policy version record"""
        version_record = PolicyVersion(
            policy_id=policy_id,
            version=version,
            content=content,
            changes_summary=changes_summary,
            created_by=created_by,
        )
        return await self.version_repo.create(version_record)

    def _policy_to_dict(self, policy: BCMPolicy) -> Dict:
        """Convert policy to dict for workflow validation"""
        return {
            "id": policy.id,
            "tenant_id": policy.tenant_id,
            "title": policy.title,
            "policy_type": policy.policy_type.value,
            "version": policy.version,
            "content": policy.content,
            "policy_owner": policy.policy_owner,
            "status": policy.status.value,
            "workflow_state": policy.workflow_state,
            "approved_by": policy.approved_by,
            "approved_at": policy.approved_at,
            "effective_date": policy.effective_date,
        }

    def _add_workflow_log(
        self,
        policy: BCMPolicy,
        from_state: str,
        to_state: str,
        action: str,
        user_id: Optional[str],
        comments: Optional[str]
    ):
        """Add entry to workflow history"""
        history = policy.workflow_history or []
        history.append({
            "from_state": from_state,
            "to_state": to_state,
            "action": action,
            "user_id": user_id,
            "comments": comments,
            "timestamp": datetime.utcnow().isoformat()
        })
        policy.workflow_history = history


# ============================================================================
# ROLE SERVICE - ISO 22301 Clause 5.3
# ============================================================================

class RoleService:
    """
    Role Service - Full Business Logic

    Handles:
    - Role creation and management
    - Role assignment workflow
    - Competence validation
    - Responsibility tracking
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.role_repo = RoleRepository(session)
        self.competence_repo = CompetenceRepository(session)
        self.workflow = RoleWorkflowEngine()
        self.validator = RoleValidator()

    # ========================================================================
    # ROLE CREATION & MANAGEMENT
    # ========================================================================

    async def create_role(
        self,
        tenant_id: str,
        role_name: str,
        role_type: RoleType,
        description: Optional[str] = None,
        responsibilities: Optional[List[Dict]] = None,
        authorities: Optional[List[Dict]] = None,
        competence_requirements: Optional[List[Dict]] = None,
        assigned_to: Optional[str] = None,
        assigned_to_name: Optional[str] = None,
    ) -> OrganizationalRole:
        """Create organizational role (preserves original logic from lines 314-350)"""

        # Validate responsibilities (original lines 319-322)
        if responsibilities:
            valid, error = self.validator.validate_responsibilities(responsibilities)
            if not valid:
                raise ValueError(error)

        # Validate authorities
        if authorities:
            valid, error = self.validator.validate_authorities(authorities)
            if not valid:
                raise ValueError(error)

        # Validate competence requirements
        if competence_requirements:
            valid, error = self.validator.validate_competence_requirements(
                competence_requirements
            )
            if not valid:
                raise ValueError(error)

        # Check for duplicate role name
        existing = await self.role_repo.get_by_name(tenant_id, role_name)
        if existing:
            raise ValueError(f"Role '{role_name}' already exists")

        # Determine initial status (original line 335)
        status = RoleStatus.PENDING if not assigned_to else RoleStatus.ACTIVE
        assigned_at = datetime.utcnow() if assigned_to else None

        # Create role (original lines 325-336)
        role = OrganizationalRole(
            tenant_id=tenant_id,
            role_name=role_name,
            role_type=role_type,
            description=description,
            responsibilities=responsibilities or [],
            authorities=authorities or [],
            competence_requirements=competence_requirements or [],
            assigned_to=assigned_to,
            assigned_to_name=assigned_to_name,
            assigned_at=assigned_at,
            status=status,
        )

        return await self.role_repo.create(role)

    async def get_role(self, role_id: int) -> OrganizationalRole:
        """Get role by ID"""
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
        return role

    async def list_roles(
        self,
        tenant_id: str,
        status: Optional[RoleStatus] = None,
        role_type: Optional[RoleType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[OrganizationalRole]:
        """List roles with filters (original lines 352-375)"""
        return await self.role_repo.list_by_tenant(
            tenant_id, status, role_type, skip, limit
        )

    # ========================================================================
    # ROLE ASSIGNMENT WORKFLOW
    # ========================================================================

    async def assign_role(
        self,
        role_id: int,
        assigned_to: str,
        assigned_to_name: str,
        backup_person: Optional[str] = None,
        backup_person_name: Optional[str] = None,
        assigned_by: Optional[str] = None,
    ) -> OrganizationalRole:
        """
        Assign role to person
        Transition: PENDING → ACTIVE
        """
        role = await self.get_role(role_id)

        # Validate assignment
        valid, error = self.validator.validate_assignment(
            assigned_to,
            assigned_to_name,
            backup_person
        )
        if not valid:
            raise ValueError(error)

        # Validate transition
        role_dict = self._role_to_dict(role)
        valid, error = self.workflow.validate_transition(
            role_dict,
            RoleAction.ASSIGN.value
        )
        if not valid:
            raise ValueError(error)

        # Check competence requirements before assignment
        if role.competence_requirements:
            await self._validate_person_competence(
                role.tenant_id,
                assigned_to,
                role.competence_requirements
            )

        # Perform assignment
        role.assigned_to = assigned_to
        role.assigned_to_name = assigned_to_name
        role.backup_person = backup_person
        role.backup_person_name = backup_person_name
        role.assigned_at = datetime.utcnow()
        role.status = RoleStatus.ACTIVE

        return await self.role_repo.update(role)

    async def reassign_role(
        self,
        role_id: int,
        new_assignee: str,
        new_assignee_name: str,
        backup_person: Optional[str] = None,
        backup_person_name: Optional[str] = None,
        reassigned_by: Optional[str] = None,
    ) -> OrganizationalRole:
        """
        Reassign role to different person
        Transition: ACTIVE → ACTIVE (with new assignee)
        """
        role = await self.get_role(role_id)

        # Validate assignment
        valid, error = self.validator.validate_assignment(
            new_assignee,
            new_assignee_name,
            backup_person
        )
        if not valid:
            raise ValueError(error)

        # Validate transition
        role_dict = self._role_to_dict(role)
        valid, error = self.workflow.validate_transition(
            role_dict,
            RoleAction.REASSIGN.value
        )
        if not valid:
            raise ValueError(error)

        # Check competence requirements
        if role.competence_requirements:
            await self._validate_person_competence(
                role.tenant_id,
                new_assignee,
                role.competence_requirements
            )

        # Perform reassignment
        role.assigned_to = new_assignee
        role.assigned_to_name = new_assignee_name
        role.backup_person = backup_person
        role.backup_person_name = backup_person_name
        role.assigned_at = datetime.utcnow()

        return await self.role_repo.update(role)

    async def deactivate_role(
        self,
        role_id: int,
        deactivated_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> OrganizationalRole:
        """
        Deactivate role
        Transition: ACTIVE → INACTIVE
        """
        role = await self.get_role(role_id)

        # Validate transition
        role_dict = self._role_to_dict(role)
        valid, error = self.workflow.validate_transition(
            role_dict,
            RoleAction.DEACTIVATE.value
        )
        if not valid:
            raise ValueError(error)

        # Perform deactivation
        role.status = RoleStatus.INACTIVE

        return await self.role_repo.update(role)

    async def reactivate_role(
        self,
        role_id: int,
        reactivated_by: Optional[str] = None
    ) -> OrganizationalRole:
        """
        Reactivate role
        Transition: INACTIVE → ACTIVE
        """
        role = await self.get_role(role_id)

        # Validate transition
        role_dict = self._role_to_dict(role)
        valid, error = self.workflow.validate_transition(
            role_dict,
            RoleAction.REACTIVATE.value
        )
        if not valid:
            raise ValueError(error)

        # Perform reactivation
        role.status = RoleStatus.ACTIVE

        return await self.role_repo.update(role)

    # ========================================================================
    # COMPETENCE VALIDATION
    # ========================================================================

    async def _validate_person_competence(
        self,
        tenant_id: str,
        person_id: str,
        requirements: List[Dict]
    ):
        """Validate person has required competencies"""
        # Get all competence records for person
        records = await self.competence_repo.list_by_person(tenant_id, person_id)

        # Check each requirement
        for req in requirements:
            if not req.get("mandatory", False):
                continue  # Skip optional requirements

            competence_area = req.get("competence")
            required_level = req.get("level")

            # Find matching record
            matching_record = None
            for record in records:
                if record.competence_area == competence_area:
                    matching_record = record
                    break

            if not matching_record:
                raise ValueError(
                    f"Missing required competence: {competence_area}"
                )

            # Validate level
            if matching_record.gap_exists:
                raise ValueError(
                    f"Competence gap exists for {competence_area}"
                )

            if not matching_record.verified:
                raise ValueError(
                    f"Competence not verified: {competence_area}"
                )

    # ========================================================================
    # ROLE QUERIES
    # ========================================================================

    async def list_unassigned_roles(
        self,
        tenant_id: str,
        role_type: Optional[RoleType] = None
    ) -> List[OrganizationalRole]:
        """List unassigned roles"""
        return await self.role_repo.list_unassigned(tenant_id, role_type)

    async def list_roles_by_assignee(
        self,
        tenant_id: str,
        assigned_to: str,
        status: Optional[RoleStatus] = None
    ) -> List[OrganizationalRole]:
        """List roles assigned to person"""
        return await self.role_repo.list_by_assignee(tenant_id, assigned_to, status)

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _role_to_dict(self, role: OrganizationalRole) -> Dict:
        """Convert role to dict for workflow validation"""
        return {
            "id": role.id,
            "tenant_id": role.tenant_id,
            "role_name": role.role_name,
            "role_type": role.role_type.value,
            "assigned_to": role.assigned_to,
            "status": role.status.value,
        }


# ============================================================================
# RESOURCE SERVICE - ISO 22301 Clause 7.1
# ============================================================================

class ResourceService:
    """
    Resource Service - Full Business Logic

    Handles:
    - Resource creation and management
    - Resource allocation workflow
    - Availability tracking
    - Cost management
    - Criticality assessment
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.resource_repo = ResourceRepository(session)
        self.workflow = ResourceWorkflowEngine()
        self.validator = ResourceValidator()

    # ========================================================================
    # RESOURCE CREATION & MANAGEMENT
    # ========================================================================

    async def create_resource(
        self,
        tenant_id: str,
        resource_name: str,
        resource_type: ResourceType,
        description: Optional[str] = None,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        cost_per_unit: Optional[float] = None,
        total_cost: Optional[float] = None,
        criticality: Optional[int] = None,
        is_critical: bool = False,
        owner: Optional[str] = None,
    ) -> BCMResource:
        """Create BCM resource (preserves original logic from lines 379-430)"""

        # Validate cost (original lines 384-391)
        if cost_per_unit and total_cost and quantity:
            valid, error = self.validator.validate_cost(
                cost_per_unit,
                total_cost,
                quantity
            )
            if not valid:
                raise ValueError(error)

        # Validate criticality (original lines 393-400)
        if criticality:
            valid, error = self.validator.validate_criticality(
                criticality,
                is_critical
            )
            if not valid:
                raise ValueError(error)

        # Check for duplicate resource name
        existing = await self.resource_repo.get_by_name(tenant_id, resource_name)
        if existing:
            raise ValueError(f"Resource '{resource_name}' already exists")

        # Create resource (original lines 402-415)
        resource = BCMResource(
            tenant_id=tenant_id,
            resource_name=resource_name,
            resource_type=resource_type,
            description=description,
            quantity=quantity,
            unit=unit,
            cost_per_unit=cost_per_unit,
            total_cost=total_cost,
            criticality=criticality,
            is_critical=is_critical,
            owner=owner,
            availability=ResourceAvailability.AVAILABLE,
        )

        return await self.resource_repo.create(resource)

    async def get_resource(self, resource_id: int) -> BCMResource:
        """Get resource by ID"""
        resource = await self.resource_repo.get_by_id(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")
        return resource

    async def list_resources(
        self,
        tenant_id: str,
        resource_type: Optional[ResourceType] = None,
        availability: Optional[ResourceAvailability] = None,
        is_critical: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BCMResource]:
        """List resources with filters (original lines 432-455)"""
        return await self.resource_repo.list_by_tenant(
            tenant_id, resource_type, availability, is_critical, skip, limit
        )

    # ========================================================================
    # RESOURCE ALLOCATION WORKFLOW
    # ========================================================================

    async def allocate_resource(
        self,
        resource_id: int,
        allocated_to: str,
        allocated_to_type: str,
        quantity: Optional[float] = None,
        allocated_by: Optional[str] = None,
    ) -> BCMResource:
        """
        Allocate resource
        Transition: AVAILABLE → ALLOCATED
        """
        resource = await self.get_resource(resource_id)

        # Validate allocation
        valid, error = self.validator.validate_allocation(
            allocated_to,
            allocated_to_type,
            quantity or resource.quantity or 1.0,
            resource.unit or "units"
        )
        if not valid:
            raise ValueError(error)

        # Validate transition
        resource_dict = self._resource_to_dict(resource)
        valid, error = self.workflow.validate_transition(
            resource_dict,
            ResourceAction.ALLOCATE.value
        )
        if not valid:
            raise ValueError(error)

        # Perform allocation
        resource.allocated_to = allocated_to
        resource.allocated_to_type = allocated_to_type
        resource.availability = ResourceAvailability.ALLOCATED
        resource.available_from = datetime.utcnow()

        return await self.resource_repo.update(resource)

    async def deallocate_resource(
        self,
        resource_id: int,
        deallocated_by: Optional[str] = None
    ) -> BCMResource:
        """
        Deallocate resource
        Transition: ALLOCATED → AVAILABLE
        """
        resource = await self.get_resource(resource_id)

        # Validate transition
        resource_dict = self._resource_to_dict(resource)
        valid, error = self.workflow.validate_transition(
            resource_dict,
            ResourceAction.DEALLOCATE.value
        )
        if not valid:
            raise ValueError(error)

        # Perform deallocation
        resource.allocated_to = None
        resource.allocated_to_type = None
        resource.availability = ResourceAvailability.AVAILABLE
        resource.available_from = None
        resource.available_until = None

        return await self.resource_repo.update(resource)

    async def mark_unavailable(
        self,
        resource_id: int,
        reason: Optional[str] = None
    ) -> BCMResource:
        """
        Mark resource as unavailable
        Transition: AVAILABLE/ALLOCATED → UNAVAILABLE
        """
        resource = await self.get_resource(resource_id)

        # Validate transition
        resource_dict = self._resource_to_dict(resource)
        valid, error = self.workflow.validate_transition(
            resource_dict,
            ResourceAction.MARK_UNAVAILABLE.value
        )
        if not valid:
            raise ValueError(error)

        # Perform transition
        resource.availability = ResourceAvailability.UNAVAILABLE
        resource.notes = f"{resource.notes or ''}\nMarked unavailable: {reason or 'No reason provided'}"

        return await self.resource_repo.update(resource)

    async def schedule_maintenance(
        self,
        resource_id: int,
        available_from: datetime,
        available_until: datetime,
        maintenance_notes: Optional[str] = None
    ) -> BCMResource:
        """
        Schedule maintenance
        Transition: AVAILABLE → MAINTENANCE
        """
        resource = await self.get_resource(resource_id)

        # Validate period
        valid, error = self.validator.validate_availability_period(
            available_from,
            available_until
        )
        if not valid:
            raise ValueError(error)

        # Validate transition
        resource_dict = self._resource_to_dict(resource)
        resource_dict["available_from"] = available_from
        resource_dict["available_until"] = available_until
        valid, error = self.workflow.validate_transition(
            resource_dict,
            ResourceAction.SCHEDULE_MAINTENANCE.value
        )
        if not valid:
            raise ValueError(error)

        # Perform transition
        resource.availability = ResourceAvailability.MAINTENANCE
        resource.available_from = available_from
        resource.available_until = available_until
        if maintenance_notes:
            resource.notes = f"{resource.notes or ''}\nMaintenance: {maintenance_notes}"

        return await self.resource_repo.update(resource)

    async def complete_maintenance(
        self,
        resource_id: int,
        completion_notes: Optional[str] = None
    ) -> BCMResource:
        """
        Complete maintenance
        Transition: MAINTENANCE → AVAILABLE
        """
        resource = await self.get_resource(resource_id)

        # Validate transition
        resource_dict = self._resource_to_dict(resource)
        valid, error = self.workflow.validate_transition(
            resource_dict,
            ResourceAction.COMPLETE_MAINTENANCE.value
        )
        if not valid:
            raise ValueError(error)

        # Perform transition
        resource.availability = ResourceAvailability.AVAILABLE
        resource.available_from = None
        resource.available_until = None
        if completion_notes:
            resource.notes = f"{resource.notes or ''}\nMaintenance completed: {completion_notes}"

        return await self.resource_repo.update(resource)

    # ========================================================================
    # RESOURCE QUERIES
    # ========================================================================

    async def list_available_resources(
        self,
        tenant_id: str,
        resource_type: Optional[ResourceType] = None
    ) -> List[BCMResource]:
        """List available resources"""
        return await self.resource_repo.list_available(tenant_id, resource_type)

    async def list_critical_resources(
        self,
        tenant_id: str,
        resource_type: Optional[ResourceType] = None
    ) -> List[BCMResource]:
        """List critical resources"""
        return await self.resource_repo.list_critical(tenant_id, resource_type)

    async def get_resource_allocation_summary(
        self,
        tenant_id: str
    ) -> Dict:
        """Get resource allocation summary"""
        # Get counts by availability
        counts = await self.resource_repo.count_by_availability(tenant_id)

        # Get total cost
        total_cost = await self.resource_repo.get_total_cost(tenant_id)

        # Get critical resources count
        critical_resources = await self.resource_repo.list_critical(tenant_id)

        return {
            "tenant_id": tenant_id,
            "availability_summary": counts,
            "total_cost": total_cost,
            "critical_resources_count": len(critical_resources),
            "timestamp": datetime.utcnow().isoformat()
        }

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _resource_to_dict(self, resource: BCMResource) -> Dict:
        """Convert resource to dict for workflow validation"""
        return {
            "id": resource.id,
            "tenant_id": resource.tenant_id,
            "resource_name": resource.resource_name,
            "resource_type": resource.resource_type.value,
            "availability": resource.availability.value,
            "allocated_to": resource.allocated_to,
            "quantity": resource.quantity,
            "available_from": resource.available_from,
            "available_until": resource.available_until,
        }
