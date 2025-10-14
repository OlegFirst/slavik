"""
Crisis Communication Models
============================

Models for crisis communication, stakeholder notifications, and AI-driven
communication templates.

Adapted from: /scenarios/bcm_incident/models/ai_communication_models.py
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class CrisisLevel(str, Enum):
    """Crisis severity levels"""
    MINOR = "1"  # Minor Disruption
    SIGNIFICANT = "2"  # Significant Disruption
    MAJOR = "3"  # Major Crisis
    SEVERE = "4"  # Severe Crisis
    CATASTROPHIC = "5"  # Catastrophic Event


class CommunicationType(str, Enum):
    """Communication delivery methods"""
    EMAIL = "email"
    SMS = "sms"
    SOCIAL = "social"
    PRESS = "press"
    INTERNAL = "internal"
    PHONE = "phone"
    PUSH = "push"


class NotificationType(str, Enum):
    """Stakeholder notification types"""
    INITIAL = "initial"  # Initial Notification
    UPDATE = "update"  # Status Update
    ESCALATION = "escalation"  # Escalation Notice
    RESOLUTION = "resolution"  # Resolution Notice
    CLOSURE = "closure"  # Closure Notice


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class IncidentType(str, Enum):
    """BCM incident types"""
    OPERATIONAL = "operational"
    CYBER = "cyber"
    NATURAL = "natural"
    SUPPLY_CHAIN = "supply_chain"
    HEALTH_SAFETY = "health_safety"
    FINANCIAL = "financial"
    REPUTATIONAL = "reputational"


class PriorityLevel(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# Communication Models
# ============================================================================

class CommunicationTemplate(BaseModel):
    """Template for crisis communications"""
    id: Optional[str] = None
    name: str
    template_type: CommunicationType
    subject: Optional[str] = None
    content: str
    send_delay_minutes: int = Field(default=0, description="Delay before sending")
    crisis_level: Optional[CrisisLevel] = None
    incident_types: List[IncidentType] = Field(default_factory=list)
    variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Template variables for personalization"
    )
    created_at: datetime = Field(default_factory=datetime.now)


class CrisisCommunicationPlan(BaseModel):
    """Crisis communication plan"""
    id: Optional[str] = None
    name: str
    crisis_level: CrisisLevel
    active: bool = True
    templates: List[CommunicationTemplate] = Field(default_factory=list)
    stakeholder_groups: List[str] = Field(
        default_factory=list,
        description="Target stakeholder groups"
    )
    escalation_thresholds: Dict[str, Any] = Field(
        default_factory=dict,
        description="Automatic escalation triggers"
    )
    approval_required: bool = True
    approvers: List[str] = Field(default_factory=list)


class StakeholderNotification(BaseModel):
    """Notification sent to stakeholder"""
    id: Optional[str] = None
    incident_id: str
    notification_type: NotificationType
    recipient_id: str
    recipient_name: str
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    delivery_method: CommunicationType
    message_content: str
    subject: Optional[str] = None
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_reason: Optional[str] = None
    retries: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# AI Response Models
# ============================================================================

class AIResponseTemplate(BaseModel):
    """AI-driven response template"""
    id: Optional[str] = None
    name: str
    incident_type: IncidentType
    priority_level: PriorityLevel
    response_checklist: List[str] = Field(
        default_factory=list,
        description="Recommended response actions"
    )
    escalation_triggers: List[str] = Field(
        default_factory=list,
        description="Conditions that trigger escalation"
    )
    ai_confidence_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Minimum AI confidence for auto-response"
    )
    communication_templates: List[str] = Field(
        default_factory=list,
        description="Associated communication template IDs"
    )
    estimated_response_time_minutes: Optional[int] = None


class AIClassificationRule(BaseModel):
    """AI classification rule for incidents"""
    id: Optional[str] = None
    name: str
    rule_type: str  # keyword_match, pattern_recognition, ml_classification
    incident_type: IncidentType
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords to match for classification"
    )
    patterns: List[str] = Field(
        default_factory=list,
        description="Regex patterns for matching"
    )
    confidence_weight: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Weight for this rule in classification"
    )
    active: bool = True


class AIEscalationRule(BaseModel):
    """AI-driven escalation rule"""
    id: Optional[str] = None
    name: str
    trigger_condition: str = Field(
        description="Condition that triggers escalation (e.g., 'duration > 120 minutes')"
    )
    action_type: str  # auto_escalate, notify_manager, activate_team, send_alert
    escalation_level: int = Field(default=1, ge=1, le=5)
    notification_template_id: Optional[str] = None
    notify_roles: List[str] = Field(default_factory=list)
    activate_teams: List[str] = Field(default_factory=list)
    active: bool = True
    cooldown_minutes: int = Field(
        default=60,
        description="Minimum time between escalation triggers"
    )


class AILearningPattern(BaseModel):
    """AI learning pattern from historical data"""
    id: Optional[str] = None
    name: str
    pattern_type: str  # recovery_time_analysis, success_factor_analysis, etc.
    incident_type: Optional[IncidentType] = None
    pattern_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Statistical pattern data"
    )
    confidence_level: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence in pattern reliability"
    )
    sample_size: int = Field(
        default=0,
        description="Number of incidents analyzed"
    )
    last_updated: datetime = Field(default_factory=datetime.now)
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations based on pattern"
    )


# ============================================================================
# Communication Analytics
# ============================================================================

class CommunicationMetrics(BaseModel):
    """Metrics for communication effectiveness"""
    incident_id: str
    total_notifications: int = 0
    sent_notifications: int = 0
    delivered_notifications: int = 0
    read_notifications: int = 0
    failed_notifications: int = 0
    avg_delivery_time_seconds: Optional[float] = None
    avg_read_time_minutes: Optional[float] = None
    delivery_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Percentage of notifications delivered"
    )
    read_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Percentage of notifications read"
    )
    by_channel: Dict[str, int] = Field(
        default_factory=dict,
        description="Notifications by communication channel"
    )
    by_stakeholder_group: Dict[str, int] = Field(
        default_factory=dict,
        description="Notifications by stakeholder group"
    )


class CommunicationTimeline(BaseModel):
    """Timeline of communications for incident"""
    incident_id: str
    events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chronological communication events"
    )
    total_events: int = 0
    first_notification: Optional[datetime] = None
    last_notification: Optional[datetime] = None
    response_time_minutes: Optional[float] = Field(
        None,
        description="Time from incident start to first notification"
    )


# ============================================================================
# Helper Functions
# ============================================================================

def create_notification(
    incident_id: str,
    notification_type: NotificationType,
    recipient_id: str,
    recipient_name: str,
    message_content: str,
    delivery_method: CommunicationType = CommunicationType.EMAIL,
    **kwargs
) -> StakeholderNotification:
    """Create a stakeholder notification"""
    return StakeholderNotification(
        incident_id=incident_id,
        notification_type=notification_type,
        recipient_id=recipient_id,
        recipient_name=recipient_name,
        message_content=message_content,
        delivery_method=delivery_method,
        **kwargs
    )


def calculate_communication_metrics(
    notifications: List[StakeholderNotification]
) -> CommunicationMetrics:
    """Calculate communication metrics from notifications"""
    if not notifications:
        return CommunicationMetrics(
            incident_id="",
            total_notifications=0
        )

    incident_id = notifications[0].incident_id
    total = len(notifications)
    sent = sum(1 for n in notifications if n.status != NotificationStatus.PENDING)
    delivered = sum(1 for n in notifications if n.status in (
        NotificationStatus.DELIVERED, NotificationStatus.READ
    ))
    read = sum(1 for n in notifications if n.status == NotificationStatus.READ)
    failed = sum(1 for n in notifications if n.status == NotificationStatus.FAILED)

    # Calculate delivery times
    delivery_times = [
        (n.delivered_at - n.sent_at).total_seconds()
        for n in notifications
        if n.sent_at and n.delivered_at
    ]
    avg_delivery_time = (
        sum(delivery_times) / len(delivery_times)
        if delivery_times else None
    )

    # Calculate read times
    read_times = [
        (n.read_at - n.delivered_at).total_seconds() / 60
        for n in notifications
        if n.delivered_at and n.read_at
    ]
    avg_read_time = (
        sum(read_times) / len(read_times)
        if read_times else None
    )

    # By channel
    by_channel = {}
    for n in notifications:
        channel = n.delivery_method
        by_channel[channel] = by_channel.get(channel, 0) + 1

    return CommunicationMetrics(
        incident_id=incident_id,
        total_notifications=total,
        sent_notifications=sent,
        delivered_notifications=delivered,
        read_notifications=read,
        failed_notifications=failed,
        avg_delivery_time_seconds=avg_delivery_time,
        avg_read_time_minutes=avg_read_time,
        delivery_rate=delivered / total if total > 0 else 0,
        read_rate=read / delivered if delivered > 0 else 0,
        by_channel=by_channel
    )
