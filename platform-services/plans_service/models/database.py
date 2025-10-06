"""
Plans Service Database Models (SQLAlchemy)
ISO 22301 Clause 8.4 - Business Continuity Plans and Procedures
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

from .domain import (
    PlanType, PlanPriority, PlanStatus, ProcedureType, ResourceType,
    ResourceCriticality, AvailabilityRequirement, ReviewFrequency,
    ContactListType, CommunicationType, ActivationType, EffectivenessRating,
    ReviewType
)


Base = declarative_base()


class Plan(Base):
    """Business Continuity Plan - ISO 22301 Clause 8.4"""
    __tablename__ = "plans"
    __table_args__ = (
        # Composite indexes for common query patterns
        Index('ix_plans_tenant_type', 'tenant_id', 'plan_type'),
        Index('ix_plans_tenant_status', 'tenant_id', 'status'),
        Index('ix_plans_tenant_priority', 'tenant_id', 'priority'),
        Index('ix_plans_tenant_review', 'tenant_id', 'next_review_date'),
        Index('ix_plans_status_priority', 'status', 'priority'),
        Index('ix_plans_priority_created', 'priority', 'created_at'),
        Index('ix_plans_review_due', 'next_review_date', 'status'),
        # Additional indexes for optimization
        Index('ix_plans_tenant_status_updated', 'tenant_id', 'status', 'updated_at'),
        Index('ix_plans_owner', 'plan_owner_user_id', 'status'),
        Index('ix_plans_team_leader', 'team_leader_user_id', 'status'),
        Index('ix_plans_next_test_date', 'next_test_date', 'status'),
        Index('ix_plans_approval_status', 'tenant_id', 'approved_by_user_id', 'approval_date'),
        {'schema': 'plans'}
    )

    # Primary Key
    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(100), nullable=False, index=True)

    # Plan Identification
    plan_code = Column(String(50), unique=True, nullable=False, index=True)
    plan_name = Column(String(255), nullable=False)

    # Classification
    plan_type = Column(SQLEnum(PlanType), nullable=False)
    priority = Column(SQLEnum(PlanPriority), default=PlanPriority.MEDIUM)
    status = Column(SQLEnum(PlanStatus), default=PlanStatus.DRAFT)
    version = Column(String(20), default='1.0')
    previous_version_id = Column(Integer, ForeignKey('plans.plans.plan_id'))

    # ISO 8.4.4 Content
    objective = Column(Text)
    scope = Column(Text)
    assumptions = Column(Text)

    # Activation
    activation_triggers = Column(JSON)
    activation_authority_user_id = Column(String(100))

    # Recovery Objectives
    rto_hours = Column(Integer)
    rpo_hours = Column(Integer)
    mtpd_hours = Column(Integer)

    # Links to Analysis
    based_on_bia_id = Column(Integer)
    based_on_risk_ids = Column(JSON)

    # Team
    plan_owner_user_id = Column(String(100), nullable=False)
    team_leader_user_id = Column(String(100))
    team_member_user_ids = Column(JSON)

    # Review & Maintenance
    review_frequency = Column(SQLEnum(ReviewFrequency))
    last_review_date = Column(DateTime)
    next_review_date = Column(DateTime)
    last_test_date = Column(DateTime)
    next_test_date = Column(DateTime)

    # Approval
    approved_by_user_id = Column(String(100))
    approval_date = Column(DateTime)
    approval_notes = Column(Text)

    # Audit Trail
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(100))
    active = Column(Boolean, default=True)

    # Relationships
    procedures = relationship("Procedure", back_populates="plan", cascade="all, delete-orphan")
    resources = relationship("PlanResource", back_populates="plan", cascade="all, delete-orphan")
    contact_lists = relationship("ContactList", back_populates="plan", cascade="all, delete-orphan")
    activations = relationship("PlanActivation", back_populates="plan", cascade="all, delete-orphan")
    reviews = relationship("PlanReview", back_populates="plan", cascade="all, delete-orphan")


class Procedure(Base):
    """Plan Procedure - ISO 22301 Clause 8.4.4"""
    __tablename__ = "procedures"
    __table_args__ = (
        # Composite indexes for procedure queries
        Index('ix_procedures_plan_sequence', 'plan_id', 'sequence'),
        Index('ix_procedures_tenant_type', 'tenant_id', 'procedure_type'),
        Index('ix_procedures_responsible_user', 'responsible_user_id', 'plan_id'),
        Index('ix_procedures_plan_active', 'plan_id', 'active'),
        {'schema': 'plans'}
    )

    procedure_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('plans.plans.plan_id'), nullable=False, index=True)
    tenant_id = Column(String(100), nullable=False, index=True)

    # Sequencing
    sequence = Column(Integer, default=10)
    procedure_name = Column(String(255), nullable=False)

    # Classification
    procedure_type = Column(SQLEnum(ProcedureType), nullable=False)

    # Content
    description = Column(Text)
    estimated_duration_minutes = Column(Integer)

    # Responsibility
    responsible_role = Column(String(100))
    responsible_user_id = Column(String(100))

    # Dependencies
    prerequisite_procedure_ids = Column(JSON)

    # Resources
    required_resources = Column(Text)

    # Verification
    success_criteria = Column(Text)
    verification_checklist = Column(JSON)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(100))
    active = Column(Boolean, default=True)

    # Relationships
    plan = relationship("Plan", back_populates="procedures")


class PlanResource(Base):
    """Plan Resource - ISO 22301 Clause 8.4.4"""
    __tablename__ = "plan_resources"
    __table_args__ = (
        # Composite indexes for resource queries
        Index('ix_resources_plan_type', 'plan_id', 'resource_type'),
        Index('ix_resources_plan_criticality', 'plan_id', 'criticality'),
        Index('ix_resources_tenant_type', 'tenant_id', 'resource_type'),
        Index('ix_resources_criticality_avail', 'criticality', 'availability_requirement'),
        {'schema': 'plans'}
    )

    resource_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('plans.plans.plan_id'), nullable=False, index=True)
    tenant_id = Column(String(100), nullable=False, index=True)

    resource_name = Column(String(255), nullable=False)

    # Classification
    resource_type = Column(SQLEnum(ResourceType), nullable=False)

    # Availability
    availability_requirement = Column(SQLEnum(AvailabilityRequirement))

    # Criticality
    criticality = Column(SQLEnum(ResourceCriticality))

    # Details
    description = Column(Text)
    quantity_required = Column(Integer, default=1)
    location = Column(String(255))
    contact_person = Column(String(255))
    contact_details = Column(Text)

    # Alternatives
    alternative_resources = Column(Text)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(100))
    active = Column(Boolean, default=True)

    # Relationships
    plan = relationship("Plan", back_populates="resources")


class ContactList(Base):
    """Contact List - ISO 22301 Clause 8.4.3"""
    __tablename__ = "contact_lists"
    __table_args__ = (
        # Composite indexes for contact list queries
        Index('ix_contacts_plan_type', 'plan_id', 'list_type'),
        Index('ix_contacts_tenant_type', 'tenant_id', 'list_type'),
        Index('ix_contacts_verification', 'next_verification_date', 'tenant_id'),
        {'schema': 'plans'}
    )

    contact_list_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('plans.plans.plan_id'), index=True)
    tenant_id = Column(String(100), nullable=False, index=True)

    list_name = Column(String(255), nullable=False)
    list_type = Column(SQLEnum(ContactListType))

    description = Column(Text)

    # Contacts stored as JSON array
    contacts = Column(JSON)

    # Call tree structure
    call_tree_structure = Column(JSON)

    # Metadata
    last_verified_date = Column(DateTime)
    next_verification_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(100))
    active = Column(Boolean, default=True)

    # Relationships
    plan = relationship("Plan", back_populates="contact_lists")


class CommunicationTemplate(Base):
    """Communication Template - ISO 22301 Clause 8.4.3"""
    __tablename__ = "communication_templates"
    __table_args__ = (
        # Composite indexes for template queries
        Index('ix_comm_templates_tenant_type', 'tenant_id', 'communication_type'),
        Index('ix_comm_templates_tenant_active', 'tenant_id', 'active'),
        {'schema': 'plans'}
    )

    template_id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(100), nullable=False, index=True)

    template_name = Column(String(255), nullable=False)
    template_code = Column(String(50), unique=True, nullable=False)

    # Classification
    communication_type = Column(SQLEnum(CommunicationType))

    audience = Column(String(100))
    channel = Column(String(50))

    # Content
    subject_template = Column(String(500))
    body_template = Column(Text)

    # Variables
    template_variables = Column(JSON)

    # Approval
    requires_approval = Column(Boolean, default=False)
    approval_authority = Column(String(100))

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    active = Column(Boolean, default=True)


class PlanActivation(Base):
    """Plan Activation - Tracking actual plan activations"""
    __tablename__ = "plan_activations"
    __table_args__ = (
        # Composite indexes for activation queries
        Index('ix_activations_plan_type', 'plan_id', 'activation_type'),
        Index('ix_activations_tenant_date', 'tenant_id', 'activation_datetime'),
        Index('ix_activations_activated_by', 'activated_by_user_id', 'activation_datetime'),
        Index('ix_activations_effectiveness', 'effectiveness_rating', 'tenant_id'),
        Index('ix_activations_rto_achieved', 'rto_achieved', 'tenant_id'),
        {'schema': 'plans'}
    )

    activation_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('plans.plans.plan_id'), nullable=False, index=True)
    tenant_id = Column(String(100), nullable=False, index=True)

    activation_name = Column(String(255), nullable=False)

    # Type
    activation_type = Column(SQLEnum(ActivationType))

    # Trigger
    trigger_event = Column(Text)
    triggered_by_incident_id = Column(Integer)

    # Timeline
    activation_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    activated_by_user_id = Column(String(100), nullable=False)
    deactivation_datetime = Column(DateTime)

    # Performance
    actual_activation_time_minutes = Column(Integer)
    actual_recovery_time_hours = Column(Float)

    # Effectiveness
    effectiveness_rating = Column(SQLEnum(EffectivenessRating))

    # RTO Achievement
    target_rto_hours = Column(Float)
    actual_rto_hours = Column(Float)
    rto_achieved = Column(Boolean)

    # Results
    summary = Column(Text)
    lessons_learned = Column(Text)
    improvement_actions = Column(Text)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    plan = relationship("Plan", back_populates="activations")


class PlanReview(Base):
    """Plan Review - Track plan reviews"""
    __tablename__ = "plan_reviews"
    __table_args__ = (
        # Composite indexes for review queries
        Index('ix_reviews_plan_type', 'plan_id', 'review_type'),
        Index('ix_reviews_tenant_date', 'tenant_id', 'review_date'),
        Index('ix_reviews_reviewed_by', 'reviewed_by_user_id', 'review_date'),
        Index('ix_reviews_approval_status', 'approved', 'approved_by_user_id'),
        {'schema': 'plans'}
    )

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('plans.plans.plan_id'), nullable=False, index=True)
    tenant_id = Column(String(100), nullable=False, index=True)

    review_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    review_type = Column(SQLEnum(ReviewType))

    reviewed_by_user_id = Column(String(100), nullable=False)

    # Review findings
    is_current = Column(Boolean)
    is_effective = Column(Boolean)

    findings = Column(Text)
    recommendations = Column(Text)

    # Action items
    action_items = Column(JSON)

    # Approval
    approved = Column(Boolean, default=False)
    approved_by_user_id = Column(String(100))
    approval_date = Column(DateTime)

    # Version management
    resulted_in_new_version = Column(Boolean, default=False)
    new_version_id = Column(Integer)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    plan = relationship("Plan", back_populates="reviews")


class PlanTemplate(Base):
    """Plan Template - Template library"""
    __tablename__ = "plan_templates"
    __table_args__ = (
        # Composite indexes for template queries
        Index('ix_templates_tenant_type', 'tenant_id', 'plan_type'),
        Index('ix_templates_tenant_active', 'tenant_id', 'active'),
        Index('ix_templates_global_type', 'is_global', 'plan_type'),
        Index('ix_templates_usage', 'times_used', 'is_global'),
        {'schema': 'plans'}
    )

    template_id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String(100), index=True)

    template_name = Column(String(255), nullable=False)
    template_code = Column(String(50), unique=True, nullable=False)

    plan_type = Column(SQLEnum(PlanType), nullable=False)

    # Template content
    template_structure = Column(JSON)

    description = Column(Text)

    # Usage
    is_global = Column(Boolean, default=False)
    times_used = Column(Integer, default=0)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    active = Column(Boolean, default=True)
