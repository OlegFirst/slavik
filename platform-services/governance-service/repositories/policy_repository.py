"""
Policy Repository
Data access layer for BCM Policies (ISO 22301 Clause 5.2)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import BCMPolicy, PolicyVersion, PolicyStatus, PolicyType


class PolicyRepository:
    """Repository for BCM Policies"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, policy: BCMPolicy) -> BCMPolicy:
        """Create policy"""
        self.session.add(policy)
        await self.session.flush()
        await self.session.refresh(policy)
        return policy

    async def get_by_id(self, policy_id: int) -> Optional[BCMPolicy]:
        """Get policy by ID"""
        result = await self.session.execute(
            select(BCMPolicy).where(BCMPolicy.id == policy_id)
        )
        return result.scalar_one_or_none()

    async def get_by_title(
        self,
        tenant_id: str,
        title: str
    ) -> Optional[BCMPolicy]:
        """Get policy by title"""
        result = await self.session.execute(
            select(BCMPolicy).where(
                and_(
                    BCMPolicy.tenant_id == tenant_id,
                    BCMPolicy.title == title
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: Optional[PolicyStatus] = None,
        policy_type: Optional[PolicyType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BCMPolicy]:
        """List policies for tenant with filters"""
        query = select(BCMPolicy).where(BCMPolicy.tenant_id == tenant_id)

        if status:
            query = query.where(BCMPolicy.status == status)
        if policy_type:
            query = query.where(BCMPolicy.policy_type == policy_type)

        query = query.offset(skip).limit(limit).order_by(BCMPolicy.created_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_for_review(
        self,
        tenant_id: str,
        before_date: datetime
    ) -> List[BCMPolicy]:
        """List policies due for review"""
        result = await self.session.execute(
            select(BCMPolicy).where(
                and_(
                    BCMPolicy.tenant_id == tenant_id,
                    BCMPolicy.status == PolicyStatus.ACTIVE,
                    BCMPolicy.next_review_date <= before_date
                )
            )
        )
        return list(result.scalars().all())

    async def list_by_owner(
        self,
        tenant_id: str,
        owner: str,
        status: Optional[PolicyStatus] = None
    ) -> List[BCMPolicy]:
        """List policies by owner"""
        query = select(BCMPolicy).where(
            and_(
                BCMPolicy.tenant_id == tenant_id,
                BCMPolicy.policy_owner == owner
            )
        )

        if status:
            query = query.where(BCMPolicy.status == status)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, policy: BCMPolicy) -> BCMPolicy:
        """Update policy"""
        policy.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(policy)
        return policy

    async def delete(self, policy_id: int) -> bool:
        """Delete policy"""
        policy = await self.get_by_id(policy_id)
        if policy:
            await self.session.delete(policy)
            await self.session.flush()
            return True
        return False

    async def count_by_status(self, tenant_id: str) -> dict:
        """Count policies by status"""
        result = await self.session.execute(
            select(
                BCMPolicy.status,
                func.count(BCMPolicy.id)
            ).where(
                BCMPolicy.tenant_id == tenant_id
            ).group_by(BCMPolicy.status)
        )

        counts = {status.value: 0 for status in PolicyStatus}
        for status, count in result.all():
            counts[status.value] = count

        return counts


class PolicyVersionRepository:
    """Repository for Policy Versions"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, version: PolicyVersion) -> PolicyVersion:
        """Create policy version"""
        self.session.add(version)
        await self.session.flush()
        await self.session.refresh(version)
        return version

    async def get_by_id(self, version_id: int) -> Optional[PolicyVersion]:
        """Get version by ID"""
        result = await self.session.execute(
            select(PolicyVersion).where(PolicyVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    async def list_by_policy(
        self,
        policy_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[PolicyVersion]:
        """List versions for policy"""
        result = await self.session.execute(
            select(PolicyVersion).where(
                PolicyVersion.policy_id == policy_id
            ).offset(skip).limit(limit).order_by(PolicyVersion.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest_version(self, policy_id: int) -> Optional[PolicyVersion]:
        """Get latest version for policy"""
        result = await self.session.execute(
            select(PolicyVersion).where(
                PolicyVersion.policy_id == policy_id
            ).order_by(PolicyVersion.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()
