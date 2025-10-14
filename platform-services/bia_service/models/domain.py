"""
BIA Service - Domain Models

All Pydantic models for Business Impact Analysis.
Copied from original main.py without any loss of functionality.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator, model_validator

from .enums import (
    CriticalityLevel,
    ProcessStatus,
    ReputationalImpact,
    RegulatoryImpact,
    PatientSafetyImpact,
    WHOTier,
    GeographicalScope,
    IndustryType,
)

# Import business validators
import sys
from pathlib import Path
shared_path = Path(__file__).resolve().parents[4] / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from validators.business_rules import BusinessValidator, BusinessValidationError

logger = logging.getLogger(__name__)


class Dependency(BaseModel):
    """Process, resource, or technology dependency"""
    type: str  # process, technology, people, facility, supplier
    name: str
    id: Optional[int] = None
    criticality: Optional[int] = Field(None, ge=1, le=5)
    required: bool = True


class ImpactAssessment(BaseModel):
    """Impact assessment at specific time period"""
    time_period: str  # 1_hour, 4_hours, 8_hours, 24_hours, 3_days, 1_week, 1_month
    financial_impact: Optional[float] = 0.0
    operational_impact: Optional[str] = None
    impact_description: Optional[str] = None


class BIAProcess(BaseModel):
    """BIA Process - Core business process for impact analysis"""
    id: Optional[int] = None
    tenant_id: str
    name: str
    description: Optional[str] = None
    department: Optional[str] = None
    process_owner: Optional[str] = None

    # Criticality
    criticality: CriticalityLevel
    criticality_score: Optional[int] = Field(None, ge=1, le=5)
    who_tier: Optional[WHOTier] = None  # Healthcare only

    # Industry context
    industry: Optional[IndustryType] = IndustryType.OTHER
    geographical_scope: Optional[GeographicalScope] = GeographicalScope.LOCAL

    # Time Objectives
    rto_hours: int = Field(..., ge=0, description="Recovery Time Objective in hours")
    rpo_hours: int = Field(..., ge=0, description="Recovery Point Objective in hours")
    mtpd_hours: int = Field(..., ge=0, description="Maximum Tolerable Period of Disruption in hours")

    # Impact Assessment (financial over time)
    financial_impact: Optional[Dict[str, float]] = Field(
        default_factory=dict,
        description="Financial impact per time period: {1_hour: 5000, 4_hours: 20000, ...}"
    )
    operational_impact: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Operational impact per time period"
    )
    reputational_impact: Optional[ReputationalImpact] = None
    regulatory_impact: Optional[RegulatoryImpact] = None
    patient_safety_impact: Optional[PatientSafetyImpact] = None

    # ISO 22301 Compliance Fields (Clause 8.2.2)
    compliance_objective: Optional[str] = Field(
        None,
        description="ISO 22301 compliance objective for this process"
    )
    legal_regulatory_requirements: Optional[List[str]] = Field(
        default_factory=list,
        description="Specific legal/regulatory requirements (e.g., HIPAA, GDPR)"
    )

    # Resource Requirements (Detailed)
    personnel_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Personnel requirements: {roles: [...], min_staff: 5, skills: [...]}"
    )
    facility_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Facility requirements: {locations: [...], space: ..., equipment: [...]}"
    )
    technology_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Technology requirements: {systems: [...], applications: [...], data: [...]}"
    )
    information_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Information requirements: {documents: [...], data_sources: [...], records: [...]}"
    )

    # Recovery Strategies
    recovery_strategies: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Recovery strategies: [{strategy: 'hot_site', cost: 50000, rto: 2}, ...]"
    )
    alternative_procedures: Optional[List[str]] = Field(
        default_factory=list,
        description="Manual workarounds during disruption"
    )
    workaround_capacity: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Percentage of normal capacity achievable with workarounds"
    )

    # Dependencies (Enhanced)
    upstream_processes: Optional[List[str]] = Field(
        default_factory=list,
        description="Processes that feed into this one"
    )
    downstream_processes: Optional[List[str]] = Field(
        default_factory=list,
        description="Processes that depend on this one"
    )
    critical_suppliers: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Critical suppliers: [{name: 'Vendor X', service: '...', rto: 4}, ...]"
    )

    # Operating Characteristics
    minimum_resource_level: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Minimum resources to operate: {staff: 3, systems: ['CRM'], ...}"
    )
    peak_periods: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Peak operating periods: [{period: 'month_end', criticality: 5}, ...]"
    )
    seasonality: Optional[str] = Field(
        None,
        description="Seasonal variations (e.g., 'Q4 peak', 'summer low')"
    )

    # ISO 22301 Assessment Results
    bia_completion_date: Optional[datetime] = None
    bia_assessor: Optional[str] = None
    bia_reviewer: Optional[str] = None
    next_review_date: Optional[datetime] = None

    # Dependencies (Original)
    dependencies: List[Dependency] = Field(default_factory=list)
    resources_required: List[Dict[str, Any]] = Field(default_factory=list)

    # Process metrics
    annual_revenue_impact: Optional[float] = 0.0
    peak_concurrent_users: Optional[int] = 0
    staff_count: Optional[int] = 1

    # AI Analysis results
    ai_suggested_rto: Optional[float] = None
    ai_confidence: Optional[float] = None
    ai_recommendations: Optional[str] = None

    # Status
    status: ProcessStatus = ProcessStatus.DRAFT
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode='after')
    def validate_time_objectives(self):
        """Validate RTO >= RPO and MTPD >= RTO"""
        if self.rto_hours is not None and self.rpo_hours is not None:
            if self.rto_hours < self.rpo_hours:
                raise ValueError('RTO must be greater than or equal to RPO')

        if self.mtpd_hours is not None and self.rto_hours is not None:
            if self.mtpd_hours < self.rto_hours:
                raise ValueError('MTPD must be greater than or equal to RTO')

        return self

    @model_validator(mode='after')
    def validate_iso_compliance(self):
        """Validate ISO 22301 compliance completeness"""
        if self.status == ProcessStatus.COMPLETED:
            # For completed BIA, ensure key ISO fields are populated
            missing_fields = []

            if not self.compliance_objective:
                missing_fields.append("compliance_objective")
            if not self.recovery_strategies:
                missing_fields.append("recovery_strategies")
            if not self.bia_completion_date:
                missing_fields.append("bia_completion_date")
            if not self.bia_assessor:
                missing_fields.append("bia_assessor")

            if missing_fields:
                logger.warning(
                    f"BIA process {self.id} marked complete but missing ISO fields: {missing_fields}"
                )

        return self

    @model_validator(mode='after')
    def validate_business_rules(self):
        """Validate comprehensive business rules"""
        try:
            # Rule 1: Recovery objectives (RTO/RPO/MTPD relationships)
            BusinessValidator.validate_recovery_objectives(
                self.rto_hours,
                self.rpo_hours,
                self.mtpd_hours,
                self.criticality.value if hasattr(self.criticality, 'value') else self.criticality
            )

            # Rule 2: Financial impact timeline (must increase over time)
            if self.financial_impact:
                BusinessValidator.validate_financial_impact_timeline(
                    self.financial_impact
                )

            # Rule 3: No self-dependency (prevent circular dependencies)
            if self.id:
                BusinessValidator.validate_no_self_dependency(
                    str(self.id),
                    self.upstream_processes or [],
                    self.downstream_processes or [],
                    self.dependencies or []
                )

            # Rule 4: Critical process requirements
            BusinessValidator.validate_critical_process_requirements(
                self.criticality.value if hasattr(self.criticality, 'value') else self.criticality,
                self.recovery_strategies or [],
                self.alternative_procedures or [],
                self.dependencies or []
            )

            # Rule 5: Workaround capacity (0-100%)
            if self.workaround_capacity is not None:
                BusinessValidator.validate_workaround_capacity(
                    self.workaround_capacity
                )

            # Rule 6: WHO tier consistency
            if self.who_tier:
                BusinessValidator.validate_who_tier_consistency(
                    self.who_tier.value if hasattr(self.who_tier, 'value') else self.who_tier,
                    self.rto_hours,
                    self.patient_safety_impact.value if self.patient_safety_impact else None
                )

            # Rule 7: Minimum staff requirements
            if self.personnel_requirements:
                BusinessValidator.validate_minimum_staff_requirements(
                    self.personnel_requirements,
                    self.criticality.value if hasattr(self.criticality, 'value') else self.criticality
                )

        except BusinessValidationError as e:
            raise ValueError(f"Business rule violation: {str(e)}")

        return self


class BIAProcessCreate(BaseModel):
    """Create BIA Process request"""
    tenant_id: str
    name: str
    description: Optional[str] = None
    department: Optional[str] = None
    process_owner: Optional[str] = None
    criticality: CriticalityLevel
    industry: Optional[IndustryType] = IndustryType.OTHER
    rto_hours: int
    rpo_hours: int
    mtpd_hours: int
    financial_impact: Optional[Dict[str, float]] = {}
    operational_impact: Optional[Dict[str, str]] = {}
    dependencies: Optional[List[Dependency]] = []

    # ISO 22301 Compliance Fields (Optional)
    compliance_objective: Optional[str] = None
    legal_regulatory_requirements: Optional[List[str]] = None
    personnel_requirements: Optional[Dict[str, Any]] = None
    facility_requirements: Optional[Dict[str, Any]] = None
    technology_requirements: Optional[Dict[str, Any]] = None
    information_requirements: Optional[Dict[str, Any]] = None
    recovery_strategies: Optional[List[Dict[str, Any]]] = None
    alternative_procedures: Optional[List[str]] = None
    workaround_capacity: Optional[float] = None
    upstream_processes: Optional[List[str]] = None
    downstream_processes: Optional[List[str]] = None
    critical_suppliers: Optional[List[Dict[str, Any]]] = None
    minimum_resource_level: Optional[Dict[str, Any]] = None
    peak_periods: Optional[List[Dict[str, Any]]] = None
    seasonality: Optional[str] = None
    bia_completion_date: Optional[datetime] = None
    bia_assessor: Optional[str] = None
    bia_reviewer: Optional[str] = None
    next_review_date: Optional[datetime] = None


class AIRTOSuggestion(BaseModel):
    """AI-powered RTO suggestion"""
    suggested_rto_hours: float
    suggested_rpo_hours: Optional[float] = None
    suggested_mtpd_hours: Optional[float] = None
    confidence: float = Field(..., ge=0, le=1)
    reasoning: str
    benchmarks: Optional[Dict[str, float]] = None


class BIASummaryReport(BaseModel):
    """BIA Summary Report"""
    tenant_id: str
    total_processes: int
    critical_processes: int
    average_rto_hours: float
    total_potential_loss_24h: float
    top_critical_processes: List[Dict[str, Any]]
    bia_completion_rate: float
