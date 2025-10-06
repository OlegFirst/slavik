"""
Pytest Configuration and Fixtures for BIA Service Tests
Comprehensive test fixtures for all BIA service test scenarios
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator, Dict, Any, List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from models.database import Base, BIAProcessDB
from models.domain import BIAProcess, BIAProcessCreate, Dependency
from models.enums import (
    CriticalityLevel, ProcessStatus, ReputationalImpact,
    RegulatoryImpact, PatientSafetyImpact, WHOTier,
    GeographicalScope, IndustryType
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    """Create test database engine with in-memory SQLite"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=NullPool,
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
def tenant_id() -> str:
    """Test tenant ID"""
    return "test-tenant-123"


@pytest.fixture
def user_id() -> str:
    """Test user ID"""
    return "test-user-456"


@pytest.fixture
def mock_cache():
    """Mock Redis cache"""
    cache_mock = AsyncMock()
    cache_mock.get.return_value = None
    cache_mock.set.return_value = True
    cache_mock.delete.return_value = True
    cache_mock.clear.return_value = True
    return cache_mock


@pytest.fixture
def mock_eventbus():
    """Mock event bus for testing event publishing"""
    eventbus_mock = AsyncMock()
    eventbus_mock.publish.return_value = True
    return eventbus_mock


@pytest.fixture
def mock_audit_logger():
    """Mock audit logger"""
    audit_mock = AsyncMock()
    audit_mock.log_create.return_value = None
    audit_mock.log_update.return_value = None
    audit_mock.log_delete.return_value = None
    audit_mock.log_state_transition.return_value = None
    return audit_mock


@pytest.fixture
def sample_dependencies() -> List[Dependency]:
    """Sample dependencies for BIA processes"""
    return [
        Dependency(
            type="technology",
            name="ERP System",
            criticality=5,
            required=True
        ),
        Dependency(
            type="people",
            name="IT Team",
            criticality=4,
            required=True
        ),
        Dependency(
            type="facility",
            name="Data Center",
            criticality=5,
            required=True
        )
    ]


@pytest.fixture
def sample_financial_impact() -> Dict[str, float]:
    """Sample financial impact timeline"""
    return {
        "1_hour": 5000.0,
        "4_hours": 25000.0,
        "8_hours": 60000.0,
        "24_hours": 200000.0,
        "3_days": 750000.0,
        "1_week": 2000000.0,
        "1_month": 10000000.0
    }


@pytest.fixture
def sample_operational_impact() -> Dict[str, str]:
    """Sample operational impact descriptions"""
    return {
        "1_hour": "Minor delays in processing",
        "4_hours": "Significant backlog building",
        "8_hours": "Cannot process new orders",
        "24_hours": "Critical service disruption",
        "3_days": "Customer exodus begins",
        "1_week": "Major reputation damage",
        "1_month": "Business viability threatened"
    }


@pytest.fixture
def sample_personnel_requirements() -> Dict[str, Any]:
    """Sample personnel requirements"""
    return {
        "roles": ["System Administrator", "Database Manager", "Support Lead"],
        "min_staff": 5,
        "skills": ["SQL", "Linux", "Network Administration"],
        "certifications": ["ITIL", "CompTIA Security+"]
    }


@pytest.fixture
def sample_recovery_strategies() -> List[Dict[str, Any]]:
    """Sample recovery strategies"""
    return [
        {
            "strategy": "hot_site",
            "description": "Failover to hot standby site",
            "cost": 50000.0,
            "rto": 2,
            "effectiveness": 95.0
        },
        {
            "strategy": "cloud_backup",
            "description": "AWS multi-region backup",
            "cost": 10000.0,
            "rto": 4,
            "effectiveness": 90.0
        }
    ]


@pytest.fixture
def sample_bia_create_data(
    tenant_id: str,
    sample_dependencies: List[Dependency],
    sample_financial_impact: Dict[str, float],
    sample_operational_impact: Dict[str, str],
    sample_personnel_requirements: Dict[str, Any],
    sample_recovery_strategies: List[Dict[str, Any]]
) -> BIAProcessCreate:
    """Sample BIA process creation data"""
    return BIAProcessCreate(
        tenant_id=tenant_id,
        name="Core Payment Processing",
        description="Critical payment processing system for all transactions",
        department="IT Operations",
        process_owner="john.doe@example.com",
        criticality=CriticalityLevel.CRITICAL,
        industry=IndustryType.FINANCIAL,
        geographical_scope=GeographicalScope.GLOBAL,
        rto_hours=4,
        rpo_hours=1,
        mtpd_hours=8,
        financial_impact=sample_financial_impact,
        operational_impact=sample_operational_impact,
        reputational_impact=ReputationalImpact.SEVERE,
        regulatory_impact=RegulatoryImpact.MAJOR_FINES,
        dependencies=sample_dependencies,
        compliance_objective="Ensure ISO 22301 compliance for critical payment processing",
        legal_regulatory_requirements=["PCI-DSS", "SOX", "GDPR"],
        personnel_requirements=sample_personnel_requirements,
        recovery_strategies=sample_recovery_strategies,
        alternative_procedures=["Manual transaction processing", "Offline backup system"],
        workaround_capacity=30.0,
        upstream_processes=["Customer Order Entry"],
        downstream_processes=["Invoice Generation", "Reporting"],
        minimum_resource_level={"staff": 3, "systems": ["Database", "Payment Gateway"]},
        bia_assessor="Jane Smith"
    )


@pytest.fixture
def sample_healthcare_bia_create(tenant_id: str) -> BIAProcessCreate:
    """Sample healthcare BIA process with WHO tier"""
    return BIAProcessCreate(
        tenant_id=tenant_id,
        name="Emergency Department Patient Care",
        description="Critical emergency department patient care process",
        department="Emergency Medicine",
        process_owner="dr.smith@hospital.com",
        criticality=CriticalityLevel.CRITICAL,
        industry=IndustryType.HEALTHCARE,
        geographical_scope=GeographicalScope.REGIONAL,
        rto_hours=1,
        rpo_hours=0,
        mtpd_hours=2,
        patient_safety_impact=PatientSafetyImpact.LIFE_THREATENING,
        financial_impact={"1_hour": 100000.0, "4_hours": 500000.0},
        operational_impact={"1_hour": "Cannot accept emergency patients"},
        who_tier=WHOTier.TIER_1_IMMEDIATE,
        compliance_objective="Maintain continuous emergency care capability",
        legal_regulatory_requirements=["HIPAA", "EMTALA"],
        recovery_strategies=[
            {
                "strategy": "backup_facility",
                "description": "Redirect to partner hospital",
                "cost": 100000.0,
                "rto": 1,
                "effectiveness": 85.0
            }
        ]
    )


@pytest.fixture
async def sample_bia_process_db(
    db_session: AsyncSession,
    tenant_id: str,
    sample_dependencies: List[Dependency],
    sample_financial_impact: Dict[str, float]
) -> BIAProcessDB:
    """Create a sample BIA process in the database"""
    process_db = BIAProcessDB(
        tenant_id=tenant_id,
        name="Sample Process",
        description="Sample BIA process for testing",
        department="IT",
        process_owner="owner@example.com",
        criticality=CriticalityLevel.HIGH.value,
        criticality_score=4,
        industry=IndustryType.TECHNOLOGY.value,
        geographical_scope=GeographicalScope.NATIONAL.value,
        rto_hours=8,
        rpo_hours=2,
        mtpd_hours=24,
        financial_impact=sample_financial_impact,
        operational_impact={"8_hours": "Moderate impact"},
        reputational_impact=ReputationalImpact.MODERATE.value,
        dependencies=[dep.dict() for dep in sample_dependencies],
        status=ProcessStatus.DRAFT.value,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(process_db)
    await db_session.commit()
    await db_session.refresh(process_db)
    return process_db


@pytest.fixture
def sample_bulk_bia_processes(tenant_id: str) -> List[BIAProcessCreate]:
    """Sample bulk BIA processes for testing bulk operations"""
    return [
        BIAProcessCreate(
            tenant_id=tenant_id,
            name=f"Process {i}",
            description=f"Test process {i}",
            department="IT",
            criticality=CriticalityLevel.HIGH if i % 2 == 0 else CriticalityLevel.MEDIUM,
            industry=IndustryType.TECHNOLOGY,
            rto_hours=4 + i,
            rpo_hours=1,
            mtpd_hours=8 + i,
            financial_impact={"24_hours": 10000.0 * i}
        )
        for i in range(1, 11)
    ]


@pytest.fixture
def invalid_time_objectives_data(tenant_id: str) -> Dict[str, Any]:
    """Invalid BIA data with RTO < RPO (should fail validation)"""
    return {
        "tenant_id": tenant_id,
        "name": "Invalid Process",
        "criticality": CriticalityLevel.HIGH,
        "industry": IndustryType.TECHNOLOGY,
        "rto_hours": 2,  # RTO < RPO (invalid!)
        "rpo_hours": 4,
        "mtpd_hours": 8
    }


@pytest.fixture
def invalid_mtpd_data(tenant_id: str) -> Dict[str, Any]:
    """Invalid BIA data with MTPD < RTO (should fail validation)"""
    return {
        "tenant_id": tenant_id,
        "name": "Invalid MTPD Process",
        "criticality": CriticalityLevel.CRITICAL,
        "industry": IndustryType.FINANCIAL,
        "rto_hours": 8,
        "rpo_hours": 2,
        "mtpd_hours": 4  # MTPD < RTO (invalid!)
    }


@pytest.fixture
def invalid_financial_impact_timeline() -> Dict[str, float]:
    """Invalid financial impact that doesn't increase over time"""
    return {
        "1_hour": 100000.0,
        "4_hours": 50000.0,  # Decreases! Invalid
        "24_hours": 200000.0
    }


@pytest.fixture
def sample_critical_process_data(tenant_id: str) -> BIAProcessCreate:
    """Sample critical BIA process for testing criticality rules"""
    return BIAProcessCreate(
        tenant_id=tenant_id,
        name="Critical Infrastructure Process",
        criticality=CriticalityLevel.CRITICAL,
        industry=IndustryType.INFRASTRUCTURE,
        rto_hours=2,
        rpo_hours=0,
        mtpd_hours=4,
        financial_impact={"1_hour": 50000.0, "24_hours": 1000000.0},
        recovery_strategies=[
            {
                "strategy": "hot_standby",
                "description": "Immediate failover",
                "cost": 200000.0,
                "rto": 1,
                "effectiveness": 99.0
            }
        ],
        alternative_procedures=["Manual emergency procedures"],
        dependencies=[
            Dependency(type="technology", name="Core System", criticality=5, required=True)
        ]
    )
