"""
Pytest Configuration and Fixtures
Shared test fixtures for Plans Service tests
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from plans_service.models.database import Base, Plan, Procedure, PlanResource, ContactList, PlanActivation, PlanReview
from plans_service.models.domain import (
    PlanType, PlanPriority, PlanStatus, ProcedureType,
    ResourceType, ResourceCriticality, AvailabilityRequirement,
    ReviewFrequency, ContactListType, ActivationType, ReviewType
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_plan_data():
    """Sample plan data for tests"""
    return {
        "tenant_id": "test-tenant",
        "plan_code": "TEST-PLAN-001",
        "plan_name": "Test Business Continuity Plan",
        "plan_type": PlanType.BUSINESS_CONTINUITY,
        "priority": PlanPriority.HIGH,
        "status": PlanStatus.DRAFT,
        "version": "1.0",
        "objective": "Ensure business continuity during major disruptions",
        "scope": "Covers all critical business processes",
        "rto_hours": 24,
        "rpo_hours": 4,
        "mtpd_hours": 48,
        "plan_owner_user_id": "user_001",
        "team_leader_user_id": "user_002",
        "review_frequency": ReviewFrequency.ANNUALLY,
        "active": True
    }


@pytest.fixture
def sample_procedure_data():
    """Sample procedure data for tests"""
    return {
        "tenant_id": "test-tenant",
        "procedure_name": "Activate Emergency Response Team",
        "procedure_type": ProcedureType.IMMEDIATE_RESPONSE,
        "sequence": 10,
        "description": "Immediately contact and activate the emergency response team",
        "estimated_duration_minutes": 30,
        "responsible_role": "Emergency Coordinator",
        "responsible_user_id": "user_003",
        "active": True
    }


@pytest.fixture
def sample_resource_data():
    """Sample resource data for tests"""
    return {
        "tenant_id": "test-tenant",
        "resource_name": "Backup Server Infrastructure",
        "resource_type": ResourceType.TECHNOLOGY,
        "availability_requirement": AvailabilityRequirement.IMMEDIATE,
        "criticality": ResourceCriticality.CRITICAL,
        "description": "Cloud-based backup server infrastructure",
        "quantity_required": 2,
        "location": "AWS us-east-1",
        "contact_person": "IT Manager",
        "active": True
    }


@pytest.fixture
def sample_contact_list_data():
    """Sample contact list data for tests"""
    return {
        "tenant_id": "test-tenant",
        "list_name": "Emergency Response Contacts",
        "list_type": ContactListType.INTERNAL,
        "description": "Internal emergency response team contacts",
        "contacts": [
            {
                "name": "John Doe",
                "role": "Emergency Coordinator",
                "primary_phone": "+1-555-0001",
                "email": "john.doe@company.com",
                "notification_priority": 1
            },
            {
                "name": "Jane Smith",
                "role": "Backup Coordinator",
                "primary_phone": "+1-555-0002",
                "email": "jane.smith@company.com",
                "notification_priority": 2
            }
        ],
        "active": True
    }


@pytest.fixture
async def sample_plan(db_session, sample_plan_data):
    """Create a sample plan in the database"""
    plan = Plan(**sample_plan_data)
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)
    return plan


@pytest.fixture
async def sample_procedure(db_session, sample_plan, sample_procedure_data):
    """Create a sample procedure in the database"""
    procedure_data = sample_procedure_data.copy()
    procedure_data["plan_id"] = sample_plan.plan_id

    procedure = Procedure(**procedure_data)
    db_session.add(procedure)
    await db_session.commit()
    await db_session.refresh(procedure)
    return procedure


@pytest.fixture
def sample_procedures_with_dependencies():
    """Sample procedures with dependency relationships for testing"""
    return [
        {
            "procedure_id": 1,
            "procedure_name": "Assess Situation",
            "prerequisite_procedure_ids": []
        },
        {
            "procedure_id": 2,
            "procedure_name": "Notify Team",
            "prerequisite_procedure_ids": [1]
        },
        {
            "procedure_id": 3,
            "procedure_name": "Activate Backup Systems",
            "prerequisite_procedure_ids": [1]
        },
        {
            "procedure_id": 4,
            "procedure_name": "Execute Recovery",
            "prerequisite_procedure_ids": [2, 3]
        }
    ]


@pytest.fixture
def sample_procedures_with_cycle():
    """Sample procedures with circular dependency for testing"""
    return [
        {
            "procedure_id": 1,
            "procedure_name": "Procedure A",
            "prerequisite_procedure_ids": [3]
        },
        {
            "procedure_id": 2,
            "procedure_name": "Procedure B",
            "prerequisite_procedure_ids": [1]
        },
        {
            "procedure_id": 3,
            "procedure_name": "Procedure C",
            "prerequisite_procedure_ids": [2]
        }
    ]
