"""
Pytest Configuration and Fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from models.database import Base
from config import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for tests"""
    return Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        JWT_PUBLIC_KEY="",
        EVENTBUS_URL="http://mock-eventbus:8001",
        JWT_SECRET="test-secret-key",
        JWT_ALGORITHM="HS256"
    )


@pytest.fixture
async def db_engine():
    """Create test database engine"""
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


@pytest.fixture
def sample_cost_breakdown():
    """Sample cost breakdown data"""
    return {
        "capex": 100000,
        "opex": 5000,
        "training": 10000,
        "maintenance": 3000,
        "other": 2000,
        "currency": "USD"
    }


@pytest.fixture
def sample_benefits():
    """Sample benefits data"""
    return {
        "quantitative_benefits": {
            "annual_revenue_protection": 150000,
            "cost_avoidance": 50000,
            "efficiency_gains": 30000
        },
        "qualitative_benefits": [
            "Improved customer trust",
            "Enhanced brand reputation",
            "Regulatory compliance"
        ],
        "risk_reduction_percentage": 75.0,
        "downtime_reduction_hours": 100.0
    }


@pytest.fixture
def mock_user_context():
    """Mock authenticated user context"""
    from auth.models import UserContext
    return UserContext(
        user_id="test-user-123",
        tenant_id="test-tenant-456",
        email="test@example.com",
        roles=["bcm_manager", "strategy_editor"],
        is_superadmin=False
    )
