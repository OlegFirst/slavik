"""
Role Repository
Data access layer for Organizational Roles (ISO 22301 Clause 5.3)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import OrganizationalRole, RoleType, RoleStatus


class RoleRepository:
    """Repository for Organizational Roles"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, role: OrganizationalRole) -> OrganizationalRole:
        """Create organizational role"""
        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)
        return role

    async def get_by_id(self, role_id: int) -> Optional[OrganizationalRole]:
        """Get role by ID"""
        result = await self.session.execute(
            select(OrganizationalRole).where(OrganizationalRole.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        tenant_id: str,
        role_name: str
    ) -> Optional[OrganizationalRole]:
        """Get role by name"""
        result = await self.session.execute(
            select(OrganizationalRole).where(
                and_(
                    OrganizationalRole.tenant_id == tenant_id,
                    OrganizationalRole.role_name == role_name
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: Optional[RoleStatus] = None,
        role_type: Optional[RoleType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[OrganizationalRole]:
        """List roles for tenant with filters"""
        query = select(OrganizationalRole).where(
            OrganizationalRole.tenant_id == tenant_id
        )

        if status:
            query = query.where(OrganizationalRole.status == status)
        if role_type:
            query = query.where(OrganizationalRole.role_type == role_type)

        query = query.offset(skip).limit(limit).order_by(
            OrganizationalRole.created_at.desc()
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_assignee(
        self,
        tenant_id: str,
        assigned_to: str,
        status: Optional[RoleStatus] = None
    ) -> List[OrganizationalRole]:
        """List roles assigned to person"""
        query = select(OrganizationalRole).where(
            and_(
                OrganizationalRole.tenant_id == tenant_id,
                OrganizationalRole.assigned_to == assigned_to
            )
        )

        if status:
            query = query.where(OrganizationalRole.status == status)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_unassigned(
        self,
        tenant_id: str,
        role_type: Optional[RoleType] = None
    ) -> List[OrganizationalRole]:
        """List unassigned roles"""
        query = select(OrganizationalRole).where(
            and_(
                OrganizationalRole.tenant_id == tenant_id,
                OrganizationalRole.assigned_to.is_(None),
                OrganizationalRole.status == RoleStatus.PENDING
            )
        )

        if role_type:
            query = query.where(OrganizationalRole.role_type == role_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, role: OrganizationalRole) -> OrganizationalRole:
        """Update role"""
        role.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(role)
        return role

    async def delete(self, role_id: int) -> bool:
        """Delete role"""
        role = await self.get_by_id(role_id)
        if role:
            await self.session.delete(role)
            await self.session.flush()
            return True
        return False

    async def count_by_status(self, tenant_id: str) -> dict:
        """Count roles by status"""
        result = await self.session.execute(
            select(
                OrganizationalRole.status,
                func.count(OrganizationalRole.id)
            ).where(
                OrganizationalRole.tenant_id == tenant_id
            ).group_by(OrganizationalRole.status)
        )

        counts = {status.value: 0 for status in RoleStatus}
        for status, count in result.all():
            counts[status.value] = count

        return counts

    async def count_by_type(self, tenant_id: str) -> dict:
        """Count roles by type"""
        result = await self.session.execute(
            select(
                OrganizationalRole.role_type,
                func.count(OrganizationalRole.id)
            ).where(
                OrganizationalRole.tenant_id == tenant_id
            ).group_by(OrganizationalRole.role_type)
        )

        counts = {role_type.value: 0 for role_type in RoleType}
        for role_type, count in result.all():
            counts[role_type.value] = count

        return counts
