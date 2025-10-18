"""
Data Models for MVP Platform
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, UUID4
from enum import Enum


# ============================================
# ENUMS
# ============================================

class UserRole(str, Enum):
    """User roles"""
    SPECIALIST = "specialist"
    ADMIN = "admin"


class OrganizationIndustry(str, Enum):
    """Organization industries"""
    HEALTHCARE = "Healthcare"
    FINANCE = "Finance"
    MANUFACTURING = "Manufacturing"
    GOVERNMENT = "Government"
    TECHNOLOGY = "Technology"
    RETAIL = "Retail"
    EDUCATION = "Education"
    OTHER = "Other"


class BIAStatus(str, Enum):
    """BIA analysis status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CollectionMethod(str, Enum):
    """BIA data collection methods"""
    QUESTIONNAIRE = "questionnaire"
    DOCUMENT_UPLOAD = "document_upload"
    ERP_INTEGRATION = "erp_integration"
    HYBRID = "hybrid"


class ProcessCriticality(str, Enum):
    """Process criticality levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingType(str, Enum):
    """Finding types"""
    GAP = "gap"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    RECOMMENDATION = "recommendation"


class FindingSeverity(str, Enum):
    """Finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# ============================================
# AUTH MODELS
# ============================================

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    organization_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    """User profile"""
    id: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime


# ============================================
# ORGANIZATION MODELS
# ============================================

class OrganizationCreate(BaseModel):
    """Create organization request"""
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[OrganizationIndustry] = None
    size: Optional[int] = Field(None, gt=0)
    country: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Update organization request"""
    name: Optional[str] = None
    industry: Optional[OrganizationIndustry] = None
    size: Optional[int] = None
    country: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None


class OrganizationResponse(BaseModel):
    """Organization response"""
    id: str
    owner_id: str
    name: str
    industry: Optional[str]
    size: Optional[int]
    country: Optional[str]
    description: Optional[str]
    website: Optional[str]
    bcm_maturity_score: int
    created_at: datetime
    updated_at: datetime


class OrganizationStats(BaseModel):
    """Organization statistics"""
    departments_count: int = 0
    processes_count: int = 0
    bia_analyses_count: int = 0


class OrganizationDetailed(OrganizationResponse):
    """Detailed organization with stats"""
    stats: OrganizationStats


# ============================================
# DEPARTMENT & PROCESS MODELS
# ============================================

class DepartmentCreate(BaseModel):
    """Create department request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    head_name: Optional[str] = None
    employee_count: Optional[int] = None


class DepartmentResponse(BaseModel):
    """Department response"""
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    head_name: Optional[str]
    employee_count: Optional[int]
    created_at: datetime


class ProcessCreate(BaseModel):
    """Create process request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    criticality: Optional[ProcessCriticality] = None
    department_id: Optional[str] = None
    owner_person: Optional[str] = None


class ProcessResponse(BaseModel):
    """Process response"""
    id: str
    organization_id: str
    department_id: Optional[str]
    name: str
    description: Optional[str]
    category: Optional[str]
    criticality: Optional[str]
    owner_person: Optional[str]
    created_at: datetime


# ============================================
# BIA MODELS
# ============================================

class BIACreate(BaseModel):
    """Create BIA analysis request"""
    name: str = Field(..., min_length=1, max_length=255)
    collection_method: CollectionMethod = CollectionMethod.QUESTIONNAIRE


class BIAUpdate(BaseModel):
    """Update BIA analysis request"""
    name: Optional[str] = None
    status: Optional[BIAStatus] = None


class BIAResponse(BaseModel):
    """BIA analysis response"""
    id: str
    organization_id: str
    name: str
    status: str
    collection_method: str
    compliance_score: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class BIAStats(BaseModel):
    """BIA statistics"""
    processes_count: int = 0
    critical_processes_count: int = 0
    dependencies_count: int = 0
    findings_count: int = 0


class BIADetailed(BIAResponse):
    """Detailed BIA with stats"""
    stats: BIAStats


# ============================================
# BIA PROCESS MODELS
# ============================================

class BIAProcessCreate(BaseModel):
    """Create BIA process request"""
    process_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    criticality: ProcessCriticality
    category: Optional[str] = None
    owner_department: Optional[str] = None
    owner_person: Optional[str] = None


class BIAProcessUpdate(BaseModel):
    """Update BIA process request"""
    name: Optional[str] = None
    criticality: Optional[ProcessCriticality] = None
    rto_hours: Optional[int] = Field(None, ge=0)
    rpo_hours: Optional[int] = Field(None, ge=0)
    mtpd_hours: Optional[int] = Field(None, ge=0)
    financial_impact_per_hour: Optional[float] = Field(None, ge=0)


class BIAProcessResponse(BaseModel):
    """BIA process response"""
    id: str
    analysis_id: str
    process_id: Optional[str]
    name: str
    description: Optional[str]
    criticality: str
    rto_hours: Optional[int]
    rpo_hours: Optional[int]
    mtpd_hours: Optional[int]
    financial_impact_per_hour: Optional[float]
    category: Optional[str]
    owner_department: Optional[str]
    owner_person: Optional[str]
    created_at: datetime


# ============================================
# BIA DEPENDENCY MODELS
# ============================================

class BIADependencyCreate(BaseModel):
    """Create BIA dependency request"""
    source_process_id: str
    target_process_id: str
    dependency_type: str = Field(..., pattern="^(hard|soft|optional|cascading)$")
    dependency_strength: int = Field(5, ge=1, le=10)


class BIADependencyResponse(BaseModel):
    """BIA dependency response"""
    id: str
    analysis_id: str
    source_process_id: str
    target_process_id: str
    dependency_type: str
    dependency_strength: int
    ai_detected: bool
    created_at: datetime


# ============================================
# BIA QUESTIONNAIRE MODELS
# ============================================

class QuestionType(str, Enum):
    """Question types"""
    TEXT = "text"
    NUMBER = "number"
    CHOICE = "choice"
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"


class BIAQuestionGenerate(BaseModel):
    """Generate questionnaire request"""
    industry: Optional[str] = None
    company_size: Optional[int] = None
    focus_areas: Optional[List[str]] = None


class BIAQuestionResponse(BaseModel):
    """BIA question response"""
    id: str
    analysis_id: str
    question_text: str
    question_type: str
    options: Optional[List[str]]
    sequence_number: int
    ai_generated: bool


class BIAAnswerSubmit(BaseModel):
    """Submit answer request"""
    question_id: str
    answer_text: Optional[str] = None
    answer_number: Optional[float] = None
    answer_choice: Optional[List[str]] = None


# ============================================
# BIA FINDING MODELS
# ============================================

class BIAFindingCreate(BaseModel):
    """Create BIA finding request"""
    finding_type: FindingType
    severity: FindingSeverity
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    affected_processes: Optional[List[str]] = None
    iso_clause: Optional[str] = None
    recommended_action: Optional[str] = None


class BIAFindingUpdate(BaseModel):
    """Update BIA finding request"""
    status: Optional[str] = None
    user_notes: Optional[str] = None


class BIAFindingResponse(BaseModel):
    """BIA finding response"""
    id: str
    analysis_id: str
    finding_type: str
    severity: str
    title: str
    description: Optional[str]
    affected_processes: Optional[List[str]]
    iso_clause: Optional[str]
    recommended_action: Optional[str]
    status: str
    user_notes: Optional[str]
    created_at: datetime


# ============================================
# AI MODELS
# ============================================

class AIGenerateProcessesRequest(BaseModel):
    """AI generate processes request"""
    industry: str
    size: int
    country: str = "United States"


class AIProcessSuggestion(BaseModel):
    """AI process suggestion"""
    name: str
    description: str
    category: str
    criticality: str


class AIGenerateProcessesResponse(BaseModel):
    """AI generate processes response"""
    processes: List[AIProcessSuggestion]


class AICalculateRTORequest(BaseModel):
    """AI calculate RTO request"""
    process_name: str
    process_description: Optional[str] = None
    industry: str
    criticality: str


class AIRTORecommendation(BaseModel):
    """AI RTO recommendation"""
    rto_hours: int
    rpo_hours: int
    mtpd_hours: int
    rationale: str
    confidence: float
