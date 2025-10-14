"""
Repository Tests
Tests for PlanRepository data access layer
"""

import pytest
from datetime import datetime
from sqlalchemy import select

from plans_service.repositories.plan_repository import PlanRepository
from plans_service.models.database import Plan, Procedure, PlanResource, ContactList, PlanActivation, PlanReview
from plans_service.models.domain import (
    PlanType, PlanPriority, PlanStatus, ProcedureType,
    ResourceType, ResourceCriticality, AvailabilityRequirement,
    ReviewFrequency, ContactListType, ActivationType, ReviewType
)


class TestPlanRepository:
    """Test suite for PlanRepository"""

    @pytest.mark.asyncio
    async def test_create_plan(self, db_session, sample_plan_data):
        """Test creating a plan"""
        repo = PlanRepository(db_session)
        plan = Plan(**sample_plan_data)

        created_plan = await repo.create(plan)

        assert created_plan.plan_id is not None
        assert created_plan.plan_name == sample_plan_data["plan_name"]
        assert created_plan.tenant_id == sample_plan_data["tenant_id"]
        assert created_plan.status == PlanStatus.DRAFT

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session, sample_plan):
        """Test getting plan by ID"""
        repo = PlanRepository(db_session)

        retrieved_plan = await repo.get_by_id(sample_plan.plan_id)

        assert retrieved_plan is not None
        assert retrieved_plan.plan_id == sample_plan.plan_id
        assert retrieved_plan.plan_name == sample_plan.plan_name

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """Test getting non-existent plan returns None"""
        repo = PlanRepository(db_session)

        retrieved_plan = await repo.get_by_id(99999)

        assert retrieved_plan is None

    @pytest.mark.asyncio
    async def test_get_by_code(self, db_session, sample_plan):
        """Test getting plan by plan_code"""
        repo = PlanRepository(db_session)

        retrieved_plan = await repo.get_by_code(sample_plan.plan_code)

        assert retrieved_plan is not None
        assert retrieved_plan.plan_id == sample_plan.plan_id
        assert retrieved_plan.plan_code == sample_plan.plan_code

    @pytest.mark.asyncio
    async def test_get_with_relationships(self, db_session, sample_plan, sample_procedure):
        """Test eager loading prevents N+1 queries"""
        repo = PlanRepository(db_session)

        # Get plan with procedures loaded
        plan = await repo.get_by_id_with_relationships(
            sample_plan.plan_id,
            load_procedures=True
        )

        assert plan is not None
        # Access procedures - should not trigger additional query
        assert len(plan.procedures) == 1
        assert plan.procedures[0].procedure_id == sample_procedure.procedure_id

    @pytest.mark.asyncio
    async def test_get_with_multiple_relationships(self, db_session, sample_plan_data, sample_procedure_data, sample_resource_data):
        """Test loading multiple relationships"""
        repo = PlanRepository(db_session)

        # Create plan
        plan = Plan(**sample_plan_data)
        db_session.add(plan)
        await db_session.commit()
        await db_session.refresh(plan)

        # Add procedure
        procedure_data = sample_procedure_data.copy()
        procedure_data["plan_id"] = plan.plan_id
        procedure = Procedure(**procedure_data)
        db_session.add(procedure)

        # Add resource
        resource_data = sample_resource_data.copy()
        resource_data["plan_id"] = plan.plan_id
        resource = PlanResource(**resource_data)
        db_session.add(resource)

        await db_session.commit()

        # Get plan with both relationships
        loaded_plan = await repo.get_by_id_with_relationships(
            plan.plan_id,
            load_procedures=True,
            load_resources=True
        )

        assert loaded_plan is not None
        assert len(loaded_plan.procedures) == 1
        assert len(loaded_plan.resources) == 1

    @pytest.mark.asyncio
    async def test_list_by_tenant(self, db_session, sample_plan_data):
        """Test listing plans by tenant"""
        repo = PlanRepository(db_session)

        # Create multiple plans
        plan1_data = sample_plan_data.copy()
        plan1_data["plan_code"] = "PLAN-001"
        plan1 = Plan(**plan1_data)
        db_session.add(plan1)

        plan2_data = sample_plan_data.copy()
        plan2_data["plan_code"] = "PLAN-002"
        plan2 = Plan(**plan2_data)
        db_session.add(plan2)

        await db_session.commit()

        # List plans
        plans = await repo.list_by_tenant(sample_plan_data["tenant_id"])

        assert len(plans) == 2

    @pytest.mark.asyncio
    async def test_list_by_tenant_with_filters(self, db_session, sample_plan_data):
        """Test listing plans with filters"""
        repo = PlanRepository(db_session)

        # Create plans with different types
        plan1_data = sample_plan_data.copy()
        plan1_data["plan_code"] = "PLAN-001"
        plan1_data["plan_type"] = PlanType.BUSINESS_CONTINUITY
        plan1 = Plan(**plan1_data)
        db_session.add(plan1)

        plan2_data = sample_plan_data.copy()
        plan2_data["plan_code"] = "PLAN-002"
        plan2_data["plan_type"] = PlanType.DISASTER_RECOVERY
        plan2 = Plan(**plan2_data)
        db_session.add(plan2)

        await db_session.commit()

        # Filter by plan type
        plans = await repo.list_by_tenant(
            sample_plan_data["tenant_id"],
            plan_type=PlanType.BUSINESS_CONTINUITY
        )

        assert len(plans) == 1
        assert plans[0].plan_type == PlanType.BUSINESS_CONTINUITY

    @pytest.mark.asyncio
    async def test_list_by_tenant_with_status_filter(self, db_session, sample_plan_data):
        """Test filtering by status"""
        repo = PlanRepository(db_session)

        # Create plans with different statuses
        plan1_data = sample_plan_data.copy()
        plan1_data["plan_code"] = "PLAN-001"
        plan1_data["status"] = PlanStatus.DRAFT
        plan1 = Plan(**plan1_data)
        db_session.add(plan1)

        plan2_data = sample_plan_data.copy()
        plan2_data["plan_code"] = "PLAN-002"
        plan2_data["status"] = PlanStatus.APPROVED
        plan2 = Plan(**plan2_data)
        db_session.add(plan2)

        await db_session.commit()

        # Filter by status
        plans = await repo.list_by_tenant(
            sample_plan_data["tenant_id"],
            status=PlanStatus.APPROVED
        )

        assert len(plans) == 1
        assert plans[0].status == PlanStatus.APPROVED

    @pytest.mark.asyncio
    async def test_list_by_tenant_pagination(self, db_session, sample_plan_data):
        """Test pagination works correctly"""
        repo = PlanRepository(db_session)

        # Create 5 plans
        for i in range(5):
            plan_data = sample_plan_data.copy()
            plan_data["plan_code"] = f"PLAN-{i:03d}"
            plan = Plan(**plan_data)
            db_session.add(plan)

        await db_session.commit()

        # Get first 2
        plans_page1 = await repo.list_by_tenant(
            sample_plan_data["tenant_id"],
            skip=0,
            limit=2
        )

        # Get next 2
        plans_page2 = await repo.list_by_tenant(
            sample_plan_data["tenant_id"],
            skip=2,
            limit=2
        )

        assert len(plans_page1) == 2
        assert len(plans_page2) == 2
        # Ensure different plans
        assert plans_page1[0].plan_id != plans_page2[0].plan_id

    @pytest.mark.asyncio
    async def test_tenant_filtering(self, db_session, sample_plan_data):
        """Test tenant isolation"""
        repo = PlanRepository(db_session)

        # Create plan for tenant1
        plan1_data = sample_plan_data.copy()
        plan1_data["tenant_id"] = "tenant1"
        plan1_data["plan_code"] = "PLAN-001"
        plan1 = Plan(**plan1_data)
        db_session.add(plan1)

        # Create plan for tenant2
        plan2_data = sample_plan_data.copy()
        plan2_data["tenant_id"] = "tenant2"
        plan2_data["plan_code"] = "PLAN-002"
        plan2 = Plan(**plan2_data)
        db_session.add(plan2)

        await db_session.commit()

        # Query for tenant1
        plans = await repo.list_by_tenant("tenant1")

        assert len(plans) == 1
        assert plans[0].tenant_id == "tenant1"

    @pytest.mark.asyncio
    async def test_update_plan(self, db_session, sample_plan):
        """Test updating a plan"""
        repo = PlanRepository(db_session)

        update_data = {
            "plan_name": "Updated Plan Name",
            "priority": PlanPriority.CRITICAL
        }

        updated_plan = await repo.update(sample_plan.plan_id, update_data)

        assert updated_plan is not None
        assert updated_plan.plan_name == "Updated Plan Name"
        assert updated_plan.priority == PlanPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_update_nonexistent_plan(self, db_session):
        """Test updating non-existent plan returns None"""
        repo = PlanRepository(db_session)

        updated_plan = await repo.update(99999, {"plan_name": "Test"})

        assert updated_plan is None

    @pytest.mark.asyncio
    async def test_delete_plan(self, db_session, sample_plan):
        """Test soft delete plan"""
        repo = PlanRepository(db_session)

        success = await repo.delete(sample_plan.plan_id)

        assert success is True

        # Verify plan is marked inactive
        deleted_plan = await repo.get_by_id(sample_plan.plan_id)
        assert deleted_plan.active is False
        assert deleted_plan.status == PlanStatus.ARCHIVED

    @pytest.mark.asyncio
    async def test_delete_nonexistent_plan(self, db_session):
        """Test deleting non-existent plan returns False"""
        repo = PlanRepository(db_session)

        success = await repo.delete(99999)

        assert success is False

    @pytest.mark.asyncio
    async def test_add_procedure(self, db_session, sample_plan, sample_procedure_data):
        """Test adding procedure to plan"""
        repo = PlanRepository(db_session)

        procedure_data = sample_procedure_data.copy()
        procedure_data["plan_id"] = sample_plan.plan_id
        procedure = Procedure(**procedure_data)

        added_procedure = await repo.add_procedure(procedure)

        assert added_procedure.procedure_id is not None
        assert added_procedure.plan_id == sample_plan.plan_id

    @pytest.mark.asyncio
    async def test_get_procedures(self, db_session, sample_plan, sample_procedure):
        """Test getting procedures for a plan"""
        repo = PlanRepository(db_session)

        procedures = await repo.get_procedures(sample_plan.plan_id)

        assert len(procedures) == 1
        assert procedures[0].procedure_id == sample_procedure.procedure_id

    @pytest.mark.asyncio
    async def test_get_procedures_ordered(self, db_session, sample_plan, sample_procedure_data):
        """Test procedures are ordered by sequence"""
        repo = PlanRepository(db_session)

        # Add procedures with different sequences
        proc1_data = sample_procedure_data.copy()
        proc1_data["plan_id"] = sample_plan.plan_id
        proc1_data["sequence"] = 30
        proc1_data["procedure_name"] = "Third"
        proc1 = Procedure(**proc1_data)
        db_session.add(proc1)

        proc2_data = sample_procedure_data.copy()
        proc2_data["plan_id"] = sample_plan.plan_id
        proc2_data["sequence"] = 10
        proc2_data["procedure_name"] = "First"
        proc2 = Procedure(**proc2_data)
        db_session.add(proc2)

        proc3_data = sample_procedure_data.copy()
        proc3_data["plan_id"] = sample_plan.plan_id
        proc3_data["sequence"] = 20
        proc3_data["procedure_name"] = "Second"
        proc3 = Procedure(**proc3_data)
        db_session.add(proc3)

        await db_session.commit()

        # Get procedures
        procedures = await repo.get_procedures(sample_plan.plan_id)

        assert len(procedures) == 3
        assert procedures[0].sequence == 10
        assert procedures[1].sequence == 20
        assert procedures[2].sequence == 30

    @pytest.mark.asyncio
    async def test_get_procedure_by_id(self, db_session, sample_procedure):
        """Test getting procedure by ID"""
        repo = PlanRepository(db_session)

        procedure = await repo.get_procedure_by_id(sample_procedure.procedure_id)

        assert procedure is not None
        assert procedure.procedure_id == sample_procedure.procedure_id

    @pytest.mark.asyncio
    async def test_update_procedure(self, db_session, sample_procedure):
        """Test updating procedure"""
        repo = PlanRepository(db_session)

        update_data = {
            "procedure_name": "Updated Procedure",
            "sequence": 100
        }

        updated = await repo.update_procedure(sample_procedure.procedure_id, update_data)

        assert updated is not None
        assert updated.procedure_name == "Updated Procedure"
        assert updated.sequence == 100

    @pytest.mark.asyncio
    async def test_delete_procedure(self, db_session, sample_procedure):
        """Test soft delete procedure"""
        repo = PlanRepository(db_session)

        success = await repo.delete_procedure(sample_procedure.procedure_id)

        assert success is True

        # Verify procedure is marked inactive
        deleted = await repo.get_procedure_by_id(sample_procedure.procedure_id)
        assert deleted.active is False

    @pytest.mark.asyncio
    async def test_add_resource(self, db_session, sample_plan, sample_resource_data):
        """Test adding resource to plan"""
        repo = PlanRepository(db_session)

        resource_data = sample_resource_data.copy()
        resource_data["plan_id"] = sample_plan.plan_id
        resource = PlanResource(**resource_data)

        added = await repo.add_resource(resource)

        assert added.resource_id is not None
        assert added.plan_id == sample_plan.plan_id

    @pytest.mark.asyncio
    async def test_get_resources(self, db_session, sample_plan, sample_resource_data):
        """Test getting resources for a plan"""
        repo = PlanRepository(db_session)

        # Add resource
        resource_data = sample_resource_data.copy()
        resource_data["plan_id"] = sample_plan.plan_id
        resource = PlanResource(**resource_data)
        db_session.add(resource)
        await db_session.commit()

        # Get resources
        resources = await repo.get_resources(sample_plan.plan_id)

        assert len(resources) == 1

    @pytest.mark.asyncio
    async def test_get_resource_by_id(self, db_session, sample_plan, sample_resource_data):
        """Test getting resource by ID"""
        repo = PlanRepository(db_session)

        # Add resource
        resource_data = sample_resource_data.copy()
        resource_data["plan_id"] = sample_plan.plan_id
        resource = PlanResource(**resource_data)
        db_session.add(resource)
        await db_session.commit()
        await db_session.refresh(resource)

        # Get by ID
        retrieved = await repo.get_resource_by_id(resource.resource_id)

        assert retrieved is not None
        assert retrieved.resource_id == resource.resource_id

    @pytest.mark.asyncio
    async def test_add_contact_list(self, db_session, sample_plan, sample_contact_list_data):
        """Test adding contact list"""
        repo = PlanRepository(db_session)

        contact_data = sample_contact_list_data.copy()
        contact_data["plan_id"] = sample_plan.plan_id
        contact_list = ContactList(**contact_data)

        added = await repo.add_contact_list(contact_list)

        assert added.contact_list_id is not None
        assert added.plan_id == sample_plan.plan_id

    @pytest.mark.asyncio
    async def test_get_contact_lists(self, db_session, sample_plan, sample_contact_list_data):
        """Test getting contact lists for a plan"""
        repo = PlanRepository(db_session)

        # Add contact list
        contact_data = sample_contact_list_data.copy()
        contact_data["plan_id"] = sample_plan.plan_id
        contact_list = ContactList(**contact_data)
        db_session.add(contact_list)
        await db_session.commit()

        # Get contact lists
        lists = await repo.get_contact_lists(sample_plan.plan_id)

        assert len(lists) == 1

    @pytest.mark.asyncio
    async def test_create_activation(self, db_session, sample_plan):
        """Test creating plan activation"""
        repo = PlanRepository(db_session)

        activation = PlanActivation(
            plan_id=sample_plan.plan_id,
            tenant_id=sample_plan.tenant_id,
            activation_name="Test Exercise 2024",
            activation_type=ActivationType.TEST_EXERCISE,
            activated_by_user_id="user_001"
        )

        created = await repo.create_activation(activation)

        assert created.activation_id is not None
        assert created.plan_id == sample_plan.plan_id

    @pytest.mark.asyncio
    async def test_get_activations(self, db_session, sample_plan):
        """Test getting activations for a plan"""
        repo = PlanRepository(db_session)

        # Add activation
        activation = PlanActivation(
            plan_id=sample_plan.plan_id,
            tenant_id=sample_plan.tenant_id,
            activation_name="Test Exercise",
            activation_type=ActivationType.TEST_EXERCISE,
            activated_by_user_id="user_001"
        )
        db_session.add(activation)
        await db_session.commit()

        # Get activations
        activations = await repo.get_activations(sample_plan.plan_id)

        assert len(activations) == 1

    @pytest.mark.asyncio
    async def test_create_review(self, db_session, sample_plan):
        """Test creating plan review"""
        repo = PlanRepository(db_session)

        review = PlanReview(
            plan_id=sample_plan.plan_id,
            tenant_id=sample_plan.tenant_id,
            review_type=ReviewType.SCHEDULED,
            reviewed_by_user_id="user_001",
            is_current=True,
            is_effective=True
        )

        created = await repo.create_review(review)

        assert created.review_id is not None
        assert created.plan_id == sample_plan.plan_id

    @pytest.mark.asyncio
    async def test_get_reviews(self, db_session, sample_plan):
        """Test getting reviews for a plan"""
        repo = PlanRepository(db_session)

        # Add review
        review = PlanReview(
            plan_id=sample_plan.plan_id,
            tenant_id=sample_plan.tenant_id,
            review_type=ReviewType.SCHEDULED,
            reviewed_by_user_id="user_001"
        )
        db_session.add(review)
        await db_session.commit()

        # Get reviews
        reviews = await repo.get_reviews(sample_plan.plan_id)

        assert len(reviews) == 1
