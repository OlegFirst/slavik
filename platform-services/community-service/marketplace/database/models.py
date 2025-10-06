"""
Marketplace Service - SQLAlchemy Models
Based on BCM_1 Odoo models
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DECIMAL, Date,
    TIMESTAMP, Enum as SQLEnum, ForeignKey, UUID, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .connection import Base


# ============================================================================
# ENUMS
# ============================================================================

class ServiceType(str, enum.Enum):
    """Service types (from BCM_1)"""
    CONSULTING = "consulting"
    ASSESSMENT = "assessment"
    BIA = "bia"
    PLANNING = "planning"
    TRAINING = "training"
    AUDIT = "audit"
    IMPLEMENTATION = "implementation"
    CRISIS_SUPPORT = "crisis_support"
    OTHER = "other"


class UrgencyLevel(str, enum.Enum):
    """Project urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BudgetType(str, enum.Enum):
    """Budget types"""
    HOURLY = "hourly"
    FIXED = "fixed"
    NEGOTIABLE = "negotiable"


class WorkLocation(str, enum.Enum):
    """Work location types"""
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class ProjectStatus(str, enum.Enum):
    """Project status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProposalStatus(str, enum.Enum):
    """Proposal status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class AvailabilityStatus(str, enum.Enum):
    """Specialist availability"""
    AVAILABLE = "available"
    BUSY = "busy"
    UNAVAILABLE = "unavailable"


# ============================================================================
# SPECIALISTS
# ============================================================================

class Specialist(Base):
    """BCM Specialist Profile (from BCM_1 bcm_specialist.py)"""
    __tablename__ = "specialists"
    __table_args__ = {'schema': 'marketplace'}

    # Primary Key
    id = Column(Integer, primary_key=True)

    # User Reference (from Clients service)
    user_id = Column(UUID, nullable=False, unique=True, index=True)
    tenant_id = Column(UUID, nullable=False, index=True)

    # Basic Information
    name = Column(String(255), nullable=False)
    title = Column(String(255))  # Professional title
    bio = Column(Text)
    years_experience = Column(Integer, default=0)

    # Pricing
    hourly_rate = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="USD")

    # Skills & Specializations (JSONB)
    specializations = Column(JSONB, default=[])  # ["ISO 22301", "BIA", ...]
    industries = Column(JSONB, default=[])       # ["Financial", "Healthcare", ...]
    skills = Column(JSONB, default=[])           # ["BCM Planning", ...]

    # Availability
    availability_status = Column(
        SQLEnum(AvailabilityStatus, name="availability_status", schema="marketplace"),
        default=AvailabilityStatus.AVAILABLE
    )
    availability_hours = Column(JSONB)  # Weekly schedule
    timezone = Column(String(50), default="UTC")

    # Location
    country = Column(String(100))
    state = Column(String(100))
    city = Column(String(100))
    remote_available = Column(Boolean, default=True)
    onsite_available = Column(Boolean, default=True)

    # Languages
    languages = Column(JSONB, default=[])  # ["English", "Spanish"]

    # Metrics
    rating = Column(DECIMAL(3, 2), default=0.00)
    total_reviews = Column(Integer, default=0)
    completed_projects = Column(Integer, default=0)
    response_time_hours = Column(DECIMAL(10, 2))
    acceptance_rate = Column(DECIMAL(5, 2))

    # Verification
    is_verified = Column(Boolean, default=False, index=True)
    verified_at = Column(TIMESTAMP)
    verified_by = Column(UUID)
    verification_notes = Column(Text)

    # ==================== PHASE 4: Learning Service Integration ====================
    certifications_jsonb = Column(JSONB, default=[])  # [{"cert_number": "BCM-2025-001", "name": "BCM Practitioner", "expiry": "2027-01-01"}]
    competency_scores = Column(JSONB, default={})  # {"bc_planning": {"level": "expert", "score": 95}}
    last_training_date = Column(TIMESTAMP)
    training_programs_completed = Column(Integer, default=0)

    # ==================== PHASE 4: Governance Service Integration ====================
    verified_by_role_id = Column(Integer)  # Role ID from governance.roles.id
    verification_source = Column(String(50))  # governance_role, competencies, manual, learning_certification
    governance_competencies = Column(JSONB, default={})  # {"risk_assessment": {"level": "advanced", "assessed_by": "manager_001"}}

    # Profile
    profile_completion = Column(Integer, default=0)

    # Status
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    certifications = relationship("Certification", back_populates="specialist", cascade="all, delete-orphan")
    portfolio_items = relationship("PortfolioItem", back_populates="specialist", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="specialist")
    reviews = relationship("Review", back_populates="specialist")


class Certification(Base):
    """Specialist Certifications"""
    __tablename__ = "certifications"
    __table_args__ = {'schema': 'marketplace'}

    id = Column(Integer, primary_key=True)
    specialist_id = Column(Integer, ForeignKey('marketplace.specialists.id', ondelete='CASCADE'), nullable=False, index=True)

    # Certification Details
    name = Column(String(255), nullable=False, index=True)
    issuing_organization = Column(String(255))
    issue_date = Column(Date)
    expiry_date = Column(Date)
    credential_id = Column(String(255))
    credential_url = Column(String(500))

    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(TIMESTAMP)
    verified_by = Column(UUID)

    # Documents
    documents = Column(JSONB, default=[])

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    specialist = relationship("Specialist", back_populates="certifications")


class PortfolioItem(Base):
    """Specialist Portfolio Items"""
    __tablename__ = "portfolio_items"
    __table_args__ = {'schema': 'marketplace'}

    id = Column(Integer, primary_key=True)
    specialist_id = Column(Integer, ForeignKey('marketplace.specialists.id', ondelete='CASCADE'), nullable=False, index=True)

    # Project Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    client_name = Column(String(255))
    industry = Column(String(100))
    project_type = Column(SQLEnum(ServiceType, name="service_type", schema="marketplace"))

    # Timeline
    start_date = Column(Date)
    end_date = Column(Date)
    duration_months = Column(Integer)

    # Deliverables
    deliverables = Column(Text)
    outcomes = Column(Text)

    # Media
    images = Column(JSONB, default=[])
    documents = Column(JSONB, default=[])

    # Visibility
    is_public = Column(Boolean, default=True, index=True)
    display_order = Column(Integer, default=0)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    specialist = relationship("Specialist", back_populates="portfolio_items")


# ============================================================================
# PROJECTS
# ============================================================================

class Project(Base):
    """Service Requests / Projects (from BCM_1 bcm.service.request)"""
    __tablename__ = "projects"
    __table_args__ = {'schema': 'marketplace'}

    id = Column(Integer, primary_key=True)

    # Client Information
    client_id = Column(UUID, nullable=False, index=True)
    tenant_id = Column(UUID, nullable=False, index=True)
    client_name = Column(String(255))
    company_name = Column(String(255))
    industry = Column(String(100))
    company_size = Column(String(50))

    # Project Details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    service_type = Column(
        SQLEnum(ServiceType, name="service_type", schema="marketplace"),
        nullable=False,
        index=True
    )
    urgency = Column(
        SQLEnum(UrgencyLevel, name="urgency_level", schema="marketplace"),
        default=UrgencyLevel.MEDIUM,
        index=True
    )

    # Scope
    scope_of_work = Column(Text)
    deliverables = Column(Text)

    # Timeline
    start_date = Column(Date)
    end_date = Column(Date)
    duration_estimate_hours = Column(DECIMAL(10, 2))

    # Budget
    budget_type = Column(
        SQLEnum(BudgetType, name="budget_type", schema="marketplace"),
        default=BudgetType.NEGOTIABLE
    )
    budget_min = Column(DECIMAL(10, 2))
    budget_max = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="USD")

    # Requirements
    required_certifications = Column(Text)
    required_experience_years = Column(Integer)
    required_skills = Column(JSONB, default=[])

    # ==================== PHASE 4: Learning & Governance Integration ====================
    required_certifications_jsonb = Column(JSONB, default=[])  # [{"certification_name": "BCM Practitioner", "required": true}]
    required_competencies = Column(JSONB, default=[])  # [{"area": "bc_planning", "min_level": "advanced"}]
    related_policies = Column(JSONB, default=[])  # [{"policy_id": 1, "relevance": "high"}]

    # Location
    work_location = Column(
        SQLEnum(WorkLocation, name="work_location", schema="marketplace"),
        default=WorkLocation.REMOTE
    )
    location_country = Column(String(100))
    location_state = Column(String(100))
    location_city = Column(String(100))

    # Status
    status = Column(
        SQLEnum(ProjectStatus, name="project_status", schema="marketplace"),
        default=ProjectStatus.DRAFT,
        index=True
    )
    published_at = Column(TIMESTAMP, index=True)

    # Selected Proposal
    selected_proposal_id = Column(Integer)
    selected_specialist_id = Column(Integer)

    # Metrics
    view_count = Column(Integer, default=0)
    proposal_count = Column(Integer, default=0)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    proposals = relationship("Proposal", back_populates="project", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="project")


# ============================================================================
# PROPOSALS
# ============================================================================

class Proposal(Base):
    """Proposals from specialists for projects"""
    __tablename__ = "proposals"
    __table_args__ = (
        UniqueConstraint('project_id', 'specialist_id', name='unique_specialist_project'),
        {'schema': 'marketplace'}
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('marketplace.projects.id', ondelete='CASCADE'), nullable=False, index=True)
    specialist_id = Column(Integer, ForeignKey('marketplace.specialists.id', ondelete='CASCADE'), nullable=False, index=True)

    # Proposal Details
    cover_letter = Column(Text, nullable=False)
    proposed_rate = Column(DECIMAL(10, 2))
    estimated_duration_hours = Column(DECIMAL(10, 2))
    estimated_total_cost = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="USD")

    # Timeline
    proposed_start_date = Column(Date)
    proposed_end_date = Column(Date)

    # Deliverables
    deliverables = Column(Text)
    methodology = Column(Text)

    # Attachments
    attachments = Column(JSONB, default=[])

    # ==================== PHASE 4: Learning Service Integration ====================
    competency_match_score = Column(Integer, default=0)  # 0-100 match score
    matching_details = Column(JSONB, default={})  # {"bc_planning": {"required": "advanced", "specialist": "expert", "match": true}}

    # Status
    status = Column(
        SQLEnum(ProposalStatus, name="proposal_status", schema="marketplace"),
        default=ProposalStatus.PENDING,
        index=True
    )

    # Response tracking
    viewed_by_client = Column(Boolean, default=False)
    viewed_at = Column(TIMESTAMP)
    responded_at = Column(TIMESTAMP)
    response_notes = Column(Text)

    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="proposals")
    specialist = relationship("Specialist", back_populates="proposals")


# ============================================================================
# REVIEWS
# ============================================================================

class Review(Base):
    """Reviews for specialists"""
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint('project_id', 'reviewer_id', name='unique_project_reviewer'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        {'schema': 'marketplace'}
    )

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('marketplace.projects.id', ondelete='CASCADE'), nullable=False, index=True)
    specialist_id = Column(Integer, ForeignKey('marketplace.specialists.id', ondelete='CASCADE'), nullable=False, index=True)
    reviewer_id = Column(UUID, nullable=False)  # Client user

    # Rating
    rating = Column(Integer, nullable=False, index=True)

    # Review Details
    title = Column(String(255))
    review_text = Column(Text)

    # Category Ratings
    communication_rating = Column(Integer)
    quality_rating = Column(Integer)
    professionalism_rating = Column(Integer)
    timeliness_rating = Column(Integer)

    # Specialist Response
    specialist_response = Column(Text)
    responded_at = Column(TIMESTAMP)

    # Visibility
    is_public = Column(Boolean, default=True, index=True)

    # Verification
    is_verified = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="reviews")
    specialist = relationship("Specialist", back_populates="reviews")


# ============================================================================
# PHASE 4: Junction Tables for Learning & Governance Integration
# ============================================================================

class SpecialistCompetency(Base):
    """
    Detailed competency records for specialists
    Sourced from Learning Service, Governance Service, or self-assessed
    """
    __tablename__ = "specialist_competencies"
    __table_args__ = {'schema': 'marketplace'}

    # Composite primary key
    specialist_id = Column(Integer, ForeignKey('marketplace.specialists.id', ondelete='CASCADE'), primary_key=True)
    competency_area = Column(String(100), primary_key=True)  # e.g., "bc_planning", "risk_assessment"

    # Competency details
    proficiency_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    score = Column(Integer, default=0)  # 0-100
    source = Column(String(50))  # learning_service, governance_service, self_assessed, client_verified

    # Evidence
    certifications_count = Column(Integer, default=0)
    trainings_completed = Column(Integer, default=0)
    projects_completed = Column(Integer, default=0)
    evidence_notes = Column(Text)

    # Assessment
    last_assessed_date = Column(TIMESTAMP)
    assessed_by = Column(String(255))
    next_review_date = Column(TIMESTAMP)

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SpecialistCompetency(specialist_id={self.specialist_id}, area='{self.competency_area}', level='{self.proficiency_level}', score={self.score})>"


class ProjectCompetencyRequirement(Base):
    """
    Competency requirements for projects
    Used in specialist matching algorithm
    """
    __tablename__ = "project_competency_requirements"
    __table_args__ = {'schema': 'marketplace'}

    # Composite primary key
    project_id = Column(Integer, ForeignKey('marketplace.projects.id', ondelete='CASCADE'), primary_key=True)
    competency_area = Column(String(100), primary_key=True)

    # Requirement details
    minimum_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    is_mandatory = Column(Boolean, default=True)
    weight = Column(Integer, default=1)  # Importance weight for matching (1-10)

    # Matching statistics
    matching_specialists_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ProjectCompetencyRequirement(project_id={self.project_id}, area='{self.competency_area}', min_level='{self.minimum_level}')>"


class SpecialistCertificationNormalized(Base):
    """
    Normalized certification records
    Alternative to JSONB storage in specialists.certifications_jsonb
    Allows better querying and expiry tracking
    """
    __tablename__ = "specialist_certifications_normalized"
    __table_args__ = {'schema': 'marketplace'}

    id = Column(Integer, primary_key=True)
    specialist_id = Column(Integer, ForeignKey('marketplace.specialists.id', ondelete='CASCADE'), nullable=False, index=True)

    # Certification details (from Learning Service)
    certification_number = Column(String(100), nullable=False, unique=True, index=True)
    certification_name = Column(String(255), nullable=False)
    program_code = Column(String(50))
    program_name = Column(String(255))

    # Dates
    issued_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    # Note: is_expired computed in application layer: expiry_date < current_date

    # Verification
    verified = Column(Boolean, default=False)
    verified_at = Column(TIMESTAMP)
    verified_by = Column(String(255))

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SpecialistCertificationNormalized(specialist_id={self.specialist_id}, cert='{self.certification_number}', name='{self.certification_name}')>"
