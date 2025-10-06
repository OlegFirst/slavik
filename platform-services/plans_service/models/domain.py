"""
Plans Service Domain Models (Pydantic)
ISO 22301 Clause 8.4 - Business Continuity Plans and Procedures
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ===== ENUMS =====

class PlanType(str, Enum):
    """Plan classification types - ISO 22301 8.4.1"""
    BUSINESS_CONTINUITY = "business_continuity"
    DISASTER_RECOVERY = "disaster_recovery"
    EMERGENCY_RESPONSE = "emergency_response"
    CRISIS_MANAGEMENT = "crisis_management"
    INCIDENT_RESPONSE = "incident_response"
    CRISIS_COMMUNICATION = "crisis_communication"


class PlanPriority(str, Enum):
    """Plan priority classification"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PlanStatus(str, Enum):
    """Plan lifecycle workflow"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ProcedureType(str, Enum):
    """Procedure types"""
    IMMEDIATE_RESPONSE = "immediate_response"
    SHORT_TERM_RECOVERY = "short_term_recovery"
    LONG_TERM_RECOVERY = "long_term_recovery"
    COMMUNICATION = "communication"
    COORDINATION = "coordination"
    LOGISTICS = "logistics"


class ResourceType(str, Enum):
    """Resource types"""
    PERSONNEL = "personnel"
    FACILITY = "facility"
    EQUIPMENT = "equipment"
    TECHNOLOGY = "technology"
    SUPPLIER = "supplier"
    INFORMATION = "information"
    FINANCIAL = "financial"


class ResourceCriticality(str, Enum):
    """Resource criticality levels"""
    CRITICAL = "critical"
    IMPORTANT = "important"
    USEFUL = "useful"
    OPTIONAL = "optional"


class AvailabilityRequirement(str, Enum):
    """Resource availability requirements"""
    IMMEDIATE = "immediate"  # 0-1h
    SHORT_TERM = "short_term"  # 1-24h
    MEDIUM_TERM = "medium_term"  # 1-7d
    LONG_TERM = "long_term"  # >7d


class ReviewFrequency(str, Enum):
    """Plan review frequency"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUALLY = "semiannually"
    ANNUALLY = "annually"


class ContactListType(str, Enum):
    """Contact list types"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    EMERGENCY_SERVICES = "emergency_services"
    SUPPLIERS = "suppliers"
    REGULATORS = "regulators"
    MEDIA = "media"


class CommunicationType(str, Enum):
    """Communication template types"""
    INTERNAL_NOTIFICATION = "internal_notification"
    EXTERNAL_NOTIFICATION = "external_notification"
    MEDIA_STATEMENT = "media_statement"
    STAKEHOLDER_UPDATE = "stakeholder_update"
    CRISIS_ALERT = "crisis_alert"
    ALL_CLEAR = "all_clear"


class ActivationType(str, Enum):
    """Plan activation types"""
    ACTUAL_INCIDENT = "actual_incident"
    TEST_EXERCISE = "test_exercise"
    DRILL = "drill"
    WALKTHROUGH = "walkthrough"


class EffectivenessRating(str, Enum):
    """Activation effectiveness rating"""
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class ReviewType(str, Enum):
    """Plan review types"""
    SCHEDULED = "scheduled"
    POST_EXERCISE = "post_exercise"
    POST_INCIDENT = "post_incident"
    ORGANIZATIONAL_CHANGE = "organizational_change"


# ===== DOMAIN MODELS =====

class Contact(BaseModel):
    """Contact information"""
    name: str = Field(min_length=2, max_length=255, description="Contact name")
    role: str = Field(min_length=2, max_length=255, description="Contact role")
    primary_phone: str = Field(min_length=7, max_length=20, description="Primary phone number")
    secondary_phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Secondary phone number")
    email: str = Field(min_length=5, max_length=255, description="Email address")
    notification_priority: int = Field(1, ge=1, le=10, description="Notification priority (1-10)")
    escalation_level: int = Field(0, ge=0, le=10, description="Escalation level (0-10)")

    @field_validator('name', 'role')
    @classmethod
    def validate_text_fields(cls, v, info):
        if len(v.strip()) < 2:
            raise ValueError(f"{info.field_name} must be at least 2 characters (excluding whitespace)")
        return v.strip()

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError("Email must contain '@' symbol")
        if len(v.strip()) < 5:
            raise ValueError("Email must be at least 5 characters")
        return v.strip().lower()

    @field_validator('primary_phone', 'secondary_phone')
    @classmethod
    def validate_phone(cls, v, info):
        if v is not None:
            if len(v.strip()) < 7:
                raise ValueError(f"{info.field_name} must be at least 7 characters")
            return v.strip()
        return v

    @field_validator('notification_priority', 'escalation_level')
    @classmethod
    def validate_priority_levels(cls, v, info):
        if v < 0:
            raise ValueError(f"{info.field_name} cannot be negative")
        if v > 10:
            raise ValueError(f"{info.field_name} cannot exceed 10")
        return v


class ActivationTrigger(BaseModel):
    """Plan activation trigger"""
    trigger_type: str = Field(min_length=2, max_length=100, description="Trigger type")
    description: str = Field(min_length=10, max_length=2000, description="Trigger description")
    threshold: Optional[str] = Field(None, max_length=500, description="Trigger threshold")
    criteria: Optional[str] = Field(None, max_length=1000, description="Trigger criteria")

    @field_validator('trigger_type')
    @classmethod
    def validate_trigger_type(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Trigger type must be at least 2 characters")
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Trigger description must be at least 10 characters to be meaningful")
        return v.strip()


class RecoveryPriority(BaseModel):
    """Recovery priority item"""
    priority_order: int = Field(ge=1, description="Priority order (must be >= 1)")
    activity: str = Field(min_length=3, max_length=500, description="Recovery activity")
    rto_hours: int = Field(ge=0, le=8760, description="RTO in hours (max 1 year)")
    dependencies: List[str] = []

    @field_validator('priority_order')
    @classmethod
    def validate_priority_order(cls, v):
        if v < 1:
            raise ValueError("Priority order must be at least 1")
        if v > 1000:
            raise ValueError("Priority order exceeds reasonable limit (max 1000)")
        return v

    @field_validator('activity')
    @classmethod
    def validate_activity(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Recovery activity must be at least 3 characters to be meaningful")
        return v.strip()

    @field_validator('rto_hours')
    @classmethod
    def validate_rto(cls, v):
        if v < 0:
            raise ValueError("RTO hours cannot be negative")
        if v > 8760:
            raise ValueError("RTO hours cannot exceed 1 year (8760 hours)")
        return v


# ===== REQUEST/RESPONSE MODELS =====

class PlanCreate(BaseModel):
    """Create plan request"""
    tenant_id: str = Field(min_length=1, max_length=255, description="Tenant ID")
    plan_code: str = Field(min_length=2, max_length=50, description="Plan code")
    plan_name: str = Field(min_length=3, max_length=255, description="Plan name (3-255 characters)")
    plan_type: PlanType
    priority: PlanPriority = PlanPriority.MEDIUM

    # ISO 8.4.4 content
    objective: Optional[str] = Field(None, min_length=10, max_length=2000, description="Plan objective")
    scope: Optional[str] = Field(None, min_length=10, max_length=2000, description="Plan scope")
    assumptions: Optional[str] = Field(None, max_length=5000, description="Plan assumptions")
    activation_triggers: Optional[List[Dict[str, Any]]] = None
    activation_authority_user_id: Optional[str] = None

    # Recovery objectives
    rto_hours: Optional[int] = Field(None, ge=0, le=8760, description="RTO in hours (max 1 year/8760 hours)")
    rpo_hours: Optional[int] = Field(None, ge=0, le=8760, description="RPO in hours (max 1 year/8760 hours)")
    mtpd_hours: Optional[int] = Field(None, ge=0, le=8760, description="MTPD in hours (max 1 year/8760 hours)")

    # Links
    based_on_bia_id: Optional[int] = None
    based_on_risk_ids: Optional[List[int]] = None

    # Team
    plan_owner_user_id: str = Field(min_length=1, max_length=255, description="Plan owner user ID")
    team_leader_user_id: Optional[str] = Field(None, min_length=1, max_length=255, description="Team leader user ID")
    team_member_user_ids: Optional[List[str]] = None

    # Review
    review_frequency: ReviewFrequency = ReviewFrequency.ANNUALLY

    @field_validator('plan_name')
    @classmethod
    def validate_plan_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Plan name must be at least 3 characters (excluding whitespace)")
        return v.strip()

    @field_validator('rto_hours', 'rpo_hours', 'mtpd_hours')
    @classmethod
    def validate_recovery_objectives(cls, v, info):
        if v is not None:
            if v < 0:
                raise ValueError(f"{info.field_name} cannot be negative")
            if v > 8760:
                raise ValueError(f"{info.field_name} cannot exceed 1 year (8760 hours)")
        return v

    @field_validator('objective', 'scope')
    @classmethod
    def validate_text_fields(cls, v, info):
        if v is not None and len(v.strip()) < 10:
            raise ValueError(f"{info.field_name} must be at least 10 characters to be meaningful")
        return v.strip() if v else v


class PlanUpdate(BaseModel):
    """Update plan request"""
    plan_name: Optional[str] = Field(None, min_length=3, max_length=255, description="Plan name (3-255 characters)")
    priority: Optional[PlanPriority] = None
    objective: Optional[str] = Field(None, min_length=10, max_length=2000, description="Plan objective")
    scope: Optional[str] = Field(None, min_length=10, max_length=2000, description="Plan scope")
    assumptions: Optional[str] = Field(None, max_length=5000, description="Plan assumptions")
    activation_triggers: Optional[List[Dict[str, Any]]] = None
    activation_authority_user_id: Optional[str] = Field(None, min_length=1, max_length=255)
    rto_hours: Optional[int] = Field(None, ge=0, le=8760, description="RTO in hours (max 1 year)")
    rpo_hours: Optional[int] = Field(None, ge=0, le=8760, description="RPO in hours (max 1 year)")
    mtpd_hours: Optional[int] = Field(None, ge=0, le=8760, description="MTPD in hours (max 1 year)")
    team_leader_user_id: Optional[str] = Field(None, min_length=1, max_length=255)
    team_member_user_ids: Optional[List[str]] = None
    review_frequency: Optional[ReviewFrequency] = None

    @field_validator('plan_name')
    @classmethod
    def validate_plan_name(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Plan name must be at least 3 characters (excluding whitespace)")
        return v.strip() if v else v

    @field_validator('objective', 'scope')
    @classmethod
    def validate_text_fields(cls, v, info):
        if v is not None and len(v.strip()) < 10:
            raise ValueError(f"{info.field_name} must be at least 10 characters to be meaningful")
        return v.strip() if v else v

    @field_validator('rto_hours', 'rpo_hours', 'mtpd_hours')
    @classmethod
    def validate_recovery_objectives(cls, v, info):
        if v is not None:
            if v < 0:
                raise ValueError(f"{info.field_name} cannot be negative")
            if v > 8760:
                raise ValueError(f"{info.field_name} cannot exceed 1 year (8760 hours)")
        return v


class PlanResponse(BaseModel):
    """Plan response"""
    plan_id: int
    tenant_id: str
    plan_code: str
    plan_name: str
    plan_type: PlanType
    priority: PlanPriority
    status: PlanStatus
    version: str

    objective: Optional[str]
    scope: Optional[str]
    rto_hours: Optional[int]
    rpo_hours: Optional[int]
    mtpd_hours: Optional[int]

    plan_owner_user_id: str
    team_leader_user_id: Optional[str]
    review_frequency: ReviewFrequency

    last_review_date: Optional[datetime]
    next_review_date: Optional[datetime]
    last_test_date: Optional[datetime]
    next_test_date: Optional[datetime]

    approved_by_user_id: Optional[str]
    approval_date: Optional[datetime]

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProcedureCreate(BaseModel):
    """Create procedure request"""
    tenant_id: str = Field(min_length=1, max_length=255, description="Tenant ID")
    sequence: int = Field(10, ge=0, description="Procedure sequence number (0 or higher)")
    procedure_name: str = Field(min_length=3, max_length=255, description="Procedure name (3-255 characters)")
    procedure_type: ProcedureType
    description: Optional[str] = Field(None, min_length=10, max_length=5000, description="Procedure description")
    estimated_duration_minutes: Optional[int] = Field(None, ge=0, le=10080, description="Estimated duration in minutes (max 1 week/10080 minutes)")
    responsible_role: Optional[str] = Field(None, min_length=2, max_length=255, description="Responsible role")
    responsible_user_id: Optional[str] = Field(None, min_length=1, max_length=255, description="Responsible user ID")
    prerequisite_procedure_ids: Optional[List[int]] = None
    required_resources: Optional[str] = Field(None, max_length=2000, description="Required resources")
    success_criteria: Optional[str] = Field(None, max_length=2000, description="Success criteria")
    verification_checklist: Optional[List[Dict[str, Any]]] = None

    @field_validator('procedure_name')
    @classmethod
    def validate_procedure_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Procedure name must be at least 3 characters (excluding whitespace)")
        return v.strip()

    @field_validator('sequence')
    @classmethod
    def validate_sequence(cls, v):
        if v < 0:
            raise ValueError("Sequence number cannot be negative")
        if v > 10000:
            raise ValueError("Sequence number exceeds reasonable limit (max 10000)")
        return v

    @field_validator('estimated_duration_minutes')
    @classmethod
    def validate_duration(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("Estimated duration cannot be negative")
            if v > 10080:  # 1 week
                raise ValueError("Estimated duration cannot exceed 1 week (10080 minutes)")
        return v


class ProcedureUpdate(BaseModel):
    """Update procedure request"""
    sequence: Optional[int] = Field(None, ge=0, description="Procedure sequence number")
    procedure_name: Optional[str] = Field(None, min_length=3, max_length=255, description="Procedure name (3-255 characters)")
    procedure_type: Optional[ProcedureType] = None
    description: Optional[str] = Field(None, min_length=10, max_length=5000, description="Procedure description")
    estimated_duration_minutes: Optional[int] = Field(None, ge=0, le=10080, description="Estimated duration (max 1 week/10080 minutes)")
    responsible_role: Optional[str] = Field(None, min_length=2, max_length=255, description="Responsible role")
    responsible_user_id: Optional[str] = Field(None, min_length=1, max_length=255, description="Responsible user ID")
    prerequisite_procedure_ids: Optional[List[int]] = None
    required_resources: Optional[str] = Field(None, max_length=2000, description="Required resources")
    success_criteria: Optional[str] = Field(None, max_length=2000, description="Success criteria")
    verification_checklist: Optional[List[Dict[str, Any]]] = None

    @field_validator('sequence')
    @classmethod
    def validate_sequence(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("Sequence number cannot be negative")
            if v > 10000:
                raise ValueError("Sequence number exceeds reasonable limit (max 10000)")
        return v

    @field_validator('procedure_name')
    @classmethod
    def validate_procedure_name(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Procedure name must be at least 3 characters (excluding whitespace)")
        return v.strip() if v else v

    @field_validator('estimated_duration_minutes')
    @classmethod
    def validate_duration(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("Estimated duration cannot be negative")
            if v > 10080:
                raise ValueError("Estimated duration cannot exceed 1 week (10080 minutes)")
        return v


class ProcedureResponse(BaseModel):
    """Procedure response"""
    procedure_id: int
    plan_id: int
    sequence: int
    procedure_name: str
    procedure_type: ProcedureType
    description: Optional[str]
    estimated_duration_minutes: Optional[int]
    responsible_role: Optional[str]
    responsible_user_id: Optional[str]
    prerequisite_procedure_ids: Optional[List[int]]
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceCreate(BaseModel):
    """Create resource request"""
    tenant_id: str = Field(min_length=1, max_length=255, description="Tenant ID")
    resource_name: str = Field(min_length=1, max_length=255, description="Resource name (1-255 characters)")
    resource_type: ResourceType
    availability_requirement: AvailabilityRequirement
    criticality: ResourceCriticality
    description: Optional[str] = Field(None, min_length=5, max_length=2000, description="Resource description")
    quantity_required: int = Field(1, ge=1, description="Quantity required (must be at least 1)")
    location: Optional[str] = Field(None, max_length=500, description="Resource location")
    contact_person: Optional[str] = Field(None, min_length=2, max_length=255, description="Contact person")
    contact_details: Optional[str] = Field(None, max_length=500, description="Contact details")
    alternative_resources: Optional[str] = Field(None, max_length=1000, description="Alternative resources")

    @field_validator('resource_name')
    @classmethod
    def validate_resource_name(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Resource name cannot be empty")
        return v.strip()

    @field_validator('quantity_required')
    @classmethod
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError("Quantity required must be at least 1")
        if v > 1000000:
            raise ValueError("Quantity required exceeds reasonable limit (max 1,000,000)")
        return v


class ResourceUpdate(BaseModel):
    """Update resource request"""
    resource_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Resource name (1-255 characters)")
    resource_type: Optional[ResourceType] = None
    availability_requirement: Optional[AvailabilityRequirement] = None
    criticality: Optional[ResourceCriticality] = None
    description: Optional[str] = Field(None, min_length=5, max_length=2000, description="Resource description")
    quantity_required: Optional[int] = Field(None, ge=1, description="Quantity required (at least 1)")
    location: Optional[str] = Field(None, max_length=500, description="Resource location")
    contact_person: Optional[str] = Field(None, min_length=2, max_length=255, description="Contact person")
    contact_details: Optional[str] = Field(None, max_length=500, description="Contact details")
    alternative_resources: Optional[str] = Field(None, max_length=1000, description="Alternative resources")

    @field_validator('resource_name')
    @classmethod
    def validate_resource_name(cls, v):
        if v is not None and len(v.strip()) < 1:
            raise ValueError("Resource name cannot be empty")
        return v.strip() if v else v

    @field_validator('quantity_required')
    @classmethod
    def validate_quantity(cls, v):
        if v is not None:
            if v < 1:
                raise ValueError("Quantity required must be at least 1")
            if v > 1000000:
                raise ValueError("Quantity required exceeds reasonable limit (max 1,000,000)")
        return v


class ResourceResponse(BaseModel):
    """Resource response"""
    resource_id: int
    plan_id: int
    resource_name: str
    resource_type: ResourceType
    availability_requirement: AvailabilityRequirement
    criticality: ResourceCriticality
    quantity_required: int
    location: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ContactListCreate(BaseModel):
    """Create contact list request"""
    tenant_id: str = Field(min_length=1, max_length=255, description="Tenant ID")
    plan_id: Optional[int] = Field(None, ge=1, description="Plan ID")
    list_name: str = Field(min_length=3, max_length=255, description="Contact list name (3-255 characters)")
    list_type: ContactListType
    description: Optional[str] = Field(None, max_length=2000, description="Contact list description")
    contacts: List[Dict[str, Any]] = Field(min_length=1, description="Contact list (at least 1 contact required)")
    call_tree_structure: Optional[Dict[str, Any]] = None

    @field_validator('list_name')
    @classmethod
    def validate_list_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Contact list name must be at least 3 characters (excluding whitespace)")
        return v.strip()

    @field_validator('contacts')
    @classmethod
    def validate_contacts(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one contact must be provided in the contact list")
        return v


class ContactListResponse(BaseModel):
    """Contact list response"""
    contact_list_id: int
    tenant_id: str
    plan_id: Optional[int]
    list_name: str
    list_type: ContactListType
    contacts: List[Dict[str, Any]]
    last_verified_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ActivationCreate(BaseModel):
    """Create activation request"""
    tenant_id: str = Field(min_length=1, max_length=255, description="Tenant ID")
    activation_name: str = Field(min_length=3, max_length=255, description="Activation name (3-255 characters)")
    activation_type: ActivationType
    trigger_event: Optional[str] = Field(None, min_length=5, max_length=1000, description="Trigger event description")
    triggered_by_incident_id: Optional[int] = Field(None, ge=1, description="Incident ID")

    @field_validator('activation_name')
    @classmethod
    def validate_activation_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Activation name must be at least 3 characters (excluding whitespace)")
        return v.strip()

    @field_validator('trigger_event')
    @classmethod
    def validate_trigger_event(cls, v):
        if v is not None and len(v.strip()) < 5:
            raise ValueError("Trigger event description must be at least 5 characters to be meaningful")
        return v.strip() if v else v

    @field_validator('triggered_by_incident_id')
    @classmethod
    def validate_incident_id(cls, v):
        if v is not None and v < 1:
            raise ValueError("Incident ID must be a positive integer")
        return v


class ActivationResponse(BaseModel):
    """Activation response"""
    activation_id: int
    plan_id: int
    activation_name: str
    activation_type: ActivationType
    activation_datetime: datetime
    activated_by_user_id: str
    actual_recovery_time_hours: Optional[float]
    rto_achieved: Optional[bool]
    effectiveness_rating: Optional[EffectivenessRating]
    summary: Optional[str]

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    """Create review request"""
    tenant_id: str = Field(min_length=1, max_length=255, description="Tenant ID")
    review_type: ReviewType
    findings: Optional[str] = Field(None, min_length=10, max_length=5000, description="Review findings")
    recommendations: Optional[str] = Field(None, min_length=10, max_length=5000, description="Review recommendations")
    is_current: Optional[bool] = None
    is_effective: Optional[bool] = None
    action_items: Optional[List[Dict[str, Any]]] = None

    @field_validator('findings', 'recommendations')
    @classmethod
    def validate_text_fields(cls, v, info):
        if v is not None and len(v.strip()) < 10:
            raise ValueError(f"{info.field_name} must be at least 10 characters to be meaningful")
        return v.strip() if v else v


class ReviewResponse(BaseModel):
    """Review response"""
    review_id: int
    plan_id: int
    review_date: datetime
    review_type: ReviewType
    reviewed_by_user_id: str
    is_current: Optional[bool]
    is_effective: Optional[bool]
    findings: Optional[str]
    recommendations: Optional[str]
    approved: bool
    created_at: datetime

    class Config:
        from_attributes = True
