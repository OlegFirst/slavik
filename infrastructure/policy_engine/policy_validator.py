"""
Policy Validator - Validates Policy YAML Before Loading
========================================================

Comprehensive validation of policy configurations:
- Schema validation against Pydantic models
- Business rule validation
- Cross-field validation
- Service name validation
- Conflict detection

Ensures policies are valid before they're loaded into the engine.
"""

import yaml
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from .policy_models import (
    PolicyConfiguration,
    RecoveryStrategy,
    ServicePriority
)
from pydantic import ValidationError


class PolicyValidationError(Exception):
    """Raised when policy validation fails"""
    pass


class PolicyValidator:
    """
    Validates policy YAML files before loading

    Features:
    - Pydantic schema validation
    - Business rule validation
    - Service name validation against known services
    - Threshold consistency checks
    - Action conflict detection
    """

    # Known infrastructure services
    KNOWN_SERVICES = {
        "database", "eventbus", "api_gateway", "redis", "rag_pipeline",
        "monitoring", "notification_service", "mio_manager", "workflow_intelligence",
        "expertise_center", "living_docs", "simulation", "digital_twin",
        "bia_service", "compliance_service", "governance_service"
    }

    # Known teams for notifications
    KNOWN_TEAMS = {
        "ops", "ops_team", "dba", "platform", "ai_team", "on_call",
        "management", "security", "compliance"
    }

    def __init__(self, strict_service_validation: bool = False):
        """
        Initialize validator

        Args:
            strict_service_validation: If True, reject unknown service names
        """
        self.strict_service_validation = strict_service_validation
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []

    def validate_file(self, policy_file: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a policy YAML file

        Args:
            policy_file: Path to policy YAML file

        Returns:
            (is_valid, errors, warnings)
        """
        self.validation_errors = []
        self.validation_warnings = []

        try:
            # 1. Load YAML
            with open(policy_file, 'r') as f:
                policy_data = yaml.safe_load(f)

            # 2. Validate structure
            self._validate_structure(policy_data)

            # 3. Validate with Pydantic models
            self._validate_with_pydantic(policy_data)

            # 4. Validate business rules
            self._validate_business_rules(policy_data)

            # 5. Validate service names
            self._validate_service_names(policy_data)

            # 6. Validate notification teams
            self._validate_notification_teams(policy_data)

            # 7. Cross-field validation
            self._validate_cross_fields(policy_data)

        except FileNotFoundError:
            self.validation_errors.append(f"Policy file not found: {policy_file}")
        except yaml.YAMLError as e:
            self.validation_errors.append(f"YAML parsing error: {str(e)}")
        except Exception as e:
            self.validation_errors.append(f"Unexpected error during validation: {str(e)}")

        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors, self.validation_warnings

    def validate_dict(self, policy_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a policy dictionary (already loaded YAML)

        Args:
            policy_data: Policy configuration as dict

        Returns:
            (is_valid, errors, warnings)
        """
        self.validation_errors = []
        self.validation_warnings = []

        try:
            self._validate_structure(policy_data)
            self._validate_with_pydantic(policy_data)
            self._validate_business_rules(policy_data)
            self._validate_service_names(policy_data)
            self._validate_notification_teams(policy_data)
            self._validate_cross_fields(policy_data)
        except Exception as e:
            self.validation_errors.append(f"Validation error: {str(e)}")

        is_valid = len(self.validation_errors) == 0
        return is_valid, self.validation_errors, self.validation_warnings

    def _validate_structure(self, policy_data: Dict[str, Any]):
        """Validate basic structure"""
        required_top_level = ['version', 'updated', 'approved_by', 'infrastructure_policies']

        for field in required_top_level:
            if field not in policy_data:
                self.validation_errors.append(f"Missing required top-level field: {field}")

        if 'infrastructure_policies' in policy_data:
            infra = policy_data['infrastructure_policies']
            required_sections = ['recovery', 'optimization', 'monitoring', 'compliance', 'notifications']

            for section in required_sections:
                if section not in infra:
                    self.validation_errors.append(f"Missing required section: infrastructure_policies.{section}")

    def _validate_with_pydantic(self, policy_data: Dict[str, Any]):
        """Validate using Pydantic models"""
        try:
            PolicyConfiguration(**policy_data)
        except ValidationError as e:
            for error in e.errors():
                field_path = '.'.join(str(loc) for loc in error['loc'])
                self.validation_errors.append(
                    f"Validation error at {field_path}: {error['msg']}"
                )

    def _validate_business_rules(self, policy_data: Dict[str, Any]):
        """Validate business-specific rules"""
        if 'infrastructure_policies' not in policy_data:
            return

        infra = policy_data['infrastructure_policies']

        # Recovery policy validations
        if 'recovery' in infra:
            self._validate_recovery_policies(infra['recovery'])

        # Optimization policy validations
        if 'optimization' in infra:
            self._validate_optimization_policies(infra['optimization'])

        # Monitoring policy validations
        if 'monitoring' in infra:
            self._validate_monitoring_policies(infra['monitoring'])

        # Compliance policy validations
        if 'compliance' in infra:
            self._validate_compliance_policies(infra['compliance'])

    def _validate_recovery_policies(self, recovery: Dict[str, Any]):
        """Validate recovery policies"""
        # Check that critical services have appropriate RTOs
        if 'by_service' in recovery:
            for service_name, policy in recovery['by_service'].items():
                # Priority 1 services should have short RTOs
                if policy.get('priority') == 1:
                    rto = policy.get('rto_seconds', 0)
                    if rto > 300:  # 5 minutes
                        self.validation_warnings.append(
                            f"Priority 1 service '{service_name}' has RTO > 5 minutes ({rto}s)"
                        )

                # Validate recovery strategy exists
                strategy = policy.get('recovery_strategy')
                if strategy:
                    try:
                        RecoveryStrategy(strategy)
                    except ValueError:
                        self.validation_errors.append(
                            f"Invalid recovery strategy '{strategy}' for service '{service_name}'"
                        )

                # If escalate_immediately is true, should notify someone
                if policy.get('escalate_immediately') and not policy.get('notify_teams'):
                    self.validation_warnings.append(
                        f"Service '{service_name}' escalates immediately but has no notify_teams"
                    )

    def _validate_optimization_policies(self, optimization: Dict[str, Any]):
        """Validate optimization policies"""
        if 'thresholds' not in optimization:
            return

        thresholds = optimization['thresholds']

        # Check that all resource types have thresholds
        required_resources = ['cpu', 'memory', 'disk']
        for resource in required_resources:
            if resource not in thresholds:
                self.validation_errors.append(
                    f"Missing threshold configuration for resource: {resource}"
                )

        # Validate actions
        if 'actions' in optimization:
            actions = optimization['actions']

            # Check for common action types
            if 'require_approval' in actions:
                approval = actions['require_approval']
                if 'scale_up' in approval and not approval['scale_up']:
                    self.validation_warnings.append(
                        "scale_up does not require approval - this may be risky"
                    )

    def _validate_monitoring_policies(self, monitoring: Dict[str, Any]):
        """Validate monitoring policies"""
        if 'intervals' not in monitoring:
            return

        intervals = monitoring['intervals']

        # Check that critical services are monitored frequently enough
        critical_interval = intervals.get('critical_services', 0)
        if critical_interval > 60:  # More than 1 minute
            self.validation_warnings.append(
                f"Critical services monitoring interval is {critical_interval}s (>1 minute)"
            )

        # Check health check timeout is reasonable
        timeout = monitoring.get('health_check_timeout', 0)
        if timeout > critical_interval:
            self.validation_errors.append(
                f"Health check timeout ({timeout}s) exceeds critical monitoring interval ({critical_interval}s)"
            )

    def _validate_compliance_policies(self, compliance: Dict[str, Any]):
        """Validate compliance policies"""
        # Check log retention is adequate for compliance
        retention_days = compliance.get('log_retention_days', 0)
        if retention_days < 90:
            self.validation_warnings.append(
                f"Log retention ({retention_days} days) may not meet compliance requirements (recommended: 90+ days)"
            )

        # If ISO 22301 compliance is enabled, audit should be enabled
        if compliance.get('iso_22301_compliance') and not compliance.get('audit_enabled'):
            self.validation_errors.append(
                "ISO 22301 compliance requires audit_enabled=true"
            )

    def _validate_service_names(self, policy_data: Dict[str, Any]):
        """Validate service names against known services"""
        if 'infrastructure_policies' not in policy_data:
            return

        recovery = policy_data['infrastructure_policies'].get('recovery', {})
        by_service = recovery.get('by_service', {})

        for service_name in by_service.keys():
            if service_name not in self.KNOWN_SERVICES:
                message = f"Unknown service name: '{service_name}'"
                if self.strict_service_validation:
                    self.validation_errors.append(message)
                else:
                    self.validation_warnings.append(
                        f"{message} (known services: {', '.join(sorted(self.KNOWN_SERVICES))})"
                    )

    def _validate_notification_teams(self, policy_data: Dict[str, Any]):
        """Validate notification team names"""
        if 'infrastructure_policies' not in policy_data:
            return

        infra = policy_data['infrastructure_policies']

        # Check recovery notification teams
        recovery = infra.get('recovery', {})
        by_service = recovery.get('by_service', {})

        for service_name, policy in by_service.items():
            teams = policy.get('notify_teams', [])
            for team in teams:
                if team not in self.KNOWN_TEAMS:
                    self.validation_warnings.append(
                        f"Unknown team '{team}' in service '{service_name}' (known teams: {', '.join(sorted(self.KNOWN_TEAMS))})"
                    )

        # Check escalation notification teams
        notifications = infra.get('notifications', {})
        escalation_levels = notifications.get('escalation_levels', [])

        for level_config in escalation_levels:
            notify_list = level_config.get('notify', [])
            for team in notify_list:
                if team not in self.KNOWN_TEAMS:
                    self.validation_warnings.append(
                        f"Unknown team '{team}' in escalation level {level_config.get('level')}"
                    )

    def _validate_cross_fields(self, policy_data: Dict[str, Any]):
        """Validate relationships between different fields"""
        if 'infrastructure_policies' not in policy_data:
            return

        infra = policy_data['infrastructure_policies']

        # Check that escalation timeout aligns with monitoring intervals
        if 'recovery' in infra and 'monitoring' in infra:
            default_recovery = infra['recovery'].get('default', {})
            escalation_timeout = default_recovery.get('escalation_timeout_seconds', 0)

            monitoring_intervals = infra['monitoring'].get('intervals', {})
            critical_interval = monitoring_intervals.get('critical_services', 0)

            if escalation_timeout < critical_interval * 2:
                self.validation_warnings.append(
                    f"Escalation timeout ({escalation_timeout}s) is less than 2x critical monitoring interval "
                    f"({critical_interval}s) - may cause premature escalations"
                )

        # Check that notification channels are properly configured
        if 'notifications' in infra:
            channels = infra['notifications'].get('channels', {})

            # Check if any channel is enabled
            has_enabled_channel = False
            for channel_name, channel_config in channels.items():
                if channel_config.get('enabled'):
                    has_enabled_channel = True
                    break

            if not has_enabled_channel:
                self.validation_warnings.append(
                    "No notification channels are enabled - notifications will not be sent"
                )


def validate_policy_file(
    policy_file: Path,
    strict: bool = False
) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate a policy file

    Args:
        policy_file: Path to policy YAML file
        strict: If True, use strict service validation

    Returns:
        (is_valid, errors, warnings)
    """
    validator = PolicyValidator(strict_service_validation=strict)
    return validator.validate_file(policy_file)


def validate_policy_dict(
    policy_data: Dict[str, Any],
    strict: bool = False
) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate a policy dictionary

    Args:
        policy_data: Policy configuration as dict
        strict: If True, use strict service validation

    Returns:
        (is_valid, errors, warnings)
    """
    validator = PolicyValidator(strict_service_validation=strict)
    return validator.validate_dict(policy_data)
