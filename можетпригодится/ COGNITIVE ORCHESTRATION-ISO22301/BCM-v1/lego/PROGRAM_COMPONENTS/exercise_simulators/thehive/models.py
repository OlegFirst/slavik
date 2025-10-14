"""Pydantic models for TheHive Adapter"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class IncidentSeverity(str, Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentType(str, Enum):
    """Incident types"""
    SECURITY = "security"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    TECHNICAL = "technical"
    BUSINESS = "business"

class CaseStatus(str, Enum):
    """TheHive case status"""
    OPEN = "Open"
    RESOLVED = "Resolved"
    DELETED = "Deleted"

class TaskStatus(str, Enum):
    """TheHive task status"""
    WAITING = "Waiting"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    CANCELLED = "Cancel"

class ObservableDataType(str, Enum):
    """TheHive observable data types"""
    DOMAIN = "domain"
    FILE = "file"
    FILENAME = "filename"
    FQDN = "fqdn"
    HASH = "hash"
    IP = "ip"
    MAIL = "mail"
    MAIL_SUBJECT = "mail_subject"
    OTHER = "other"
    REGEXP = "regexp"
    REGISTRY = "registry"
    URI_PATH = "uri_path"
    URL = "url"
    USER_AGENT = "user-agent"

class IncidentData(BaseModel):
    """BCM incident data model"""
    incident_id: str = Field(..., description="Unique incident identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    title: str = Field(..., description="Incident title")
    description: Optional[str] = Field(None, description="Incident description")
    severity: IncidentSeverity = Field(default=IncidentSeverity.MEDIUM, description="Incident severity")
    type: IncidentType = Field(default=IncidentType.OPERATIONAL, description="Incident type")
    status: Optional[str] = Field(None, description="Incident status")
    
    # Additional incident details
    source_ip: Optional[str] = Field(None, description="Source IP address")
    affected_systems: List[str] = Field(default_factory=list, description="Affected systems")
    tags: List[str] = Field(default_factory=list, description="Incident tags")
    observables: List[Dict[str, Any]] = Field(default_factory=list, description="Incident observables")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Incident creation time")
    updated_at: Optional[datetime] = Field(None, description="Last update time")
    resolved_at: Optional[datetime] = Field(None, description="Resolution time")
    
    # Response details
    assigned_to: Optional[str] = Field(None, description="Assigned responder")
    response_team: List[str] = Field(default_factory=list, description="Response team members")
    resolution: Optional[str] = Field(None, description="Resolution description")

class HiveCaseCreationRequest(BaseModel):
    """Request to create TheHive case"""
    incident_id: str = Field(..., description="BCM incident ID")
    tenant_id: str = Field(..., description="Tenant identifier")
    title: str = Field(..., description="Case title")
    description: str = Field(..., description="Case description")
    severity: IncidentSeverity = Field(default=IncidentSeverity.MEDIUM, description="Case severity")
    tags: List[str] = Field(default_factory=list, description="Case tags")
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        return v.strip()

class HiveCaseUpdate(BaseModel):
    """Request to update TheHive case"""
    tenant_id: str = Field(..., description="Tenant identifier")
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    severity: Optional[int] = Field(None, ge=1, le=4, description="Updated severity (1-4)")
    status: Optional[CaseStatus] = Field(None, description="Updated status")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    assignee: Optional[str] = Field(None, description="Assigned analyst")
    resolution_status: Optional[str] = Field(None, description="Resolution status")

class HiveCase(BaseModel):
    """TheHive case model"""
    id: str = Field(..., description="Case ID")
    case_number: int = Field(..., description="Case number")
    title: str = Field(..., description="Case title")
    description: str = Field(..., description="Case description")
    severity: int = Field(..., ge=1, le=4, description="Case severity")
    status: CaseStatus = Field(..., description="Case status")
    tags: List[str] = Field(default_factory=list, description="Case tags")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    
    # Assignment and workflow
    assignee: Optional[str] = Field(None, description="Assigned analyst")
    owner: Optional[str] = Field(None, description="Case owner")
    
    # Custom fields for BCM integration
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
    
    # Statistics
    task_count: int = Field(default=0, description="Number of tasks")
    observable_count: int = Field(default=0, description="Number of observables")

class HiveTask(BaseModel):
    """TheHive task model"""
    id: str = Field(..., description="Task ID")
    case_id: str = Field(..., description="Parent case ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatus = Field(..., description="Task status")
    
    # Assignment
    assignee: Optional[str] = Field(None, description="Assigned analyst")
    owner: Optional[str] = Field(None, description="Task owner")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    
    # Task properties
    flag: bool = Field(default=False, description="Task flagged")
    order: int = Field(default=0, description="Task order")

class HiveObservable(BaseModel):
    """TheHive observable model"""
    id: str = Field(..., description="Observable ID")
    case_id: str = Field(..., description="Parent case ID")
    data_type: ObservableDataType = Field(..., description="Observable data type")
    data: str = Field(..., description="Observable data value")
    message: Optional[str] = Field(None, description="Observable message")
    tags: List[str] = Field(default_factory=list, description="Observable tags")
    
    # Traffic Light Protocol
    tlp: int = Field(default=2, ge=0, le=3, description="TLP level (0-3)")
    pap: int = Field(default=2, ge=0, le=3, description="PAP level (0-3)")
    
    # Analysis flags
    ioc: bool = Field(default=False, description="Indicator of Compromise")
    sighted: bool = Field(default=False, description="Sighted in environment")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    start_date: Optional[datetime] = Field(None, description="Start date")

class CaseStatistics(BaseModel):
    """Case statistics model"""
    tenant_id: str = Field(..., description="Tenant identifier")
    total_cases: int = Field(default=0, description="Total number of cases")
    open_cases: int = Field(default=0, description="Number of open cases")
    critical_cases: int = Field(default=0, description="Number of critical cases")
    
    # Distribution
    severity_distribution: Dict[str, int] = Field(default_factory=dict, description="Cases by severity")
    status_distribution: Dict[str, int] = Field(default_factory=dict, description="Cases by status")
    type_distribution: Dict[str, int] = Field(default_factory=dict, description="Cases by type")
    
    # Time-based metrics
    average_resolution_time: Optional[float] = Field(None, description="Average resolution time (hours)")
    cases_this_week: int = Field(default=0, description="Cases created this week")
    cases_this_month: int = Field(default=0, description="Cases created this month")
    
    # Response metrics
    response_time_sla: float = Field(default=24.0, description="Response time SLA (hours)")
    cases_within_sla: int = Field(default=0, description="Cases meeting SLA")
    sla_compliance_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="SLA compliance rate")

class WebhookPayload(BaseModel):
    """TheHive webhook payload model"""
    operation: str = Field(..., description="Webhook operation")
    object_type: str = Field(..., description="Object type (case, task, observable)")
    object_id: str = Field(..., description="Object ID")
    object: Dict[str, Any] = Field(..., description="Object data")
    request_id: Optional[str] = Field(None, description="Request ID")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Webhook timestamp")

class EventData(BaseModel):
    """Event data for EventBus integration"""
    event_type: str = Field(..., description="Event type")
    tenant_id: str = Field(..., description="Tenant identifier")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    correlation_id: Optional[str] = Field(None, description="Correlation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    source: str = Field(default="thehive-adapter", description="Event source")

class CaseSearchQuery(BaseModel):
    """Case search query model"""
    tenant_id: str = Field(..., description="Tenant identifier")
    status: Optional[CaseStatus] = Field(None, description="Filter by status")
    severity: Optional[int] = Field(None, ge=1, le=4, description="Filter by severity")
    assignee: Optional[str] = Field(None, description="Filter by assignee")
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    
    # Date range
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    updated_after: Optional[datetime] = Field(None, description="Updated after date")
    updated_before: Optional[datetime] = Field(None, description="Updated before date")
    
    # Pagination
    limit: int = Field(default=20, ge=1, le=100, description="Results limit")
    offset: int = Field(default=0, ge=0, description="Results offset")
    
    # Sorting
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order (asc/desc)")

class CaseSearchResult(BaseModel):
    """Case search result model"""
    cases: List[HiveCase] = Field(..., description="Found cases")
    total_count: int = Field(..., description="Total matching cases")
    query: CaseSearchQuery = Field(..., description="Original search query")
    execution_time: float = Field(..., description="Search execution time")

class IntegrationStatus(BaseModel):
    """Integration status model"""
    thehive_connected: bool = Field(..., description="TheHive connection status")
    eventbus_connected: bool = Field(..., description="EventBus connection status")
    last_sync: Optional[datetime] = Field(None, description="Last synchronization time")
    
    # Statistics
    cases_created_today: int = Field(default=0, description="Cases created today")
    events_processed_today: int = Field(default=0, description="Events processed today")
    errors_today: int = Field(default=0, description="Errors encountered today")
    
    # Health metrics
    average_response_time: float = Field(default=0.0, description="Average API response time")
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0, description="Success rate")
    
class AdapterConfiguration(BaseModel):
    """Adapter configuration model"""
    thehive_url: str = Field(..., description="TheHive instance URL")
    api_key_configured: bool = Field(..., description="API key configured")
    webhook_url: Optional[str] = Field(None, description="Webhook endpoint URL")
    
    # Integration settings
    auto_create_cases: bool = Field(default=True, description="Auto-create cases from incidents")
    auto_close_cases: bool = Field(default=True, description="Auto-close resolved incidents")
    sync_case_updates: bool = Field(default=True, description="Sync case updates back to BCM")
    
    # Default settings
    default_severity: int = Field(default=2, ge=1, le=4, description="Default case severity")
    default_tlp: int = Field(default=2, ge=0, le=3, description="Default TLP level")
    default_pap: int = Field(default=2, ge=0, le=3, description="Default PAP level")
    
    # Task automation
    create_initial_tasks: bool = Field(default=True, description="Create initial response tasks")
    task_templates: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Task templates by incident type"
    )
