"""
Proposal Pydantic Schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date

from database.models import ProposalStatus


class ProposalBase(BaseModel):
    """Base proposal fields"""
    cover_letter: str
    proposed_rate: Optional[Decimal] = None
    estimated_duration_hours: Optional[Decimal] = None
    estimated_total_cost: Optional[Decimal] = None
    currency: str = "USD"
    proposed_start_date: Optional[date] = None
    proposed_end_date: Optional[date] = None
    deliverables: Optional[str] = None
    methodology: Optional[str] = None


class ProposalCreate(ProposalBase):
    """Create proposal"""
    attachments: List[str] = []


class ProposalUpdate(BaseModel):
    """Update proposal"""
    cover_letter: Optional[str] = None
    proposed_rate: Optional[Decimal] = None
    estimated_duration_hours: Optional[Decimal] = None
    estimated_total_cost: Optional[Decimal] = None
    proposed_start_date: Optional[date] = None
    proposed_end_date: Optional[date] = None
    deliverables: Optional[str] = None
    methodology: Optional[str] = None
    attachments: Optional[List[str]] = None


class ProposalResponse(ProposalBase):
    """Proposal response"""
    id: int
    project_id: int
    specialist_id: int
    status: ProposalStatus
    attachments: List[str]
    viewed_by_client: bool
    viewed_at: Optional[datetime]
    responded_at: Optional[datetime]
    response_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProposalWithSpecialist(ProposalResponse):
    """Proposal with specialist info"""
    specialist_name: str
    specialist_rating: Decimal
    specialist_verified: bool
