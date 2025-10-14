"""
Decision Center - Infrastructure Governance Layer
=================================================

Phase 1.1: Minimal Governance Layer for Infrastructure Coordination

This module provides the central policy engine for infrastructure governance.
Instead of hardcoding thresholds and rules in Python, all policies are defined
in YAML files and loaded dynamically.

Key Components:
--------------
1. PolicyEngine - Central policy management and query interface
2. PolicyValidator - Validates policies before loading
3. Policy Models - Pydantic models for type safety
4. YAML Configuration - Human-readable policy files
5. EscalationManager - Manages escalations when auto-recovery fails
6. NotificationService - Multi-channel notifications

Usage Example:
-------------
```python
from infrastructure.policy_engine import (
    initialize_policy_engine,
    get_policy_engine
)

# Initialize at startup
engine = initialize_policy_engine("policies.yaml")

# Query policies anywhere in your code
policy = engine.get_recovery_policy("database")
print(f"Database RTO: {policy.rto_seconds}s")

# Get thresholds
cpu_critical = engine.get_threshold("cpu", "critical")

# Check compliance
compliance = engine.check_compliance("scale_up", "api_gateway")
if compliance["requires_approval"]:
    print("This action requires approval")

# Hot reload without restart
engine.reload_policies()
```

Migration from Hardcoded Values:
-------------------------------
Before:
```python
MAX_RETRY_ATTEMPTS = 3  # Hardcoded
DATABASE_RTO = 120      # Hardcoded
CPU_THRESHOLD = 80      # Hardcoded
```

After:
```python
engine = get_policy_engine()
max_attempts = engine.get_recovery_policy(service).max_auto_attempts
rto = engine.get_recovery_policy("database").rto_seconds
cpu_threshold = engine.get_threshold("cpu", "critical")
```
"""

from pathlib import Path

# Core policy engine
from infrastructure.policy_engine.policy_engine import (
    PolicyEngine,
    PolicyLoadError,
    get_policy_engine,
    initialize_policy_engine,
    reload_global_policies
)

# Validator
from infrastructure.policy_engine.policy_validator import (
    PolicyValidator,
    PolicyValidationError,
    validate_policy_file,
    validate_policy_dict
)

# Models
from infrastructure.policy_engine.policy_models import (
    # Main configuration
    PolicyConfiguration,
    InfrastructurePolicies,

    # Recovery policies
    RecoveryPolicy,
    RecoveryServicePolicy,
    RecoveryDefaultPolicy,
    RecoveryStrategy,
    ServicePriority,

    # Optimization policies
    OptimizationPolicy,
    OptimizationThresholds,
    OptimizationActions,
    ThresholdLevels,

    # Monitoring policies
    MonitoringPolicy,
    MonitoringIntervals,

    # Compliance policies
    CompliancePolicy,

    # Notification policies
    NotificationPolicy,
    NotificationChannels,
    NotificationChannel,
    EscalationLevel
)

# Existing components (if available)
try:
    from infrastructure.policy_engine.escalation_manager import (
        EscalationManager,
        EscalationPolicy,
        EscalationReason,
        EscalationStatus,
        Escalation
    )
    _has_escalation = True
except ImportError:
    _has_escalation = False

try:
    from infrastructure.policy_engine.notification_service import (
        NotificationService,
        NotificationConfig,
        NotificationPriority,
        NotificationChannel as NotificationChannelEnum,
        Notification
    )
    _has_notification = True
except ImportError:
    _has_notification = False

# Phase 1.1 additions
try:
    from infrastructure.policy_engine.decision_center import InfrastructureDecisionCenter
    from infrastructure.policy_engine.audit_logger import AuditLogger
    from infrastructure.policy_engine.decision_models import (
        Decision,
        DecisionType,
        DecisionOutcome,
        EscalationRequest as DecisionEscalationRequest,
        EscalationStatus as DecisionEscalationStatus,
        ApprovalRequest,
        ApprovalStatus,
        DecisionAuditLog,
        PolicyRule
    )
    _has_decision_center = True
except ImportError:
    _has_decision_center = False

# Phase 2 additions - Wishlist Integration
# DISABLED: Has errors with ResourceCost, not critical for Phase 1
_has_wishlist = False

__all__ = [
    # Policy Engine
    "PolicyEngine",
    "PolicyLoadError",
    "get_policy_engine",
    "initialize_policy_engine",
    "reload_global_policies",

    # Validator
    "PolicyValidator",
    "PolicyValidationError",
    "validate_policy_file",
    "validate_policy_dict",

    # Models - Main
    "PolicyConfiguration",
    "InfrastructurePolicies",

    # Models - Recovery
    "RecoveryPolicy",
    "RecoveryServicePolicy",
    "RecoveryDefaultPolicy",
    "RecoveryStrategy",
    "ServicePriority",

    # Models - Optimization
    "OptimizationPolicy",
    "OptimizationThresholds",
    "OptimizationActions",
    "ThresholdLevels",

    # Models - Monitoring
    "MonitoringPolicy",
    "MonitoringIntervals",

    # Models - Compliance
    "CompliancePolicy",

    # Models - Notifications
    "NotificationPolicy",
    "NotificationChannels",
    "NotificationChannel",
    "EscalationLevel",
]

# Add existing components if available
if _has_escalation:
    __all__.extend([
        'EscalationManager',
        'EscalationPolicy',
        'EscalationReason',
        'EscalationStatus',
        'Escalation',
    ])

if _has_notification:
    __all__.extend([
        'NotificationService',
        'NotificationConfig',
        'NotificationPriority',
        'NotificationChannelEnum',
        'Notification'
    ])

if _has_decision_center:
    __all__.extend([
        'InfrastructureDecisionCenter',
        'AuditLogger',
        'Decision',
        'DecisionType',
        'DecisionOutcome',
        'DecisionEscalationRequest',
        'DecisionEscalationStatus',
        'ApprovalRequest',
        'ApprovalStatus',
        'DecisionAuditLog',
        'PolicyRule'
    ])

if _has_wishlist:
    __all__.extend([
        'WishlistDecisionIntegration',
        'Wish',
        'WishStatus',
        'WishNeedType'
    ])

# Version
__version__ = "1.1.0"


def get_default_policy_path() -> Path:
    """
    Get the default path to policies.yaml

    Returns:
        Path to policies.yaml in this directory
    """
    return Path(__file__).parent / "policies.yaml"


def create_default_engine() -> PolicyEngine:
    """
    Create a PolicyEngine with the default policies.yaml

    Returns:
        Initialized PolicyEngine

    Raises:
        PolicyLoadError: If policies.yaml not found or invalid
    """
    policy_file = get_default_policy_path()
    return PolicyEngine(policy_file)
