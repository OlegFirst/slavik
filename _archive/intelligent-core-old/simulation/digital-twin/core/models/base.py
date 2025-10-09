"""
Base Models for Digital Twin Universal Service
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


# ============================================
# ENUMS
# ============================================

class OrganizationType(str, Enum):
    """Organization type"""
    CORPORATE = "corporate"
    GOVERNMENT = "government"
    NPO = "npo"
    INFRASTRUCTURE = "infrastructure"


class SimulationScenarioType(str, Enum):
    """Simulation scenario types"""
    FUNDING_SHOCK = "funding_shock"
    STAFF_DISRUPTION = "staff_disruption"
    SUPPLY_CHAIN_BREAK = "supply_chain_break"
    CYBER_ATTACK = "cyber_attack"
    REGULATORY_CHANGE = "regulatory_change"
    REPUTATION_CRISIS = "reputation_crisis"
    ECONOMIC_DOWNTURN = "economic_downturn"
    NATURAL_DISASTER = "natural_disaster"
    PANDEMIC = "pandemic"
    MARKET_SHIFT = "market_shift"
    CUSTOM = "custom"


class SimulationStatus(str, Enum):
    """Simulation status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DataSourceType(str, Enum):
    """Data source types"""
    ODOO = "odoo"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    QUICKBOOKS = "quickbooks"
    SLACK = "slack"
    JIRA = "jira"
    GOOGLE_WORKSPACE = "google_workspace"
    MICROSOFT_DYNAMICS = "microsoft_dynamics"
    SAP = "sap"
    CUSTOM = "custom"


# ============================================
# BASE MODELS
# ============================================

class TimestampedModel(BaseModel):
    """Base model with timestamps"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class IdentifiableModel(TimestampedModel):
    """Base model with ID"""
    id: str = Field(default_factory=lambda: str(uuid4()))


# ============================================
# ORGANIZATION MODELS
# ============================================

class Location(BaseModel):
    """Location model"""
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 0.0, "lng": 0.0}
    timezone: Optional[str] = None


class Contact(BaseModel):
    """Contact information"""
    type: str  # email, phone, website, etc.
    value: str
    primary: bool = False


class DataSource(BaseModel):
    """Data source information"""
    source_type: DataSourceType
    source_id: str
    last_sync: datetime = Field(default_factory=datetime.utcnow)
    sync_status: str = "active"  # active, paused, error
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Organization(IdentifiableModel):
    """Organization/Digital Twin model"""

    # Identity
    twin_id: str = Field(default_factory=lambda: f"twin_{uuid4().hex[:12]}")
    name: str
    canonical_name: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)

    # Classification
    org_type: OrganizationType
    industry: Optional[str] = None
    industry_codes: Dict[str, str] = Field(default_factory=dict)  # NAICS, SIC, etc.

    # Size & Financials
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    annual_budget: Optional[float] = None

    # Location
    headquarters: Optional[Location] = None
    locations: List[Location] = Field(default_factory=list)

    # Contacts
    contacts: List[Contact] = Field(default_factory=list)
    email_domain: Optional[str] = None

    # Data Sources
    sources: List[DataSource] = Field(default_factory=list)
    source_ids: Dict[str, str] = Field(default_factory=dict)  # {source: source_id}

    # Metadata
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Digital Twin Metrics
    health_score: float = 0.0  # 0-100
    maturity_level: int = 1  # 1-5
    completeness_score: float = 0.0  # 0-100
    quality_score: float = 0.0  # 0-100
    risk_score: float = 0.0  # 0-100

    # BCM Specific (if available)
    bcm_data: Dict[str, Any] = Field(default_factory=dict)


class OrganizationCreate(BaseModel):
    """Create organization request"""
    name: str
    org_type: OrganizationType
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    headquarters: Optional[Location] = None
    contacts: List[Contact] = Field(default_factory=list)
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Source information
    source: Optional[DataSourceType] = None
    source_id: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Update organization request"""
    name: Optional[str] = None
    org_type: Optional[OrganizationType] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    headquarters: Optional[Location] = None
    contacts: Optional[List[Contact]] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================
# SIMULATION MODELS
# ============================================

class SimulationParameters(BaseModel):
    """Simulation parameters"""
    scenario: SimulationScenarioType
    duration_months: int = 6
    severity: float = 0.5  # 0-1
    custom_params: Dict[str, Any] = Field(default_factory=dict)


class SimulationResult(IdentifiableModel):
    """Simulation result"""
    twin_id: str
    scenario: SimulationScenarioType
    parameters: SimulationParameters
    status: SimulationStatus = SimulationStatus.PENDING

    # Results
    impact_score: Optional[float] = None  # 0-100
    financial_impact: Optional[float] = None
    operational_impact: Optional[float] = None
    recovery_time_days: Optional[int] = None

    # Detailed results
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    recovery_plan: Dict[str, Any] = Field(default_factory=dict)

    # Execution info
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None


# ============================================
# METRICS MODELS
# ============================================

class HealthScore(BaseModel):
    """Health score breakdown"""
    overall: float  # 0-100
    financial: float  # 0-100
    operational: float  # 0-100
    impact: float  # 0-100
    sustainability: float  # 0-100
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class MetricPoint(BaseModel):
    """Single metric point"""
    timestamp: datetime
    value: float
    unit: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetricSeries(BaseModel):
    """Time series of metrics"""
    metric_name: str
    twin_id: str
    points: List[MetricPoint] = Field(default_factory=list)
    aggregation: Optional[str] = None  # sum, avg, min, max


# ============================================
# PREDICTION MODELS
# ============================================

class Prediction(IdentifiableModel):
    """Prediction model"""
    twin_id: str
    prediction_type: str  # financial_trend, impact, risk, etc.
    timeframe_months: int

    # Prediction values
    predicted_value: float
    confidence: float  # 0-1
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

    # Context
    assumptions: List[str] = Field(default_factory=list)
    factors: Dict[str, Any] = Field(default_factory=dict)
    methodology: Optional[str] = None


# ============================================
# THEORY OF CHANGE MODELS
# ============================================

class TheoryOfChange(IdentifiableModel):
    """Theory of Change model"""
    twin_id: str

    # ToC Components
    inputs: List[Dict[str, Any]] = Field(default_factory=list)
    activities: List[Dict[str, Any]] = Field(default_factory=list)
    outputs: List[Dict[str, Any]] = Field(default_factory=list)
    outcomes: List[Dict[str, Any]] = Field(default_factory=list)
    impact: Dict[str, Any] = Field(default_factory=dict)

    # Supporting data
    assumptions: List[str] = Field(default_factory=list)
    indicators: List[Dict[str, Any]] = Field(default_factory=list)
    pathways: List[Dict[str, Any]] = Field(default_factory=list)


# ============================================
# IMPACT PASSPORT MODELS
# ============================================

class ImpactPassport(IdentifiableModel):
    """Impact Passport model"""
    twin_id: str

    # Identity
    passport_number: str = Field(default_factory=lambda: f"IP-{uuid4().hex[:8].upper()}")
    organization_name: str

    # Claims
    claims: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    verification_status: str = "pending"  # pending, verified, rejected

    # Metadata
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    qr_code: Optional[str] = None
    verification_url: Optional[str] = None


# ============================================
# DATA QUALITY MODELS
# ============================================

class QualityScore(BaseModel):
    """Data quality score"""
    overall: float  # 0-100
    dimensions: Dict[str, float]  # completeness, accuracy, consistency, etc.
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=datetime.utcnow)


class ConflictValue(BaseModel):
    """Conflicting value from different sources"""
    source: DataSourceType
    value: Any
    timestamp: datetime
    quality_score: float
    source_trust_score: float = 1.0


# ============================================
# API RESPONSE MODELS
# ============================================

class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: List[Any]
    total: int
    page: int = 1
    page_size: int = 50
    total_pages: int


class SuccessResponse(BaseModel):
    """Success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    details: Optional[Any] = None


# ============================================
# FRONTEND-COMPATIBLE DIGITAL TWIN MODELS
# (Based on TypeScript interfaces from frontend)
# ============================================

class TwinInsightType(str, Enum):
    """Insight type classification"""
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    WARNING = "warning"
    RECOMMENDATION = "recommendation"


class ImpactLevel(str, Enum):
    """Impact level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TwinInsight(BaseModel):
    """
    AI-generated insight for digital twin
    Based on frontend TypeScript interface for frontend-backend compatibility
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: TwinInsightType
    title: str
    description: str
    confidence: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    impact: ImpactLevel
    source: str = Field(..., description="Source of insight (e.g., 'queue_theory', 'ai_generator', 'monte_carlo')")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actionable: bool = Field(default=True, description="Whether this insight has actionable steps")
    suggested_actions: List[str] = Field(default_factory=list, description="List of suggested actions")

    # Optional metadata
    related_processes: List[str] = Field(default_factory=list)
    priority: Optional[int] = Field(default=None, ge=1, le=5, description="Priority 1-5")
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RiskLandscape(BaseModel):
    """
    Organization risk landscape
    Based on frontend TypeScript interface
    """
    total_risks: int = 0
    critical_risks: int = 0
    high_risks: int = 0
    medium_risks: int = 0
    low_risks: int = 0
    mitigation_coverage: float = Field(default=0.0, ge=0, le=100, description="Percentage of risks with mitigation")

    # Risk breakdown by category
    by_category: Dict[str, int] = Field(default_factory=dict)
    # Example: {"cyber": 5, "operational": 3, "financial": 2}

    # Trend data
    trend: Optional[str] = Field(default=None, description="'increasing', 'stable', or 'decreasing'")

    model_config = ConfigDict(from_attributes=True)


class ComplianceFramework(BaseModel):
    """Individual compliance framework status"""
    name: str = Field(..., description="Framework name (e.g., 'ISO 22301', 'NIST', 'SOC 2')")
    compliance_percentage: float = Field(..., ge=0, le=100, description="Compliance percentage 0-100")
    last_assessment: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="in_progress", description="'compliant', 'in_progress', 'non_compliant'")
    gaps: List[str] = Field(default_factory=list, description="Identified compliance gaps")

    model_config = ConfigDict(from_attributes=True)


class ComplianceStatus(BaseModel):
    """
    Organization compliance status
    Based on frontend TypeScript interface
    """
    overall_score: float = Field(default=0.0, ge=0, le=100, description="Overall compliance score 0-100")
    frameworks: List[ComplianceFramework] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class DepartmentTwin(BaseModel):
    """Department-level digital twin summary"""
    name: str
    twin_count: int = Field(default=0, description="Number of personal twins in department")
    avg_health_score: float = Field(default=0.0, ge=0, le=100)
    key_metrics: Dict[str, Any] = Field(default_factory=dict)
    # Example: {"active_users": 15, "avg_engagement": 0.85, "risk_level": "low"}

    # Optional fields
    head_of_department: Optional[str] = None
    critical_processes: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PersonalDigitalTwin(IdentifiableModel):
    """
    Personal Digital Twin Pydantic model
    Based on frontend TypeScript interface
    """
    user_id: str
    display_name: str

    # Workspace Configuration
    workspace_config: Dict[str, Any] = Field(default_factory=dict)
    # Format: {theme, language, dashboard_layout, widgets}

    # Personal Metrics
    personal_metrics: Dict[str, Any] = Field(default_factory=dict)
    # Format: {login_count_month, features_used, total_sessions, avg_session_hours, etc.}

    # Activity Patterns
    activity_patterns: Dict[str, Any] = Field(default_factory=dict)
    # Format: {activity_level, peak_usage_hours, preferred_modules, engagement_trend, etc.}

    # Twin Health
    twin_health_score: float = Field(default=0.0, ge=0, le=100)
    activity_score: float = Field(default=0.0, ge=0, le=100)

    # Sync Status
    last_sync: datetime = Field(default_factory=datetime.utcnow)
    sync_status: str = Field(default="active", description="'active', 'syncing', 'offline', 'error'")

    # Optional organization link
    organization_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationTwin(BaseModel):
    """
    Organization-level digital twin with frontend-compatible fields
    Extended version of Organization model
    """
    id: str
    name: str
    health_score: float = Field(default=0.0, ge=0, le=100)

    # Frontend-specific fields
    twin_health_score: Optional[float] = Field(default=None, ge=0, le=100)
    personal_twins_count: int = Field(default=0, description="Number of personal twins in organization")
    departments: List[DepartmentTwin] = Field(default_factory=list)
    risk_landscape: RiskLandscape = Field(default_factory=RiskLandscape)
    compliance_status: ComplianceStatus = Field(default_factory=ComplianceStatus)

    # Metadata
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class AIInsightsResponse(BaseModel):
    """
    Response model for AI insights endpoint
    Returns multiple insights for organization
    """
    organization_id: str
    total_insights: int
    insights: List[TwinInsight]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Summary statistics
    risk_count: int = 0
    opportunity_count: int = 0
    warning_count: int = 0
    recommendation_count: int = 0

    model_config = ConfigDict(from_attributes=True)
