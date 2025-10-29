from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Tenant


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_tenant_by_id(session: AsyncSession, tenant_id: str) -> Optional[Tenant]:
    result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalar_one_or_none()


async def get_tenant_by_domain(session: AsyncSession, domain: str) -> Optional[Tenant]:
    result = await session.execute(select(Tenant).where(Tenant.domain == domain))
    return result.scalar_one_or_none()


async def list_users_by_tenant(session: AsyncSession, tenant_id: str) -> List[User]:
    result = await session.execute(select(User).where(User.tenant_id == tenant_id))
    return result.scalars().all()


async def list_tenants(session: AsyncSession) -> List[Tenant]:
    result = await session.execute(select(Tenant))
    return result.scalars().all()


async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def users_count(session: AsyncSession) -> int:
    result = await session.execute(select(func.count()).select_from(User))
    return result.scalar_one()


async def tenants_count(session: AsyncSession) -> int:
    result = await session.execute(select(func.count()).select_from(Tenant))
    return result.scalar_one()

