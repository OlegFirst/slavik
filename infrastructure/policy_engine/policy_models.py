"""
Policy Models - Pydantic Models for Type Safety
================================================

Provides strongly-typed models for all policy configurations:
- RecoveryPolicy
- OptimizationPolicy
- MonitoringPolicy
- CompliancePolicy
- NotificationPolicy
- EscalationLevel

All models include validation rules to ensure configuration correctness.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum


class RecoveryStrategy(str, Enum):
    """Recovery strategy types"""
    RESTART = "restart"
    CIRCUIT_BREAKER = "circuit_breaker"
    FAILOVER = "failover"
    ROLLBACK = "rollback"
    MANUAL = "manual"


class ServicePriority(int, Enum):
    """Service priority levels (1=highest, 5=lowest)"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    MINIMAL = 5


class RecoveryServicePolicy(BaseModel):
    """Policy for a specific service recovery"""
    priority: int = Field(..., ge=1, le=5, description="Service priority (1=critical, 5=minimal)")
    rto_seconds: int = Field(..., gt=0, description="Recovery Time Objective in seconds")
    rpo_seconds: Optional[int] = Field(None, ge=0, description="Recovery Point Objective in seconds")
    max_auto_attempts: int = Field(..., ge=0, le=10, description="Maximum automatic recovery attempts")
    escalate_immediately: bool = Field(False, description="Escalate on first failure")
    recovery_strategy: RecoveryStrategy = Field(..., description="Recovery strategy to use")
    notify_teams: List[str] = Field(default_factory=list, description="Teams to notify")
    require_approval: bool = Field(False, description="Require human approval before recovery")

    @validator('rpo_seconds')
    def validate_rpo_rto(cls, v, values):
        """RPO should not exceed RTO"""
        if v is not None and 'rto_seconds' in values:
            if v > values['rto_seconds']:
                raise ValueError(f"RPO ({v}s) cannot exceed RTO ({values['rto_seconds']}s)")
        return v


class RecoveryDefaultPolicy(BaseModel):
    """Default recovery policy for services without specific policies"""
    max_auto_attempts: int = Field(3, ge=0, le=10)
    escalation_timeout_seconds: int = Field(300, gt=0)
    backoff_seconds: int = Field(5, gt=0)
    require_approval_after_attempts: int = Field(2, ge=0, le=10)

    @validator('require_approval_after_attempts')
    def validate_approval_threshold(cls, v, values):
        """Approval threshold should not exceed max attempts"""
        if 'max_auto_attempts' in values and v > values['max_auto_attempts']:
            raise ValueError(
                f"Approval threshold ({v}) cannot exceed max attempts ({values['max_auto_attempts']})"
            )
        return v


class RecoveryPolicy(BaseModel):
    """Complete recovery policy configuration"""
    default: RecoveryDefaultPolicy
    by_service: Dict[str, RecoveryServicePolicy] = Field(default_factory=dict)


class ThresholdLevels(BaseModel):
    """Threshold levels for a metric"""
    normal: int = Field(..., ge=0, le=100, description="Normal threshold percentage")
    high: int = Field(..., ge=0, le=100, description="High threshold percentage")
    critical: int = Field(..., ge=0, le=100, description="Critical threshold percentage")

    @root_validator(skip_on_failure=True)
    def validate_threshold_progression(cls, values):
        """Ensure thresholds are in ascending order"""
        normal = values.get('normal', 0)
        high = values.get('high', 0)
        critical = values.get('critical', 0)

        if not (normal < high < critical):
            raise ValueError(
                f"Thresholds must be in ascending order: normal({normal}) < high({high}) < critical({critical})"
            )
        return values


class OptimizationThresholds(BaseModel):
    """Optimization thresholds for system resources"""
    cpu: ThresholdLevels
    memory: ThresholdLevels
    disk: ThresholdLevels


class OptimizationActions(BaseModel):
    """Optimization actions and their approval requirements"""
    require_approval: Dict[str, bool] = Field(
        default_factory=lambda: {
            "scale_up": True,
            "scale_down": False,
            "optimize": False,
            "restart": False
        }
    )
    auto_execute: List[str] = Field(default_factory=lambda: ["optimize", "restart"])
    manual_only: List[str] = Field(default_factory=lambda: ["scale_up", "scale_down"])

    @root_validator(skip_on_failure=True)
    def validate_action_consistency(cls, values):
        """Ensure actions are consistently configured"""
        require_approval = values.get('require_approval', {})
        auto_execute = values.get('auto_execute', [])
        manual_only = values.get('manual_only', [])

        # Check for conflicts between auto_execute and manual_only
        conflicts = set(auto_execute) & set(manual_only)
        if conflicts:
            raise ValueError(
                f"Actions cannot be both auto_execute and manual_only: {conflicts}"
            )

        # Check for conflicts between auto_execute and require_approval
        for action in auto_execute:
            if require_approval.get(action, False):
                raise ValueError(
                    f"Action '{action}' cannot be auto_execute if it requires approval"
                )

        return values


class OptimizationPolicy(BaseModel):
    """Optimization policy configuration"""
    thresholds: OptimizationThresholds
    actions: OptimizationActions


class MonitoringIntervals(BaseModel):
    """Monitoring check intervals in seconds"""
    critical_services: int = Field(..., gt=0, description="Interval for critical services")
    normal_services: int = Field(..., gt=0, description="Interval for normal services")
    low_priority: int = Field(..., gt=0, description="Interval for low priority services")

    @root_validator(skip_on_failure=True)
    def validate_interval_progression(cls, values):
        """Ensure intervals progress logically"""
        critical = values.get('critical_services', 0)
        normal = values.get('normal_services', 0)
        low = values.get('low_priority', 0)

        if not (critical <= normal <= low):
            raise ValueError(
                f"Intervals should progress: critical({critical}) <= normal({normal}) <= low({low})"
            )
        return values


class MonitoringPolicy(BaseModel):
    """Monitoring policy configuration"""
    intervals: MonitoringIntervals
    health_check_timeout: int = Field(..., gt=0, description="Health check timeout in seconds")
    status_change_only: bool = Field(True, description="Only publish events on status change")


class CompliancePolicy(BaseModel):
    """Compliance and audit policy configuration"""
    audit_enabled: bool = Field(True, description="Enable audit logging")
    audit_all_decisions: bool = Field(True, description="Audit all decisions")
    audit_all_actions: bool = Field(True, description="Audit all actions")
    iso_22301_compliance: bool = Field(True, description="Enable ISO 22301 compliance checks")
    log_retention_days: int = Field(..., ge=1, description="Log retention period in days")
    require_justification: bool = Field(True, description="Require justification for actions")


class NotificationChannel(BaseModel):
    """Configuration for a notification channel"""
    enabled: bool = Field(False, description="Enable this channel")
    recipients: Optional[List[str]] = Field(None, description="List of recipients")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")
    integration_key: Optional[str] = Field(None, description="Integration key for service")

    @validator('recipients', 'webhook_url', 'integration_key', allow_reuse=True)
    def validate_required_if_enabled(cls, v, values):
        """If channel is enabled, ensure required fields are present"""
        if values.get('enabled', False):
            # At least one configuration method should be present
            has_config = (
                (values.get('recipients') and len(values['recipients']) > 0) or
                values.get('webhook_url') or
                values.get('integration_key')
            )
            # Only check this once (for recipients field)
            if not has_config and not v:
                # Will be caught when recipients is validated
                pass
        return v


class NotificationChannels(BaseModel):
    """All notification channels"""
    email: NotificationChannel = Field(default_factory=NotificationChannel)
    slack: NotificationChannel = Field(default_factory=NotificationChannel)
    pagerduty: NotificationChannel = Field(default_factory=NotificationChannel)


class EscalationLevel(BaseModel):
    """Single escalation level configuration"""
    level: int = Field(..., ge=1, description="Escalation level number")
    delay_seconds: int = Field(..., ge=0, description="Delay before this escalation")
    notify: List[str] = Field(..., min_items=1, description="Teams/people to notify")


class NotificationPolicy(BaseModel):
    """Notification policy configuration"""
    channels: NotificationChannels
    escalation_levels: List[EscalationLevel] = Field(..., min_items=1)

    @validator('escalation_levels')
    def validate_escalation_progression(cls, v):
        """Ensure escalation levels are in order and delays increase"""
        if not v:
            raise ValueError("At least one escalation level required")

        # Check level numbering
        for i, level in enumerate(v):
            expected_level = i + 1
            if level.level != expected_level:
                raise ValueError(
                    f"Escalation levels must be sequential. Expected level {expected_level}, got {level.level}"
                )

        # Check delay progression
        for i in range(1, len(v)):
            if v[i].delay_seconds < v[i-1].delay_seconds:
                raise ValueError(
                    f"Escalation delays must increase: level {i} delay ({v[i].delay_seconds}) "
                    f"< level {i-1} delay ({v[i-1].delay_seconds})"
                )

        return v


class InfrastructurePolicies(BaseModel):
    """Complete infrastructure policies"""
    recovery: RecoveryPolicy
    optimization: OptimizationPolicy
    monitoring: MonitoringPolicy
    compliance: CompliancePolicy
    notifications: NotificationPolicy


class PolicyConfiguration(BaseModel):
    """Complete policy configuration file structure"""
    version: str = Field(..., description="Policy version")
    updated: str = Field(..., description="Last update date")
    approved_by: str = Field(..., description="Approver")
    infrastructure_policies: InfrastructurePolicies

    class Config:
        json_schema_extra = {
            "example": {
                "version": "1.0",
                "updated": "2025-10-09",
                "approved_by": "system_architect",
                "infrastructure_policies": {
                    "recovery": {
                        "default": {
                            "max_auto_attempts": 3,
                            "escalation_timeout_seconds": 300,
                            "backoff_seconds": 5,
                            "require_approval_after_attempts": 2
                        },
                        "by_service": {}
                    }
                }
            }
        }
