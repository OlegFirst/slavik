"""
Plan Service - Business Logic
ISO 22301 Clause 8.4 - Business Continuity Plans and Procedures
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import httpx
import logging

from ..repositories.plan_repository import PlanRepository
from ..models.domain import (
    PlanCreate, PlanUpdate, PlanResponse,
    ProcedureCreate, ProcedureUpdate, ProcedureResponse,
    ResourceCreate, ResourceUpdate, ResourceResponse,
    ContactListCreate, ContactListResponse,
    ActivationCreate, ActivationResponse,
    ReviewCreate, ReviewResponse,
    PlanStatus,
)
from ..models.database import Plan, Procedure, PlanResource, ContactList, PlanActivation, PlanReview
from ..workflows.plan_lifecycle import execute_plan_transition, PlanWorkflowAction
from ..workflows.review_workflow import calculate_next_review_date
from ..config import settings
from .procedure_validator import ProcedureDependencyValidator

logger = logging.getLogger(__name__)


class PlanService:
    """Business logic for plan management"""

    def __init__(self, repository: PlanRepository):
        self.repo = repository
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for EventBus"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=5.0)
        return self._http_client

    async def _publish_event(self, topic: str, data: Dict[str, Any]) -> None:
        """
        Publish event to EventBus

        Args:
            topic: Event topic (e.g., "plans.plan.created")
            data: Event data payload
        """
        try:
            client = await self._get_http_client()
            await client.post(
                f"{settings.EVENTBUS_URL}/publish",
                json={
                    "topic": topic,
                    "data": data,
                    "source": settings.SERVICE_NAME,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            logger.info(f"Published event: {topic} for plan_id={data.get('plan_id')}")
        except Exception as e:
            # Don't fail the main operation if EventBus is unavailable
            logger.warning(f"Failed to publish event {topic}: {e}")

    async def close(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    # ===== PLAN OPERATIONS =====

    async def create_plan(
        self,
        plan_data: PlanCreate,
        created_by: str
    ) -> PlanResponse:
        """
        Create new business continuity plan
        ISO 22301: Clause 8.4.1
        """
        # Create plan
        plan = Plan(
            tenant_id=plan_data.tenant_id,
            plan_code=plan_data.plan_code,
            plan_name=plan_data.plan_name,
            plan_type=plan_data.plan_type,
            priority=plan_data.priority,
            status=PlanStatus.DRAFT,
            version="1.0",
            objective=plan_data.objective,
            scope=plan_data.scope,
            assumptions=plan_data.assumptions,
            activation_triggers=plan_data.activation_triggers,
            activation_authority_user_id=plan_data.activation_authority_user_id,
            rto_hours=plan_data.rto_hours,
            rpo_hours=plan_data.rpo_hours,
            mtpd_hours=plan_data.mtpd_hours,
            based_on_bia_id=plan_data.based_on_bia_id,
            based_on_risk_ids=plan_data.based_on_risk_ids,
            plan_owner_user_id=plan_data.plan_owner_user_id,
            team_leader_user_id=plan_data.team_leader_user_id,
            team_member_user_ids=plan_data.team_member_user_ids,
            review_frequency=plan_data.review_frequency,
            created_by=created_by,
        )

        # Calculate next review date
        if plan.review_frequency:
            plan.next_review_date = calculate_next_review_date(
                datetime.utcnow(),
                plan.review_frequency.value
            )

        created_plan = await self.repo.create(plan)

        # Publish event
        await self._publish_event(
            topic="plans.plan.created",
            data={
                "plan_id": created_plan.plan_id,
                "tenant_id": created_plan.tenant_id,
                "plan_code": created_plan.plan_code,
                "plan_name": created_plan.plan_name,
                "plan_type": created_plan.plan_type.value,
                "priority": created_plan.priority.value,
                "status": created_plan.status.value,
                "version": created_plan.version,
                "plan_owner_user_id": created_plan.plan_owner_user_id,
                "team_leader_user_id": created_plan.team_leader_user_id,
                "rto_hours": created_plan.rto_hours,
                "rpo_hours": created_plan.rpo_hours,
                "mtpd_hours": created_plan.mtpd_hours,
                "based_on_bia_id": created_plan.based_on_bia_id,
                "based_on_risk_ids": created_plan.based_on_risk_ids,
                "created_by": created_by,
            }
        )

        return self._to_plan_response(created_plan)

    async def get_plan(self, plan_id: int) -> Optional[PlanResponse]:
        """Get plan by ID"""
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            return None
        return self._to_plan_response(plan)

    async def list_plans(
        self,
        tenant_id: str,
        **filters
    ) -> List[PlanResponse]:
        """List plans with filters"""
        plans = await self.repo.list_by_tenant(tenant_id, **filters)
        return [self._to_plan_response(p) for p in plans]

    async def update_plan(
        self,
        plan_id: int,
        plan_data: PlanUpdate,
        updated_by: str
    ) -> Optional[PlanResponse]:
        """Update plan (only in DRAFT status)"""
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            return None

        if plan.status != PlanStatus.DRAFT:
            raise ValueError(f"Cannot update plan in {plan.status} status")

        update_dict = plan_data.model_dump(exclude_unset=True)
        update_dict["updated_by"] = updated_by
        update_dict["updated_at"] = datetime.utcnow()

        updated_plan = await self.repo.update(plan_id, update_dict)
        return self._to_plan_response(updated_plan)

    async def delete_plan(self, plan_id: int) -> bool:
        """Soft delete plan"""
        return await self.repo.delete(plan_id)

    # ===== PLAN WORKFLOW =====

    async def submit_for_review(
        self,
        plan_id: int,
        user_id: str
    ) -> PlanResponse:
        """
        Submit plan for review (DRAFT → UNDER_REVIEW)

        Performance: Uses eager loading to prevent N+1 queries
        """
        # Use eager loading for procedures - prevents N+1 query problem
        plan = await self.repo.get_by_id_with_relationships(
            plan_id,
            load_procedures=True
        )
        if not plan:
            raise ValueError("Plan not found")

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.SUBMIT_FOR_REVIEW,
            user_id
        )

        if not success:
            raise ValueError(error)

        updated_plan = await self.repo.update(plan_id, update_dict)
        return self._to_plan_response(updated_plan)

    async def approve_plan(
        self,
        plan_id: int,
        approved_by: str,
        approval_notes: Optional[str] = None
    ) -> PlanResponse:
        """Approve plan (UNDER_REVIEW → APPROVED)"""
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.APPROVE,
            approved_by,
            approval_notes=approval_notes
        )

        if not success:
            raise ValueError(error)

        updated_plan = await self.repo.update(plan_id, update_dict)

        # Publish event
        await self._publish_event(
            topic="plans.plan.approved",
            data={
                "plan_id": updated_plan.plan_id,
                "tenant_id": updated_plan.tenant_id,
                "plan_code": updated_plan.plan_code,
                "plan_name": updated_plan.plan_name,
                "plan_type": updated_plan.plan_type.value,
                "priority": updated_plan.priority.value,
                "status": updated_plan.status.value,
                "version": updated_plan.version,
                "approved_by_user_id": approved_by,
                "approval_date": updated_plan.approval_date.isoformat() if updated_plan.approval_date else None,
                "approval_notes": approval_notes,
                "plan_owner_user_id": updated_plan.plan_owner_user_id,
                "rto_hours": updated_plan.rto_hours,
                "rpo_hours": updated_plan.rpo_hours,
            }
        )

        return self._to_plan_response(updated_plan)

    async def activate_plan(
        self,
        plan_id: int,
        activated_by: str
    ) -> PlanResponse:
        """
        Activate plan (APPROVED → ACTIVE)

        Performance: Uses eager loading to prevent N+1 queries
        """
        # Use eager loading for contact lists - prevents N+1 query problem
        plan = await self.repo.get_by_id_with_relationships(
            plan_id,
            load_contacts=True
        )
        if not plan:
            raise ValueError("Plan not found")

        success, error, update_dict = execute_plan_transition(
            plan,
            PlanWorkflowAction.ACTIVATE,
            activated_by
        )

        if not success:
            raise ValueError(error)

        updated_plan = await self.repo.update(plan_id, update_dict)

        # Publish event
        await self._publish_event(
            topic="plans.plan.activated",
            data={
                "plan_id": updated_plan.plan_id,
                "tenant_id": updated_plan.tenant_id,
                "plan_code": updated_plan.plan_code,
                "plan_name": updated_plan.plan_name,
                "plan_type": updated_plan.plan_type.value,
                "priority": updated_plan.priority.value,
                "status": updated_plan.status.value,
                "version": updated_plan.version,
                "activated_by_user_id": activated_by,
                "plan_owner_user_id": updated_plan.plan_owner_user_id,
                "team_leader_user_id": updated_plan.team_leader_user_id,
                "rto_hours": updated_plan.rto_hours,
                "rpo_hours": updated_plan.rpo_hours,
                "mtpd_hours": updated_plan.mtpd_hours,
            }
        )

        return self._to_plan_response(updated_plan)

    # ===== PROCEDURE OPERATIONS =====

    async def add_procedure(
        self,
        plan_id: int,
        procedure_data: ProcedureCreate,
        created_by: str
    ) -> ProcedureResponse:
        """Add procedure to plan"""
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")

        if plan.status != PlanStatus.DRAFT:
            raise ValueError("Can only add procedures to draft plans")

        # Validate procedure dependencies
        if procedure_data.prerequisite_procedure_ids:
            # Check for self-reference
            is_valid, error_msg = ProcedureDependencyValidator.validate_no_self_reference(
                procedure_id=0,  # New procedure, ID not assigned yet
                prerequisite_ids=procedure_data.prerequisite_procedure_ids
            )
            if not is_valid:
                raise ValueError(error_msg)

            # Get existing procedures to validate dependencies
            existing_procs = await self.repo.get_procedures(plan_id)
            existing_procs_dict = [
                {
                    'procedure_id': p.procedure_id,
                    'prerequisite_procedure_ids': p.prerequisite_procedure_ids or []
                }
                for p in existing_procs
            ]

            # Use a temporary ID for validation (will be assigned by DB)
            temp_proc_id = max([p.procedure_id for p in existing_procs], default=0) + 1

            # Validate no circular dependencies
            is_valid, error_msg = ProcedureDependencyValidator.validate_dependencies(
                plan_id=plan_id,
                new_procedure_id=temp_proc_id,
                prerequisite_ids=procedure_data.prerequisite_procedure_ids,
                existing_procedures=existing_procs_dict
            )
            if not is_valid:
                raise ValueError(error_msg)

        procedure = Procedure(
            plan_id=plan_id,
            tenant_id=procedure_data.tenant_id,
            sequence=procedure_data.sequence,
            procedure_name=procedure_data.procedure_name,
            procedure_type=procedure_data.procedure_type,
            description=procedure_data.description,
            estimated_duration_minutes=procedure_data.estimated_duration_minutes,
            responsible_role=procedure_data.responsible_role,
            responsible_user_id=procedure_data.responsible_user_id,
            prerequisite_procedure_ids=procedure_data.prerequisite_procedure_ids,
            required_resources=procedure_data.required_resources,
            success_criteria=procedure_data.success_criteria,
            verification_checklist=procedure_data.verification_checklist,
            created_by=created_by,
        )

        created_procedure = await self.repo.add_procedure(procedure)
        return self._to_procedure_response(created_procedure)

    async def list_procedures(self, plan_id: int) -> List[ProcedureResponse]:
        """List all procedures for a plan"""
        procedures = await self.repo.get_procedures(plan_id)
        return [self._to_procedure_response(p) for p in procedures]

    async def update_procedure(
        self,
        procedure_id: int,
        procedure_data: ProcedureUpdate,
        updated_by: str
    ) -> Optional[ProcedureResponse]:
        """Update procedure"""
        procedure = await self.repo.get_procedure_by_id(procedure_id)
        if not procedure:
            return None

        # Check if parent plan is in draft status
        plan = await self.repo.get_by_id(procedure.plan_id)
        if plan.status != PlanStatus.DRAFT:
            raise ValueError("Can only update procedures in draft plans")

        # Validate procedure dependencies if prerequisites are being updated
        if procedure_data.prerequisite_procedure_ids is not None:
            # Check for self-reference
            is_valid, error_msg = ProcedureDependencyValidator.validate_no_self_reference(
                procedure_id=procedure_id,
                prerequisite_ids=procedure_data.prerequisite_procedure_ids
            )
            if not is_valid:
                raise ValueError(error_msg)

            # Get existing procedures to validate dependencies
            existing_procs = await self.repo.get_procedures(procedure.plan_id)
            existing_procs_dict = [
                {
                    'procedure_id': p.procedure_id,
                    'prerequisite_procedure_ids': p.prerequisite_procedure_ids or []
                }
                for p in existing_procs
                if p.procedure_id != procedure_id  # Exclude the procedure being updated
            ]

            # Validate no circular dependencies
            is_valid, error_msg = ProcedureDependencyValidator.validate_dependencies(
                plan_id=procedure.plan_id,
                new_procedure_id=procedure_id,
                prerequisite_ids=procedure_data.prerequisite_procedure_ids,
                existing_procedures=existing_procs_dict
            )
            if not is_valid:
                raise ValueError(error_msg)

        update_dict = procedure_data.model_dump(exclude_unset=True)
        update_dict["updated_by"] = updated_by
        update_dict["updated_at"] = datetime.utcnow()

        updated_procedure = await self.repo.update_procedure(procedure_id, update_dict)
        return self._to_procedure_response(updated_procedure)

    async def delete_procedure(self, procedure_id: int) -> bool:
        """Delete procedure"""
        return await self.repo.delete_procedure(procedure_id)

    # ===== RESOURCE OPERATIONS =====

    async def add_resource(
        self,
        plan_id: int,
        resource_data: ResourceCreate,
        created_by: str
    ) -> ResourceResponse:
        """Add resource to plan"""
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")

        resource = PlanResource(
            plan_id=plan_id,
            tenant_id=resource_data.tenant_id,
            resource_name=resource_data.resource_name,
            resource_type=resource_data.resource_type,
            availability_requirement=resource_data.availability_requirement,
            criticality=resource_data.criticality,
            description=resource_data.description,
            quantity_required=resource_data.quantity_required,
            location=resource_data.location,
            contact_person=resource_data.contact_person,
            contact_details=resource_data.contact_details,
            alternative_resources=resource_data.alternative_resources,
            created_by=created_by,
        )

        created_resource = await self.repo.add_resource(resource)
        return self._to_resource_response(created_resource)

    async def list_resources(self, plan_id: int) -> List[ResourceResponse]:
        """List all resources for a plan"""
        resources = await self.repo.get_resources(plan_id)
        return [self._to_resource_response(r) for r in resources]

    # ===== CONTACT LIST OPERATIONS =====

    async def add_contact_list(
        self,
        contact_list_data: ContactListCreate,
        created_by: str
    ) -> ContactListResponse:
        """Add contact list"""
        contact_list = ContactList(
            tenant_id=contact_list_data.tenant_id,
            plan_id=contact_list_data.plan_id,
            list_name=contact_list_data.list_name,
            list_type=contact_list_data.list_type,
            description=contact_list_data.description,
            contacts=contact_list_data.contacts,
            call_tree_structure=contact_list_data.call_tree_structure,
            created_by=created_by,
        )

        created_list = await self.repo.add_contact_list(contact_list)
        return self._to_contact_list_response(created_list)

    async def list_contact_lists(self, plan_id: int) -> List[ContactListResponse]:
        """List all contact lists for a plan"""
        lists = await self.repo.get_contact_lists(plan_id)
        return [self._to_contact_list_response(cl) for cl in lists]

    # ===== ACTIVATION OPERATIONS =====

    async def activate_for_incident(
        self,
        plan_id: int,
        activation_data: ActivationCreate,
        activated_by: str
    ) -> ActivationResponse:
        """Activate plan for incident"""
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")

        activation = PlanActivation(
            plan_id=plan_id,
            tenant_id=activation_data.tenant_id,
            activation_name=activation_data.activation_name,
            activation_type=activation_data.activation_type,
            trigger_event=activation_data.trigger_event,
            triggered_by_incident_id=activation_data.triggered_by_incident_id,
            activated_by_user_id=activated_by,
            target_rto_hours=plan.rto_hours,
        )

        created_activation = await self.repo.create_activation(activation)
        return self._to_activation_response(created_activation)

    async def list_activations(self, plan_id: int) -> List[ActivationResponse]:
        """List all activations for a plan"""
        activations = await self.repo.get_activations(plan_id)
        return [self._to_activation_response(a) for a in activations]

    # ===== REVIEW OPERATIONS =====

    async def create_review(
        self,
        plan_id: int,
        review_data: ReviewCreate,
        reviewed_by: str
    ) -> ReviewResponse:
        """Create plan review"""
        plan = await self.repo.get_by_id(plan_id)
        if not plan:
            raise ValueError("Plan not found")

        review = PlanReview(
            plan_id=plan_id,
            tenant_id=review_data.tenant_id,
            review_type=review_data.review_type,
            reviewed_by_user_id=reviewed_by,
            findings=review_data.findings,
            recommendations=review_data.recommendations,
            is_current=review_data.is_current,
            is_effective=review_data.is_effective,
            action_items=review_data.action_items,
        )

        created_review = await self.repo.create_review(review)

        # Update plan last review date
        next_review_date = calculate_next_review_date(
            datetime.utcnow(),
            plan.review_frequency.value
        )
        await self.repo.update(plan_id, {
            "last_review_date": datetime.utcnow(),
            "next_review_date": next_review_date
        })

        # Publish event
        await self._publish_event(
            topic="plans.review.completed",
            data={
                "review_id": created_review.review_id,
                "plan_id": plan_id,
                "tenant_id": created_review.tenant_id,
                "plan_code": plan.plan_code,
                "plan_name": plan.plan_name,
                "review_type": created_review.review_type.value,
                "reviewed_by_user_id": reviewed_by,
                "is_current": created_review.is_current,
                "is_effective": created_review.is_effective,
                "findings": created_review.findings,
                "recommendations": created_review.recommendations,
                "action_items": created_review.action_items,
                "review_date": created_review.review_date.isoformat() if created_review.review_date else None,
                "next_review_date": next_review_date.isoformat() if next_review_date else None,
            }
        )

        return self._to_review_response(created_review)

    async def list_reviews(self, plan_id: int) -> List[ReviewResponse]:
        """List all reviews for a plan"""
        reviews = await self.repo.get_reviews(plan_id)
        return [self._to_review_response(r) for r in reviews]

    # ===== HELPER METHODS =====

    def _to_plan_response(self, plan: Plan) -> PlanResponse:
        """Convert database model to response model"""
        return PlanResponse(
            plan_id=plan.plan_id,
            tenant_id=plan.tenant_id,
            plan_code=plan.plan_code,
            plan_name=plan.plan_name,
            plan_type=plan.plan_type,
            priority=plan.priority,
            status=plan.status,
            version=plan.version,
            objective=plan.objective,
            scope=plan.scope,
            rto_hours=plan.rto_hours,
            rpo_hours=plan.rpo_hours,
            mtpd_hours=plan.mtpd_hours,
            plan_owner_user_id=plan.plan_owner_user_id,
            team_leader_user_id=plan.team_leader_user_id,
            review_frequency=plan.review_frequency,
            last_review_date=plan.last_review_date,
            next_review_date=plan.next_review_date,
            last_test_date=plan.last_test_date,
            next_test_date=plan.next_test_date,
            approved_by_user_id=plan.approved_by_user_id,
            approval_date=plan.approval_date,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )

    def _to_procedure_response(self, procedure: Procedure) -> ProcedureResponse:
        """Convert procedure to response model"""
        return ProcedureResponse(
            procedure_id=procedure.procedure_id,
            plan_id=procedure.plan_id,
            sequence=procedure.sequence,
            procedure_name=procedure.procedure_name,
            procedure_type=procedure.procedure_type,
            description=procedure.description,
            estimated_duration_minutes=procedure.estimated_duration_minutes,
            responsible_role=procedure.responsible_role,
            responsible_user_id=procedure.responsible_user_id,
            prerequisite_procedure_ids=procedure.prerequisite_procedure_ids,
            created_at=procedure.created_at,
        )

    def _to_resource_response(self, resource: PlanResource) -> ResourceResponse:
        """Convert resource to response model"""
        return ResourceResponse(
            resource_id=resource.resource_id,
            plan_id=resource.plan_id,
            resource_name=resource.resource_name,
            resource_type=resource.resource_type,
            availability_requirement=resource.availability_requirement,
            criticality=resource.criticality,
            quantity_required=resource.quantity_required,
            location=resource.location,
            created_at=resource.created_at,
        )

    def _to_contact_list_response(self, contact_list: ContactList) -> ContactListResponse:
        """Convert contact list to response model"""
        return ContactListResponse(
            contact_list_id=contact_list.contact_list_id,
            tenant_id=contact_list.tenant_id,
            plan_id=contact_list.plan_id,
            list_name=contact_list.list_name,
            list_type=contact_list.list_type,
            contacts=contact_list.contacts,
            last_verified_date=contact_list.last_verified_date,
            created_at=contact_list.created_at,
        )

    def _to_activation_response(self, activation: PlanActivation) -> ActivationResponse:
        """Convert activation to response model"""
        return ActivationResponse(
            activation_id=activation.activation_id,
            plan_id=activation.plan_id,
            activation_name=activation.activation_name,
            activation_type=activation.activation_type,
            activation_datetime=activation.activation_datetime,
            activated_by_user_id=activation.activated_by_user_id,
            actual_recovery_time_hours=activation.actual_recovery_time_hours,
            rto_achieved=activation.rto_achieved,
            effectiveness_rating=activation.effectiveness_rating,
            summary=activation.summary,
        )

    def _to_review_response(self, review: PlanReview) -> ReviewResponse:
        """Convert review to response model"""
        return ReviewResponse(
            review_id=review.review_id,
            plan_id=review.plan_id,
            review_date=review.review_date,
            review_type=review.review_type,
            reviewed_by_user_id=review.reviewed_by_user_id,
            is_current=review.is_current,
            is_effective=review.is_effective,
            findings=review.findings,
            recommendations=review.recommendations,
            approved=review.approved,
            created_at=review.created_at,
        )
