"""
Domain Models (Pydantic)
Request/Response models for API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


# ===== Enums =====

class ProgramStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class EnrollmentStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ASSESSED = "assessed"
    CERTIFIED = "certified"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"
    ARCHIVED = "archived"


class CompetencyLevel(str, Enum):
    NONE = "none"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class AssessmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AchievementLevel(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


# ===== Training Programs =====

class ProgramCreate(BaseModel):
    """Create Training Program Request"""
    tenant_id: str
    program_code: str
    program_name: str
    description: Optional[str] = None
    program_type: str
    bci_training_level: Optional[str] = None
    target_audience: Optional[str] = None
    iso_clause: Optional[str] = "7.2"
    learning_objectives: List[str] = Field(default_factory=list)
    curriculum: List[Dict] = Field(default_factory=list)
    duration_hours: Optional[int] = None
    delivery_method: str = "online"
    assessment_required: bool = True
    passing_score: int = 70
    certification_awarded: bool = False


class ProgramUpdate(BaseModel):
    """Update Training Program Request"""
    program_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProgramStatus] = None
    learning_objectives: Optional[List[str]] = None
    curriculum: Optional[List[Dict]] = None
    passing_score: Optional[int] = None


class ProgramResponse(BaseModel):
    """Training Program Response"""
    id: int
    tenant_id: str
    program_code: str
    program_name: str
    program_type: str
    bci_training_level: Optional[str]
    duration_hours: Optional[int]
    status: str
    enrollment_count: int
    completion_rate: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Training Enrollments =====

class EnrollmentCreate(BaseModel):
    """Enroll in Training Program"""
    tenant_id: str
    program_id: int
    person_id: str
    person_name: str
    department: Optional[str] = None
    enrolled_by: Optional[str] = None
    target_completion_date: Optional[datetime] = None


class EnrollmentProgressUpdate(BaseModel):
    """Update Training Progress"""
    progress_percentage: int = Field(ge=0, le=100)
    modules_completed: Optional[List[str]] = None
    time_spent_minutes: Optional[int] = None
    notes: Optional[str] = None


class EnrollmentAssessment(BaseModel):
    """Submit Assessment Result"""
    assessment_score: float = Field(ge=0, le=100)
    assessment_date: Optional[datetime] = None
    assessment_type: str = "final"
    assessor: Optional[str] = None
    feedback: Optional[str] = None


class EnrollmentResponse(BaseModel):
    """Training Enrollment Response"""
    id: int
    tenant_id: str
    program_id: int
    person_id: str
    person_name: str
    status: str
    progress_percentage: int
    assessment_score: Optional[float]
    assessment_attempts: int = 0
    assessment_passed: bool
    certification_issued: bool
    certification_expiry_date: Optional[datetime]
    points_earned: int
    enrolled_date: datetime
    completion_date: Optional[datetime]
    target_completion_date: Optional[datetime]

    class Config:
        from_attributes = True


# ===== Competency Assessments =====

class CompetencyCreate(BaseModel):
    """Create Competency Assessment"""
    tenant_id: str
    person_id: str
    person_name: str
    department: Optional[str] = None
    role: Optional[str] = None
    competency_area: str
    required_level: CompetencyLevel
    current_level: CompetencyLevel
    evidence_type: Optional[str] = None
    evidence_details: Dict = Field(default_factory=dict)
    assessed_by: Optional[str] = None
    assessment_date: Optional[datetime] = None


class CompetencyResponse(BaseModel):
    """Competency Assessment Response"""
    id: int
    tenant_id: str
    person_id: str
    person_name: str
    competency_area: str
    required_level: str
    current_level: str
    gap_exists: bool
    gap_severity: Optional[str]
    training_required: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Awareness Campaigns =====

class CampaignCreate(BaseModel):
    """Create Awareness Campaign"""
    tenant_id: str
    campaign_name: str
    description: Optional[str] = None
    campaign_type: str
    target_groups: List[str] = Field(default_factory=list)
    communication_channels: List[str] = Field(default_factory=list)
    start_date: datetime
    end_date: datetime
    content: Dict = Field(default_factory=dict)
    success_metrics: Dict = Field(default_factory=dict)


class CampaignResponse(BaseModel):
    """Awareness Campaign Response"""
    id: int
    tenant_id: str
    campaign_name: str
    campaign_type: str
    status: str
    start_date: datetime
    end_date: datetime
    reach: int
    engagement_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Gamification =====

class AchievementResponse(BaseModel):
    """User Achievement Response"""
    id: int
    tenant_id: str
    person_id: str
    achievement_type: str
    achievement_name: str
    level: str
    points: int
    earned_date: datetime
    badge_icon: str
    badge_color: str

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Leaderboard Entry"""
    rank: int
    person_id: str
    person_name: str
    total_points: int
    trainings_completed: int
    achievements_count: int
    current_streak: int
    level: int


class LeaderboardResponse(BaseModel):
    """Leaderboard Response"""
    tenant_id: str
    period: str
    updated_at: datetime
    entries: List[LeaderboardEntry]
