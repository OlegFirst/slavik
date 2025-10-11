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
