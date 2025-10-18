"""
Community Level Data Models

Pydantic models for community features
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4


# ============================================
# ENUMS
# ============================================

class IndustryType(str, Enum):
    """Industry types for matching"""
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    NONPROFIT = "nonprofit"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    GOVERNMENT = "government"
    OTHER = "other"


class OrganizationSize(str, Enum):
    """Organization size categories"""
    MICRO = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-1000"
    ENTERPRISE = "1000+"


class BCMMaturityLevel(str, Enum):
    """BCM maturity levels"""
    BEGINNER = "beginner"
    DEVELOPING = "developing"
    ESTABLISHED = "established"
    ADVANCED = "advanced"
    OPTIMIZED = "optimized"


class ExperienceLevel(str, Enum):
    """Professional experience levels"""
    JUNIOR = "0-2 years"
    INTERMEDIATE = "3-5 years"
    SENIOR = "6-10 years"
    EXPERT = "10+ years"


class MatchingPurpose(str, Enum):
    """Purpose of peer matching"""
    MENTORSHIP = "mentorship"
    COLLABORATION = "collaboration"
    KNOWLEDGE_EXCHANGE = "knowledge_exchange"
    NETWORKING = "networking"


# ============================================
# TWIN MATCHING MODELS
# ============================================

class SimilarityBreakdown(BaseModel):
    """Detailed similarity scores by dimension"""
    industry: float = Field(ge=0.0, le=1.0, description="Industry similarity (0-1)")
    size: float = Field(ge=0.0, le=1.0, description="Size similarity (0-1)")
    geography: float = Field(ge=0.0, le=1.0, description="Geographic similarity (0-1)")
    challenges: float = Field(ge=0.0, le=1.0, description="Challenge similarity (0-1)")
    maturity: float = Field(ge=0.0, le=1.0, description="BCM maturity similarity (0-1)")
    patterns: float = Field(ge=0.0, le=1.0, description="Operational pattern similarity (0-1)")


class SimilarityScore(BaseModel):
    """Overall similarity score with breakdown"""
    overall: float = Field(ge=0.0, le=1.0, description="Overall similarity score (0-1)")
    breakdown: SimilarityBreakdown
    matching_factors: List[str] = Field(default_factory=list, description="Key matching factors")

    class Config:
        json_schema_extra = {
            "example": {
                "overall": 0.82,
                "breakdown": {
                    "industry": 1.0,
                    "size": 0.8,
                    "geography": 0.6,
                    "challenges": 0.9,
                    "maturity": 0.7,
                    "patterns": 0.85
                },
                "matching_factors": [
                    "Same industry (healthcare)",
                    "Similar size (100-500 employees)",
                    "Both facing BCM implementation challenges"
                ]
            }
        }


class TwinMatch(BaseModel):
    """A matched organization twin"""
    twin_id: str
    organization_name: Optional[str] = None  # Only if they opted in to show name
    industry: IndustryType
    size: OrganizationSize
    location: str  # Generalized (e.g., "Boston, MA" not full address)
    similarity_score: SimilarityScore
    bcm_maturity_level: BCMMaturityLevel
    common_challenges: List[str] = Field(default_factory=list)
    shared_topics: List[str] = Field(default_factory=list)
    match_timestamp: datetime = Field(default_factory=datetime.utcnow)


class MatchFilters(BaseModel):
    """Filters for twin matching"""
    industries: Optional[List[IndustryType]] = None
    size_categories: Optional[List[OrganizationSize]] = None
    countries: Optional[List[str]] = None
    min_maturity: Optional[BCMMaturityLevel] = None
    max_maturity: Optional[BCMMaturityLevel] = None
    challenges: Optional[List[str]] = None
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0)
    max_results: int = Field(default=10, ge=1, le=100)


# ============================================
# KNOWLEDGE EXCHANGE MODELS
# ============================================

class LearningOutcome(str, Enum):
    """Outcome of learning application"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    IN_PROGRESS = "in_progress"


class Learning(BaseModel):
    """A shared learning/best practice"""
    learning_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    challenge: str = Field(description="What problem was being solved")
    solution: str = Field(description="What was done to solve it")
    outcome: str = Field(description="What was the result")
    effectiveness_score: float = Field(ge=0.0, le=1.0, description="How effective (0-1)")

    # Metadata for matching (anonymized)
    industry: IndustryType
    size_category: OrganizationSize
    bcm_maturity: BCMMaturityLevel
    challenge_type: str
    topic: str

    # Usage statistics
    times_used: int = Field(default=0, description="How many orgs tried this")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Success rate (0-1)")
    avg_time_saved_days: Optional[int] = None

    # Timestamps
    contributed_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    # Privacy: NO identifiable information
    # contributor_id is stored separately in secure table


class LearningContribution(BaseModel):
    """Request to contribute a learning"""
    title: str
    challenge: str
    solution: str
    outcome: str
    effectiveness_score: float = Field(ge=0.0, le=1.0)
    challenge_type: str
    topic: str
    time_saved_estimate_days: Optional[int] = None


class LearningQuery(BaseModel):
    """Query for relevant learnings"""
    context: str = Field(description="What are you trying to do?")
    industry: Optional[IndustryType] = None
    size_category: Optional[OrganizationSize] = None
    maturity_level: Optional[BCMMaturityLevel] = None
    topics: Optional[List[str]] = None
    min_effectiveness: float = Field(default=0.7, ge=0.0, le=1.0)
    limit: int = Field(default=10, ge=1, le=50)


class LearningFeedback(BaseModel):
    """Feedback on applied learning"""
    learning_id: str
    outcome: LearningOutcome
    effectiveness_rating: float = Field(ge=0.0, le=1.0)
    time_saved_days: Optional[int] = None
    comments: Optional[str] = None
    would_recommend: bool


# ============================================
# PEOPLE MATCHING MODELS
# ============================================

class ProfessionalRole(str, Enum):
    """BCM professional roles"""
    BCM_MANAGER = "bcm_manager"
    BCM_COORDINATOR = "bcm_coordinator"
    RISK_MANAGER = "risk_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    IT_DIRECTOR = "it_director"
    OPERATIONS_MANAGER = "operations_manager"
    EXECUTIVE = "executive"
    CONSULTANT = "consultant"
    OTHER = "other"


class PeerMatch(BaseModel):
    """A matched peer professional"""
    user_id: str
    name: Optional[str] = None  # Only if opted in
    role: ProfessionalRole
    experience_level: ExperienceLevel

    # Organization context (anonymized)
    organization_industry: IndustryType
    organization_size: OrganizationSize
    organization_similarity: float = Field(ge=0.0, le=1.0)

    # Matching details
    common_challenges: List[str] = Field(default_factory=list)
    complementary_skills: List[str] = Field(default_factory=list)
    geographic_proximity: str  # e.g., "same_country", "same_region", "different_region"

    # Match quality
    overall_score: float = Field(ge=0.0, le=1.0)

    # Networking preferences
    available_for_mentorship: bool = False
    available_for_collaboration: bool = False
    languages: List[str] = Field(default_factory=list)
    timezone: Optional[str] = None

    match_timestamp: datetime = Field(default_factory=datetime.utcnow)


class PeerCriteria(BaseModel):
    """Criteria for peer matching"""
    role: Optional[ProfessionalRole] = None
    purpose: MatchingPurpose
    experience_level: Optional[ExperienceLevel] = None

    # Organization filters
    organization_filters: Optional[MatchFilters] = None

    # Geographic preferences
    same_country_only: bool = False
    same_timezone_preferred: bool = False

    # Matching parameters
    min_match_score: float = Field(default=0.6, ge=0.0, le=1.0)
    max_results: int = Field(default=10, ge=1, le=50)


class UserNetworkingProfile(BaseModel):
    """User's networking profile"""
    user_id: str
    role: ProfessionalRole
    experience_level: ExperienceLevel

    # Skills and expertise
    skills: List[str] = Field(default_factory=list)
    expertise_areas: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)

    # Current challenges/interests
    current_challenges: List[str] = Field(default_factory=list)
    learning_interests: List[str] = Field(default_factory=list)

    # Networking preferences
    available_for_mentorship: bool = False
    seeking_mentor: bool = False
    available_for_collaboration: bool = False
    languages: List[str] = Field(default_factory=list)
    timezone: Optional[str] = None

    # Privacy settings
    show_name: bool = False
    show_organization: bool = False
    allow_direct_contact: bool = False

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# PRIVACY & ANONYMIZATION MODELS
# ============================================

class AnonymizationLevel(str, Enum):
    """Level of anonymization"""
    FULL = "full"  # Remove all identifiers
    PARTIAL = "partial"  # Generalize some fields
    MINIMAL = "minimal"  # Only remove PII


class PrivacySettings(BaseModel):
    """Privacy settings for community participation"""
    user_id: str

    # Community participation
    participate_in_knowledge_exchange: bool = True
    contribute_learnings: bool = True
    allow_twin_matching: bool = True
    allow_peer_matching: bool = True

    # Visibility
    show_organization_name: bool = False
    show_personal_name: bool = False
    show_contact_info: bool = False

    # Data sharing
    share_anonymized_data: bool = True
    share_aggregated_statistics: bool = True

    # Communication
    allow_direct_messages: bool = False
    allow_collaboration_requests: bool = True

    # Defaults
    default_anonymization_level: AnonymizationLevel = AnonymizationLevel.FULL

    # Metadata
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================
# COMMUNITY STATISTICS MODELS
# ============================================

class CommunityStats(BaseModel):
    """Community-wide statistics"""

    # Twin statistics
    total_twins: int
    active_twins: int  # Updated in last 30 days
    twins_by_industry: Dict[str, int]
    twins_by_size: Dict[str, int]
    twins_by_maturity: Dict[str, int]

    # Knowledge exchange
    total_learnings: int
    learnings_by_topic: Dict[str, int]
    avg_effectiveness_score: float
    total_times_applied: int

    # People matching
    total_professionals: int
    professionals_by_role: Dict[str, int]
    active_mentorships: int
    active_collaborations: int

    # Engagement
    monthly_active_twins: int
    monthly_contributions: int
    monthly_matches: int

    # Timestamp
    generated_at: datetime = Field(default_factory=datetime.utcnow)
