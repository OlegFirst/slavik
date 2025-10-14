"""
Domain Models (Pydantic)
ISO 22301 Clauses 8.5, 9.1, 9.2, 9.3, 10

These are the Pydantic models for validation, serialization, and API contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


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
    """KPI performance direction"""
    HIGHER_BETTER = "higher_better"
    LOWER_BETTER = "lower_better"
    TARGET_VALUE = "target_value"


class MeasurementFrequency(str, Enum):
    """KPI measurement frequency"""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


class PerformanceStatus(str, Enum):
    """KPI performance status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    NO_DATA = "no_data"


class TrendDirection(str, Enum):
    """KPI trend direction"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    NO_DATA = "no_data"


class DataQuality(str, Enum):
    """Data quality levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ESTIMATED = "estimated"


class CollectionMethod(str, Enum):
    """Data collection method"""
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
    CRITICAL = "critical"
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


# ==================== EXERCISE DOMAIN MODELS ====================

class Exercise(BaseModel):
    """Exercise domain model"""
    id: int
    tenant_id: str
    exercise_code: str
    exercise_name: str
    description: Optional[str] = None
    exercise_type: ExerciseType
    scenario_id: Optional[int] = None
    complexity_level: Optional[str] = None
    objectives: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    planned_date: Optional[datetime] = None
    planned_duration_hours: Optional[float] = None
    facilitator: Optional[str] = None
    facilitator_name: Optional[str] = None
    participants: List[Dict] = Field(default_factory=list)
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    actual_duration_hours: Optional[float] = None
    status: ExerciseStatus
    overall_success: Optional[bool] = None
    objectives_met: List[str] = Field(default_factory=list)
    lessons_learned: Optional[str] = None
    corrective_actions_required: int = 0
    corrective_actions_completed: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExerciseScenario(BaseModel):
    """Exercise scenario domain model"""
    id: int
    tenant_id: str
    scenario_code: str
    scenario_name: str
    description: Optional[str] = None
    scenario_type: str
    category: str
    complexity_level: str = "intermediate"
    full_scenario: str
    injects: List[Dict] = Field(default_factory=list)
    recommended_exercise_type: ExerciseType
    estimated_duration_hours: float
    reusable: bool = True
    times_used: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseObservation(BaseModel):
    """Exercise observation domain model"""
    id: int
    tenant_id: str
    exercise_id: int
    observation_type: ObservationType
    severity: ObservationSeverity
    title: str
    description: str
    evidence: Optional[str] = None
    timestamp: Optional[datetime] = None
    process_area: Optional[str] = None
    recommendation: Optional[str] = None
    corrective_action_required: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== KPI DOMAIN MODELS ====================

class KPI(BaseModel):
    """KPI domain model"""
    id: int
    tenant_id: str
    kpi_code: str
    kpi_name: str
    category_id: int
    description: Optional[str] = None
    objective: Optional[str] = None
    measurement_unit: str
    calculation_method: Optional[str] = None
    data_source: Optional[str] = None
    target_value: float
    warning_threshold: float
    critical_threshold: float
    performance_direction: PerformanceDirection
    measurement_frequency: MeasurementFrequency
    owner_id: str
    owner_name: str
    iso_clause: Optional[str] = None
    status: str = "active"
    current_value: Optional[float] = None
    current_status: PerformanceStatus = PerformanceStatus.NO_DATA
    trend: TrendDirection = TrendDirection.NO_DATA
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KPIMeasurement(BaseModel):
    """KPI measurement domain model"""
    id: int
    tenant_id: str
    kpi_id: int
    measurement_date: datetime
    value: float
    notes: Optional[str] = None
    data_quality: DataQuality = DataQuality.HIGH
    collection_method: CollectionMethod = CollectionMethod.MANUAL
    collected_by: Optional[str] = None
    status: Optional[PerformanceStatus] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== AUDIT DOMAIN MODELS ====================

class AuditPlan(BaseModel):
    """Audit plan domain model"""
    id: int
    tenant_id: str
    audit_code: str
    audit_name: str
    description: Optional[str] = None
    audit_type: AuditType
    audit_scope: str
    iso_clauses_covered: List[str] = Field(default_factory=list)
    processes_covered: List[str] = Field(default_factory=list)
    planned_date: datetime
    planned_duration_hours: float
    lead_auditor: str
    lead_auditor_name: str
    audit_team: List[Dict] = Field(default_factory=list)
    audit_criteria: List[str] = Field(default_factory=list)
    status: AuditStatus
    findings_count: int = 0
    major_findings: int = 0
    minor_findings: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditFinding(BaseModel):
    """Audit finding domain model"""
    id: int
    tenant_id: str
    audit_id: int
    finding_number: str
    finding_type: FindingType
    severity: FindingSeverity
    iso_clause: Optional[str] = None
    title: str
    description: str
    evidence: str
    requirement: str
    corrective_action_required: bool = False
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "open"
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== CAPA DOMAIN MODEL ====================

class CAPA(BaseModel):
    """CAPA domain model"""
    id: int
    tenant_id: str
    capa_number: str
    capa_type: CAPAType
    source: CAPASource
    source_reference_id: Optional[int] = None
    source_reference_code: Optional[str] = None
    title: str
    problem_description: str
    root_cause_analysis: str
    action_plan: str
    assigned_to: str
    assigned_to_name: str
    priority: str
    due_date: datetime
    status: CAPAStatus
    implementation_date: Optional[datetime] = None
    implementation_evidence: List[Dict] = Field(default_factory=list)
    effectiveness_verified: bool = False
    verification_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== MANAGEMENT REVIEW DOMAIN MODEL ====================

class ManagementReview(BaseModel):
    """Management review domain model"""
    id: int
    tenant_id: str
    review_code: str
    review_name: str
    review_type: str
    review_date: datetime
    review_period_from: datetime
    review_period_to: datetime
    chairperson: str
    chairperson_name: str
    attendees: List[Dict] = Field(default_factory=list)
    action_items_count: int = 0
    action_items_completed: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
