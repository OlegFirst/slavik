"""
Policy Engine - Loads and validates governance policies
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class PolicyEngine:
    """
    Управляет policies из YAML файла
    - Загрузка policies.yaml
    - Валидация структуры
    - Hot reload при изменении файла
    - Получение policies для конкретного сервиса
    """

    def __init__(self, policy_file: str = "policies.yaml"):
        """
        Initialize Policy Engine

        Args:
            policy_file: Path to policies.yaml (relative or absolute)
        """
        # Resolve path relative to decision_center directory
        if not Path(policy_file).is_absolute():
            base_dir = Path(__file__).parent.parent
            self.policy_file = base_dir / policy_file
        else:
            self.policy_file = Path(policy_file)

        self.policies: Optional[Dict[str, Any]] = None
        self.last_loaded: Optional[datetime] = None
        self.load_policies()

    def load_policies(self) -> None:
        """
        Загружает policies из YAML файла

        Raises:
            FileNotFoundError: If policy file doesn't exist
            yaml.YAMLError: If YAML is invalid
            ValueError: If policy structure is invalid
        """
        try:
            if not self.policy_file.exists():
                raise FileNotFoundError(f"Policy file not found: {self.policy_file}")

            with open(self.policy_file, 'r') as f:
                self.policies = yaml.safe_load(f)

            self.last_loaded = datetime.utcnow()
            self.validate_policies()

            logger.info(
                f"Policies loaded successfully from {self.policy_file} "
                f"(version: {self.policies.get('version', 'unknown')})"
            )

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise

        except Exception as e:
            logger.error(f"Failed to load policies: {e}")
            raise

    def validate_policies(self) -> None:
        """
        Валидирует структуру policies

        Raises:
            ValueError: If required sections are missing
        """
        required_sections = [
            "recovery",
            "escalation",
            "goals",
            "decision_rules"
        ]

        for section in required_sections:
            if section not in self.policies:
                raise ValueError(
                    f"Missing required policy section: {section}. "
                    f"Please check your policies.yaml file."
                )

        # Validate recovery policies
        recovery = self.policies.get("recovery", {})
        if "default" not in recovery:
            raise ValueError("Missing 'default' recovery policy")

        # Validate escalation policies
        escalation = self.policies.get("escalation", {})
        if "pattern_detection" not in escalation:
            raise ValueError("Missing 'pattern_detection' in escalation policies")

        logger.debug("Policy validation passed")

    def get_policies(self, service: str) -> Dict[str, Any]:
        """
        Возвращает policies для конкретного сервиса

        Args:
            service: Service name (e.g., "database", "redis", "eventbus")

        Returns:
            Dict containing merged policies (default + service-specific)
        """
        # Check if hot reload needed
        if self._should_reload():
            logger.info("Policy file changed, reloading...")
            self.load_policies()

        recovery_policies = self.policies.get("recovery", {})
        default_policies = recovery_policies.get("default", {})

        # Look for service in critical_services
        critical = recovery_policies.get("critical_services", {})
        if service in critical:
            return {**default_policies, **critical[service]}

        # Look for service in standard_services
        standard = recovery_policies.get("standard_services", {})
        if service in standard:
            return {**default_policies, **standard[service]}

        # Return default policies
        logger.debug(f"No specific policies for '{service}', using defaults")
        return default_policies

    def get_all_policies(self) -> Dict[str, Any]:
        """
        Возвращает все policies

        Returns:
            Complete policies dictionary
        """
        if self._should_reload():
            self.load_policies()

        return self.policies.copy()

    def get_goal(self, goal_name: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает цель из policies

        Args:
            goal_name: Name of goal (e.g., "availability", "mttr")

        Returns:
            Goal configuration or None if not found
        """
        goals = self.policies.get("goals", {}).get("infrastructure", {})
        return goals.get(goal_name)

    def get_threshold(self, resource: str, level: str) -> int:
        """
        Возвращает threshold для ресурса

        Args:
            resource: Resource type (cpu, memory, disk, network)
            level: Threshold level (high, critical, low)

        Returns:
            Threshold percentage (default 80%)
        """
        thresholds = (
            self.policies
            .get("optimization", {})
            .get("thresholds", {})
        )
        resource_thresholds = thresholds.get(resource, {})
        return resource_thresholds.get(level, 80)  # default 80%

    def get_decision_rule(self, rule_name: str) -> Optional[str]:
        """
        Возвращает decision rule

        Args:
            rule_name: Rule name (e.g., "availability_vs_cost")

        Returns:
            Rule value or None
        """
        rules = (
            self.policies
            .get("decision_rules", {})
            .get("conflict_resolution", {})
        )
        return rules.get(rule_name)

    def is_auto_approval_allowed(self, action: str) -> bool:
        """
        Проверяет разрешен ли auto-approval для действия

        Args:
            action: Action name (e.g., "restart", "scale_up")

        Returns:
            True if auto-approval allowed
        """
        auto_approval = (
            self.policies
            .get("decision_rules", {})
            .get("auto_approval", {})
        )

        action_key = f"{action}_allowed"
        return auto_approval.get(action_key, False)

    def _should_reload(self) -> bool:
        """
        Проверяет нужно ли перезагрузить policies (hot reload)

        Returns:
            True if file was modified since last load
        """
        if not self.last_loaded:
            return True

        if not self.policy_file.exists():
            logger.warning(f"Policy file disappeared: {self.policy_file}")
            return False

        file_mtime = datetime.fromtimestamp(
            self.policy_file.stat().st_mtime
        )

        return file_mtime > self.last_loaded

    def reload(self) -> None:
        """
        Принудительная перезагрузка policies

        Useful for testing or manual refresh
        """
        logger.info("Manual policy reload requested")
        self.load_policies()

    def get_version(self) -> str:
        """
        Возвращает версию policies

        Returns:
            Version string (e.g., "1.0.0")
        """
        return self.policies.get("version", "unknown")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Возвращает metadata policies

        Returns:
            Dict with version, approved_by, effective_date, etc.
        """
        return {
            "version": self.policies.get("version"),
            "approved_by": self.policies.get("approved_by"),
            "effective_date": self.policies.get("effective_date"),
            "review_date": self.policies.get("review_date"),
            "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None,
            "policy_file": str(self.policy_file)
        }


# Singleton instance for convenience
_policy_engine_instance: Optional[PolicyEngine] = None


def get_policy_engine(policy_file: str = "policies.yaml") -> PolicyEngine:
    """
    Get singleton PolicyEngine instance

    Args:
        policy_file: Path to policies.yaml

    Returns:
        PolicyEngine instance
    """
    global _policy_engine_instance

    if _policy_engine_instance is None:
        _policy_engine_instance = PolicyEngine(policy_file)

    return _policy_engine_instance
