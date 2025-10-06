"""
Learning Module Database Models
ISO 22301 Clause 7.2 (Competence) & 7.3 (Awareness)
BCI GPG Practice 2 (PP2: Embracing BC)

Reference: /services/SERVICES/BCM/analysis/bia/database/models.py
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON, Enum as SQLEnum, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

# ==================== ENUMS ====================

class ProgramStatus(str, Enum):
    """Training program status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

class EnrollmentStatus(str, Enum):
    """Training enrollment status"""
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
    """BCI competency levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class AssessmentStatus(str, Enum):
    """Assessment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PASSED = "passed"
    FAILED = "failed"

class CampaignStatus(str, Enum):
    """Awareness campaign status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AchievementLevel(str, Enum):
    """Gamification achievement levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

# ==================== CORE MODELS ====================

class TrainingProgram(Base):
    """
    Training programs for BC competency development
    ISO 22301 Clause 7.2 - Competence
    BCI GPG PP2 - Training and Education
    """
    __tablename__ = "training_programs"
    __table_args__ = {'schema': 'learning'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Program Details
    program_code = Column(String(50), unique=True, nullable=False, index=True)
    program_name = Column(String(255), nullable=False)
    description = Column(Text)
    program_type = Column(String(50), nullable=False)  # Links to program_types seed data

    # Classification
    bci_training_level = Column(String(50))  # Links to bci_training_levels
    target_audience = Column(String(100))
    iso_clause = Column(String(20))  # e.g., "7.2", "7.3"

    # Content
    learning_objectives = Column(JSON)  # Array of objectives
    curriculum = Column(JSON)  # Course modules/chapters
    materials = Column(JSON)  # Training materials (PDFs, videos, etc.)
    prerequisites = Column(JSON)  # Required prior training

    # Logistics
    duration_hours = Column(Integer)
    delivery_method = Column(String(50))  # online, classroom, hybrid, self_paced
    instructor_required = Column(Boolean, default=False)
    max_participants = Column(Integer)

    # Assessment
    assessment_required = Column(Boolean, default=True)
    passing_score = Column(Integer, default=70)
    certification_awarded = Column(Boolean, default=False)
    certification_name = Column(String(255))
    certification_validity_months = Column(Integer)  # Recertification period

    # Status
    status = Column(SQLEnum(ProgramStatus), default=ProgramStatus.DRAFT, nullable=False)
    published_date = Column(DateTime)

    # Metadata
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments = relationship("TrainingEnrollment", back_populates="program")

    def __repr__(self):
        return f"<TrainingProgram {self.program_code}: {self.program_name}>"


class TrainingEnrollment(Base):
    """
    Individual enrollments in training programs
    Tracks progress and completion
    """
    __tablename__ = "training_enrollments"
    __table_args__ = (
        # Performance indexes for common queries
        Index('idx_enrollment_person', 'tenant_id', 'person_id'),
        Index('idx_enrollment_status', 'tenant_id', 'status'),
        Index('idx_enrollment_program', 'program_id', 'status'),
        Index('idx_enrollment_dates', 'tenant_id', 'enrolled_date', 'completed_date'),
        Index('idx_enrollment_certification', 'tenant_id', 'certification_issued', 'certification_expiry_date'),
        {'schema': 'learning'}
    )

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Program & Person
    program_id = Column(Integer, ForeignKey('learning.training_programs.id'), nullable=False)
    person_id = Column(String(255), nullable=False, index=True)  # Employee ID
    person_name = Column(String(255), nullable=False)
    person_role = Column(String(100))
    person_department = Column(String(100))

    # Enrollment Details
    enrolled_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    enrollment_type = Column(String(50))  # mandatory, voluntary, role_based
    assigned_by = Column(String(255))  # Manager who assigned
    target_completion_date = Column(DateTime)  # Target deadline for completion

    # Progress Tracking
    status = Column(SQLEnum(EnrollmentStatus), default=EnrollmentStatus.ENROLLED, nullable=False)
    progress_percentage = Column(Integer, default=0, nullable=False)
    CheckConstraint('progress_percentage BETWEEN 0 AND 100', name='check_progress_range')

    submitted_date = Column(DateTime)
    approved_by = Column(String(255))
    approved_date = Column(DateTime)
    started_date = Column(DateTime)
    completed_date = Column(DateTime)
    due_date = Column(DateTime)

    # Assessment Results
    assessment_attempts = Column(Integer, default=0)
    assessment_score = Column(Float)
    assessment_passed = Column(Boolean, default=False)
    assessment_date = Column(DateTime)
    assessment_type = Column(String(50))
    assessor = Column(String(255))
    assessment_feedback = Column(Text)

    # Certification
    certification_issued = Column(Boolean, default=False)
    certification_number = Column(String(100))
    certification_date = Column(DateTime)
    certification_expiry_date = Column(DateTime)  # Auto-calculated based on program validity

    # Learning Data
    time_spent_hours = Column(Float, default=0)
    modules_completed = Column(JSON)  # Array of completed module IDs
    last_activity_date = Column(DateTime)

    # Gamification
    points_earned = Column(Integer, default=0)
    achievements_unlocked = Column(JSON)  # Array of achievement IDs

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    program = relationship("TrainingProgram", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment {self.person_name} in Program {self.program_id}: {self.status.value}>"


class CompetencyAssessment(Base):
    """
    Competency assessments and gap analysis
    ISO 22301 Clause 7.2 - Competence determination
    BCI GPG PP2 - Competency matrix
    """
    __tablename__ = "competency_assessments"
    __table_args__ = {'schema': 'learning'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Person & Competency
    person_id = Column(String(255), nullable=False, index=True)
    person_name = Column(String(255), nullable=False)
    person_role = Column(String(100))

    competency_area = Column(String(50), nullable=False)  # Links to competency_areas seed
    competency_name = Column(String(255), nullable=False)

    # BCI Framework
    bci_practice = Column(String(10))  # PP1-PP6
    competency_category = Column(String(50))  # awareness, training, communication, etc.

    # Assessment Levels
    required_level = Column(SQLEnum(CompetencyLevel), nullable=False)
    current_level = Column(SQLEnum(CompetencyLevel), nullable=False)
    target_level = Column(SQLEnum(CompetencyLevel))

    # Gap Analysis
    gap_exists = Column(Boolean, default=False, nullable=False, index=True)
    gap_severity = Column(String(20))  # low, medium, high, critical
    gap_description = Column(Text)

    # Evidence
    evidence_type = Column(String(50))  # training, certification, experience, demonstration
    evidence_details = Column(JSON)  # Structured evidence data
    evidence_date = Column(DateTime)
    evidence_verified = Column(Boolean, default=False)
    verified_by = Column(String(255))
    verified_date = Column(DateTime)

    # Training Plan
    training_required = Column(Boolean, default=False)
    recommended_programs = Column(JSON)  # Array of program IDs
    training_plan = Column(Text)
    estimated_duration_hours = Column(Integer)
    target_completion_date = Column(DateTime)

    # Assessment Details
    assessment_method = Column(String(50))  # Links to assessment_methods seed
    assessment_date = Column(DateTime, nullable=False)
    assessor_id = Column(String(255))
    assessor_name = Column(String(255))

    # Status
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.PENDING, nullable=False)
    next_assessment_date = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CompetencyAssessment {self.person_name} - {self.competency_area}: {self.current_level.value}>"


class AwarenessCampaign(Base):
    """
    BC Awareness campaigns
    ISO 22301 Clause 7.3 - Awareness
    BCI GPG PP2 - BC Awareness Programme
    """
    __tablename__ = "awareness_campaigns"
    __table_args__ = {'schema': 'learning'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Campaign Details
    campaign_code = Column(String(50), unique=True, nullable=False, index=True)
    campaign_name = Column(String(255), nullable=False)
    description = Column(Text)
    campaign_type = Column(String(50), nullable=False)  # Links to awareness_campaign_types seed

    # Target Audience
    target_groups = Column(JSON)  # Array of departments/roles
    target_audience_count = Column(Integer)

    # Content
    key_messages = Column(JSON)  # Array of messages
    materials = Column(JSON)  # Posters, videos, emails, etc.
    communication_channels = Column(JSON)  # email, intranet, town_halls, etc.

    # Schedule
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    frequency = Column(String(50))  # one_time, weekly, monthly, quarterly, annual

    # Execution
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.PLANNED, nullable=False)
    campaign_owner = Column(String(255), nullable=False)
    responsible_team = Column(JSON)

    # Participation Tracking
    total_participants = Column(Integer, default=0)
    participation_rate = Column(Float)  # Percentage

    # Effectiveness Metrics
    awareness_survey_sent = Column(Boolean, default=False)
    survey_responses = Column(Integer, default=0)
    survey_results = Column(JSON)  # Survey data
    effectiveness_score = Column(Float)  # 0-100

    # Feedback
    feedback_collected = Column(JSON)
    lessons_learned = Column(Text)

    # Metadata
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    def __repr__(self):
        return f"<AwarenessCampaign {self.campaign_code}: {self.campaign_name}>"


class TrainingTemplate(Base):
    """
    Training templates and forms library
    Templates for assessments, checklists, materials
    """
    __tablename__ = "training_templates"
    __table_args__ = {'schema': 'learning'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Template Details
    template_code = Column(String(50), unique=True, nullable=False, index=True)
    template_name = Column(String(255), nullable=False)
    description = Column(Text)

    # Classification
    template_type = Column(String(50), nullable=False)  # Links to template_types seed
    category = Column(String(50), nullable=False)  # form, checklist, document, report
    iso_clause = Column(String(20))

    # Content
    content = Column(JSON)  # Template structure (HTML, JSON schema, etc.)
    content_format = Column(String(20))  # html, json, markdown, pdf
    form_schema = Column(JSON)  # For interactive forms

    # Usage
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=False)  # Shared across tenants
    usage_count = Column(Integer, default=0)
    last_used_date = Column(DateTime)

    # AI Enhancement
    is_ai_enhanced = Column(Boolean, default=False)
    ai_prompt = Column(Text)  # For AI-generated content

    # Metadata
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TrainingTemplate {self.template_code}: {self.template_name}>"


class UserAchievement(Base):
    """
    Gamification: User achievements and points
    Tracks learning progress, badges, leaderboards
    """
    __tablename__ = "user_achievements"
    __table_args__ = (
        # Indexes for leaderboard and user achievement queries
        Index('idx_achievement_person_points', 'tenant_id', 'person_id', 'total_points'),
        Index('idx_achievement_leaderboard', 'tenant_id', 'total_points', 'earned_date'),
        Index('idx_achievement_action', 'tenant_id', 'action_type', 'earned_date'),
        {'schema': 'learning'}
    )

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # User
    person_id = Column(String(255), nullable=False, index=True)
    person_name = Column(String(255), nullable=False)

    # Achievement
    achievement_code = Column(String(50), nullable=False)  # Links to achievement_types seed
    achievement_name = Column(String(255), nullable=False)
    achievement_level = Column(SQLEnum(AchievementLevel))

    # Action that triggered achievement
    action_code = Column(String(50), nullable=False)  # Links to points_actions seed
    action_type = Column(String(50), nullable=False)  # training, competency, awareness, etc.

    # Points
    points_earned = Column(Integer, default=0, nullable=False)
    total_points = Column(Integer, default=0, nullable=False)  # Cumulative

    # Context
    related_entity_type = Column(String(50))  # program, enrollment, campaign, etc.
    related_entity_id = Column(Integer)

    # Achievement Details
    earned_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    badge_icon = Column(String(50))
    badge_color = Column(String(20))

    # Streaks
    is_streak_achievement = Column(Boolean, default=False)
    streak_count = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Achievement {self.person_name}: {self.achievement_name} ({self.points_earned} pts)>"


# ==================== INDEXES ====================

Index('idx_training_programs_tenant_status', TrainingProgram.tenant_id, TrainingProgram.status)
Index('idx_training_programs_type', TrainingProgram.program_type)

Index('idx_enrollments_tenant_person', TrainingEnrollment.tenant_id, TrainingEnrollment.person_id)
Index('idx_enrollments_status', TrainingEnrollment.status)
Index('idx_enrollments_program', TrainingEnrollment.program_id)

Index('idx_competency_tenant_person', CompetencyAssessment.tenant_id, CompetencyAssessment.person_id)
Index('idx_competency_area', CompetencyAssessment.competency_area)
Index('idx_competency_gap', CompetencyAssessment.gap_exists)

Index('idx_campaigns_tenant_status', AwarenessCampaign.tenant_id, AwarenessCampaign.status)
Index('idx_campaigns_type', AwarenessCampaign.campaign_type)

Index('idx_templates_tenant_active', TrainingTemplate.tenant_id, TrainingTemplate.is_active)
Index('idx_templates_type', TrainingTemplate.template_type)

Index('idx_achievements_tenant_person', UserAchievement.tenant_id, UserAchievement.person_id)
Index('idx_achievements_code', UserAchievement.achievement_code)
