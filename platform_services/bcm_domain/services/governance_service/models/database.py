"""
Governance Service - Database Models (SQLAlchemy)
ISO 22301 Clauses: 4 (Context), 5 (Leadership), 6 (Planning), 7 (Support)
PostgreSQL implementation with full multi-tenancy support
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, JSON,
    CheckConstraint, Index, ForeignKey, Boolean, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

# Enums
class PolicyStatus(str, enum.Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    ARCHIVED = "archived"

class PolicyType(str, enum.Enum):
    BCMS_POLICY = "bcms_policy"
    BC_POLICY = "bc_policy"
    IT_DR_POLICY = "it_dr_policy"
    SECURITY_POLICY = "security_policy"
    HR_POLICY = "hr_policy"
    OTHER = "other"

class RoleType(str, enum.Enum):
    BCMS_MANAGER = "bcms_manager"
    BC_COORDINATOR = "bc_coordinator"
    INCIDENT_COMMANDER = "incident_commander"
    RECOVERY_TEAM_LEADER = "recovery_team_leader"
    DEPARTMENT_HEAD = "department_head"
    EXECUTIVE = "executive"
    OTHER = "other"

class RoleStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class ResourceType(str, enum.Enum):
    HUMAN = "human"
    TECHNOLOGY = "technology"
    FACILITY = "facility"
    BUDGET = "budget"
    EQUIPMENT = "equipment"
    DOCUMENTATION = "documentation"
    OTHER = "other"

class ResourceAvailability(str, enum.Enum):
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"

class CompetenceLevel(str, enum.Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class EvidenceType(str, enum.Enum):
    TRAINING = "training"
    CERTIFICATION = "certification"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    ASSESSMENT = "assessment"

# Main Tables

class BCMPolicy(Base):
    """BCM Policy Management - ISO 22301 Clause 5.2"""
    __tablename__ = "bcm_policies"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=False, index=True)

    # Policy Details
    title = Column(String(255), nullable=False)
    policy_type = Column(SQLEnum(PolicyType), nullable=False)
    version = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)

    # ISO 22301 Clause Reference
    iso_clause = Column(String(50))  # 5.2, 6.2, etc.

    # Approval Workflow
    status = Column(SQLEnum(PolicyStatus), default=PolicyStatus.DRAFT)
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    approval_comments = Column(Text)

    # Review Schedule
    review_frequency_months = Column(Integer, default=12)
    last_review_date = Column(DateTime)
    next_review_date = Column(DateTime)

    # Scope and Applicability
    scope = Column(Text)
    applicable_departments = Column(JSON, default=[])
    applicable_locations = Column(JSON, default=[])

    # Ownership
    policy_owner = Column(String(255))
    created_by = Column(String(255))

    # Workflow tracking
    workflow_state = Column(String(50), default="draft")
    workflow_history = Column(JSON, default=[])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    effective_date = Column(DateTime)
    expiry_date = Column(DateTime)

    # Relationships
    versions = relationship("PolicyVersion", back_populates="policy", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_policy_tenant', 'tenant_id'),
        Index('idx_policy_status', 'status'),
        Index('idx_policy_type', 'policy_type'),
        Index('idx_policy_next_review', 'next_review_date'),
    )

    def __repr__(self):
        return f"<BCMPolicy(id={self.id}, title='{self.title}', version={self.version})>"


class PolicyVersion(Base):
    """Policy Version History"""
    __tablename__ = "policy_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer, ForeignKey('bcm_policies.id', ondelete='CASCADE'), nullable=False)

    # Version Info
    version = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    changes_summary = Column(Text)

    # Metadata
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    policy = relationship("BCMPolicy", back_populates="versions")

    __table_args__ = (
        Index('idx_version_policy', 'policy_id'),
    )


class OrganizationalRole(Base):
    """Organizational Roles & Responsibilities - ISO 22301 Clause 5.3"""
    __tablename__ = "organizational_roles"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=False, index=True)

    # Role Details
    role_name = Column(String(255), nullable=False)
    role_type = Column(SQLEnum(RoleType), nullable=False)
    description = Column(Text)

    # Responsibilities (JSONB array)
    responsibilities = Column(JSON, default=[])
    """
    [
        {"description": "Maintain BCMS documentation", "priority": "high"},
        {"description": "Conduct annual reviews", "priority": "medium"}
    ]
    """

    # Authorities (JSONB array)
    authorities = Column(JSON, default=[])
    """
    [
        {"authority": "Approve BC plans", "scope": "organization-wide"},
        {"authority": "Declare incidents", "scope": "all-locations"}
    ]
    """

    # Assignment
    assigned_to = Column(String(255))  # User ID
    assigned_to_name = Column(String(255))
    assigned_at = Column(DateTime)
    backup_person = Column(String(255))
    backup_person_name = Column(String(255))

    # ISO 22301 Requirements
    iso_clause = Column(String(50), default="5.3")
    competence_requirements = Column(JSON, default=[])
    """
    [
        {"competence": "BCM Certification", "level": "advanced", "mandatory": true},
        {"competence": "ISO 22301 Knowledge", "level": "expert", "mandatory": true}
    ]
    """

    # Status
    status = Column(SQLEnum(RoleStatus), default=RoleStatus.ACTIVE)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    competence_records = relationship("CompetenceRecord", back_populates="role", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_role_tenant', 'tenant_id'),
        Index('idx_role_type', 'role_type'),
        Index('idx_role_assigned', 'assigned_to'),
        Index('idx_role_status', 'status'),
    )

    def __repr__(self):
        return f"<OrganizationalRole(id={self.id}, role_name='{self.role_name}', type={self.role_type})>"


class BCMResource(Base):
    """BCM Resources - ISO 22301 Clause 7.1"""
    __tablename__ = "bcm_resources"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=False, index=True)

    # Resource Details
    resource_name = Column(String(255), nullable=False)
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    description = Column(Text)

    # Allocation
    allocated_to = Column(String(255))  # Process/Activity/Department
    allocated_to_type = Column(String(50))  # process, activity, department, team
    quantity = Column(Float)
    unit = Column(String(50))  # hours, units, licenses, sq_meters

    # Availability
    availability = Column(SQLEnum(ResourceAvailability), default=ResourceAvailability.AVAILABLE)
    available_from = Column(DateTime)
    available_until = Column(DateTime)

    # Cost & Budget
    cost_per_unit = Column(Float)
    total_cost = Column(Float)
    budget_code = Column(String(100))
    cost_center = Column(String(100))

    # Location (for physical resources)
    location = Column(String(255))
    geographical_scope = Column(String(100))

    # Criticality
    criticality = Column(Integer, CheckConstraint('criticality BETWEEN 1 AND 5'))
    is_critical = Column(Boolean, default=False)

    # Recovery Information
    alternative_resource = Column(String(255))
    recovery_time_hours = Column(Integer)

    # Metadata
    owner = Column(String(255))
    contact_person = Column(String(255))
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_resource_tenant', 'tenant_id'),
        Index('idx_resource_type', 'resource_type'),
        Index('idx_resource_availability', 'availability'),
        Index('idx_resource_allocated', 'allocated_to'),
    )

    def __repr__(self):
        return f"<BCMResource(id={self.id}, name='{self.resource_name}', type={self.resource_type})>"


class CompetenceRecord(Base):
    """Competence Records - ISO 22301 Clause 7.2"""
    __tablename__ = "competence_records"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=False, index=True)

    # Person
    person_id = Column(String(255), nullable=False)
    person_name = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('organizational_roles.id', ondelete='SET NULL'))

    # Competence Area
    competence_area = Column(String(255), nullable=False)
    competence_category = Column(String(100))  # bcm, technical, leadership, crisis_management

    # Required vs Current Level
    required_level = Column(SQLEnum(CompetenceLevel), nullable=False)
    current_level = Column(SQLEnum(CompetenceLevel))
    gap_exists = Column(Boolean, default=False)
    gap_description = Column(Text)

    # Evidence (JSONB)
    evidence_type = Column(SQLEnum(EvidenceType), nullable=False)
    evidence_details = Column(JSON, default={})
    """
    {
        "training_name": "ISO 22301 Lead Implementer",
        "provider": "BSI",
        "completion_date": "2024-01-15",
        "certificate_number": "ISO22301-2024-001",
        "expiry_date": "2027-01-15"
    }
    """

    # Verification
    verified = Column(Boolean, default=False)
    verified_by = Column(String(255))
    verified_at = Column(DateTime)
    verification_notes = Column(Text)

    # Training Plan (if gap exists)
    training_required = Column(Boolean, default=False)
    training_plan = Column(Text)
    training_deadline = Column(DateTime)
    training_budget = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow)

    # Relationship
    role = relationship("OrganizationalRole", back_populates="competence_records")

    __table_args__ = (
        Index('idx_competence_tenant', 'tenant_id'),
        Index('idx_competence_person', 'person_id'),
        Index('idx_competence_role', 'role_id'),
        Index('idx_competence_gap', 'gap_exists'),
    )

    def __repr__(self):
        return f"<CompetenceRecord(id={self.id}, person='{self.person_name}', area='{self.competence_area}')>"


class BCMObjective(Base):
    """BCM Objectives - ISO 22301 Clause 6.2"""
    __tablename__ = "bcm_objectives"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=False, index=True)

    # Objective Details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    objective_type = Column(String(100))  # strategic, operational, tactical

    # SMART Criteria
    specific = Column(Text)
    measurable = Column(Text)
    achievable = Column(Text)
    relevant = Column(Text)
    time_bound = Column(Text)

    # Target & Metrics
    target_value = Column(Float)
    current_value = Column(Float)
    unit_of_measure = Column(String(50))
    measurement_frequency = Column(String(50))  # daily, weekly, monthly, quarterly

    # Ownership
    objective_owner = Column(String(255), nullable=False)
    department = Column(String(255))

    # Timeline
    start_date = Column(DateTime)
    target_date = Column(DateTime, nullable=False)
    completion_date = Column(DateTime)

    # Status
    status = Column(String(50), default="not_started")  # not_started, in_progress, completed, cancelled
    progress_percentage = Column(Integer, CheckConstraint('progress_percentage BETWEEN 0 AND 100'), default=0)

    # Resources
    allocated_budget = Column(Float)
    resources_required = Column(JSON, default=[])

    # Related Plans/Processes
    related_processes = Column(JSON, default=[])
    related_risks = Column(JSON, default=[])

    # ISO 22301 Clause
    iso_clause = Column(String(50), default="6.2")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_objective_tenant', 'tenant_id'),
        Index('idx_objective_owner', 'objective_owner'),
        Index('idx_objective_status', 'status'),
        Index('idx_objective_target_date', 'target_date'),
    )

    def __repr__(self):
        return f"<BCMObjective(id={self.id}, title='{self.title}', status={self.status})>"


class CommunicationPlan(Base):
    """Communication Plan - ISO 22301 Clause 7.4"""
    __tablename__ = "communication_plans"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=False, index=True)

    # Plan Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    plan_type = Column(String(50))  # internal, external, crisis, stakeholder

    # Stakeholders (JSONB)
    stakeholders = Column(JSON, default=[])
    """
    [
        {
            "name": "Executive Team",
            "type": "internal",
            "contact_method": "email",
            "frequency": "daily",
            "responsible_person": "BCMS Manager"
        }
    ]
    """

    # Communication Channels
    channels = Column(JSON, default=[])
    """
    [
        {"channel": "email", "primary": true, "backup": "phone"},
        {"channel": "sms", "primary": false, "backup": "messenger"}
    ]
    """

    # Activation Triggers
    triggers = Column(JSON, default=[])

    # Templates
    templates = Column(JSON, default={})

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_comm_tenant', 'tenant_id'),
        Index('idx_comm_type', 'plan_type'),
    )

    def __repr__(self):
        return f"<CommunicationPlan(id={self.id}, name='{self.name}')>"


class Stakeholder(Base):
    """Stakeholder Register - ISO 22301 Clause 4.2"""
    __tablename__ = "stakeholders"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=False, index=True)

    # Basic Information
    stakeholder_name = Column(String(255), nullable=False)
    stakeholder_type = Column(String(50), nullable=False)
    # customer, regulator, supplier, employee, investor, partner, community, media
    category = Column(String(50))  # internal, external

    # Contact Information
    contact_person = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(100))

    # Influence Analysis
    influence_level = Column(String(20), nullable=False)  # high, medium, low
    interest_level = Column(String(20), nullable=False)   # high, medium, low
    power_level = Column(String(20))                      # high, medium, low

    # Requirements and Expectations
    requirements = Column(JSON, default=[])
    """
    [
        {"requirement": "...", "priority": "high|medium|low", "source": "..."}
    ]
    """
    expectations = Column(JSON, default=[])
    """
    [
        {"expectation": "...", "category": "service|communication|response_time"}
    ]
    """

    # Communication
    communication_frequency = Column(String(50))  # daily, weekly, monthly, quarterly, as_needed
    communication_method = Column(String(50))     # email, phone, meeting, portal, report
    communication_language = Column(String(10))   # en, ru, etc.

    # BC-specific fields
    needs_notification_during_incident = Column(Boolean, default=False)
    notification_priority = Column(Integer)  # 1 (highest) - 5 (lowest)
    critical_to_bcms = Column(Boolean, default=False)

    # Relationships
    related_processes = Column(JSON, default=[])  # process_ids from BIA
    related_risks = Column(JSON, default=[])      # risk_ids from Risk module

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(255))
    notes = Column(Text)

    __table_args__ = (
        Index('idx_stakeholder_tenant', 'tenant_id'),
        Index('idx_stakeholder_type', 'stakeholder_type'),
        Index('idx_stakeholder_influence', 'influence_level', 'interest_level'),
    )

    def __repr__(self):
        return f"<Stakeholder(id={self.id}, name='{self.stakeholder_name}', type='{self.stakeholder_type}')>"


class ContextAnalysis(Base):
    """Context Analysis - ISO 22301 Clause 4.1"""
    __tablename__ = "context_analysis"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Multi-tenancy
    tenant_id = Column(String(255), nullable=False, index=True)

    # Analysis Type
    analysis_type = Column(String(50), nullable=False)
    # PESTLE, SWOT, PORTER, VUCA, SCENARIO

    analysis_name = Column(String(255), nullable=False)
    analysis_date = Column(DateTime, nullable=False)
    review_date = Column(DateTime)  # when to review

    # Analysis Data (flexible structure)
    analysis_data = Column(JSON, nullable=False)
    """
    PESTLE: {"political": [...], "economic": [...], "social": [...],
             "technological": [...], "legal": [...], "environmental": [...]}

    SWOT: {"strengths": [...], "weaknesses": [...],
           "opportunities": [...], "threats": [...]}

    PORTER: {"competitive_rivalry": {...}, "supplier_power": {...},
             "buyer_power": {...}, "threat_of_substitution": {...},
             "threat_of_new_entry": {...}}

    VUCA: {"volatility": {...}, "uncertainty": {...},
           "complexity": {...}, "ambiguity": {...}}
    """

    # Insights and Actions
    insights = Column(JSON, default=[])
    """
    [{"insight": "...", "impact": "high|medium|low", "category": "..."}]
    """

    action_items = Column(JSON, default=[])
    """
    [{"action": "...", "owner": "...", "due_date": "...", "status": "..."}]
    """

    identified_risks = Column(JSON, default=[])        # risk_ids for Risk module
    identified_opportunities = Column(JSON, default=[])

    # Status
    status = Column(String(50), default='draft')  # draft, approved, archived
    approved_by = Column(String(255))
    approved_date = Column(DateTime)

    # BCMS Links
    impacts_on_scope = Column(Boolean, default=False)
    impacts_on_objectives = Column(Boolean, default=False)
    related_bc_objectives = Column(JSON, default=[])  # objective IDs

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(255))
    notes = Column(Text)

    __table_args__ = (
        Index('idx_context_tenant', 'tenant_id'),
        Index('idx_context_type', 'analysis_type'),
        Index('idx_context_date', 'analysis_date'),
    )

    def __repr__(self):
        return f"<ContextAnalysis(id={self.id}, type='{self.analysis_type}', name='{self.analysis_name}')>"
