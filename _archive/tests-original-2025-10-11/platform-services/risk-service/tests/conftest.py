"""
Test Configuration and Fixtures
Provides shared test fixtures for all test modules
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import sys
from pathlib import Path

# Add shared models to path
shared_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Import common models
import importlib.util
spec = importlib.util.spec_from_file_location("common", shared_path / "models" / "common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
User = common.User

from models.domain import (
    Risk,
    RiskCategory,
    RiskLikelihood,
    RiskImpact,
    RiskStatus,
    TreatmentStrategy,
    FAIRAnalysis,
    MonteCarloSimulation,
    RiskTreatmentPlan
)
from models.database import Base, RiskDB, FAIRAnalysisDB, MonteCarloSimulationDB, RiskTreatmentPlanDB


# =============================================================================
# Test Database Setup
# =============================================================================

@pytest_asyncio.fixture
async def test_db_engine():
    """Create in-memory SQLite database engine for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_db_engine):
    """Create async database session for testing"""
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def mock_db_session():
    """Create mock database session"""
    session = AsyncMock(spec=AsyncSession)
    session.add = Mock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


# =============================================================================
# User Fixtures
# =============================================================================

@pytest.fixture
def test_user():
    """Create test user"""
    return User(
        user_id="test-user-123",
        tenant_id="test-org-456",
        email="test@example.com",
        role="bcm_manager",
        full_name="Test User",
        is_active=True
    )


@pytest.fixture
def admin_user():
    """Create admin test user"""
    return User(
        user_id="admin-user-123",
        tenant_id="test-org-456",
        email="admin@example.com",
        role="admin",
        full_name="Admin User",
        is_active=True
    )


# =============================================================================
# Risk Domain Model Fixtures
# =============================================================================

@pytest.fixture
def test_organization_id():
    """Test organization ID"""
    return uuid4()


@pytest.fixture
def sample_risk(test_organization_id):
    """Create sample risk domain model"""
    return Risk(
        organization_id=test_organization_id,
        risk_title="Data Breach Risk",
        risk_code="RISK-001",
        risk_category=RiskCategory.CYBERSECURITY,
        description="Risk of data breach exposing customer information",
        threat_source="External hackers",
        vulnerabilities=["Weak passwords", "Outdated software"],
        likelihood=RiskLikelihood.POSSIBLE,
        impact=RiskImpact.MAJOR,
        inherent_risk_score=12,
        treatment_strategy=TreatmentStrategy.MITIGATE,
        status=RiskStatus.IDENTIFIED,
        risk_owner_id=uuid4(),
        related_processes=[{"id": "proc-1", "name": "Customer data processing"}],
        related_assets=[{"id": "asset-1", "name": "Customer database"}]
    )


@pytest.fixture
def sample_fair_analysis():
    """Create sample FAIR analysis"""
    risk_id = uuid4()
    return FAIRAnalysis(
        risk_id=risk_id,
        threat_event_frequency=12.0,  # 12 threats per year
        vulnerability_score=0.3,  # 30% vulnerability
        primary_loss_min=10000.0,
        primary_loss_max=500000.0,
        primary_loss_most_likely=100000.0,
        secondary_loss_min=5000.0,
        secondary_loss_max=50000.0
    )


@pytest.fixture
def sample_monte_carlo():
    """Create sample Monte Carlo simulation"""
    risk_id = uuid4()
    return MonteCarloSimulation(
        risk_id=risk_id,
        iterations=10000,
        factors=[
            {"name": "Primary Loss", "min": 10000, "most_likely": 50000, "max": 200000},
            {"name": "Secondary Loss", "min": 5000, "most_likely": 15000, "max": 50000}
        ]
    )


@pytest.fixture
def sample_treatment_plan():
    """Create sample treatment plan"""
    risk_id = uuid4()
    return RiskTreatmentPlan(
        risk_id=risk_id,
        strategy=TreatmentStrategy.MITIGATE,
        description="Implement multi-factor authentication",
        actions=[
            {"id": 1, "description": "Deploy MFA solution", "status": "planned"},
            {"id": 2, "description": "Train users on MFA", "status": "planned"}
        ],
        responsible_party=uuid4(),
        start_date=datetime.utcnow(),
        target_date=datetime.utcnow() + timedelta(days=90),
        estimated_cost=50000.0,
        expected_residual_likelihood=RiskLikelihood.UNLIKELY,
        expected_residual_impact=RiskImpact.MODERATE,
        status="planned"
    )


# =============================================================================
# Database Model Fixtures
# =============================================================================

@pytest.fixture
def sample_risk_db(test_organization_id):
    """Create sample risk database model"""
    return RiskDB(
        id=uuid4(),
        organization_id=test_organization_id,
        risk_title="Data Breach Risk",
        risk_code="RISK-001",
        risk_category="cybersecurity",
        description="Risk of data breach exposing customer information",
        threat_source="External hackers",
        vulnerabilities=["Weak passwords", "Outdated software"],
        likelihood=3,
        impact=4,
        inherent_risk_score=12,
        treatment_strategy="mitigate",
        status="identified",
        risk_owner_id=uuid4(),
        related_processes=[{"id": "proc-1", "name": "Customer data processing"}],
        related_assets=[{"id": "asset-1", "name": "Customer database"}],
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_fair_db(test_organization_id):
    """Create sample FAIR analysis database model"""
    risk_id = uuid4()
    return FAIRAnalysisDB(
        id=uuid4(),
        risk_id=risk_id,
        organization_id=test_organization_id,
        threat_event_frequency=12,
        vulnerability_score=30,  # Stored as percentage
        loss_event_frequency=3.6,
        primary_loss_min=10000,
        primary_loss_max=500000,
        primary_loss_most_likely=100000,
        secondary_loss_min=5000,
        secondary_loss_max=50000,
        annual_loss_expectancy=450000,
        risk_rating="high",
        confidence_interval_low=360000,
        confidence_interval_high=540000,
        analyzed_at=datetime.utcnow(),
        analyzed_by=uuid4()
    )


@pytest.fixture
def sample_monte_carlo_db(test_organization_id):
    """Create sample Monte Carlo database model"""
    risk_id = uuid4()
    return MonteCarloSimulationDB(
        id=uuid4(),
        risk_id=risk_id,
        organization_id=test_organization_id,
        iterations=10000,
        factors=[
            {"name": "Primary Loss", "min": 10000, "most_likely": 50000, "max": 200000}
        ],
        mean_loss=75000,
        median_loss=70000,
        percentile_95=150000,
        percentile_99=180000,
        distribution_data={
            "histogram": [100, 200, 300],
            "bin_edges": [0, 50000, 100000, 150000]
        },
        simulated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_treatment_plan_db(test_organization_id):
    """Create sample treatment plan database model"""
    risk_id = uuid4()
    return RiskTreatmentPlanDB(
        id=uuid4(),
        risk_id=risk_id,
        organization_id=test_organization_id,
        strategy="mitigate",
        description="Implement multi-factor authentication",
        actions=[
            {"id": 1, "description": "Deploy MFA solution", "status": "planned"}
        ],
        responsible_party=uuid4(),
        start_date=datetime.utcnow(),
        target_date=datetime.utcnow() + timedelta(days=90),
        estimated_cost=50000,
        expected_residual_likelihood=2,
        expected_residual_impact=3,
        status="planned",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


# =============================================================================
# JWT Token Fixtures
# =============================================================================

@pytest.fixture
def valid_jwt_payload():
    """Create valid JWT token payload"""
    return {
        "sub": "test-user-123",
        "tenant_id": "test-org-456",
        "email": "test@example.com",
        "role": "bcm_manager",
        "full_name": "Test User",
        "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()
    }


@pytest.fixture
def expired_jwt_payload():
    """Create expired JWT token payload"""
    return {
        "sub": "test-user-123",
        "tenant_id": "test-org-456",
        "email": "test@example.com",
        "role": "bcm_manager",
        "exp": (datetime.utcnow() - timedelta(hours=1)).timestamp()
    }


@pytest.fixture
def jwt_secret_key():
    """JWT secret key for testing"""
    return "test-secret-key-12345"


# =============================================================================
# Mock Response Fixtures
# =============================================================================

@pytest.fixture
def mock_sqlalchemy_result():
    """Create mock SQLAlchemy result"""
    result = Mock()
    result.scalar_one_or_none = Mock()
    result.scalars = Mock()
    result.all = Mock()
    return result


# =============================================================================
# Helper Functions
# =============================================================================

def create_multiple_risks(organization_id: UUID, count: int = 5):
    """Create multiple risk models for testing"""
    risks = []
    categories = list(RiskCategory)
    statuses = list(RiskStatus)

    for i in range(count):
        risk = Risk(
            id=uuid4(),
            organization_id=organization_id,
            risk_title=f"Risk {i+1}",
            risk_code=f"RISK-{i+1:03d}",
            risk_category=categories[i % len(categories)],
            description=f"Description for risk {i+1}",
            threat_source="Test threat",
            vulnerabilities=["Vulnerability 1"],
            likelihood=RiskLikelihood((i % 5) + 1),
            impact=RiskImpact((i % 5) + 1),
            inherent_risk_score=((i % 5) + 1) * ((i % 5) + 1),
            status=statuses[i % len(statuses)],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        risks.append(risk)

    return risks
