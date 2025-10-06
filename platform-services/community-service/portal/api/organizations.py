"""
Organizations API
Get organization information
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from database.connection import get_db
from database.organization_model import Organization
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/portal/organizations", tags=["Organizations"])


# Pydantic schemas
class OrganizationResponse(BaseModel):
    id: str
    name: str
    legal_name: Optional[str]
    industry: Optional[str]
    organization_size: Optional[str]
    organization_type: Optional[str]

    country: Optional[str]
    city: Optional[str]
    timezone: Optional[str]

    bcm_maturity_level: Optional[str]
    iso22301_certified: bool
    certification_date: Optional[date]

    subscription_tier: Optional[str]
    subscription_status: str
    max_users: int
    enabled_modules: List[str]

    is_active: bool
    onboarding_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationDetailResponse(OrganizationResponse):
    """Extended organization details"""
    address: Optional[str]
    website: Optional[str]
    primary_contact_name: Optional[str]
    primary_contact_email: Optional[str]
    primary_contact_phone: Optional[str]

    certification_body: Optional[str]
    applicable_standards: List
    regulatory_requirements: List

    critical_services: List
    key_dependencies: List
    risk_appetite: Optional[str]

    feature_flags: dict
    settings: dict
    branding: dict

    subscription_start_date: Optional[date]
    subscription_end_date: Optional[date]

    notes: Optional[str]
    tags: List

    updated_at: datetime


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/me", response_model=OrganizationDetailResponse)
async def get_my_organization(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's organization details

    Returns full organization information including:
    - Basic info (name, industry, size)
    - Subscription & licensing
    - BCM program maturity
    - Enabled modules and features
    - Configuration and branding
    """
    tenant_id = current_user.get('tenant_id')

    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant_id in user context")

    stmt = select(Organization).where(Organization.id == tenant_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {tenant_id} not found")

    return org


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get public organization info by ID

    Returns basic organization information (public view)
    """
    stmt = select(Organization).where(Organization.id == org_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")

    if not org.is_active:
        raise HTTPException(status_code=404, detail="Organization not active")

    return org


@router.get("", response_model=List[OrganizationResponse])
async def list_organizations(
    industry: Optional[str] = None,
    organization_size: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List organizations (admin only)

    Filters:
    - industry: Filter by industry
    - organization_size: small, medium, large, enterprise
    """
    stmt = select(Organization).where(Organization.is_active == True)

    if industry:
        stmt = stmt.where(Organization.industry == industry)

    if organization_size:
        stmt = stmt.where(Organization.organization_size == organization_size)

    stmt = stmt.order_by(Organization.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    organizations = result.scalars().all()

    return organizations
