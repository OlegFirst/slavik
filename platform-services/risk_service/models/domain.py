"""
Risk Management - Domain Models (Pydantic)
ISO 22301:2019 Clause 8.2.3
"""

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class RiskCategory(str, Enum):
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"
    REPUTATIONAL = "reputational"
    CYBERSECURITY = "cybersecurity"
    NATURAL_DISASTER = "natural_disaster"


class RiskLikelihood(int, Enum):
    RARE = 1              # < 5% probability
    UNLIKELY = 2          # 5-20% probability
    POSSIBLE = 3          # 20-50% probability
    LIKELY = 4            # 50-80% probability
    ALMOST_CERTAIN = 5    # > 80% probability


class RiskImpact(int, Enum):
    INSIGNIFICANT = 1     # Minimal impact
    MINOR = 2             # Minor impact
    MODERATE = 3          # Moderate impact
    MAJOR = 4             # Major impact
    CATASTROPHIC = 5      # Catastrophic impact


class TreatmentStrategy(str, Enum):
    AVOID = "avoid"               # Eliminate the risk
    MITIGATE = "mitigate"        # Reduce likelihood/impact
    TRANSFER = "transfer"        # Insurance, outsourcing
    ACCEPT = "accept"            # Accept the risk


class RiskStatus(str, Enum):
    IDENTIFIED = "identified"
    ANALYZING = "analyzing"
    TREATED = "treated"
    MONITORING = "monitoring"
    CLOSED = "closed"


# =============================================================================
# CORE MODELS
# =============================================================================

class Risk(BaseModel):
    """Risk Assessment Model - ISO 22301 Clause 8.2.3"""
    id: Optional[UUID4] = None
    organization_id: UUID4

    # Identification
    risk_title: str = Field(..., min_length=1, max_length=255)
    risk_code: Optional[str] = Field(None, max_length=50)
    risk_category: RiskCategory = Field(default=RiskCategory.OPERATIONAL)

    # Description
    description: str
    threat_source: Optional[str] = Field(None, max_length=255)
    vulnerabilities: List[str] = Field(default_factory=list)

    # Analysis
    likelihood: RiskLikelihood = Field(default=RiskLikelihood.POSSIBLE)
    impact: RiskImpact = Field(default=RiskImpact.MODERATE)
    inherent_risk_score: int = Field(default=0)  # likelihood * impact

    # Treatment
    treatment_strategy: Optional[TreatmentStrategy] = None
    residual_likelihood: Optional[RiskLikelihood] = None
    residual_impact: Optional[RiskImpact] = None
    residual_risk_score: Optional[int] = None

    # Ownership
    risk_owner_id: Optional[UUID4] = None

    # Related entities
    related_processes: List[Dict[str, Any]] = Field(default_factory=list)
    related_assets: List[Dict[str, Any]] = Field(default_factory=list)

    # Status
    status: RiskStatus = Field(default=RiskStatus.IDENTIFIED)

    # Review
    last_reviewed_at: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

    # Timestamps
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FAIRAnalysis(BaseModel):
    """FAIR (Factor Analysis of Information Risk) Quantitative Analysis"""
    risk_id: UUID4

    # Loss Event Frequency
    threat_event_frequency: float = Field(..., description="Threats per year")
    vulnerability_score: float = Field(..., ge=0, le=1, description="0-1 vulnerability probability")
    loss_event_frequency: float = Field(default=0)  # TEF * VS

    # Loss Magnitude
    primary_loss_min: float = Field(..., description="Minimum primary loss ($)")
    primary_loss_max: float = Field(..., description="Maximum primary loss ($)")
    primary_loss_most_likely: float = Field(..., description="Most likely primary loss ($)")

    secondary_loss_min: float = Field(default=0, description="Minimum secondary loss ($)")
    secondary_loss_max: float = Field(default=0, description="Maximum secondary loss ($)")

    # Results
    annual_loss_expectancy: float = Field(default=0)  # LEF * avg loss
    risk_rating: str = Field(default="medium")  # low/medium/high/critical
    confidence_interval_low: float = Field(default=0)
    confidence_interval_high: float = Field(default=0)

    # Metadata
    analyzed_at: Optional[datetime] = None
    analyzed_by: Optional[UUID4] = None


class MonteCarloSimulation(BaseModel):
    """Monte Carlo Risk Simulation"""
    risk_id: UUID4
    iterations: int = Field(default=10000, ge=1000, le=100000)

    # Risk factors (variable inputs)
    factors: List[Dict[str, Any]] = Field(default_factory=list)

    # Results
    mean_loss: float = Field(default=0)
    median_loss: float = Field(default=0)
    percentile_95: float = Field(default=0)
    percentile_99: float = Field(default=0)

    # Distribution
    distribution_data: Optional[Dict[str, Any]] = None

    simulated_at: Optional[datetime] = None


class RiskTreatmentPlan(BaseModel):
    """Risk Treatment/Mitigation Plan"""
    id: Optional[UUID4] = None
    risk_id: UUID4

    strategy: TreatmentStrategy
    description: str

    # Actions
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    responsible_party: Optional[UUID4] = None

    # Timeline
    start_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None

    # Cost
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None

    # Effectiveness
    expected_residual_likelihood: Optional[RiskLikelihood] = None
    expected_residual_impact: Optional[RiskImpact] = None

    status: str = Field(default="planned")  # planned/in_progress/completed

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RiskReport(BaseModel):
    """Risk Assessment Report"""
    organization_id: UUID4

    # Summary
    total_risks: int
    critical_risks: int  # score >= 20
    high_risks: int      # score 15-19
    medium_risks: int    # score 8-14
    low_risks: int       # score < 8

    # Top risks
    top_risks: List[Risk]

    # By category
    risks_by_category: Dict[str, int]

    # Treatment status
    risks_by_status: Dict[str, int]

    # Trend analysis
    trend_data: Optional[Dict[str, Any]] = None

    generated_at: datetime
    generated_by: Optional[UUID4] = None


class AIRiskAdvisor(BaseModel):
    """AI Risk Advisor Session"""
    id: Optional[UUID4] = None
    risk_id: UUID4

    # AI Analysis
    ai_risk_analysis: Optional[str] = None
    risk_prediction: Optional[Dict[str, Any]] = None
    mitigation_recommendations: List[str] = Field(default_factory=list)

    # FAIR insights
    fair_quantification: Optional[Dict[str, Any]] = None

    # Context
    context_data: Dict[str, Any] = Field(default_factory=dict)

    # Results
    confidence_score: float = Field(default=0, ge=0, le=1)

    created_at: Optional[datetime] = None
