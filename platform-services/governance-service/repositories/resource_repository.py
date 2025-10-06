"""
Resource Repository
Data access layer for BCM Resources (ISO 22301 Clause 7.1)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import BCMResource, ResourceType, ResourceAvailability


class ResourceRepository:
    """Repository for BCM Resources"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, resource: BCMResource) -> BCMResource:
        """Create BCM resource"""
        self.session.add(resource)
        await self.session.flush()
        await self.session.refresh(resource)
        return resource

    async def get_by_id(self, resource_id: int) -> Optional[BCMResource]:
        """Get resource by ID"""
        result = await self.session.execute(
            select(BCMResource).where(BCMResource.id == resource_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        tenant_id: str,
        resource_name: str
    ) -> Optional[BCMResource]:
        """Get resource by name"""
        result = await self.session.execute(
            select(BCMResource).where(
                and_(
                    BCMResource.tenant_id == tenant_id,
                    BCMResource.resource_name == resource_name
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        resource_type: Optional[ResourceType] = None,
        availability: Optional[ResourceAvailability] = None,
        is_critical: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BCMResource]:
        """List resources for tenant with filters"""
        query = select(BCMResource).where(BCMResource.tenant_id == tenant_id)

        if resource_type:
            query = query.where(BCMResource.resource_type == resource_type)
        if availability:
            query = query.where(BCMResource.availability == availability)
        if is_critical is not None:
            query = query.where(BCMResource.is_critical == is_critical)

        query = query.offset(skip).limit(limit).order_by(
            BCMResource.created_at.desc()
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_allocation(
        self,
        tenant_id: str,
        allocated_to: str,
        allocated_to_type: Optional[str] = None
    ) -> List[BCMResource]:
        """List resources allocated to specific target"""
        query = select(BCMResource).where(
            and_(
                BCMResource.tenant_id == tenant_id,
                BCMResource.allocated_to == allocated_to
            )
        )

        if allocated_to_type:
            query = query.where(BCMResource.allocated_to_type == allocated_to_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_available(
        self,
        tenant_id: str,
        resource_type: Optional[ResourceType] = None
    ) -> List[BCMResource]:
        """List available resources"""
        query = select(BCMResource).where(
            and_(
                BCMResource.tenant_id == tenant_id,
                BCMResource.availability == ResourceAvailability.AVAILABLE
            )
        )

        if resource_type:
            query = query.where(BCMResource.resource_type == resource_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_critical(
        self,
        tenant_id: str,
        resource_type: Optional[ResourceType] = None
    ) -> List[BCMResource]:
        """List critical resources"""
        query = select(BCMResource).where(
            and_(
                BCMResource.tenant_id == tenant_id,
                BCMResource.is_critical == True
            )
        )

        if resource_type:
            query = query.where(BCMResource.resource_type == resource_type)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_owner(
        self,
        tenant_id: str,
        owner: str
    ) -> List[BCMResource]:
        """List resources by owner"""
        result = await self.session.execute(
            select(BCMResource).where(
                and_(
                    BCMResource.tenant_id == tenant_id,
                    BCMResource.owner == owner
                )
            )
        )
        return list(result.scalars().all())

    async def update(self, resource: BCMResource) -> BCMResource:
        """Update resource"""
        resource.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(resource)
        return resource

    async def delete(self, resource_id: int) -> bool:
        """Delete resource"""
        resource = await self.get_by_id(resource_id)
        if resource:
            await self.session.delete(resource)
            await self.session.flush()
            return True
        return False

    async def count_by_type(self, tenant_id: str) -> dict:
        """Count resources by type"""
        result = await self.session.execute(
            select(
                BCMResource.resource_type,
                func.count(BCMResource.id)
            ).where(
                BCMResource.tenant_id == tenant_id
            ).group_by(BCMResource.resource_type)
        )

        counts = {resource_type.value: 0 for resource_type in ResourceType}
        for resource_type, count in result.all():
            counts[resource_type.value] = count

        return counts

    async def count_by_availability(self, tenant_id: str) -> dict:
        """Count resources by availability"""
        result = await self.session.execute(
            select(
                BCMResource.availability,
                func.count(BCMResource.id)
            ).where(
                BCMResource.tenant_id == tenant_id
            ).group_by(BCMResource.availability)
        )

        counts = {avail.value: 0 for avail in ResourceAvailability}
        for avail, count in result.all():
            counts[avail.value] = count

        return counts

    async def get_total_cost(
        self,
        tenant_id: str,
        resource_type: Optional[ResourceType] = None
    ) -> float:
        """Calculate total cost of resources"""
        query = select(func.sum(BCMResource.total_cost)).where(
            BCMResource.tenant_id == tenant_id
        )

        if resource_type:
            query = query.where(BCMResource.resource_type == resource_type)

        result = await self.session.execute(query)
        return result.scalar() or 0.0
