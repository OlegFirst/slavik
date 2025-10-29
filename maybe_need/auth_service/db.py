import os
from datetime import datetime
import bcrypt
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from models import Base, User, Tenant

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./auth.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed sample data if tables are empty
    async with AsyncSessionLocal() as session:
        u_count = (await session.execute(select(func.count()).select_from(User))).scalar_one()
        t_count = (await session.execute(select(func.count()).select_from(Tenant))).scalar_one()

        if t_count == 0:
            tenant1 = Tenant(
                id="tenant_001",
                name="ACME Corporation",
                domain="acme.com",
                plan="enterprise",
                is_active=True,
                settings={
                    "max_users": 100,
                    "features": ["bia", "plans", "incidents", "kpi", "documents", "exercises"],
                },
                created_at=datetime.utcnow(),
            )
            tenant2 = Tenant(
                id="tenant_002",
                name="TechStart Ltd",
                domain="techstart.io",
                plan="professional",
                is_active=True,
                settings={
                    "max_users": 25,
                    "features": ["bia", "plans", "incidents", "kpi"],
                },
                created_at=datetime.utcnow(),
            )
            session.add_all([tenant1, tenant2])

        if u_count == 0:
            user1 = User(
                id="user_001",
                email="admin@bcm.local",
                password_hash=bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
                full_name="BCM Administrator",
                tenant_id="tenant_001",
                roles=["admin", "user"],
                is_active=True,
                created_at=datetime.utcnow(),
            )
            user2 = User(
                id="user_002",
                email="manager@bcm.local",
                password_hash=bcrypt.hashpw("manager123".encode(), bcrypt.gensalt()).decode(),
                full_name="BCM Manager",
                tenant_id="tenant_001",
                roles=["manager", "user"],
                is_active=True,
                created_at=datetime.utcnow(),
            )
            user3 = User(
                id="user_003",
                email="user@bcm.local",
                password_hash=bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode(),
                full_name="BCM User",
                tenant_id="tenant_002",
                roles=["user"],
                is_active=True,
                created_at=datetime.utcnow(),
            )
            session.add_all([user1, user2, user3])

        await session.commit()


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

