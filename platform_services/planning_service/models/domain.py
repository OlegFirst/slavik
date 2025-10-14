"""
Planning Service Domain Models (Pydantic)
ISO 22301 Clause 8.3 - Business Continuity Strategy
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ===== ENUMS =====

class StrategyType(str, Enum):
    """Strategy classification types"""
    RECOVERY = "recovery"
    RESILIENCE = "resilience"
    PREVENTION = "prevention"
    MITIGATION = "mitigation"
    CONTINUITY = "continuity"
    CRISIS_MANAGEMENT = "crisis_management"


class StrategyPhase(str, Enum):
    """Strategy implementation phase"""
    PRE_INCIDENT = "pre_incident"
    DURING_INCIDENT = "during_incident"
    POST_INCIDENT = "post_incident"


class StrategyStatus(str, Enum):
    """Strategy lifecycle status"""
    DRAFT = "draft"
    ANALYSIS = "analysis"
    REVIEW = "review"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    ARCHIVED = "archived"


# ===== DOMAIN MODELS =====

class ResourceRequirement(BaseModel):
    """Resource requirement detail"""
    resource_type: str = Field(min_length=1, max_length=100, description="Resource type (people, technology, facility, etc.)")
    description: str = Field(min_length=3, max_length=1000, description="Resource description")
    quantity: Optional[int] = Field(None, ge=0, description="Quantity required (must be non-negative)")
    estimated_cost: Optional[float] = Field(None, ge=0, description="Estimated cost (must be non-negative)")
    availability: Optional[str] = None  # immediate, short_term, long_term
    criticality: str = Field(min_length=1, max_length=50, description="Criticality level")

    @field_validator('resource_type')
    @classmethod
    def validate_resource_type(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Resource type cannot be empty")
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Resource description must be at least 3 characters to be meaningful")
        return v.strip()

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v is not None and v < 0:
            raise ValueError("Quantity required cannot be negative")
        if v is not None and v > 1000000:
            raise ValueError("Quantity required exceeds reasonable limit (max 1,000,000)")
        return v

    @field_validator('estimated_cost')
    @classmethod
    def validate_cost(cls, v):
        if v is not None and v < 0:
            raise ValueError("Estimated cost cannot be negative")
        if v is not None and v > 1000000000:  # 1 billion
            raise ValueError("Estimated cost exceeds reasonable limit (max 1 billion)")
        return v

    @field_validator('criticality')
    @classmethod
    def validate_criticality(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Criticality level cannot be empty")
        return v.strip()


class CostBreakdown(BaseModel):
    """Cost breakdown for strategy"""
    capex: float = Field(0.0, ge=0, description="Capital expenditure (must be non-negative)")
    opex: float = Field(0.0, ge=0, description="Operational expenditure (must be non-negative)")
    training: float = Field(0.0, ge=0, description="Training cost (must be non-negative)")
    maintenance: float = Field(0.0, ge=0, description="Maintenance cost (must be non-negative)")
    other: float = Field(0.0, ge=0, description="Other costs (must be non-negative)")
    currency: str = Field("USD", min_length=3, max_length=3, description="ISO currency code")

    @field_validator('capex', 'opex', 'training', 'maintenance', 'other')
    @classmethod
    def validate_costs(cls, v, info):
        if v < 0:
            raise ValueError(f"{info.field_name} cannot be negative")
        if v > 1000000000:  # 1 billion max per category
            raise ValueError(f"{info.field_name} exceeds reasonable limit (max 1 billion)")
        return v

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError("Currency must be a 3-letter ISO code (e.g., USD, EUR, GBP)")
        if not v.isalpha():
            raise ValueError("Currency code must contain only letters")
        return v.upper()


class BenefitAnalysis(BaseModel):
    """Expected benefits from strategy"""
    quantitative_benefits: Dict[str, float] = Field(description="Quantifiable benefits {metric: value}")
    qualitative_benefits: List[str] = Field(description="Qualitative benefits")
    risk_reduction_percentage: Optional[float] = Field(None, ge=0, le=100, description="Risk reduction (0-100%)")
    downtime_reduction_hours: Optional[float] = Field(None, ge=0, description="Downtime reduction in hours")

    @field_validator('quantitative_benefits')
    @classmethod
    def validate_quantitative_benefits(cls, v):
        if not v:
            raise ValueError("At least one quantitative benefit must be provided")
        for key, value in v.items():
            if not key or len(key.strip()) == 0:
                raise ValueError("Benefit metric name cannot be empty")
            if value < 0:
                raise ValueError(f"Benefit value for '{key}' cannot be negative")
        return v

    @field_validator('qualitative_benefits')
    @classmethod
    def validate_qualitative_benefits(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one qualitative benefit must be provided")
        for benefit in v:
            if not benefit or len(benefit.strip()) < 3:
                raise ValueError("Each qualitative benefit must be at least 3 characters")
        return v

    @field_validator('risk_reduction_percentage')
    @classmethod
    def validate_risk_reduction(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Risk reduction percentage must be between 0% and 100%")
        return v

    @field_validator('downtime_reduction_hours')
    @classmethod
    def validate_downtime(cls, v):
        if v is not None and v < 0:
            raise ValueError("Downtime reduction hours cannot be negative")
        if v is not None and v > 87600:  # 10 years max
            raise ValueError("Downtime reduction hours exceeds reasonable limit (max 87600 hours/10 years)")
        return v


class ROIAnalysis(BaseModel):
    """Return on Investment analysis"""
    total_investment: float = Field(ge=0, description="Total investment (must be non-negative)")
    annual_savings: float = Field(ge=0, description="Annual savings (must be non-negative)")
    payback_period_months: float = Field(ge=0, description="Payback period in months")
    roi_percentage: float = Field(description="ROI percentage (can be negative)")
    net_present_value: Optional[float] = Field(None, description="Net present value")

    @field_validator('total_investment', 'annual_savings')
    @classmethod
    def validate_positive_values(cls, v, info):
        if v < 0:
            raise ValueError(f"{info.field_name} cannot be negative")
        return v

    @field_validator('payback_period_months')
    @classmethod
    def validate_payback(cls, v):
        if v < 0:
            raise ValueError("Payback period cannot be negative")
        if v > 600:  # 50 years max
            raise ValueError("Payback period exceeds reasonable timeframe (max 600 months/50 years)")
        return v


class ImplementationPhase(BaseModel):
    """Implementation phase details"""
    phase_number: int = Field(ge=1, description="Phase number (must be >= 1)")
    phase_name: str = Field(min_length=3, max_length=255, description="Phase name")
    description: str = Field(min_length=10, max_length=2000, description="Phase description")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    milestones: List[str] = []
    dependencies: List[str] = []

    @field_validator('phase_number')
    @classmethod
    def validate_phase_number(cls, v):
        if v < 1:
            raise ValueError("Phase number must be at least 1")
        if v > 100:
            raise ValueError("Phase number exceeds reasonable limit (max 100)")
        return v

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        if v is not None and hasattr(info.data, 'start_date') and info.data.get('start_date'):
            if v < info.data['start_date']:
                raise ValueError("End date cannot be before start date")
        return v


# ===== REQUEST/RESPONSE MODELS =====

class StrategyCreate(BaseModel):
    """Create strategy request"""
    tenant_id: str = Field(min_length=1, max_length=255, description="Tenant ID")
    name: str = Field(min_length=3, max_length=255, description="Strategy name (3-255 characters)")
    description: Optional[str] = Field(None, max_length=5000, description="Strategy description")
    strategy_type: StrategyType
    strategy_phase: StrategyPhase = StrategyPhase.PRE_INCIDENT
    objective: str = Field(min_length=10, max_length=2000, description="Strategy objective (minimum 10 characters)")
    scope: List[str] = Field(min_length=1, description="Business units/processes covered (at least 1 required)")
    risk_mitigation: List[str] = Field(description="Risks addressed")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Strategy name must be at least 3 characters (excluding whitespace)")
        return v.strip()

    @field_validator('objective')
    @classmethod
    def validate_objective(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Strategy objective must be at least 10 characters to be meaningful")
        return v.strip()

    @field_validator('scope')
    @classmethod
    def validate_scope(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one scope item (business unit/process) must be specified")
        return v


class StrategyUpdate(BaseModel):
    """Update strategy request"""
    name: Optional[str] = None
    description: Optional[str] = None
    strategy_type: Optional[StrategyType] = None
    strategy_phase: Optional[StrategyPhase] = None
    objective: Optional[str] = None
    scope: Optional[List[str]] = None
    risk_mitigation: Optional[List[str]] = None


class StrategyResponse(BaseModel):
    """Strategy response"""
    id: str
    tenant_id: str
    strategy_number: str
    name: str
    description: Optional[str]
    strategy_type: StrategyType
    strategy_phase: StrategyPhase
    status: StrategyStatus
    objective: str
    scope: List[str]
    risk_mitigation: List[str]

    # Cost-Benefit
    estimated_cost: Optional[float]
    cost_breakdown: Optional[CostBreakdown]
    expected_benefits: Optional[BenefitAnalysis]
    roi_analysis: Optional[ROIAnalysis]
    cost_benefit_ratio: Optional[float]

    # Resources
    resource_requirements: List[ResourceRequirement] = []
    resource_gaps: List[str] = []

    # Implementation
    implementation_phases: List[ImplementationPhase] = []
    dependencies: List[str] = []
    success_criteria: List[str] = []

    # Links
    linked_bia_ids: List[str] = []
    linked_risk_ids: List[str] = []

    # Approval
    submitted_for_review_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    # Audit
    created_by: str
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CostBenefitRequest(BaseModel):
    """Request for cost-benefit analysis"""
    cost_breakdown: CostBreakdown
    expected_benefits: BenefitAnalysis
    implementation_years: int = Field(3, ge=1, le=30, description="Implementation period (1-30 years)")
    discount_rate: float = Field(0.1, ge=0.0, le=0.5, description="Discount rate (0-50%)")

    @field_validator('implementation_years')
    @classmethod
    def validate_years(cls, v):
        if v < 1:
            raise ValueError("Implementation years must be at least 1")
        if v > 30:
            raise ValueError("Implementation years must not exceed 30 years (reasonable business planning horizon)")
        return v

    @field_validator('discount_rate')
    @classmethod
    def validate_discount_rate(cls, v):
        if v < 0:
            raise ValueError("Discount rate cannot be negative")
        if v > 0.5:
            raise ValueError("Discount rate cannot exceed 50% (0.5) - this would indicate unrealistic economic conditions")
        return v


class CostBenefitResponse(BaseModel):
    """Cost-benefit analysis result"""
    strategy_id: str
    total_cost: float
    total_benefits: float
    cost_benefit_ratio: float
    roi_analysis: ROIAnalysis
    recommendation: str  # proceed, review, reject
    confidence_level: str  # high, medium, low
