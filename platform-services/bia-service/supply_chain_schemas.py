"""
Supply Chain BCM - Pydantic Schemas
Supplier management and supply chain resilience tracking
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


# ===== ENUMS =====

class SupplierCriticalityLevel(str, Enum):
    """Supplier criticality classification"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SupplierStatus(str, Enum):
    """Supplier operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    AT_RISK = "at_risk"
    UNDER_REVIEW = "under_review"


class FinancialStability(str, Enum):
    """Financial stability assessment"""
    STRONG = "strong"
    ADEQUATE = "adequate"
    WEAK = "weak"
    AT_RISK = "at_risk"


class DependencyLevel(str, Enum):
    """Organization's dependency level on supplier"""
    EXCLUSIVE = "exclusive"    # Only this supplier can provide
    PRIMARY = "primary"        # Primary supplier with alternatives
    SECONDARY = "secondary"    # Backup/secondary supplier
    BACKUP = "backup"          # Tertiary backup


class DisruptionType(str, Enum):
    """Type of supplier disruption"""
    DELIVERY_DELAY = "delivery_delay"
    QUALITY_ISSUE = "quality_issue"
    OUTAGE = "outage"
    BANKRUPTCY = "bankruptcy"
    FORCE_MAJEURE = "force_majeure"
    CYBER_INCIDENT = "cyber_incident"
    LABOR_STRIKE = "labor_strike"
    REGULATORY_ISSUE = "regulatory_issue"
    OTHER = "other"


class DisruptionSeverity(str, Enum):
    """Severity of disruption impact"""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


# ===== NESTED MODELS =====

class ServiceProvided(BaseModel):
    """Service provided by supplier"""
    service: str
    criticality: str
    volume: Optional[str] = None
    description: Optional[str] = None


class ProductSupplied(BaseModel):
    """Product supplied by supplier"""
    product: str
    criticality: str
    lead_time_days: Optional[int] = None
    description: Optional[str] = None


class AlternativeSupplier(BaseModel):
    """Alternative supplier information"""
    supplier_id: int
    can_replace: List[str]  # Services/products that can be replaced
    transition_time_days: int
    capacity_percentage: int  # % of capacity vs primary
    notes: Optional[str] = None


class GeographicRisk(BaseModel):
    """Geographic risk factor"""
    risk_type: str  # political_instability, natural_disaster, war, etc.
    severity: str  # low, medium, high, critical
    description: str


class CorrectiveAction(BaseModel):
    """Corrective action from disruption"""
    action: str
    responsible: str
    due_date: Optional[datetime] = None
    status: str  # planned, in_progress, completed
    completion_date: Optional[datetime] = None


# ===== SUPPLIER SCHEMAS =====

class SupplierBase(BaseModel):
    """Base supplier fields"""
    supplier_code: str = Field(..., max_length=50)
    supplier_name: str = Field(..., max_length=255)
    supplier_type: Optional[str] = None  # manufacturer, distributor, service_provider, logistics

    # Contact
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None

    # Criticality
    criticality_level: SupplierCriticalityLevel
    single_point_of_failure: bool = False

    # Services/Products
    services_provided: List[ServiceProvided] = []
    products_supplied: List[ProductSupplied] = []

    # BCM Assessment
    has_bcm_program: bool = False
    has_iso22301_certification: bool = False
    last_bcm_assessment_date: Optional[datetime] = None
    bcm_assessment_score: Optional[int] = Field(None, ge=0, le=100)
    bcm_assessment_notes: Optional[str] = None

    # Alternatives
    alternative_suppliers: List[AlternativeSupplier] = []

    # Contract
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    contractual_rto: Optional[int] = None  # hours
    contractual_rpo: Optional[int] = None  # hours
    sla_availability_percentage: Optional[float] = Field(None, ge=0, le=100)
    penalties_for_breach: Optional[Dict[str, Any]] = None

    # Dependencies
    dependent_processes: List[int] = []  # BIA process IDs

    # Risk
    geographic_risks: List[GeographicRisk] = []
    financial_stability: Optional[FinancialStability] = None
    dependency_level: Optional[DependencyLevel] = None

    # Performance
    reliability_score: Optional[float] = Field(None, ge=0, le=100)
    on_time_delivery_rate: Optional[float] = Field(None, ge=0, le=100)
    quality_score: Optional[float] = Field(None, ge=0, le=100)

    # Status
    status: SupplierStatus = SupplierStatus.ACTIVE
    notes: Optional[str] = None

    @validator('contractual_rto', 'contractual_rpo')
    def validate_time_objectives(cls, v):
        if v is not None and v < 0:
            raise ValueError('RTO/RPO must be positive')
        return v


class SupplierCreate(SupplierBase):
    """Create supplier request"""
    tenant_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "hospital_001",
                "supplier_code": "SUP-001",
                "supplier_name": "Critical Cloud Provider",
                "supplier_type": "service_provider",
                "criticality_level": "critical",
                "single_point_of_failure": True,
                "services_provided": [
                    {
                        "service": "Cloud Infrastructure",
                        "criticality": "critical",
                        "volume": "100% capacity"
                    }
                ],
                "has_iso22301_certification": True,
                "financial_stability": "strong",
                "dependency_level": "exclusive",
                "dependent_processes": [1, 2, 5]
            }
        }


class SupplierUpdate(BaseModel):
    """Update supplier request - all fields optional"""
    supplier_name: Optional[str] = None
    supplier_type: Optional[str] = None
    criticality_level: Optional[SupplierCriticalityLevel] = None
    single_point_of_failure: Optional[bool] = None
    services_provided: Optional[List[ServiceProvided]] = None
    products_supplied: Optional[List[ProductSupplied]] = None
    has_bcm_program: Optional[bool] = None
    has_iso22301_certification: Optional[bool] = None
    bcm_assessment_score: Optional[int] = Field(None, ge=0, le=100)
    bcm_assessment_notes: Optional[str] = None
    alternative_suppliers: Optional[List[AlternativeSupplier]] = None
    financial_stability: Optional[FinancialStability] = None
    dependency_level: Optional[DependencyLevel] = None
    reliability_score: Optional[float] = Field(None, ge=0, le=100)
    on_time_delivery_rate: Optional[float] = Field(None, ge=0, le=100)
    quality_score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[SupplierStatus] = None
    notes: Optional[str] = None


class SupplierResponse(SupplierBase):
    """Supplier response"""
    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


# ===== SUPPLIER DISRUPTION SCHEMAS =====

class SupplierDisruptionBase(BaseModel):
    """Base disruption fields"""
    supplier_id: int
    disruption_date: datetime
    disruption_type: DisruptionType
    severity: DisruptionSeverity

    # Impact
    description: str
    impact_description: Optional[str] = None
    affected_processes: List[int] = []  # BIA process IDs
    affected_products_services: List[str] = []

    # Resolution
    resolution_date: Optional[datetime] = None
    resolution_description: Optional[str] = None

    # Metrics
    downtime_hours: Optional[int] = None
    financial_impact: Optional[float] = None
    customer_impact_count: Optional[int] = None

    # Lessons
    lessons_learned: Optional[str] = None
    corrective_actions: List[CorrectiveAction] = []
    preventive_actions: List[Dict[str, Any]] = []

    # RCA
    root_cause: Optional[str] = None
    contributing_factors: List[str] = []

    @validator('resolution_date')
    def validate_resolution_date(cls, v, values):
        if v is not None and 'disruption_date' in values:
            if v < values['disruption_date']:
                raise ValueError('Resolution date must be after disruption date')
        return v


class SupplierDisruptionCreate(SupplierDisruptionBase):
    """Create disruption request"""
    tenant_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "hospital_001",
                "supplier_id": 1,
                "disruption_date": "2024-10-01T14:30:00",
                "disruption_type": "outage",
                "severity": "major",
                "description": "Complete service outage due to data center failure",
                "impact_description": "Unable to access EHR system",
                "affected_processes": [1, 2],
                "downtime_hours": 6,
                "financial_impact": 50000,
                "root_cause": "Power failure in primary data center"
            }
        }


class SupplierDisruptionUpdate(BaseModel):
    """Update disruption request"""
    resolution_date: Optional[datetime] = None
    resolution_description: Optional[str] = None
    lessons_learned: Optional[str] = None
    corrective_actions: Optional[List[CorrectiveAction]] = None
    preventive_actions: Optional[List[Dict[str, Any]]] = None


class SupplierDisruptionResponse(SupplierDisruptionBase):
    """Disruption response"""
    id: int
    tenant_id: str
    resolution_time_hours: Optional[int] = None  # Auto-calculated
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True


# ===== ANALYSIS SCHEMAS =====

class SupplierRiskProfile(BaseModel):
    """Supplier risk profile analysis"""
    supplier_id: int
    supplier_name: str
    supplier_code: str

    # Risk Factors (0-100 scale, higher = more risk)
    criticality_risk: float
    spof_risk: float
    financial_risk: float
    bcm_maturity_risk: float
    reliability_risk: float
    alternative_availability_risk: float
    disruption_frequency_risk: float

    # Overall Risk
    overall_risk_score: float  # 0-100
    risk_level: str  # critical, high, medium, low

    # Metadata
    analysis_date: datetime
    recommendation: str


class SPOFSupplier(BaseModel):
    """Single Point of Failure supplier"""
    id: int
    supplier_code: str
    supplier_name: str
    criticality_level: str
    alternative_count: int
    dependent_process_count: int
    bcm_assessment_score: Optional[int]
    disruption_count_12m: int
    avg_downtime_hours: Optional[float]
    total_financial_impact_12m: Optional[float]
    risk_score: float
    recommendation: str


class SupplyChainRiskMap(BaseModel):
    """Supply chain risk heat map data"""
    tenant_id: str
    total_suppliers: int
    critical_suppliers: int
    spof_suppliers: int

    # Quadrants (criticality vs risk)
    high_criticality_high_risk: List[Dict[str, Any]]  # Immediate action
    high_criticality_low_risk: List[Dict[str, Any]]   # Monitor closely
    low_criticality_high_risk: List[Dict[str, Any]]   # Review alternatives
    low_criticality_low_risk: List[Dict[str, Any]]    # Normal monitoring

    generation_date: datetime


class BCMAssessment(BaseModel):
    """Supplier BCM assessment request"""
    assessment_date: datetime
    bcm_assessment_score: int = Field(..., ge=0, le=100)
    has_bcm_program: bool
    has_iso22301_certification: bool
    assessment_notes: str
    assessor_name: str

    # Assessment criteria
    bcm_policy_exists: bool
    bia_conducted: bool
    bc_plans_documented: bool
    plans_tested_annually: bool
    training_program_exists: bool
    management_review_conducted: bool


class WhatIfScenario(BaseModel):
    """What-if analysis scenario"""
    scenario_name: str
    affected_supplier_ids: List[int]
    disruption_type: DisruptionType
    assumed_duration_hours: int

    # Optional context
    description: Optional[str] = None
    additional_assumptions: Optional[Dict[str, Any]] = None


class WhatIfResult(BaseModel):
    """What-if analysis result"""
    scenario_name: str

    # Impact
    affected_suppliers: List[Dict[str, Any]]
    affected_processes: List[Dict[str, Any]]
    total_processes_impacted: int
    estimated_financial_impact: float
    estimated_downtime_hours: int

    # Mitigation
    available_alternatives: List[Dict[str, Any]]
    transition_time_required: int  # hours
    capacity_gap: float  # percentage

    # Recommendations
    immediate_actions: List[str]
    medium_term_actions: List[str]
    long_term_actions: List[str]

    analysis_date: datetime


# ===== LIST RESPONSES =====

class SupplierListResponse(BaseModel):
    """Paginated supplier list"""
    total: int
    suppliers: List[SupplierResponse]
    filters_applied: Dict[str, Any]


class DisruptionListResponse(BaseModel):
    """Paginated disruption list"""
    total: int
    disruptions: List[SupplierDisruptionResponse]
    filters_applied: Dict[str, Any]


# ===== SUMMARY SCHEMAS =====

class SupplyChainSummary(BaseModel):
    """Supply chain summary statistics"""
    tenant_id: str
    total_suppliers: int
    active_suppliers: int
    critical_suppliers: int
    spof_count: int
    suppliers_with_iso22301: int
    suppliers_with_bcm: int

    avg_reliability_score: Optional[float]
    avg_bcm_assessment_score: Optional[float]

    total_disruptions_12m: int
    total_downtime_hours_12m: float
    total_financial_impact_12m: float

    # Top risks
    top_5_critical_suppliers: List[Dict[str, Any]]
    suppliers_needing_attention: List[Dict[str, Any]]

    summary_date: datetime
