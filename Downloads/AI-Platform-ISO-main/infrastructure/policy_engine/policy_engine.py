"""
Policy Engine - Central Policy Management for Infrastructure
=============================================================

The Policy Engine is the central authority for all infrastructure policies.
It loads policies from YAML files, validates them, and provides a clean API
for other components to query policies.

Features:
- Load policies from YAML files
- Hot reload without service restart
- Type-safe policy access via Pydantic models
- Default policies for services without specific configs
- Compliance checking
- Threshold lookup
- Service priority management
- Policy versioning support

Usage:
    engine = PolicyEngine("/path/to/policies.yaml")

    # Get recovery policy for a service
    policy = engine.get_recovery_policy("database")

    # Get optimization threshold
    cpu_critical = engine.get_threshold("cpu", "critical")

    # Check if action requires approval
    needs_approval = engine.check_compliance("scale_up", "database")

    # Hot reload policies
    engine.reload_policies()
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime
import logging
from threading import RLock

from .policy_models import (
    PolicyConfiguration,
    RecoveryServicePolicy,
    RecoveryDefaultPolicy,
    RecoveryStrategy,
    ThresholdLevels,
    OptimizationActions,
    MonitoringIntervals,
    NotificationChannels,
    EscalationLevel
)
from .policy_validator import PolicyValidator, PolicyValidationError


logger = logging.getLogger(__name__)


class PolicyLoadError(Exception):
    """Raised when policy loading fails"""
    pass


class PolicyEngine:
    """
    Central Policy Engine for Infrastructure Governance

    Provides thread-safe access to all infrastructure policies.
    Supports hot reloading and validation.
    """

    def __init__(self, policy_file: Optional[Path] = None, auto_reload: bool = False):
        """
        Initialize Policy Engine

        Args:
            policy_file: Path to policies.yaml file (optional, can load later)
            auto_reload: Enable automatic reload on file change (not implemented yet)
        """
        self.policy_file = policy_file
        self.auto_reload = auto_reload
        self._lock = RLock()

        # Policy storage
        self._config: Optional[PolicyConfiguration] = None
        self._loaded_at: Optional[datetime] = None
        self._version: Optional[str] = None

        # Validator
        self.validator = PolicyValidator(strict_service_validation=False)

        # Load policies if file provided
        if policy_file:
            self.load_policies(policy_file)

    def load_policies(self, policy_file: Optional[Path] = None) -> bool:
        """
        Load policies from YAML file

        Args:
            policy_file: Path to policies.yaml (uses self.policy_file if not provided)

        Returns:
            True if loaded successfully

        Raises:
            PolicyLoadError: If loading or validation fails
        """
        with self._lock:
            # Use provided file or stored file
            file_to_load = policy_file or self.policy_file

            if not file_to_load:
                raise PolicyLoadError("No policy file specified")

            file_to_load = Path(file_to_load)

            if not file_to_load.exists():
                raise PolicyLoadError(f"Policy file not found: {file_to_load}")

            logger.info(f"Loading policies from {file_to_load}")

            try:
                # Validate first
                is_valid, errors, warnings = self.validator.validate_file(file_to_load)

                # Log warnings
                for warning in warnings:
                    logger.warning(f"Policy validation warning: {warning}")

                # Fail on errors
                if not is_valid:
                    error_msg = "\n".join(errors)
                    raise PolicyValidationError(f"Policy validation failed:\n{error_msg}")

                # Load YAML
                with open(file_to_load, 'r') as f:
                    policy_data = yaml.safe_load(f)

                # Parse into Pydantic model
                self._config = PolicyConfiguration(**policy_data)
                self._loaded_at = datetime.utcnow()
                self._version = self._config.version
                self.policy_file = file_to_load

                logger.info(
                    f"Policies loaded successfully: version={self._version}, "
                    f"updated={self._config.updated}, approved_by={self._config.approved_by}"
                )

                return True

            except yaml.YAMLError as e:
                raise PolicyLoadError(f"YAML parsing error: {str(e)}")
            except Exception as e:
                raise PolicyLoadError(f"Failed to load policies: {str(e)}")

    def reload_policies(self) -> bool:
        """
        Hot reload policies from the same file

        Returns:
            True if reloaded successfully
        """
        logger.info("Reloading policies...")
        try:
            old_version = self._version
            self.load_policies()
            new_version = self._version

            if old_version != new_version:
                logger.info(f"Policies updated: {old_version} -> {new_version}")
            else:
                logger.info("Policies reloaded (same version)")

            return True
        except Exception as e:
            logger.error(f"Failed to reload policies: {str(e)}")
            return False

    def get_recovery_policy(self, service_name: str) -> RecoveryServicePolicy:
        """
        Get recovery policy for a specific service

        Args:
            service_name: Name of the service

        Returns:
            RecoveryServicePolicy for the service (or default if not found)
        """
        with self._lock:
            self._ensure_loaded()

            # Check if service has specific policy
            service_policies = self._config.infrastructure_policies.recovery.by_service

            if service_name in service_policies:
                return service_policies[service_name]

            # Return default policy converted to service policy
            default = self._config.infrastructure_policies.recovery.default
            return self._default_to_service_policy(default)

    def get_default_recovery_policy(self) -> RecoveryDefaultPolicy:
        """Get default recovery policy"""
        with self._lock:
            self._ensure_loaded()
            return self._config.infrastructure_policies.recovery.default

    def get_threshold(
        self,
        resource_type: Literal["cpu", "memory", "disk"],
        level: Literal["normal", "high", "critical"]
    ) -> int:
        """
        Get optimization threshold for a resource

        Args:
            resource_type: Type of resource (cpu, memory, disk)
            level: Threshold level (normal, high, critical)

        Returns:
            Threshold percentage (0-100)
        """
        with self._lock:
            self._ensure_loaded()

            thresholds = self._config.infrastructure_policies.optimization.thresholds
            resource_thresholds: ThresholdLevels = getattr(thresholds, resource_type)

            return getattr(resource_thresholds, level)

    def get_all_thresholds(self, resource_type: Literal["cpu", "memory", "disk"]) -> ThresholdLevels:
        """
        Get all threshold levels for a resource

        Args:
            resource_type: Type of resource

        Returns:
            ThresholdLevels object
        """
        with self._lock:
            self._ensure_loaded()

            thresholds = self._config.infrastructure_policies.optimization.thresholds
            return getattr(thresholds, resource_type)

    def check_compliance(self, action: str, service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if an action complies with policies

        Args:
            action: Action to check (e.g., "scale_up", "restart")
            service_name: Service name (for service-specific checks)

        Returns:
            Dict with compliance info:
            {
                "allowed": bool,
                "requires_approval": bool,
                "auto_execute": bool,
                "manual_only": bool,
                "reason": str
            }
        """
        with self._lock:
            self._ensure_loaded()

            actions: OptimizationActions = self._config.infrastructure_policies.optimization.actions

            # Check action status
            requires_approval = actions.require_approval.get(action, True)  # Default to requiring approval
            auto_execute = action in actions.auto_execute
            manual_only = action in actions.manual_only

            # Determine if allowed
            allowed = not manual_only or requires_approval

            # Build reason
            if manual_only:
                reason = f"Action '{action}' requires manual execution"
            elif auto_execute:
                reason = f"Action '{action}' can be auto-executed"
            elif requires_approval:
                reason = f"Action '{action}' requires approval before execution"
            else:
                reason = f"Action '{action}' can proceed without approval"

            return {
                "allowed": allowed,
                "requires_approval": requires_approval,
                "auto_execute": auto_execute,
                "manual_only": manual_only,
                "reason": reason
            }

    def get_service_priority(self, service_name: str) -> int:
        """
        Get priority for a service (1=highest, 5=lowest)

        Args:
            service_name: Name of the service

        Returns:
            Priority level (1-5)
        """
        policy = self.get_recovery_policy(service_name)
        return policy.priority

    def get_monitoring_interval(self, service_priority: int) -> int:
        """
        Get monitoring interval for a service based on its priority

        Args:
            service_priority: Service priority (1-5)

        Returns:
            Monitoring interval in seconds
        """
        with self._lock:
            self._ensure_loaded()

            intervals: MonitoringIntervals = self._config.infrastructure_policies.monitoring.intervals

            # Map priority to interval
            if service_priority == 1:
                return intervals.critical_services
            elif service_priority in [2, 3]:
                return intervals.normal_services
            else:
                return intervals.low_priority

    def get_escalation_levels(self) -> List[EscalationLevel]:
        """Get all escalation levels"""
        with self._lock:
            self._ensure_loaded()
            return self._config.infrastructure_policies.notifications.escalation_levels

    def get_notification_channels(self) -> NotificationChannels:
        """Get all notification channel configurations"""
        with self._lock:
            self._ensure_loaded()
            return self._config.infrastructure_policies.notifications.channels

    def should_audit(self, action_type: Literal["decision", "action"]) -> bool:
        """
        Check if an action should be audited

        Args:
            action_type: Type of action ("decision" or "action")

        Returns:
            True if should be audited
        """
        with self._lock:
            self._ensure_loaded()

            compliance = self._config.infrastructure_policies.compliance

            if not compliance.audit_enabled:
                return False

            if action_type == "decision":
                return compliance.audit_all_decisions
            elif action_type == "action":
                return compliance.audit_all_actions

            return False

    def requires_justification(self) -> bool:
        """Check if actions require justification"""
        with self._lock:
            self._ensure_loaded()
            return self._config.infrastructure_policies.compliance.require_justification

    @property
    def loaded_at(self) -> Optional[datetime]:
        """Get timestamp when policies were loaded"""
        return self._loaded_at

    @property
    def version(self) -> Optional[str]:
        """Get current policy version"""
        return self._version

    @property
    def policies(self) -> Optional[Dict[str, Any]]:
        """Get raw policies dict"""
        if not self._config:
            return None
        return {
            'recovery': self._config.infrastructure_policies.recovery.dict(),
            'optimization': self._config.infrastructure_policies.optimization.dict(),
            'monitoring': self._config.infrastructure_policies.monitoring.dict(),
            'compliance': self._config.infrastructure_policies.compliance.dict(),
            'notifications': self._config.infrastructure_policies.notifications.dict()
        }

    def get_policy_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about loaded policies

        Returns:
            Dict with version, loaded_at, updated, approved_by
        """
        with self._lock:
            if not self._config:
                return {
                    "loaded": False,
                    "message": "No policies loaded"
                }

            return {
                "loaded": True,
                "version": self._version,
                "loaded_at": self._loaded_at.isoformat() if self._loaded_at else None,
                "updated": self._config.updated,
                "approved_by": self._config.approved_by,
                "policy_file": str(self.policy_file) if self.policy_file else None
            }

    def validate_action_context(
        self,
        action: str,
        service_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate an action against policies

        Args:
            action: Action to validate
            service_name: Service the action applies to
            context: Additional context (metrics, state, etc.)

        Returns:
            Validation result with allowed, violations, recommendations
        """
        with self._lock:
            self._ensure_loaded()

            violations = []
            recommendations = []

            # Get service policy
            service_policy = self.get_recovery_policy(service_name)

            # Get compliance check
            compliance = self.check_compliance(action, service_name)

            # Check if action is allowed
            if not compliance["allowed"]:
                violations.append(compliance["reason"])

            # Check if requires approval
            if compliance["requires_approval"]:
                recommendations.append("This action requires approval before execution")

            # Check against recovery policy
            if action in ["restart", "failover"]:
                # Check max attempts
                current_attempts = context.get("attempts", 0)
                if current_attempts >= service_policy.max_auto_attempts:
                    violations.append(
                        f"Maximum auto-recovery attempts reached: {current_attempts}/{service_policy.max_auto_attempts}"
                    )

            # Check threshold violations for optimization actions
            if action in ["scale_up", "scale_down", "optimize"]:
                metrics = context.get("metrics", {})

                for resource in ["cpu", "memory", "disk"]:
                    if resource in metrics:
                        value = metrics[resource]
                        thresholds = self.get_all_thresholds(resource)

                        if value >= thresholds.critical:
                            recommendations.append(
                                f"{resource.upper()} at critical level: {value}% (threshold: {thresholds.critical}%)"
                            )

            return {
                "allowed": len(violations) == 0,
                "violations": violations,
                "recommendations": recommendations,
                "requires_approval": compliance["requires_approval"],
                "service_priority": service_policy.priority,
                "recovery_strategy": service_policy.recovery_strategy.value
            }

    def get_optimization_policy(self, service_name: str) -> Dict[str, Any]:
        """
        Get optimization policy for a service

        Args:
            service_name: Name of the service

        Returns:
            Dict with optimization policy settings
        """
        with self._lock:
            self._ensure_loaded()

            # Get optimization settings from policies
            opt_policy = self._config.infrastructure_policies.optimization

            # Check if service has specific optimization settings
            # For now, return general optimization policy
            # In future, can add service-specific overrides

            return {
                "allow_optimization": True,  # Default: allow optimization
                "auto_scale_enabled": opt_policy.actions.auto_scale_enabled if hasattr(opt_policy.actions, 'auto_scale_enabled') else False,
                "require_approval_for_scale": opt_policy.actions.require_approval_for_scale if hasattr(opt_policy.actions, 'require_approval_for_scale') else True,
                "thresholds": {
                    "cpu": opt_policy.thresholds.cpu.dict(),
                    "memory": opt_policy.thresholds.memory.dict(),
                    "disk": opt_policy.thresholds.disk.dict()
                },
                "services": {}  # Placeholder for service-specific overrides
            }

    def get_approval_policy(self, action_type: str) -> Dict[str, Any]:
        """
        Get approval policy for a specific action type

        Args:
            action_type: Type of action (scale_up, scale_down, etc.)

        Returns:
            Dict with approval requirements
        """
        with self._lock:
            self._ensure_loaded()

            opt_actions = self._config.infrastructure_policies.optimization.actions

            # Check if action requires approval
            require_approval_map = {
                "scale_up": opt_actions.require_approval.get("scale_up", True) if hasattr(opt_actions, 'require_approval') else True,
                "scale_down": opt_actions.require_approval.get("scale_down", False) if hasattr(opt_actions, 'require_approval') else False,
                "optimize": opt_actions.require_approval.get("optimize", False) if hasattr(opt_actions, 'require_approval') else False,
                "restart": opt_actions.require_approval.get("restart", False) if hasattr(opt_actions, 'require_approval') else False,
                "failover": opt_actions.require_approval.get("failover", True) if hasattr(opt_actions, 'require_approval') else True,
                "rollback": opt_actions.require_approval.get("rollback", True) if hasattr(opt_actions, 'require_approval') else True,
            }

            requires_approval = require_approval_map.get(action_type, True)  # Default: require approval

            return {
                "requires_approval": requires_approval,
                "allowed_approvers": ["ops_team", "platform_admin"],  # Default approvers
                "expires_in": 3600,  # 1 hour expiration
                "min_approvers": 1
            }

    def get_escalation_policy(self, severity: str) -> Dict[str, Any]:
        """
        Get escalation policy for a severity level

        Args:
            severity: Severity level (low, medium, high, critical)

        Returns:
            Dict with escalation settings
        """
        with self._lock:
            self._ensure_loaded()

            # Get escalation levels
            escalation_levels = self._config.infrastructure_policies.notifications.escalation_levels

            # Find matching level by severity or default to first level
            for level in escalation_levels:
                # Match by delay - higher delay = lower severity
                if severity == "critical" and level.delay_seconds == 0:
                    return {
                        "level": level.level,
                        "delay_seconds": level.delay_seconds,
                        "teams": level.notify,
                        "channels": ["email", "slack"]  # Critical gets all channels
                    }
                elif severity == "high" and level.delay_seconds <= 300:
                    return {
                        "level": level.level,
                        "delay_seconds": level.delay_seconds,
                        "teams": level.notify,
                        "channels": ["email", "slack"]
                    }
                elif severity == "medium" and 300 < level.delay_seconds <= 900:
                    return {
                        "level": level.level,
                        "delay_seconds": level.delay_seconds,
                        "teams": level.notify,
                        "channels": ["email"]
                    }

            # Default escalation policy
            return {
                "level": 1,
                "delay_seconds": 0,
                "teams": ["ops_team"],
                "channels": ["email"]
            }

    def get_thresholds(self) -> Dict[str, Any]:
        """
        Get all resource thresholds

        Returns:
            Dict with thresholds for all resources
        """
        with self._lock:
            self._ensure_loaded()

            thresholds = self._config.infrastructure_policies.optimization.thresholds

            return {
                "cpu": thresholds.cpu.dict(),
                "memory": thresholds.memory.dict(),
                "disk": thresholds.disk.dict()
            }

    def is_business_hours(self) -> bool:
        """
        Check if current time is within business hours

        Returns:
            True if within business hours, False otherwise
        """
        from datetime import datetime, time

        # Get current time
        now = datetime.utcnow()
        current_time = now.time()
        current_day = now.strftime("%A").lower()  # monday, tuesday, etc.

        with self._lock:
            self._ensure_loaded()

            # Get business hours from optimization schedule if available
            opt_policy = self._config.infrastructure_policies.optimization

            # Check if schedule exists and has business_hours
            if hasattr(opt_policy, 'schedule') and hasattr(opt_policy.schedule, 'business_hours'):
                business_hours = opt_policy.schedule.business_hours

                # Parse start and end times
                try:
                    start = datetime.strptime(business_hours.start, "%H:%M").time()
                    end = datetime.strptime(business_hours.end, "%H:%M").time()

                    # Check if current time is within business hours
                    return start <= current_time <= end
                except (AttributeError, ValueError):
                    pass

            # Default business hours: 9 AM to 6 PM UTC, Monday-Friday
            default_start = time(9, 0)
            default_end = time(18, 0)
            business_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]

            is_business_day = current_day in business_days
            is_business_time = default_start <= current_time <= default_end

            return is_business_day and is_business_time

    def check_policy_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if an action complies with policies

        Args:
            context: Context dict with service_name, action_type, etc.

        Returns:
            Dict with compliance result
        """
        with self._lock:
            self._ensure_loaded()

            service_name = context.get("service_name", "unknown")
            action_type = context.get("action_type", "unknown")
            current_attempt = context.get("current_attempt", 1)
            is_business_hours = context.get("is_business_hours", self.is_business_hours())

            # Get service policy
            try:
                service_policy = self.get_recovery_policy(service_name)
            except Exception:
                # Service not found, use default
                return {
                    "compliant": True,
                    "reason": f"No specific policy for {service_name}, using defaults",
                    "requires_approval": False,
                    "requires_escalation": False,
                    "policy_reference": "default"
                }

            # Check if attempts exceeded
            if current_attempt > service_policy.max_auto_attempts:
                return {
                    "compliant": False,
                    "reason": f"Max attempts exceeded: {current_attempt}/{service_policy.max_auto_attempts}",
                    "requires_approval": True,
                    "requires_escalation": True,
                    "policy_reference": f"recovery/{service_name}/max_attempts"
                }

            # Check if requires immediate escalation
            if service_policy.escalate_immediately and current_attempt >= 1:
                return {
                    "compliant": True,  # Allow action but escalate
                    "reason": f"Critical service {service_name} requires escalation",
                    "requires_approval": service_policy.require_approval,
                    "requires_escalation": True,
                    "policy_reference": f"recovery/{service_name}/escalate_immediately"
                }

            # Check if requires approval
            if service_policy.require_approval:
                return {
                    "compliant": True,  # Compliant but needs approval
                    "reason": f"Action {action_type} on {service_name} requires approval",
                    "requires_approval": True,
                    "requires_escalation": False,
                    "policy_reference": f"recovery/{service_name}/require_approval"
                }

            # All checks passed
            return {
                "compliant": True,
                "reason": f"Action {action_type} on {service_name} is compliant",
                "requires_approval": False,
                "requires_escalation": False,
                "policy_reference": f"recovery/{service_name}"
            }

    def _ensure_loaded(self):
        """Ensure policies are loaded"""
        if self._config is None:
            raise PolicyLoadError("No policies loaded. Call load_policies() first.")

    def _default_to_service_policy(self, default: RecoveryDefaultPolicy) -> RecoveryServicePolicy:
        """Convert default policy to service policy"""
        return RecoveryServicePolicy(
            priority=3,  # Medium priority
            rto_seconds=300,  # 5 minutes
            max_auto_attempts=default.max_auto_attempts,
            escalate_immediately=False,
            recovery_strategy=RecoveryStrategy.RESTART,
            notify_teams=["ops"],
            require_approval=False
        )


# Global policy engine instance
_global_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """
    Get global policy engine instance

    Returns:
        Global PolicyEngine instance

    Raises:
        PolicyLoadError: If engine not initialized
    """
    global _global_engine

    if _global_engine is None:
        raise PolicyLoadError(
            "Policy engine not initialized. "
            "Call initialize_policy_engine() first."
        )

    return _global_engine


def initialize_policy_engine(policy_file: Path) -> PolicyEngine:
    """
    Initialize global policy engine

    Args:
        policy_file: Path to policies.yaml

    Returns:
        Initialized PolicyEngine instance
    """
    global _global_engine

    logger.info(f"Initializing global policy engine with {policy_file}")
    _global_engine = PolicyEngine(policy_file)

    return _global_engine


def reload_global_policies() -> bool:
    """
    Reload global policies

    Returns:
        True if reloaded successfully
    """
    engine = get_policy_engine()
    return engine.reload_policies()
