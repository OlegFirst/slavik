"""
Pydantic Schemas for API Validation

Модели для:
- Request validation
- Response serialization
- API documentation (OpenAPI)
"""

from pydantic import BaseModel, Field, validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .enums import (
    ComplianceStandard,
    ComplianceStatus,
    Severity,
    RequirementCategory,
    EvidenceType,
    AssessmentType,
    GapPriority,
    NCType,
    NCSource,
    AuditType,
    AuditResult,
    RCAMethod
)

# Import business validators
import sys
from pathlib import Path
shared_path = Path(__file__).resolve().parents[4] / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from validators.business_rules import BusinessValidator, BusinessValidationError


# =============================================================================
# REQUIREMENTS
# =============================================================================

class ComplianceRequirementBase(BaseModel):
    """Base requirement schema"""
    standard: ComplianceStandard
    clause: str = Field(..., description="Clause number (e.g., '4.1', '8.2.2')")
    title: str
    description: str
    category: RequirementCategory
    weight: float = Field(default=1.0, ge=0.1, le=5.0)
    is_mandatory: bool = True
    evidence_types: List[str] = []
    min_evidence_count: int = 1


class ComplianceRequirementCreate(ComplianceRequirementBase):
    """Create requirement"""
    pass


class ComplianceRequirementUpdate(BaseModel):
    """Update requirement"""
    title: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    is_mandatory: Optional[bool] = None
    evidence_types: Optional[List[str]] = None


class ComplianceRequirement(ComplianceRequirementBase):
    """Full requirement with ID and metadata"""
    id: UUID
    tenant_id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]

    class Config:
        from_attributes = True


# =============================================================================
# EVIDENCE
# =============================================================================

class EvidenceBase(BaseModel):
    """Base evidence schema"""
    requirement_id: UUID
    document_id: Optional[UUID] = None
    document_reference: Optional[str] = None
    evidence_type: EvidenceType
    title: str
    description: Optional[str] = None
    validity_period_start: Optional[datetime] = None
    validity_period_end: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_evidence_business_rules(self):
        """Validate evidence business rules"""
        try:
            # Rule 1: Evidence dates (valid_from < valid_to)
            BusinessValidator.validate_evidence_dates(
                self.validity_period_start,
                self.validity_period_end,
                is_critical_control=False  # Can be enhanced with actual criticality
            )

            # Rule 2: Document or reference required
            BusinessValidator.validate_evidence_document_reference(
                self.document_id,
                self.document_reference
            )

        except BusinessValidationError as e:
            raise ValueError(f"Evidence business rule violation: {str(e)}")

        return self


class EvidenceCreate(EvidenceBase):
    """Create evidence"""
    pass


class EvidenceUpdate(BaseModel):
    """Update evidence"""
    title: Optional[str] = None
    description: Optional[str] = None
    document_id: Optional[UUID] = None
    document_reference: Optional[str] = None
    validity_period_end: Optional[datetime] = None


class Evidence(EvidenceBase):
    """Full evidence with workflow status"""
    id: UUID
    status: str  # EvidenceState
    verification_status: str
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    reviewer_id: Optional[str]
    review_started_at: Optional[datetime]
    rejection_reason: Optional[str]
    metadata: Optional[Dict[str, Any]]
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    version: int = 1  # For optimistic locking

    class Config:
        from_attributes = True


class EvidenceResponse(BaseModel):
    """Evidence with requirement details"""
    evidence: Evidence
    requirement: Optional[ComplianceRequirement]
    document_title: Optional[str]


# =============================================================================
# ASSESSMENTS
# =============================================================================

class AssessmentBase(BaseModel):
    """Base assessment schema"""
    standard: ComplianceStandard
    assessment_type: AssessmentType = AssessmentType.REGULAR
    scope: Optional[str] = None
    scope_clauses: List[str] = []
    planned_date: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_assessment_business_rules(self):
        """Validate assessment business rules"""
        try:
            # Rule: Assessment must cover at least 1 requirement
            if self.scope_clauses is not None:
                BusinessValidator.validate_assessment_scope(
                    self.scope_clauses
                )

        except BusinessValidationError as e:
            raise ValueError(f"Assessment business rule violation: {str(e)}")

        return self


class AssessmentCreate(AssessmentBase):
    """Create assessment"""
    pass


class AssessmentUpdate(BaseModel):
    """Update assessment"""
    scope: Optional[str] = None
    scope_clauses: Optional[List[str]] = None
    assessment_comment: Optional[str] = None


class Assessment(AssessmentBase):
    """Full assessment with results"""
    id: UUID
    status: str  # AssessmentState
    assessor_id: Optional[str]
    reviewer_id: Optional[str]
    start_date: Optional[datetime]
    review_date: Optional[datetime]
    completion_date: Optional[datetime]
    overall_score: Optional[float]
    compliance_status: Optional[ComplianceStatus]
    requirements_assessed: Optional[Dict[str, Any]]
    gaps_identified: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    assessment_comment: Optional[str]
    approval_comment: Optional[str]
    approved_by: Optional[str]
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    version: int = 1  # For optimistic locking

    @model_validator(mode='after')
    def validate_assessment_dates_sequence(self):
        """Validate assessment date sequence"""
        try:
            # Rule: planned_date < actual_date < completion_date
            BusinessValidator.validate_assessment_dates(
                self.planned_date,
                self.start_date,  # actual_date
                self.completion_date
            )

        except BusinessValidationError as e:
            raise ValueError(f"Assessment date validation error: {str(e)}")

        return self

    class Config:
        from_attributes = True


class AssessmentResult(BaseModel):
    """Detailed assessment results"""
    assessment_id: UUID
    overall_score: float
    compliance_status: ComplianceStatus
    requirements_results: List[Dict[str, Any]]
    gaps: List[Dict[str, Any]]
    recommendations: List[str]
    completion_date: datetime


class AssessmentResponse(BaseModel):
    """Assessment with related data"""
    assessment: Assessment
    requirements_count: int
    evidence_count: int
    gaps_count: int


# =============================================================================
# GAPS
# =============================================================================

class RemediationAction(BaseModel):
    """Remediation action schema"""
    description: str
    responsible: str
    deadline: Optional[datetime]
    status: str = "pending"  # pending, in_progress, completed


class GapBase(BaseModel):
    """Base gap schema"""
    requirement_id: UUID
    gap_description: str
    severity: Severity
    priority: Optional[GapPriority] = None
    current_coverage: Optional[float] = None
    target_coverage: float = 100.0

    @model_validator(mode='after')
    def validate_gap_business_rules(self):
        """Validate gap business rules"""
        try:
            # Rule: Target coverage must exceed current coverage
            BusinessValidator.validate_gap_target_coverage(
                self.current_coverage,
                self.target_coverage
            )

        except BusinessValidationError as e:
            raise ValueError(f"Gap business rule violation: {str(e)}")

        return self


class GapCreate(GapBase):
    """Create gap"""
    assessment_id: Optional[UUID] = None
    remediation_actions: Optional[List[RemediationAction]] = []


class GapUpdate(BaseModel):
    """Update gap"""
    gap_description: Optional[str] = None
    severity: Optional[Severity] = None
    priority: Optional[GapPriority] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    remediation_actions: Optional[List[RemediationAction]] = None


class Gap(GapBase):
    """Full gap with workflow status"""
    id: UUID
    assessment_id: Optional[UUID]
    status: str  # GapState
    impact_score: Optional[float]
    remediation_actions: Optional[List[Dict[str, Any]]]
    estimated_effort: Optional[str]
    assigned_to: Optional[str]
    due_date: Optional[datetime]
    resolution_description: Optional[str]
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    evidence_id: Optional[UUID]
    verification_comment: Optional[str]
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    risk_acceptance_justification: Optional[str]
    accepted_by: Optional[str]
    risk_owner: Optional[str]
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    version: int = 1  # For optimistic locking

    @model_validator(mode='after')
    def validate_gap_due_date_sla(self):
        """Validate gap due date based on severity SLA"""
        try:
            # Rule: Due date must align with severity SLA
            if self.due_date:
                BusinessValidator.validate_gap_due_date(
                    self.severity.value if hasattr(self.severity, 'value') else self.severity,
                    self.due_date,
                    self.created_at
                )

        except BusinessValidationError as e:
            raise ValueError(f"Gap due date validation error: {str(e)}")

        return self

    class Config:
        from_attributes = True


class GapResponse(BaseModel):
    """Gap with requirement details"""
    gap: Gap
    requirement: Optional[ComplianceRequirement]


# =============================================================================
# NONCONFORMITIES
# =============================================================================

class RootCause(BaseModel):
    """Root cause schema"""
    id: str
    description: str
    evidence: Optional[str]


class CorrectiveAction(BaseModel):
    """Corrective action schema"""
    description: str
    owner: str
    deadline: datetime
    addresses_cause_id: str
    status: str = "pending"  # pending, in_progress, completed


class RootCauseAnalysis(BaseModel):
    """RCA result schema"""
    method: RCAMethod
    root_causes: List[RootCause]
    analysis_summary: str
    completed_at: datetime
    completed_by: str


class NonconformityBase(BaseModel):
    """Base nonconformity schema"""
    requirement_id: Optional[UUID] = None
    nc_type: NCType
    source: NCSource
    title: str
    description: str
    identified_by: str
    identified_date: datetime


class NonconformityCreate(NonconformityBase):
    """Create nonconformity"""
    audit_id: Optional[UUID] = None


class NonconformityUpdate(BaseModel):
    """Update nonconformity"""
    title: Optional[str] = None
    description: Optional[str] = None
    nc_type: Optional[NCType] = None


class Nonconformity(NonconformityBase):
    """Full nonconformity with workflow"""
    id: UUID
    nc_number: str
    audit_id: Optional[UUID]
    status: str  # NCState
    rca_lead: Optional[str]
    rca_team: Optional[List[str]]
    rca_method: Optional[RCAMethod]
    rca_started_at: Optional[datetime]
    rca_completed_at: Optional[datetime]
    root_causes: Optional[List[Dict[str, Any]]]
    corrective_actions: Optional[List[Dict[str, Any]]]
    actions_completed_at: Optional[datetime]
    evidence_ids: Optional[List[UUID]]
    verifier_id: Optional[str]
    verification_requested_at: Optional[datetime]
    verification_result: Optional[str]
    effectiveness_confirmed: Optional[bool]
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    closed_at: Optional[datetime]
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    version: int = 1  # For optimistic locking

    @model_validator(mode='after')
    def validate_nc_business_rules(self):
        """Validate nonconformity business rules"""
        try:
            # Rule 1: MAJOR NC requires RCA
            if self.rca_method:
                rca_method_str = self.rca_method.value if hasattr(self.rca_method, 'value') else self.rca_method
            else:
                rca_method_str = None

            BusinessValidator.validate_nc_type_requires_rca(
                self.nc_type.value if hasattr(self.nc_type, 'value') else self.nc_type,
                rca_method_str
            )

            # Rule 2: All root causes must be addressed by corrective actions
            if self.root_causes and self.corrective_actions:
                BusinessValidator.validate_nc_root_cause_coverage(
                    self.root_causes,
                    self.corrective_actions
                )

            # Rule 3: Effectiveness review timing (optional validation)
            # Commented out as it may be too strict for workflow
            # if self.corrective_actions and self.actions_completed_at:
            #     BusinessValidator.validate_nc_effectiveness_review(
            #         self.corrective_actions,
            #         self.actions_completed_at
            #     )

        except BusinessValidationError as e:
            raise ValueError(f"NC business rule violation: {str(e)}")

        return self

    class Config:
        from_attributes = True


class NonconformityResponse(BaseModel):
    """NC with requirement and audit details"""
    nonconformity: Nonconformity
    requirement: Optional[ComplianceRequirement]
    audit_number: Optional[str]


# =============================================================================
# AUDITS
# =============================================================================

class AuditFinding(BaseModel):
    """Audit finding schema"""
    type: NCType  # MAJOR, MINOR, OBSERVATION
    clause: str
    description: str
    evidence: str


class AuditBase(BaseModel):
    """Base audit schema"""
    audit_type: AuditType
    standard: ComplianceStandard
    scope: Optional[str] = None
    scope_clauses: List[str] = []
    planned_date: Optional[datetime] = None


class AuditCreate(AuditBase):
    """Create audit"""
    pass


class AuditUpdate(BaseModel):
    """Update audit"""
    scope: Optional[str] = None
    scope_clauses: Optional[List[str]] = None
    auditor_name: Optional[str] = None
    auditor_organization: Optional[str] = None


class Audit(AuditBase):
    """Full audit with workflow"""
    id: UUID
    audit_number: str
    status: str  # AuditState
    actual_date: Optional[datetime]
    completion_date: Optional[datetime]
    auditor_name: Optional[str]
    auditor_organization: Optional[str]
    auditor_independent: bool
    preparation_lead: Optional[str]
    audit_package_generated: bool
    audit_package_url: Optional[str]
    findings: Optional[List[Dict[str, Any]]]
    nc_ids: Optional[List[UUID]]
    overall_result: Optional[AuditResult]
    audit_report_url: Optional[str]
    certification_valid_until: Optional[datetime]
    next_surveillance_date: Optional[datetime]
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    planned_by: Optional[str]
    version: int = 1  # For optimistic locking

    @model_validator(mode='after')
    def validate_audit_business_rules(self):
        """Validate audit business rules"""
        try:
            # Rule 1: Auditor independence
            BusinessValidator.validate_audit_independence(
                self.audit_type.value if hasattr(self.audit_type, 'value') else self.audit_type,
                self.auditor_name,
                process_owner=None,  # Would need to be provided if checking internal audits
                auditor_independent=self.auditor_independent
            )

            # Rule 2: Surveillance interval (if applicable)
            if self.next_surveillance_date and self.actual_date:
                BusinessValidator.validate_surveillance_interval(
                    self.actual_date,
                    self.next_surveillance_date,
                    self.standard.value if hasattr(self.standard, 'value') else self.standard
                )

        except BusinessValidationError as e:
            raise ValueError(f"Audit business rule violation: {str(e)}")

        return self

    class Config:
        from_attributes = True


class AuditResponse(BaseModel):
    """Audit with findings and NC details"""
    audit: Audit
    findings_count: int
    major_nc_count: int
    minor_nc_count: int
    observations_count: int


# =============================================================================
# WORKFLOW TRANSITIONS
# =============================================================================

class WorkflowTransitionRequest(BaseModel):
    """Request to transition workflow state"""
    from_state: str
    to_state: str
    actor_id: str
    metadata: Dict[str, Any] = {}
    expected_version: Optional[int] = None  # For optimistic locking


class WorkflowStatusResponse(BaseModel):
    """Current workflow status"""
    entity_id: UUID
    entity_type: str
    current_state: str
    available_transitions: List[Dict[str, Any]]
    workflow_metadata: Dict[str, Any]


# =============================================================================
# DASHBOARDS & REPORTS
# =============================================================================

class ComplianceDashboard(BaseModel):
    """Compliance dashboard summary"""
    tenant_id: str
    standard: ComplianceStandard
    overall_score: float
    compliance_status: ComplianceStatus
    requirements_total: int
    requirements_compliant: int
    requirements_partial: int
    requirements_non_compliant: int
    evidence_count: int
    evidence_verified_count: int
    gaps_open: int
    gaps_critical: int
    nc_open: int
    nc_major: int
    last_assessment_date: Optional[datetime]
    next_audit_date: Optional[datetime]
    certification_valid_until: Optional[datetime]
    last_updated: datetime


class ComplianceScore(BaseModel):
    """Detailed compliance score"""
    overall_score: float
    clause_scores: Dict[str, float]
    coverage: float
    gaps: List[str]
    recommendations: List[str]


class ComplianceTrend(BaseModel):
    """Compliance trend over time"""
    date: datetime
    score: float
    status: ComplianceStatus


class ComplianceTrendsResponse(BaseModel):
    """Compliance trends analysis"""
    standard: ComplianceStandard
    period_days: int
    trend: str  # improving, stable, declining
    data_points: List[ComplianceTrend]
