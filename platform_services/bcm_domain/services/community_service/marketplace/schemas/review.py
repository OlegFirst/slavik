"""
Review Pydantic Schemas
"""

from pydantic import BaseModel, UUID4, field_validator
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    """Base review fields"""
    rating: int
    title: Optional[str] = None
    review_text: Optional[str] = None
    communication_rating: Optional[int] = None
    quality_rating: Optional[int] = None
    professionalism_rating: Optional[int] = None
    timeliness_rating: Optional[int] = None

    @field_validator('rating', 'communication_rating', 'quality_rating', 'professionalism_rating', 'timeliness_rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v


class ReviewCreate(ReviewBase):
    """Create review"""
    project_id: int
    specialist_id: int
    reviewer_id: UUID4


class ReviewResponse(ReviewBase):
    """Review response"""
    id: int
    project_id: int
    specialist_id: int
    reviewer_id: UUID4
    specialist_response: Optional[str]
    responded_at: Optional[datetime]
    is_public: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewWithProject(ReviewResponse):
    """Review with project info"""
    project_title: str
    project_type: str


class SpecialistResponseCreate(BaseModel):
    """Specialist response to review"""
    specialist_response: str
