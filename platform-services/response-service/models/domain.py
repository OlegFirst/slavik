"""
Response Module - Domain Models (Pydantic)
ISO 22301:2019 Clause 8.4 - Incident Response

All Pydantic models for API request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Enumerations
# ============================================================================

class IncidentSeverity(str, Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident lifecycle status"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentType(str, Enum):
    """Types of incidents"""
    SECURITY_BREACH = "security_breach"
    SYSTEM_FAILURE = "system_failure"
    NATURAL_DISASTER = "natural_disaster"
    HUMAN_ERROR = "human_error"
    SUPPLIER_FAILURE = "supplier_failure"
    CYBER_ATTACK = "cyber_attack"
    DATA_BREACH = "data_breach"
    SERVICE_DISRUPTION = "service_disruption"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    OTHER = "other"


class ActionStatus(str, Enum):
    """Response action status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActionPriority(str, Enum):
    """Response action priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CommunicationType(str, Enum):
    """Communication channel types"""
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    MEETING = "meeting"
    CHAT = "chat"
    NOTIFICATION = "notification"
    REPORT = "report"


class TeamMemberRole(str, Enum):
    """Response team member roles"""
    INCIDENT_MANAGER = "incident_manager"
    TECHNICAL_LEAD = "technical_lead"
    COMMUNICATIONS_LEAD = "communications_lead"
    BUSINESS_CONTINUITY = "business_continuity"
    SECURITY_ANALYST = "security_analyst"
    LEGAL = "legal"
    EXECUTIVE = "executive"
    SUPPORT = "support"


# ============================================================================
# Response Team Member Models
# ============================================================================

class ResponseTeamMemberBase(BaseModel):
    """Base model for response team member"""
    user_id: UUID = Field(..., description="User ID from user service")
    role: TeamMemberRole = Field(..., description="Role in response team")
    name: str = Field(..., min_length=1, max_length=200, description="Member name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    is_primary: bool = Field(default=False, description="Primary contact for this role")
    availability_status: str = Field(default="available", description="Availability status")
    notes: Optional[str] = Field(None, description="Additional notes")


class ResponseTeamMemberCreate(ResponseTeamMemberBase):
    """Create response team member"""
    pass


class ResponseTeamMemberUpdate(BaseModel):
    """Update response team member"""
    role: Optional[TeamMemberRole] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    is_primary: Optional[bool] = None
    availability_status: Optional[str] = None
    notes: Optional[str] = None


class ResponseTeamMember(ResponseTeamMemberBase):
    """Response team member with metadata"""
    id: UUID
    team_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Response Team Models
# ============================================================================

class ResponseTeamBase(BaseModel):
    """Base model for response team"""
    name: str = Field(..., min_length=1, max_length=200, description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    is_active: bool = Field(default=True, description="Team active status")
    activation_criteria: Optional[Dict[str, Any]] = Field(None, description="Activation criteria")
    escalation_procedures: Optional[Dict[str, Any]] = Field(None, description="Escalation procedures")


class ResponseTeamCreate(ResponseTeamBase):
    """Create response team"""
    members: List[ResponseTeamMemberCreate] = Field(default_factory=list, description="Initial team members")


class ResponseTeamUpdate(BaseModel):
    """Update response team"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    activation_criteria: Optional[Dict[str, Any]] = None
    escalation_procedures: Optional[Dict[str, Any]] = None


class ResponseTeam(ResponseTeamBase):
    """Response team with metadata"""
    id: UUID
    organization_id: UUID
    members: List[ResponseTeamMember] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Response Action Models
# ============================================================================

class ResponseActionBase(BaseModel):
    """Base model for response action"""
    title: str = Field(..., min_length=1, max_length=500, description="Action title")
    description: str = Field(..., description="Action description")
    action_type: str = Field(..., description="Type of action")
    priority: ActionPriority = Field(..., description="Action priority")
    assigned_to: Optional[UUID] = Field(None, description="Assigned user ID")
    assigned_to_name: Optional[str] = Field(None, description="Assigned user name")
    due_date: Optional[datetime] = Field(None, description="Due date")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours")
    dependencies: Optional[List[UUID]] = Field(None, description="Dependent action IDs")
    checklist: Optional[List[Dict[str, Any]]] = Field(None, description="Action checklist")


class ResponseActionCreate(ResponseActionBase):
    """Create response action"""
    pass


class ResponseActionUpdate(BaseModel):
    """Update response action"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    action_type: Optional[str] = None
    priority: Optional[ActionPriority] = None
    status: Optional[ActionStatus] = None
    assigned_to: Optional[UUID] = None
    assigned_to_name: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    completion_notes: Optional[str] = None
    dependencies: Optional[List[UUID]] = None
    checklist: Optional[List[Dict[str, Any]]] = None


class ResponseAction(ResponseActionBase):
    """Response action with metadata"""
    id: UUID
    incident_id: UUID
    status: ActionStatus
    actual_hours: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completion_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Communication Log Models
# ============================================================================

class CommunicationLogBase(BaseModel):
    """Base model for communication log"""
    communication_type: CommunicationType = Field(..., description="Type of communication")
    subject: str = Field(..., min_length=1, max_length=500, description="Communication subject")
    content: str = Field(..., description="Communication content")
    sender: str = Field(..., description="Sender name/identifier")
    recipients: List[str] = Field(..., description="Recipients list")
    cc_recipients: Optional[List[str]] = Field(None, description="CC recipients")
    channel: Optional[str] = Field(None, description="Communication channel")
    is_stakeholder_notification: bool = Field(default=False, description="Stakeholder notification flag")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CommunicationLogCreate(CommunicationLogBase):
    """Create communication log"""
    pass


class CommunicationLogUpdate(BaseModel):
    """Update communication log"""
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CommunicationLog(CommunicationLogBase):
    """Communication log with metadata"""
    id: UUID
    incident_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Incident Timeline Models
# ============================================================================

class IncidentTimelineEntry(BaseModel):
    """Incident timeline entry"""
    id: UUID
    incident_id: UUID
    timestamp: datetime
    event_type: str = Field(..., description="Type of event")
    description: str = Field(..., description="Event description")
    actor: Optional[str] = Field(None, description="Who performed the action")
    actor_id: Optional[UUID] = Field(None, description="Actor user ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Recovery Metrics Models
# ============================================================================

class RecoveryMetricsBase(BaseModel):
    """Base model for recovery metrics"""
    service_name: str = Field(..., description="Service/system name")
    target_rto_hours: float = Field(..., ge=0, description="Target Recovery Time Objective (hours)")
    target_rpo_hours: float = Field(..., ge=0, description="Target Recovery Point Objective (hours)")
    actual_rto_hours: Optional[float] = Field(None, ge=0, description="Actual RTO achieved")
    actual_rpo_hours: Optional[float] = Field(None, ge=0, description="Actual RPO achieved")
    downtime_start: datetime = Field(..., description="Downtime start timestamp")
    downtime_end: Optional[datetime] = Field(None, description="Downtime end timestamp")
    data_loss_start: Optional[datetime] = Field(None, description="Data loss period start")
    data_loss_end: Optional[datetime] = Field(None, description="Data loss period end")
    impact_description: Optional[str] = Field(None, description="Impact description")
    recovery_actions: Optional[List[str]] = Field(None, description="Recovery actions taken")


class RecoveryMetricsCreate(RecoveryMetricsBase):
    """Create recovery metrics"""
    pass


class RecoveryMetricsUpdate(BaseModel):
    """Update recovery metrics"""
    actual_rto_hours: Optional[float] = Field(None, ge=0)
    actual_rpo_hours: Optional[float] = Field(None, ge=0)
    downtime_end: Optional[datetime] = None
    data_loss_start: Optional[datetime] = None
    data_loss_end: Optional[datetime] = None
    impact_description: Optional[str] = None
    recovery_actions: Optional[List[str]] = None


class RecoveryMetrics(RecoveryMetricsBase):
    """Recovery metrics with metadata"""
    id: UUID
    incident_id: UUID
    rto_met: Optional[bool] = None
    rpo_met: Optional[bool] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Incident Models
# ============================================================================

class IncidentBase(BaseModel):
    """Base model for incident"""
    title: str = Field(..., min_length=1, max_length=500, description="Incident title")
    description: str = Field(..., description="Detailed incident description")
    incident_type: IncidentType = Field(..., description="Type of incident")
    severity: IncidentSeverity = Field(..., description="Incident severity")
    affected_systems: List[str] = Field(default_factory=list, description="Affected systems/services")
    affected_locations: Optional[List[str]] = Field(None, description="Affected locations")
    estimated_impact: Optional[str] = Field(None, description="Estimated business impact")
    root_cause: Optional[str] = Field(None, description="Root cause analysis")
    lessons_learned: Optional[str] = Field(None, description="Lessons learned")
    external_reference: Optional[str] = Field(None, description="External ticket/reference number")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")


class IncidentCreate(IncidentBase):
    """Create incident"""
    detected_at: Optional[datetime] = Field(None, description="Detection timestamp")
    detected_by: Optional[str] = Field(None, description="Who detected the incident")
    initial_response: Optional[str] = Field(None, description="Initial response actions")


class IncidentUpdate(BaseModel):
    """Update incident"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    incident_type: Optional[IncidentType] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    affected_systems: Optional[List[str]] = None
    affected_locations: Optional[List[str]] = None
    estimated_impact: Optional[str] = None
    root_cause: Optional[str] = None
    lessons_learned: Optional[str] = None
    external_reference: Optional[str] = None
    tags: Optional[List[str]] = None


class IncidentStatusChange(BaseModel):
    """Change incident status"""
    status: IncidentStatus = Field(..., description="New status")
    reason: Optional[str] = Field(None, description="Reason for status change")
    notes: Optional[str] = Field(None, description="Additional notes")


class Incident(IncidentBase):
    """Incident with full details"""
    id: UUID
    organization_id: UUID
    incident_number: str
    status: IncidentStatus
    detected_at: datetime
    detected_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    duration_hours: Optional[float] = None
    response_team_id: Optional[UUID] = None
    response_team: Optional[ResponseTeam] = None
    actions: List[ResponseAction] = Field(default_factory=list)
    communications: List[CommunicationLog] = Field(default_factory=list)
    timeline: List[IncidentTimelineEntry] = Field(default_factory=list)
    metrics: List[RecoveryMetrics] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Incident Report Models
# ============================================================================

class IncidentReport(BaseModel):
    """Comprehensive incident report"""
    incident: Incident
    summary: Dict[str, Any] = Field(
        ...,
        description="Executive summary"
    )
    impact_analysis: Dict[str, Any] = Field(
        ...,
        description="Business impact analysis"
    )
    timeline_summary: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Key timeline events"
    )
    actions_summary: Dict[str, Any] = Field(
        ...,
        description="Actions taken summary"
    )
    metrics_summary: Dict[str, Any] = Field(
        ...,
        description="Recovery metrics summary"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations for improvement"
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Report generation timestamp"
    )


# ============================================================================
# Dashboard Models
# ============================================================================

class IncidentDashboard(BaseModel):
    """Incident response dashboard data"""
    organization_id: UUID
    total_incidents: int = Field(..., description="Total incidents")
    active_incidents: int = Field(..., description="Active incidents")
    critical_incidents: int = Field(..., description="Critical severity incidents")
    incidents_by_status: Dict[str, int] = Field(..., description="Incidents grouped by status")
    incidents_by_severity: Dict[str, int] = Field(..., description="Incidents grouped by severity")
    incidents_by_type: Dict[str, int] = Field(..., description="Incidents grouped by type")
    avg_resolution_hours: Optional[float] = Field(None, description="Average resolution time")
    avg_response_hours: Optional[float] = Field(None, description="Average response time")
    rto_compliance_rate: Optional[float] = Field(None, description="RTO compliance rate %")
    rpo_compliance_rate: Optional[float] = Field(None, description="RPO compliance rate %")
    recent_incidents: List[Incident] = Field(default_factory=list, description="Recent incidents")
    trending_types: List[Dict[str, Any]] = Field(default_factory=list, description="Trending incident types")
    period_start: datetime = Field(..., description="Dashboard period start")
    period_end: datetime = Field(..., description="Dashboard period end")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class OrganizationMetrics(BaseModel):
    """Organization-level incident metrics"""
    organization_id: UUID
    total_incidents: int
    total_actions: int
    total_communications: int
    avg_incident_duration_hours: Optional[float] = None
    avg_actions_per_incident: Optional[float] = None
    incidents_this_month: int
    incidents_last_month: int
    trend_percentage: Optional[float] = None
    mttr: Optional[float] = Field(None, description="Mean Time To Resolve (hours)")
    mtbf: Optional[float] = Field(None, description="Mean Time Between Failures (hours)")
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# List/Query Models
# ============================================================================

class IncidentListQuery(BaseModel):
    """Query parameters for listing incidents"""
    organization_id: Optional[UUID] = None
    status: Optional[IncidentStatus] = None
    severity: Optional[IncidentSeverity] = None
    incident_type: Optional[IncidentType] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class IncidentListResponse(BaseModel):
    """Response for incident list"""
    items: List[Incident]
    total: int
    skip: int
    limit: int


# ============================================================================
# Escalation Models
# ============================================================================

class IncidentEscalation(BaseModel):
    """Escalate incident"""
    escalation_reason: str = Field(..., description="Reason for escalation")
    escalate_to: Optional[List[UUID]] = Field(None, description="Escalate to user IDs")
    escalation_level: str = Field(..., description="Escalation level")
    notify_stakeholders: bool = Field(default=True, description="Send notifications")
    additional_notes: Optional[str] = Field(None, description="Additional notes")


# ============================================================================
# Health Check
# ============================================================================

class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")
    database: Optional[Dict[str, Any]] = None
