"""
Pytest Configuration and Fixtures
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/digital_twin_test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

from api.app import create_app
from storage.models import Base
from storage import PostgreSQLStorage, RedisCache


# ============================================
# FIXTURES: Database
# ============================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_engine():
    """Create test database engine"""
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/digital_twin_test")

    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for test"""
    async_session = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def storage(test_db_engine) -> AsyncGenerator[PostgreSQLStorage, None]:
    """Create storage instance for test"""
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'digital_twin_test',
        'username': 'postgres',
        'password': 'postgres'
    }

    storage = PostgreSQLStorage(config)
    storage.engine = test_db_engine

    # Create session factory
    storage.Session = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    yield storage

    # Cleanup - delete all data
    async with storage.Session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


# ============================================
# FIXTURES: Cache
# ============================================

@pytest.fixture
async def cache() -> AsyncGenerator[RedisCache, None]:
    """Create cache instance for test"""
    config = {
        'host': 'localhost',
        'port': 6379,
        'db': 1,
        'prefix': 'test:'
    }

    cache = RedisCache(config)
    await cache.initialize()

    yield cache

    # Cleanup
    await cache.close()


# ============================================
# FIXTURES: FastAPI App
# ============================================

@pytest.fixture
async def app(storage, cache):
    """Create FastAPI app for testing"""
    config = {
        'postgres': {
            'host': 'localhost',
            'port': 5432,
            'database': 'digital_twin_test',
            'username': 'postgres',
            'password': 'postgres'
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 1,
            'prefix': 'test:'
        }
    }

    app = create_app(config)

    # Override storage and cache
    app.state.app_state.storage = storage
    app.state.app_state.cache = cache

    return app


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================
# FIXTURES: Authentication
# ============================================

@pytest.fixture
async def test_tenant(storage):
    """Create test tenant"""
    tenant_data = {
        "id": f"tenant-{uuid4().hex[:12]}",
        "name": "Test Tenant",
        "slug": "test-tenant",
        "plan": "free",
        "is_active": True,
        "is_trial": True
    }

    tenant = await storage.create_tenant(tenant_data)
    return tenant


@pytest.fixture
async def test_user(storage, test_tenant):
    """Create test user"""
    from api.auth import hash_password

    user_data = {
        "id": f"user-{uuid4().hex[:12]}",
        "tenant_id": test_tenant.id,
        "email": "test@example.com",
        "hashed_password": hash_password("TestPass123!"),
        "full_name": "Test User",
        "role": "admin",
        "is_active": True
    }

    user = await storage.create_user(user_data)
    return user


@pytest.fixture
async def auth_token(test_user):
    """Create auth token for test user"""
    from api.auth import create_access_token

    token = create_access_token(
        user_id=test_user.id,
        tenant_id=test_user.tenant_id,
        email=test_user.email
    )

    return token


@pytest.fixture
async def authenticated_client(client, auth_token) -> AsyncClient:
    """Create authenticated HTTP client"""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client


# ============================================
# FIXTURES: Test Data
# ============================================

@pytest.fixture
async def test_organization(storage, test_tenant):
    """Create test organization"""
    org_data = {
        "id": f"org-{uuid4().hex[:12]}",
        "tenant_id": test_tenant.id,
        "name": "Test Organization",
        "industry": "Technology",
        "size": "medium",
        "rpo_hours": 4,
        "rto_hours": 8
    }

    org = await storage.create_organization(org_data)
    return org


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for import tests"""
    return """name,industry,size,rpo_hours,rto_hours
Acme Corp,Technology,large,2,4
Beta Inc,Finance,medium,4,8
Gamma LLC,Healthcare,small,1,2
"""
