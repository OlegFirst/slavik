"""
API Request/Response Schemas
Pydantic models for API validation and serialization
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

from models.domain import (
    ExerciseType, ExerciseStatus, ObservationType, ObservationSeverity,
    PerformanceDirection, MeasurementFrequency, DataQuality, CollectionMethod,
    AuditType, AuditStatus, FindingType, FindingSeverity,
    CAPAType, CAPAStatus, CAPASource,
)


# ==================== EXERCISE SCHEMAS ====================

class ExerciseCreate(BaseModel):
    """Create Exercise Request"""
    tenant_id: str
    exercise_code: str
    exercise_name: str
    description: Optional[str] = None
    exercise_type: ExerciseType
    scenario_id: Optional[int] = None
    complexity_level: Optional[str] = "intermediate"
    objectives: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    planned_date: Optional[datetime] = None
    planned_duration_hours: Optional[float] = None
    facilitator: Optional[str] = None
    participants: List[Dict] = Field(default_factory=list)


class ExerciseUpdate(BaseModel):
    """Update Exercise Request"""
    exercise_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ExerciseStatus] = None
    planned_date: Optional[datetime] = None
    facilitator: Optional[str] = None
    participants: Optional[List[Dict]] = None
    lessons_learned: Optional[str] = None


class ExerciseResponse(BaseModel):
    """Exercise Response"""
    id: int
    tenant_id: str
    exercise_code: str
    exercise_name: str
    exercise_type: str
    status: str
    planned_date: Optional[datetime]
    actual_start_date: Optional[datetime]
    facilitator: Optional[str]
    overall_success: Optional[bool]
    corrective_actions_required: int
    created_at: datetime

    class Config:
        from_attributes = True


class ObservationCreate(BaseModel):
    """Create Exercise Observation"""
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


class ScenarioCreate(BaseModel):
    """Create Exercise Scenario"""
    tenant_id: str
    scenario_code: str
    scenario_name: str
    description: str
    scenario_type: str
    category: str
    complexity_level: str = "intermediate"
    full_scenario: str
    injects: List[Dict] = Field(default_factory=list)
    recommended_exercise_type: ExerciseType
    estimated_duration_hours: float


# ==================== KPI SCHEMAS ====================

class KPICreate(BaseModel):
    """Create KPI Request"""
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


class KPIUpdate(BaseModel):
    """Update KPI Request"""
    kpi_name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    status: Optional[str] = None


class KPIResponse(BaseModel):
    """KPI Response"""
    id: int
    tenant_id: str
    kpi_code: str
    kpi_name: str
    measurement_unit: str
    target_value: float
    performance_direction: str
    measurement_frequency: str
    current_value: Optional[float]
    current_status: str
    trend: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MeasurementCreate(BaseModel):
    """Create KPI Measurement"""
    tenant_id: str
    kpi_id: int
    measurement_date: datetime
    value: float
    notes: Optional[str] = None
    data_quality: DataQuality = DataQuality.HIGH
    collection_method: CollectionMethod = CollectionMethod.MANUAL
    collected_by: Optional[str] = None


# ==================== AUDIT SCHEMAS ====================

class AuditCreate(BaseModel):
    """Create Audit Plan"""
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
    checklist_items: List[Dict] = Field(default_factory=list)


class AuditUpdate(BaseModel):
    """Update Audit"""
    audit_name: Optional[str] = None
    status: Optional[AuditStatus] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    audit_report: Optional[str] = None


class AuditResponse(BaseModel):
    """Audit Response"""
    id: int
    tenant_id: str
    audit_code: str
    audit_name: str
    audit_type: str
    status: str
    planned_date: datetime
    lead_auditor_name: str
    findings_count: int
    major_findings: int
    minor_findings: int
    created_at: datetime

    class Config:
        from_attributes = True


class FindingCreate(BaseModel):
    """Create Audit Finding"""
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


# ==================== CAPA SCHEMAS ====================

class CAPACreate(BaseModel):
    """Create CAPA"""
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


class CAPAUpdate(BaseModel):
    """Update CAPA"""
    status: Optional[CAPAStatus] = None
    root_cause_analysis: Optional[str] = None
    action_plan: Optional[str] = None
    implementation_date: Optional[datetime] = None
    implementation_evidence: Optional[List[Dict]] = None
    effectiveness_verified: Optional[bool] = None
    verification_notes: Optional[str] = None


class CAPAResponse(BaseModel):
    """CAPA Response"""
    id: int
    tenant_id: str
    capa_number: str
    capa_type: str
    source: str
    title: str
    assigned_to_name: str
    priority: str
    status: str
    due_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== MANAGEMENT REVIEW SCHEMAS ====================

class ManagementReviewCreate(BaseModel):
    """Create Management Review"""
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


class ManagementReviewResponse(BaseModel):
    """Management Review Response"""
    id: int
    tenant_id: str
    review_code: str
    review_name: str
    review_type: str
    review_date: datetime
    chairperson_name: str
    action_items_count: int
    created_at: datetime

    class Config:
        from_attributes = True
