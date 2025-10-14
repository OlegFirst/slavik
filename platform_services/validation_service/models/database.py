"""
Validation Module Database Models
ISO 22301 Clauses 8.5, 9.1, 9.2, 9.3, 10
BCI GPG Practice 6 (PP6: Validation)

Reference:
- /services/BCM_1/bcm_exercise/models/models.py (exercise patterns)
- /services/BCM_1/bcm_kpi/models/models.py (KPI models - 852 lines)
- /services/SERVICES/BCM/governance/database/models.py (architecture)
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON, Enum as SQLEnum, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

# ==================== ENUMS ====================

class ExerciseType(str, Enum):
    """Exercise types from BCI GPG PP6"""
    TABLETOP = "tabletop"
    WALKTHROUGH = "walkthrough"
    SIMULATION = "simulation"
    FULL_SCALE = "full_scale"
    COMPONENT_TEST = "component_test"

class ExerciseStatus(str, Enum):
    """Exercise lifecycle status"""
    PLANNED = "planned"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    CANCELLED = "cancelled"

class ObservationType(str, Enum):
    """Exercise observation types"""
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    GAP = "gap"
    IMPROVEMENT = "improvement"

class ObservationSeverity(str, Enum):
    """Observation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class PerformanceDirection(str, Enum):
    """KPI performance direction from bcm_kpi"""
    HIGHER_BETTER = "higher_better"
    LOWER_BETTER = "lower_better"
    TARGET_VALUE = "target_value"

class MeasurementFrequency(str, Enum):
    """KPI measurement frequency from bcm_kpi"""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

class PerformanceStatus(str, Enum):
    """KPI performance status from bcm_kpi"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    NO_DATA = "no_data"

class TrendDirection(str, Enum):
    """KPI trend direction from bcm_kpi"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    NO_DATA = "no_data"

class DataQuality(str, Enum):
    """Data quality levels from bcm_kpi"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ESTIMATED = "estimated"

class CollectionMethod(str, Enum):
    """Data collection method from bcm_kpi"""
    MANUAL = "manual"
    AUTOMATED = "automated"
    IMPORT = "import"
    CALCULATED = "calculated"

class AuditType(str, Enum):
    """Audit types"""
    COMPLIANCE = "compliance"
    PROCESS = "process"
    PLAN = "plan"
    FOLLOW_UP = "follow_up"

class AuditStatus(str, Enum):
    """Audit lifecycle status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    FIELDWORK_COMPLETE = "fieldwork_complete"
    REPORT_DRAFT = "report_draft"
    REPORTED = "reported"
    CLOSED = "closed"

class FindingType(str, Enum):
    """Audit finding types"""
    MAJOR_NONCONFORMITY = "major_nonconformity"
    MINOR_NONCONFORMITY = "minor_nonconformity"
    OBSERVATION = "observation"
    OPPORTUNITY = "opportunity"

class FindingSeverity(str, Enum):
    """Finding severity levels"""
    MAJOR = "major"
    MINOR = "minor"
    OBSERVATION = "observation"

class CAPAType(str, Enum):
    """CAPA types"""
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"

class CAPAStatus(str, Enum):
    """CAPA workflow status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    CLOSED = "closed"
    REJECTED = "rejected"

class CAPASource(str, Enum):
    """CAPA source"""
    AUDIT = "audit"
    EXERCISE = "exercise"
    INCIDENT = "incident"
    SUGGESTION = "suggestion"
    MANAGEMENT_REVIEW = "management_review"

# ==================== EXERCISE MODELS ====================

class Exercise(Base):
    """
    BC Exercise Management
    ISO 22301 Clause 8.5 - Exercising and Testing

    Based on: bcm_exercise/models/models.py
    """
    __tablename__ = "exercises"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Exercise Details
    exercise_code = Column(String(50), unique=True, nullable=False, index=True)
    exercise_name = Column(String(255), nullable=False)
    description = Column(Text)

    # Classification
    exercise_type = Column(SQLEnum(ExerciseType), nullable=False)
    scenario_id = Column(Integer, ForeignKey('validation.exercise_scenarios.id'))
    complexity_level = Column(String(20))  # basic, intermediate, advanced

    # Objectives
    objectives = Column(JSON)  # Array of objectives
    success_criteria = Column(JSON)  # Array of criteria
    scope = Column(Text)  # What's being tested

    # Planning
    planned_date = Column(DateTime)
    planned_duration_hours = Column(Float)
    facilitator = Column(String(255))
    facilitator_name = Column(String(255))
    participants = Column(JSON)  # Array of {person_id, person_name, role}

    # Execution
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    actual_duration_hours = Column(Float)
    status = Column(SQLEnum(ExerciseStatus), default=ExerciseStatus.PLANNED, index=True)

    # Scenario & Injects
    scenario_description = Column(Text)
    injects = Column(JSON)  # Timeline of scenario events

    # BPMN Workflow Integration (from bcm_exercise)
    bpmn_process_id = Column(String(100))
    workflow_status = Column(String(50))
    workflow_variables = Column(JSON)

    # Results
    overall_success = Column(Boolean)
    objectives_met = Column(JSON)  # Which objectives were achieved
    rto_achieved = Column(Boolean)
    rpo_achieved = Column(Boolean)

    # Lessons Learned
    strengths = Column(JSON)  # What went well
    weaknesses = Column(JSON)  # What needs improvement
    gaps_identified = Column(JSON)  # Gaps in plans/capabilities
    lessons_learned = Column(Text)

    # Feedback (from bcm_exercise)
    feedback_data = Column(JSON)
    feedback_submitted = Column(Boolean, default=False)
    feedback_date = Column(DateTime)

    # Follow-up
    corrective_actions_required = Column(Integer, default=0)
    corrective_actions_completed = Column(Integer, default=0)

    # Documentation
    exercise_report = Column(Text)
    report_generated_date = Column(DateTime)
    report_distributed = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))

    # Relationships
    scenario = relationship("ExerciseScenario", back_populates="exercises")
    observations = relationship("ExerciseObservation", back_populates="exercise", cascade="all, delete-orphan")
    actions = relationship("ExerciseAction", back_populates="exercise", cascade="all, delete-orphan")

class ExerciseScenario(Base):
    """
    Exercise Scenario Library
    Reusable scenarios for exercises

    Based on: bcm_exercise scenario patterns
    """
    __tablename__ = "exercise_scenarios"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Scenario Details
    scenario_code = Column(String(50), unique=True, nullable=False, index=True)
    scenario_name = Column(String(255), nullable=False)
    description = Column(Text)

    # Classification
    scenario_type = Column(String(50), nullable=False, index=True)  # Links to seed data
    category = Column(String(50))  # cyber, natural_disaster, operational, etc.
    complexity_level = Column(String(20))  # basic, intermediate, advanced

    # Content
    full_scenario = Column(Text)  # Complete scenario description
    injects = Column(JSON)  # Timeline of events
    decision_points = Column(JSON)  # Key decisions to test

    # Exercise Planning
    recommended_exercise_type = Column(SQLEnum(ExerciseType))
    estimated_duration_hours = Column(Float)
    recommended_participants = Column(JSON)  # Roles/positions
    required_resources = Column(JSON)

    # Objectives
    learning_objectives = Column(JSON)
    tests_capabilities = Column(JSON)  # Which BC capabilities this tests

    # Usage
    reusable = Column(Boolean, default=True)
    times_used = Column(Integer, default=0)
    last_used_date = Column(DateTime)
    average_success_rate = Column(Float)

    # AI Generation (from bcm_exercise)
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    is_active = Column(Boolean, default=True)

    # Relationships
    exercises = relationship("Exercise", back_populates="scenario")

class ExerciseObservation(Base):
    """
    Exercise Observations
    Strengths, weaknesses, gaps identified during exercise
    """
    __tablename__ = "exercise_observations"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey('validation.exercises.id'), nullable=False, index=True)

    # Observation Details
    observation_type = Column(SQLEnum(ObservationType), nullable=False, index=True)
    severity = Column(SQLEnum(ObservationSeverity))

    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text)  # What was observed

    # Context
    timestamp = Column(DateTime)  # When during exercise
    phase = Column(String(50))  # Which phase of exercise
    process_area = Column(String(100))  # Affected process
    plan_reference = Column(String(100))  # Which plan was being tested

    # Impact
    impact_description = Column(Text)
    potential_consequences = Column(Text)

    # Observer
    observer = Column(String(255))
    observer_name = Column(String(255))
    observer_role = Column(String(100))

    # Recommendation
    recommendation = Column(Text)
    corrective_action_required = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    exercise = relationship("Exercise", back_populates="observations")
    actions = relationship("ExerciseAction", back_populates="observation")

class ExerciseAction(Base):
    """
    Exercise Corrective Actions
    Actions resulting from exercise observations
    """
    __tablename__ = "exercise_actions"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey('validation.exercises.id'), nullable=False, index=True)
    observation_id = Column(Integer, ForeignKey('validation.exercise_observations.id'), index=True)

    # Action Details
    action_number = Column(String(50), unique=True, nullable=False, index=True)
    action_description = Column(Text, nullable=False)
    action_type = Column(String(50))  # corrective, preventive, improvement

    # Assignment
    assigned_to = Column(String(255), nullable=False)
    assigned_to_name = Column(String(255))
    assigned_department = Column(String(100))

    # Priority & Timing
    priority = Column(String(20), index=True)  # critical, high, medium, low
    due_date = Column(DateTime)
    target_completion_date = Column(DateTime)

    # Status
    status = Column(String(50), default='open', index=True)  # open, in_progress, completed, verified
    completion_date = Column(DateTime)
    completion_notes = Column(Text)

    # Verification
    effectiveness_verified = Column(Boolean, default=False)
    verified_by = Column(String(255))
    verified_by_name = Column(String(255))
    verification_date = Column(DateTime)
    verification_notes = Column(Text)

    # Cost
    estimated_cost = Column(Float)
    actual_cost = Column(Float)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exercise = relationship("Exercise", back_populates="actions")
    observation = relationship("ExerciseObservation", back_populates="actions")

# ==================== KPI MODELS ====================
# Based on: bcm_kpi/models/models.py (519 lines)

class KPICategory(Base):
    """
    KPI Categories
    Based on: bcm_kpi.kpi.category
    """
    __tablename__ = "kpi_categories"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Category Details
    category_code = Column(String(50), unique=True, nullable=False, index=True)
    category_name = Column(String(255), nullable=False)
    description = Column(Text)

    # Display
    sequence = Column(Integer, default=10)
    color = Column(String(20))  # Hex color for visualization
    icon = Column(String(50))

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    kpis = relationship("KPI", back_populates="category")

class KPI(Base):
    """
    Key Performance Indicators
    ISO 22301 Clause 9.1 - Monitoring and Measurement

    Based on: bcm_kpi/models/models.py BcmKpi (lines 41-253)
    This is THE MODEL from bcm_kpi - adapted for async PostgreSQL
    """
    __tablename__ = "kpis"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # KPI Details
    kpi_code = Column(String(50), unique=True, nullable=False, index=True)
    kpi_name = Column(String(255), nullable=False)
    sequence = Column(Integer, default=10)

    # Category
    category_id = Column(Integer, ForeignKey('validation.kpi_categories.id'), nullable=False, index=True)

    # Definition (from bcm_kpi lines 65-74)
    description = Column(Text)
    objective = Column(Text)  # What this KPI measures and why

    # Measurement Details (from bcm_kpi lines 76-90)
    measurement_unit = Column(String(50), nullable=False)  # %, hours, count, etc.
    calculation_method = Column(Text)  # How this KPI is calculated
    data_source = Column(String(255))  # Where the data comes from

    # Targets and Thresholds (from bcm_kpi lines 93-106)
    target_value = Column(Float)
    critical_threshold = Column(Float)  # Below this = critical
    warning_threshold = Column(Float)  # Below this = warning

    # Performance Direction (from bcm_kpi lines 109-113)
    performance_direction = Column(SQLEnum(PerformanceDirection), nullable=False, default=PerformanceDirection.HIGHER_BETTER)

    # Frequency and Timing (from bcm_kpi lines 116-123)
    measurement_frequency = Column(SQLEnum(MeasurementFrequency), nullable=False, default=MeasurementFrequency.MONTHLY)

    # Responsible Parties (from bcm_kpi lines 126-137)
    owner_id = Column(String(255), nullable=False)
    owner_name = Column(String(255))
    department = Column(String(100))

    # Status (from bcm_kpi lines 140-144)
    status = Column(String(50), default='active', index=True)  # active, inactive, under_review

    # Current Performance (from bcm_kpi lines 147-167)
    # These will be computed in application layer
    current_value = Column(Float)
    current_status = Column(SQLEnum(PerformanceStatus), default=PerformanceStatus.NO_DATA)
    trend = Column(SQLEnum(TrendDirection), default=TrendDirection.NO_DATA)

    # ISO/BCI Reference
    iso_clause = Column(String(20))  # e.g., "9.1", "8.5"
    bci_practice = Column(String(20))  # e.g., "PP6"

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("KPICategory", back_populates="kpis")
    measurements = relationship("KPIMeasurement", back_populates="kpi", cascade="all, delete-orphan")

class KPIMeasurement(Base):
    """
    KPI Measurements/Data Points

    Based on: bcm_kpi/models/models.py BcmKpiMeasurement (lines 254-333)
    """
    __tablename__ = "kpi_measurements"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)
    kpi_id = Column(Integer, ForeignKey('validation.kpis.id'), nullable=False, index=True)

    # Measurement (from bcm_kpi lines 269-276)
    measurement_date = Column(DateTime, nullable=False, index=True)
    value = Column(Float, nullable=False)

    # Additional Context (from bcm_kpi lines 279-283)
    notes = Column(Text)

    # Data Quality (from bcm_kpi lines 285-290)
    data_quality = Column(SQLEnum(DataQuality), default=DataQuality.HIGH)

    # Data Collection (from bcm_kpi lines 293-304)
    collected_by = Column(String(255))
    collected_by_name = Column(String(255))
    collection_method = Column(SQLEnum(CollectionMethod), default=CollectionMethod.MANUAL)

    # Verification (from bcm_kpi lines 307-318)
    verified = Column(Boolean, default=False)
    verified_by = Column(String(255))
    verified_by_name = Column(String(255))
    verification_date = Column(DateTime)

    # Computed Status
    status = Column(SQLEnum(PerformanceStatus))  # Computed based on thresholds

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    kpi = relationship("KPI", back_populates="measurements")

class KPIDashboard(Base):
    """
    KPI Dashboards for different audiences

    Based on: bcm_kpi/models/models.py BcmKpiDashboard (lines 335-417)
    """
    __tablename__ = "kpi_dashboards"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Dashboard Details (from bcm_kpi lines 342-353)
    dashboard_name = Column(String(255), nullable=False)
    sequence = Column(Integer, default=10)
    description = Column(Text)

    # Dashboard Configuration (from bcm_kpi lines 356-372)
    dashboard_type = Column(String(50), nullable=False)  # executive, operational, tactical, compliance, custom
    target_audience = Column(String(50), nullable=False)  # executives, bcm_team, department_heads, all_staff, external

    # KPIs in Dashboard (from bcm_kpi lines 374-377)
    kpi_ids = Column(JSON)  # Array of KPI IDs

    # Layout and Display (from bcm_kpi lines 380-390)
    layout_config = Column(JSON)  # JSON configuration for dashboard layout
    refresh_frequency = Column(String(20), default='daily')  # real_time, hourly, daily, weekly

    # Access Control (from bcm_kpi lines 393-407)
    authorized_users = Column(JSON)  # Array of user IDs
    authorized_groups = Column(JSON)  # Array of group names
    public_access = Column(Boolean, default=False)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== AUDIT MODELS ====================

class AuditPlan(Base):
    """
    Audit Planning and Execution
    ISO 22301 Clause 9.2 - Internal Audit
    """
    __tablename__ = "audit_plans"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Audit Details
    audit_code = Column(String(50), unique=True, nullable=False, index=True)
    audit_name = Column(String(255), nullable=False)
    description = Column(Text)

    # Classification
    audit_type = Column(SQLEnum(AuditType), nullable=False, index=True)
    audit_scope = Column(Text)  # What's being audited

    # ISO 22301 Coverage
    iso_clauses_covered = Column(JSON)  # Array of clause numbers
    processes_covered = Column(JSON)  # Array of process names
    departments_covered = Column(JSON)

    # Planning
    planned_date = Column(DateTime)
    planned_duration_hours = Column(Float)
    lead_auditor = Column(String(255), nullable=False)
    lead_auditor_name = Column(String(255))
    audit_team = Column(JSON)  # Array of {auditor_id, auditor_name, role}

    # Execution
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    actual_duration_hours = Column(Float)
    status = Column(SQLEnum(AuditStatus), default=AuditStatus.PLANNED, index=True)

    # Audit Criteria
    audit_criteria = Column(JSON)  # Standards, requirements
    checklist_items = Column(JSON)  # Audit checklist

    # Results
    findings_count = Column(Integer, default=0)
    major_findings = Column(Integer, default=0)
    minor_findings = Column(Integer, default=0)
    observations = Column(Integer, default=0)
    opportunities = Column(Integer, default=0)

    # Report
    audit_report = Column(Text)
    report_date = Column(DateTime)
    report_distributed = Column(Boolean, default=False)

    # Follow-up
    corrective_actions_required = Column(Integer, default=0)
    corrective_actions_completed = Column(Integer, default=0)
    follow_up_audit_required = Column(Boolean, default=False)
    follow_up_audit_date = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))

    # Relationships
    findings = relationship("AuditFinding", back_populates="audit", cascade="all, delete-orphan")

class AuditFinding(Base):
    """
    Audit Findings
    Nonconformities, observations, opportunities
    """
    __tablename__ = "audit_findings"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)
    audit_id = Column(Integer, ForeignKey('validation.audit_plans.id'), nullable=False, index=True)

    # Finding Details
    finding_number = Column(String(50), unique=True, nullable=False, index=True)
    finding_type = Column(SQLEnum(FindingType), nullable=False, index=True)
    severity = Column(SQLEnum(FindingSeverity), nullable=False)

    # Classification
    iso_clause = Column(String(20), index=True)  # Which ISO clause
    process_area = Column(String(100))
    department = Column(String(100))

    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text)  # What was found
    requirement = Column(Text)  # What the requirement is

    # Analysis
    root_cause_analysis = Column(Text)
    potential_impact = Column(Text)

    # Corrective Action
    corrective_action_required = Column(Boolean, default=False)
    corrective_action_description = Column(Text)
    assigned_to = Column(String(255))
    assigned_to_name = Column(String(255))
    due_date = Column(DateTime)

    # Status
    status = Column(String(50), default='open', index=True)  # open, in_progress, completed, verified, closed
    completion_date = Column(DateTime)
    verification_date = Column(DateTime)
    verified_by = Column(String(255))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    audit = relationship("AuditPlan", back_populates="findings")

# ==================== CAPA MODEL ====================

class CAPA(Base):
    """
    Corrective and Preventive Actions
    ISO 22301 Clause 10 - Improvement
    """
    __tablename__ = "capa"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # CAPA Details
    capa_number = Column(String(50), unique=True, nullable=False, index=True)
    capa_type = Column(SQLEnum(CAPAType), nullable=False, index=True)

    # Source
    source = Column(SQLEnum(CAPASource), nullable=False, index=True)
    source_reference_id = Column(Integer)  # ID of audit, exercise, incident, etc.
    source_reference_code = Column(String(100))

    # Problem Description
    title = Column(String(255), nullable=False)
    problem_description = Column(Text, nullable=False)
    impact_if_not_resolved = Column(Text)

    # Root Cause Analysis
    root_cause_analysis = Column(Text)
    root_cause_category = Column(String(100))
    contributing_factors = Column(JSON)

    # Action Plan
    action_plan = Column(Text, nullable=False)
    action_steps = Column(JSON)  # Array of steps
    resources_required = Column(JSON)

    # Assignment
    assigned_to = Column(String(255), nullable=False)
    assigned_to_name = Column(String(255))
    assigned_department = Column(String(100))

    # Priority & Timing
    priority = Column(String(20), nullable=False, index=True)  # critical, high, medium, low
    due_date = Column(DateTime, nullable=False)
    target_completion_date = Column(DateTime)

    # Status
    status = Column(SQLEnum(CAPAStatus), default=CAPAStatus.OPEN, index=True)
    status_notes = Column(Text)

    # Implementation
    implementation_date = Column(DateTime)
    implementation_evidence = Column(JSON)  # Documents, photos, etc.
    implementation_notes = Column(Text)

    # Verification
    verification_required = Column(Boolean, default=True)
    verification_date = Column(DateTime)
    verified_by = Column(String(255))
    verified_by_name = Column(String(255))
    effectiveness_verified = Column(Boolean, default=False)
    verification_notes = Column(Text)

    # Closure
    closure_date = Column(DateTime)
    closed_by = Column(String(255))
    closure_notes = Column(Text)

    # Cost
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    cost_benefit_analysis = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))

# ==================== MANAGEMENT REVIEW MODEL ====================

class ManagementReview(Base):
    """
    Management Review
    ISO 22301 Clause 9.3 - Management Review
    """
    __tablename__ = "management_reviews"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)

    # Review Details
    review_code = Column(String(50), unique=True, nullable=False, index=True)
    review_name = Column(String(255), nullable=False)
    review_type = Column(String(50))  # quarterly, annual, ad_hoc

    # Timing
    review_date = Column(DateTime, nullable=False)
    review_period_from = Column(DateTime, nullable=False)
    review_period_to = Column(DateTime, nullable=False)

    # Attendees
    chairperson = Column(String(255))
    chairperson_name = Column(String(255))
    attendees = Column(JSON)  # Array of {person_id, person_name, role}

    # Inputs (ISO 9.3.2)
    inputs = Column(JSON)  # Structured inputs
    kpi_summary = Column(JSON)
    audit_results_summary = Column(JSON)
    exercise_outcomes_summary = Column(JSON)
    incident_summary = Column(JSON)
    capa_status_summary = Column(JSON)
    stakeholder_feedback = Column(Text)
    context_changes = Column(Text)
    resource_adequacy_assessment = Column(Text)

    # Outputs (ISO 9.3.3)
    outputs = Column(JSON)  # Structured outputs
    decisions = Column(JSON)  # Array of decisions made
    action_items = Column(JSON)  # Array of action items
    resource_allocation_decisions = Column(JSON)
    bcms_improvement_opportunities = Column(JSON)
    objectives_updates = Column(JSON)

    # BCMS Effectiveness Assessment
    bcms_effectiveness_rating = Column(String(50))  # excellent, good, needs_improvement, inadequate
    effectiveness_justification = Column(Text)

    # Minutes
    minutes = Column(Text)  # Full meeting minutes
    action_register = Column(JSON)  # Actions with owners and deadlines

    # Follow-up
    next_review_date = Column(DateTime)
    action_items_count = Column(Integer, default=0)
    action_items_completed = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))

# ==================== KPI ALERT MODEL ====================

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class AlertStatus(str, Enum):
    """Alert lifecycle status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    AUTO_RESOLVED = "auto_resolved"

class KPIAlert(Base):
    """
    KPI Threshold Alerts
    Stage 2 Implementation - Auto-alerting for KPI threshold breaches

    Created when a KPI value breaches its critical/warning thresholds.
    Sends email notifications to stakeholders.
    Auto-resolves when KPI returns to acceptable levels.
    """
    __tablename__ = "kpi_alerts"
    __table_args__ = {'schema': 'validation'}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(255), nullable=False, index=True)
    kpi_id = Column(Integer, ForeignKey('validation.kpis.id'), nullable=False, index=True)

    # Alert Details
    alert_code = Column(String(50), unique=True, nullable=False, index=True)  # ALERT-KPI-2024-001
    severity = Column(SQLEnum(AlertSeverity), nullable=False, index=True)

    # Trigger Information
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    triggered_value = Column(Float, nullable=False)
    threshold_breached = Column(Float)  # The threshold that was breached
    threshold_type = Column(String(20))  # 'critical' or 'warning'

    # Message
    alert_title = Column(String(500), nullable=False)
    alert_message = Column(Text, nullable=False)

    # Status & Lifecycle
    status = Column(SQLEnum(AlertStatus), nullable=False, default=AlertStatus.ACTIVE, index=True)

    # Acknowledgement
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(255))
    acknowledged_by_name = Column(String(255))
    acknowledgement_notes = Column(Text)

    # Resolution
    resolved_at = Column(DateTime)
    resolved_by = Column(String(255))
    resolved_by_name = Column(String(255))
    resolution_notes = Column(Text)
    resolved_value = Column(Float)  # KPI value when resolved
    auto_resolved = Column(Boolean, default=False)

    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime)
    recipients = Column(JSON)  # Array of email addresses
    notification_error = Column(Text)  # If sending failed

    # Escalation
    escalated = Column(Boolean, default=False)
    escalated_at = Column(DateTime)
    escalated_to = Column(JSON)  # Array of escalation recipients

    # Related Data
    measurement_id = Column(Integer)  # Link to specific KPI measurement
    related_incidents = Column(JSON)  # Array of related incident IDs

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    kpi = relationship("KPI", foreign_keys=[kpi_id])

# ==================== INDEXES ====================

# Exercise indexes
Index('idx_exercises_tenant_status', Exercise.tenant_id, Exercise.status)
Index('idx_exercises_planned_date', Exercise.planned_date)
Index('idx_exercises_type', Exercise.exercise_type)

# KPI indexes
Index('idx_kpis_tenant_category', KPI.tenant_id, KPI.category_id)
Index('idx_kpis_status', KPI.status)
Index('idx_kpi_measurements_kpi_date', KPIMeasurement.kpi_id, KPIMeasurement.measurement_date)

# Audit indexes
Index('idx_audits_tenant_status', AuditPlan.tenant_id, AuditPlan.status)
Index('idx_audits_planned_date', AuditPlan.planned_date)
Index('idx_audit_findings_audit', AuditFinding.audit_id)
Index('idx_audit_findings_severity', AuditFinding.severity)

# CAPA indexes
Index('idx_capa_tenant_status', CAPA.tenant_id, CAPA.status)
Index('idx_capa_source', CAPA.source)
Index('idx_capa_priority', CAPA.priority)
Index('idx_capa_due_date', CAPA.due_date)

# Management Review indexes
Index('idx_mgmt_reviews_tenant', ManagementReview.tenant_id)
Index('idx_mgmt_reviews_date', ManagementReview.review_date)

# KPI Alert indexes
Index('idx_kpi_alerts_tenant_status', KPIAlert.tenant_id, KPIAlert.status)
Index('idx_kpi_alerts_kpi', KPIAlert.kpi_id)
Index('idx_kpi_alerts_severity', KPIAlert.severity)
Index('idx_kpi_alerts_triggered', KPIAlert.triggered_at)
