"""
KQM Data Models
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class GapType(str, Enum):
    """Type of knowledge gap"""
    STANDARD_REQUIREMENT = "standard_requirement"  # ISO/NIST/WHO not documented
    PLATFORM_CAPABILITY = "platform_capability"    # Feature without docs
    USER_REQUEST = "user_request"                  # Unanswered question
    COMMUNITY_PATTERN = "community_pattern"        # Pattern from k=5


class ScenarioType(str, Enum):
    """Type of scenario"""
    EXISTING = "existing"          # From catalog
    GENERATED = "generated"        # Auto-generated
    STANDARD = "standard"          # From ISO/NIST/WHO
    COMMUNITY = "community"        # From collective intelligence


class ValidationStatus(str, Enum):
    """Validation status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


# ===== KNOWLEDGE GAPS =====

class KnowledgeGap(BaseModel):
    """Detected knowledge gap"""
    id: str
    type: GapType
    description: str
    priority: int = Field(ge=1, le=10)  # 1-10

    # Context
    standard: Optional[str] = None       # e.g., "ISO22301"
    clause: Optional[str] = None         # e.g., "8.2.2"
    service: Optional[str] = None        # e.g., "BIA"
    capability: Optional[str] = None     # e.g., "AI-assisted RTO"
    user_question: Optional[str] = None  # Original user query

    # Metadata
    detected_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    status: str = "detected"  # detected, in_progress, resolved


# ===== SCENARIOS =====

class Scenario(BaseModel):
    """Scenario (existing or generated)"""
    id: str
    title: str
    content: str
    type: ScenarioType

    # Classification
    service: Optional[str] = None
    category: Optional[str] = None
    iso_clause: Optional[str] = None

    # Metadata
    source: str  # Where it came from
    confidence: float = Field(ge=0, le=1)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Optional details
    inputs: Optional[str] = None
    outputs: Optional[str] = None
    events: Optional[str] = None
    components: Optional[str] = None


class ValidatedScenario(BaseModel):
    """Validated scenario"""
    scenario: Scenario

    # Validation results
    iso_compliant: bool
    technically_valid: bool
    expert_approved: bool
    quality_score: float = Field(ge=0, le=1)

    # Status
    status: ValidationStatus
    validation_notes: Optional[str] = None
    validated_at: datetime = Field(default_factory=datetime.now)


# ===== KNOWLEDGE STATE =====

class CoverageReport(BaseModel):
    """Knowledge coverage report"""
    iso_coverage: float  # 0-1
    platform_coverage: float  # 0-1
    user_gaps: int  # Count of unanswered questions
    total_scenarios: int

    # Details
    iso_clauses_total: int = 0
    iso_clauses_documented: int = 0
    endpoints_total: int = 0
    endpoints_documented: int = 0


class QualityReport(BaseModel):
    """Knowledge quality report"""
    validation_rate: float  # % validated
    expert_approval_rate: float  # % expert approved
    usage_rate: float  # % actually used
    stale_count: int  # Scenarios > 90 days old
    avg_confidence: float


class KnowledgeState(BaseModel):
    """Current knowledge state"""
    coverage: CoverageReport
    quality: QualityReport
    gaps: List[KnowledgeGap] = []
    timestamp: datetime = Field(default_factory=datetime.now)


# ===== COMPLIANCE =====

class ComplianceCheck(BaseModel):
    """Compliance check result"""
    passed: bool
    clause: Optional[str] = None
    requirements_met: int = 0
    requirements_total: int = 0
    gaps: List[str] = []
    note: Optional[str] = None


class ComplianceStatus(BaseModel):
    """Overall compliance status"""
    iso_22301: Dict[str, bool] = {}  # clause -> compliant
    nist_sp_800_34: Dict[str, bool] = {}
    who_emergency: Dict[str, bool] = {}

    overall_compliance: float = 0.0  # 0-1
    critical_gaps: List[str] = []


# ===== METRICS =====

class GenerationMetrics(BaseModel):
    """Scenario generation metrics"""
    scenarios_generated_today: int = 0
    scenarios_generated_this_week: int = 0
    scenarios_generated_this_month: int = 0
    pending_validation: int = 0
    approved_today: int = 0


class PerformanceMetrics(BaseModel):
    """System performance metrics"""
    search_latency_ms: float
    generation_time_min: float
    cache_hit_rate: float
    avg_quality_score: float


class KQMMetrics(BaseModel):
    """Complete KQM metrics"""
    knowledge_coverage: CoverageReport
    knowledge_quality: QualityReport
    generation: GenerationMetrics
    performance: PerformanceMetrics
    gaps_detected: Dict[str, int]  # type -> count
    timestamp: datetime = Field(default_factory=datetime.now)
