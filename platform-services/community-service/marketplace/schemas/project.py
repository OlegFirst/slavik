"""
Project Pydantic Schemas
"""

from pydantic import BaseModel, UUID4
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date

from database.models import ServiceType, UrgencyLevel, BudgetType, WorkLocation, ProjectStatus


class ProjectBase(BaseModel):
    """Base project fields"""
    title: str
    description: str
    service_type: ServiceType
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    scope_of_work: Optional[str] = None
    deliverables: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_estimate_hours: Optional[Decimal] = None
    budget_type: BudgetType = BudgetType.NEGOTIABLE
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    currency: str = "USD"
    required_certifications: Optional[str] = None
    required_experience_years: Optional[int] = None
    required_skills: List[str] = []
    work_location: WorkLocation = WorkLocation.REMOTE
    location_country: Optional[str] = None
    location_state: Optional[str] = None
    location_city: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Create project"""
    client_id: UUID4
    tenant_id: UUID4
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Update project (all optional)"""
    title: Optional[str] = None
    description: Optional[str] = None
    service_type: Optional[ServiceType] = None
    urgency: Optional[UrgencyLevel] = None
    scope_of_work: Optional[str] = None
    deliverables: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_estimate_hours: Optional[Decimal] = None
    budget_type: Optional[BudgetType] = None
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    required_skills: Optional[List[str]] = None
    work_location: Optional[WorkLocation] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    """Project response"""
    id: int
    client_id: UUID4
    tenant_id: UUID4
    client_name: Optional[str]
    company_name: Optional[str]
    industry: Optional[str]
    company_size: Optional[str]
    status: ProjectStatus
    published_at: Optional[datetime]
    selected_proposal_id: Optional[int]
    selected_specialist_id: Optional[int]
    view_count: int
    proposal_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListItem(BaseModel):
    """Project list item (lighter)"""
    id: int
    title: str
    service_type: ServiceType
    urgency: UrgencyLevel
    budget_type: BudgetType
    budget_min: Optional[Decimal]
    budget_max: Optional[Decimal]
    work_location: WorkLocation
    status: ProjectStatus
    proposal_count: int
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectSearchFilters(BaseModel):
    """Project search filters"""
    service_type: Optional[ServiceType] = None
    urgency: Optional[UrgencyLevel] = None
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    work_location: Optional[WorkLocation] = None
    required_skills: Optional[List[str]] = None
    status: Optional[ProjectStatus] = None
