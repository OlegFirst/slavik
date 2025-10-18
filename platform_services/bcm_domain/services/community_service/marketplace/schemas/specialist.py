"""
Specialist Pydantic Schemas
"""

from pydantic import BaseModel, UUID4, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from database.models import AvailabilityStatus


# Base schemas
class SpecialistBase(BaseModel):
    """Base specialist fields"""
    name: str
    title: Optional[str] = None
    bio: Optional[str] = None
    years_experience: int = 0
    hourly_rate: Optional[Decimal] = None
    currency: str = "USD"
    specializations: List[str] = []
    industries: List[str] = []
    skills: List[str] = []
    availability_status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    availability_hours: Optional[dict] = None
    timezone: str = "UTC"
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    remote_available: bool = True
    onsite_available: bool = True
    languages: List[str] = []


class SpecialistCreate(SpecialistBase):
    """Create specialist profile"""
    user_id: UUID4
    tenant_id: UUID4


class SpecialistUpdate(BaseModel):
    """Update specialist profile (all fields optional)"""
    name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    hourly_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    specializations: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    availability_status: Optional[AvailabilityStatus] = None
    availability_hours: Optional[dict] = None
    timezone: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    remote_available: Optional[bool] = None
    onsite_available: Optional[bool] = None
    languages: Optional[List[str]] = None


class SpecialistResponse(SpecialistBase):
    """Specialist response with computed fields"""
    id: int
    user_id: UUID4
    tenant_id: UUID4
    rating: Decimal
    total_reviews: int
    completed_projects: int
    response_time_hours: Optional[Decimal]
    acceptance_rate: Optional[Decimal]
    is_verified: bool
    verified_at: Optional[datetime]
    profile_completion: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SpecialistListItem(BaseModel):
    """Specialist list item (lighter response)"""
    id: int
    user_id: UUID4
    name: str
    title: Optional[str]
    hourly_rate: Optional[Decimal]
    specializations: List[str]
    rating: Decimal
    total_reviews: int
    is_verified: bool
    availability_status: AvailabilityStatus
    country: Optional[str]
    city: Optional[str]

    class Config:
        from_attributes = True


# Certification schemas
class CertificationBase(BaseModel):
    """Base certification fields"""
    name: str
    issuing_organization: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationCreate(CertificationBase):
    """Create certification"""
    documents: List[str] = []


class CertificationResponse(CertificationBase):
    """Certification response"""
    id: int
    specialist_id: int
    is_verified: bool
    verified_at: Optional[datetime]
    documents: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Portfolio schemas
class PortfolioItemBase(BaseModel):
    """Base portfolio item fields"""
    title: str
    description: Optional[str] = None
    client_name: Optional[str] = None
    industry: Optional[str] = None
    project_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_months: Optional[int] = None
    deliverables: Optional[str] = None
    outcomes: Optional[str] = None
    is_public: bool = True


class PortfolioItemCreate(PortfolioItemBase):
    """Create portfolio item"""
    images: List[str] = []
    documents: List[str] = []


class PortfolioItemResponse(PortfolioItemBase):
    """Portfolio item response"""
    id: int
    specialist_id: int
    images: List[str]
    documents: List[str]
    display_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# Search/Filter schemas
class SpecialistSearchFilters(BaseModel):
    """Specialist search filters"""
    specializations: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    min_rating: Optional[Decimal] = None
    max_hourly_rate: Optional[Decimal] = None
    min_hourly_rate: Optional[Decimal] = None
    verified_only: bool = False
    availability_status: Optional[AvailabilityStatus] = None
    remote_available: Optional[bool] = None
    country: Optional[str] = None
    skills: Optional[List[str]] = None
    min_experience_years: Optional[int] = None
