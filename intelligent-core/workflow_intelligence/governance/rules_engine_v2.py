"""
Rules Engine v2 - Recursive & Multi-Level Rule System
=======================================================

Extends original RulesEngine with:
1. Multi-level rule hierarchy (Constitution → Compliance → Organization → Best Practice → ML)
2. Recursive application (User, System, Component, Platform)
3. Override capability with justification tracking
4. Load from goals.yaml configuration

Key Improvements:
- Rules can now apply to system itself, not just user input
- Rules have configurable override capability
- Rules are loaded from YAML configuration
- Rule violations tracked with escalation paths

Created: 2025-10-09
Based on: rules_engine.py
"""

from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RuleSeverity(Enum):
    """Severity of rule violation"""
    CRITICAL = "critical"      # Блокировка + немедленная эскалация
    HIGH = "high"              # Блокировка или override с обоснованием
    MEDIUM = "medium"          # Warning + логирование
    LOW = "low"                # Recommendation


class RuleCategory(Enum):
    """Category of rule in hierarchy"""
    CONSTITUTION = "constitution"      # Неизменяемые принципы платформы
    COMPLIANCE = "compliance"          # ISO, NIST, WHO - can override с обоснованием
    ORGANIZATION = "organization"      # Корпоративные политики - configurable
    BEST_PRACTICE = "best_practice"    # Из Case Library - suggestions
    ML_DRIVEN = "ml_driven"            # Adaptive rules from ML - dynamic


class RuleAppliesTo(Enum):
    """Level at which rule applies (recursive)"""
    USER = "user"                      # User input/workflows
    SYSTEM = "system"                  # Workflow Intelligence itself
    COMPONENT = "component"            # Other platform components
    PLATFORM = "platform"              # Entire AI-Platform-ISO


class RuleAction(Enum):
    """Action to take on rule violation"""
    BLOCK = "BLOCK"                            # Stop execution
    BLOCK_OR_OVERRIDE = "BLOCK_OR_OVERRIDE"   # Stop unless override approved
    WARN_OR_BLOCK = "WARN_OR_BLOCK"           # Configurable per organization
    WARN = "WARN"                              # Log warning, continue
    SUGGEST = "SUGGEST"                        # Show suggestion, continue


@dataclass
class Rule:
    """
    Enhanced rule with multi-level hierarchy and recursive application
    """
    rule_id: str
    name: str
    description: str
    category: RuleCategory
    severity: RuleSeverity
    applies_to: List[RuleAppliesTo]            # Can apply to multiple levels
    validation: str                             # Validation expression or function name
    can_override: bool = False
    override_requires: List[str] = field(default_factory=list)  # ['ciso_approval', 'justification']
    configurable: bool = False                  # Can be configured per organization
    default_value: Any = None
    source: Optional[str] = None                # 'case_library', 'iso_22301', etc.
    source_details: Dict[str, Any] = field(default_factory=dict)
    applies_to_stages: Optional[List[str]] = None  # None = all stages
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleViolation:
    """Enhanced rule violation with recursive context"""
    rule_id: str
    rule_name: str
    category: RuleCategory
    severity: RuleSeverity
    applies_to: RuleAppliesTo                   # Which level violated (user/system/component/platform)
    message: str
    context: Dict[str, Any]
    can_override: bool
    override_requires: List[str]
    timestamp: str
    escalated: bool = False
    override_approved: bool = False
    override_justification: Optional[str] = None
    override_approved_by: Optional[str] = None


@dataclass
class RuleOverrideRequest:
    """Request to override a rule"""
    violation_id: str
    rule_id: str
    justification: str
    requested_by: str
    approved_by: Optional[str] = None
    approved: bool = False
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class RulesEngineV2:
    """
    Enhanced Rules Engine with multi-level hierarchy and recursive application

    Features:
    - Load rules from goals.yaml configuration
    - Multi-level hierarchy (Constitution → ML-Driven)
    - Recursive application (User, System, Component, Platform)
    - Override capability with approval tracking
    - Validation against different target levels
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Rules Engine V2

        Args:
            config_path: Path to goals.yaml config file
        """
        self.rules: Dict[str, Rule] = {}
        self.violations_history: List[RuleViolation] = []
        self.override_requests: Dict[str, RuleOverrideRequest] = {}
        self.config: Dict[str, Any] = {}
        self.validation_functions: Dict[str, Callable] = {}

        # Register built-in validation functions
        self._register_builtin_validations()

        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str):
        """Load rules configuration from goals.yaml"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Rules config not found: {config_path}")

        with open(path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Parse rules from config
        rules_config = self.config.get('rules', {})

        # Load Constitution rules
        for rule_data in rules_config.get('constitution', []):
            self._parse_and_register_rule(rule_data, RuleCategory.CONSTITUTION)

        # Load Compliance rules
        compliance_config = rules_config.get('compliance', {})
        for standard, rule_list in compliance_config.items():
            for rule_data in rule_list:
                rule_data['source'] = standard
                self._parse_and_register_rule(rule_data, RuleCategory.COMPLIANCE)

        # Load Organization rules
        for rule_data in rules_config.get('organization', []):
            self._parse_and_register_rule(rule_data, RuleCategory.ORGANIZATION)

        # Load Best Practice rules
        for rule_data in rules_config.get('best_practice', []):
            self._parse_and_register_rule(rule_data, RuleCategory.BEST_PRACTICE)

        # Load ML-Driven rules
        for rule_data in rules_config.get('ml_driven', []):
            self._parse_and_register_rule(rule_data, RuleCategory.ML_DRIVEN)

        logger.info(f"Loaded {len(self.rules)} rules from configuration")

    def _parse_and_register_rule(self, rule_data: Dict[str, Any], category: RuleCategory):
        """Parse rule data and register it"""
        # Parse applies_to field
        applies_to_raw = rule_data.get('applies_to', ['user'])
        applies_to = [RuleAppliesTo(level) for level in applies_to_raw]

        # Determine severity from category if not specified
        severity_map = {
            RuleCategory.CONSTITUTION: RuleSeverity.CRITICAL,
            RuleCategory.COMPLIANCE: RuleSeverity.HIGH,
            RuleCategory.ORGANIZATION: RuleSeverity.MEDIUM,
            RuleCategory.BEST_PRACTICE: RuleSeverity.LOW,
            RuleCategory.ML_DRIVEN: RuleSeverity.MEDIUM
        }
        severity_str = rule_data.get('severity', severity_map[category].value)
        severity = RuleSeverity(severity_str.lower())

        rule = Rule(
            rule_id=rule_data['id'],
            name=rule_data['name'],
            description=rule_data['description'],
            category=category,
            severity=severity,
            applies_to=applies_to,
            validation=rule_data['validation'],
            can_override=rule_data.get('can_override', False),
            override_requires=rule_data.get('override_requires', []),
            configurable=rule_data.get('configurable', False),
            default_value=rule_data.get('default_value'),
            source=rule_data.get('source'),
            source_details={
                'source_case_count': rule_data.get('source_case_count'),
                'model': rule_data.get('model'),
                'accuracy': rule_data.get('accuracy')
            },
            metadata=rule_data
        )

        self.register_rule(rule)

    def register_rule(self, rule: Rule):
        """Register a rule"""
        self.rules[rule.rule_id] = rule
        logger.debug(f"Registered rule: {rule.rule_id} ({rule.category.value})")

    def register_validation_function(self, name: str, fn: Callable):
        """Register a custom validation function"""
        self.validation_functions[name] = fn

    def _register_builtin_validations(self):
        """Register built-in validation functions"""
        # Simple validation functions that can be referenced by name

        def no_data_loss(context: Dict[str, Any]) -> tuple[bool, Optional[str]]:
            """Constitution: No data loss allowed"""
            has_backup = context.get('postgresql_wal_retention', False)
            backup_verified = context.get('backup_verified', False)

            if not (has_backup and backup_verified):
                return False, "Data loss risk detected: backup not verified"
            return True, None

        def audit_trail_integrity(context: Dict[str, Any]) -> tuple[bool, Optional[str]]:
            """Constitution: Audit trail must be tamper-proof"""
            audit_signed = context.get('audit_log_signed', False)
            immutable = context.get('immutable_storage', False)

            if not (audit_signed and immutable):
                return False, "Audit trail integrity compromised"
            return True, None

        def performance_threshold(context: Dict[str, Any]) -> tuple[bool, Optional[str]]:
            """System: Performance must meet threshold"""
            transition_time = context.get('transition_time_seconds', 0)
            threshold = context.get('threshold_seconds', 5.0)

            if transition_time > threshold:
                return False, f"Performance degraded: {transition_time}s > {threshold}s"
            return True, None

        self.validation_functions['no_data_loss'] = no_data_loss
        self.validation_functions['audit_trail_integrity'] = audit_trail_integrity
        self.validation_functions['performance_threshold'] = performance_threshold

    def validate(
        self,
        context: Dict[str, Any],
        target_level: RuleAppliesTo,
        current_stage: Optional[str] = None
    ) -> tuple[bool, List[RuleViolation]]:
        """
        Validate context against rules for specific target level

        Args:
            context: Data to validate
            target_level: Level being validated (USER, SYSTEM, COMPONENT, PLATFORM)
            current_stage: Current workflow stage (optional)

        Returns:
            (all_passed, violations)
        """
        violations = []

        for rule in self.rules.values():
            # Check if rule applies to target level
            if target_level not in rule.applies_to:
                continue

            # Check if rule applies to current stage
            if rule.applies_to_stages and current_stage:
                if current_stage not in rule.applies_to_stages:
                    continue

            # Execute validation
            try:
                is_valid, message = self._execute_validation(rule, context)

                if not is_valid:
                    violation = RuleViolation(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        applies_to=target_level,
                        message=message or f"Rule violation: {rule.name}",
                        context=context.copy(),
                        can_override=rule.can_override,
                        override_requires=rule.override_requires,
                        timestamp=datetime.utcnow().isoformat()
                    )
                    violations.append(violation)
                    self.violations_history.append(violation)

            except Exception as e:
                logger.error(f"Validation error for rule {rule.rule_id}: {e}")
                violation = RuleViolation(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=RuleSeverity.HIGH,
                    applies_to=target_level,
                    message=f"Validation error: {str(e)}",
                    context=context.copy(),
                    can_override=False,
                    override_requires=[],
                    timestamp=datetime.utcnow().isoformat()
                )
                violations.append(violation)

        # Sort by severity
        violations.sort(key=lambda v: self._severity_order(v.severity))

        # Determine if validation passed
        blocking_violations = [
            v for v in violations
            if v.severity in [RuleSeverity.CRITICAL, RuleSeverity.HIGH]
            and not v.override_approved
        ]
        all_passed = len(blocking_violations) == 0

        return all_passed, violations

    def _execute_validation(
        self,
        rule: Rule,
        context: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Execute validation for a rule

        Args:
            rule: Rule to validate
            context: Data to validate

        Returns:
            (is_valid, error_message)
        """
        validation_str = rule.validation

        # Check if validation is a function name
        if validation_str in self.validation_functions:
            return self.validation_functions[validation_str](context)

        # Otherwise, evaluate validation expression
        return self._evaluate_validation_expression(validation_str, context)

    def _evaluate_validation_expression(
        self,
        expression: str,
        context: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Evaluate validation expression string

        Args:
            expression: Validation expression (e.g., "rto_hours > 0")
            context: Data context

        Returns:
            (is_valid, error_message)
        """
        try:
            # Simple expression evaluation
            # In production, use safer eval or AST parser

            # Handle common patterns
            if ' is not None' in expression:
                field = expression.split(' is not None')[0].strip()
                value = context.get(field)
                if value is None:
                    return False, f"Required field '{field}' is None"
                return True, None

            if ' && ' in expression:
                # Multiple conditions
                conditions = expression.split(' && ')
                for cond in conditions:
                    is_valid, msg = self._evaluate_validation_expression(cond.strip(), context)
                    if not is_valid:
                        return False, msg
                return True, None

            # For simple comparisons, extract field and check
            # This is a simplified implementation - extend as needed
            for field_name, field_value in context.items():
                if field_name in expression:
                    # Replace field with value
                    eval_expr = expression.replace(field_name, str(field_value))

                    # Safe evaluation (only allow comparison operators)
                    allowed_chars = set('0123456789.<>= ()andornot')
                    if all(c in allowed_chars or c.isspace() for c in eval_expr):
                        result = eval(eval_expr)
                        if not result:
                            return False, f"Validation failed: {expression}"
                        return True, None

            return True, None

        except Exception as e:
            logger.error(f"Expression evaluation error: {e}")
            return False, f"Validation error: {str(e)}"

    def _severity_order(self, severity: RuleSeverity) -> int:
        """Order for sorting by severity"""
        return {
            RuleSeverity.CRITICAL: 0,
            RuleSeverity.HIGH: 1,
            RuleSeverity.MEDIUM: 2,
            RuleSeverity.LOW: 3
        }[severity]

    def should_escalate(self, violations: List[RuleViolation]) -> bool:
        """Determine if violations require escalation"""
        # Get escalation configuration from config
        rule_handling = self.config.get('coordination', {}).get('rule_violation_handling', {})

        # Escalate if constitution violations
        constitution_violations = [
            v for v in violations if v.category == RuleCategory.CONSTITUTION
        ]
        if constitution_violations:
            return True

        # Escalate if compliance violations
        compliance_violations = [
            v for v in violations if v.category == RuleCategory.COMPLIANCE
        ]
        if compliance_violations:
            return True

        # Escalate if many high-severity violations
        high_violations = [
            v for v in violations if v.severity in [RuleSeverity.CRITICAL, RuleSeverity.HIGH]
        ]
        if len(high_violations) >= 3:
            return True

        return False

    def get_violation_action(self, violation: RuleViolation) -> RuleAction:
        """
        Determine action to take for a violation

        Args:
            violation: Rule violation

        Returns:
            RuleAction enum
        """
        # Get action from configuration
        rule_handling = self.config.get('coordination', {}).get('rule_violation_handling', {})
        category_key = violation.category.value

        if category_key in rule_handling:
            action_str = rule_handling[category_key].get('action', 'WARN')
            return RuleAction(action_str)

        # Fallback based on severity
        if violation.severity == RuleSeverity.CRITICAL:
            return RuleAction.BLOCK

        if violation.severity == RuleSeverity.HIGH:
            return RuleAction.BLOCK_OR_OVERRIDE if violation.can_override else RuleAction.BLOCK

        if violation.severity == RuleSeverity.MEDIUM:
            return RuleAction.WARN

        return RuleAction.SUGGEST

    def request_override(
        self,
        violation_id: str,
        justification: str,
        requested_by: str
    ) -> RuleOverrideRequest:
        """
        Request override for a rule violation

        Args:
            violation_id: ID of violation to override
            justification: Justification for override
            requested_by: User requesting override

        Returns:
            RuleOverrideRequest object
        """
        # Find violation
        violation = next(
            (v for v in self.violations_history if id(v) == int(violation_id)),
            None
        )

        if not violation:
            raise ValueError(f"Violation not found: {violation_id}")

        if not violation.can_override:
            raise ValueError(f"Rule {violation.rule_id} cannot be overridden")

        request = RuleOverrideRequest(
            violation_id=violation_id,
            rule_id=violation.rule_id,
            justification=justification,
            requested_by=requested_by
        )

        self.override_requests[violation_id] = request

        return request

    def approve_override(
        self,
        violation_id: str,
        approved_by: str,
        approved: bool
    ):
        """
        Approve or reject override request

        Args:
            violation_id: ID of violation
            approved_by: User approving/rejecting
            approved: True to approve, False to reject
        """
        if violation_id not in self.override_requests:
            raise ValueError(f"Override request not found: {violation_id}")

        request = self.override_requests[violation_id]
        request.approved = approved
        request.approved_by = approved_by

        # Update violation
        violation = next(
            (v for v in self.violations_history if id(v) == int(violation_id)),
            None
        )

        if violation:
            violation.override_approved = approved
            violation.override_justification = request.justification
            violation.override_approved_by = approved_by

        logger.info(
            f"Override {'approved' if approved else 'rejected'} "
            f"for rule {request.rule_id} by {approved_by}"
        )

    def get_constitution_violations(
        self,
        violations: List[RuleViolation]
    ) -> List[RuleViolation]:
        """Get constitution-level violations (most serious)"""
        return [v for v in violations if v.category == RuleCategory.CONSTITUTION]

    def get_rules_by_category(self, category: RuleCategory) -> List[Rule]:
        """Get all rules in a category"""
        return [r for r in self.rules.values() if r.category == category]

    def get_rules_for_level(self, level: RuleAppliesTo) -> List[Rule]:
        """Get all rules that apply to a specific level"""
        return [r for r in self.rules.values() if level in r.applies_to]


# ============= SYSTEM SELF-VALIDATION =============

class SystemRulesValidator:
    """
    Validator for system-level rules (Workflow Intelligence validating itself)

    This is the "eat own dog food" implementation - the system checks
    itself against rules and takes corrective action.
    """

    def __init__(self, rules_engine: RulesEngineV2):
        self.rules_engine = rules_engine
        self.last_check: Optional[datetime] = None

    async def validate_system_state(self, system_metrics: Dict[str, Any]) -> List[str]:
        """
        Validate Workflow Intelligence against system-level rules

        Args:
            system_metrics: Current system state (performance, accuracy, etc.)

        Returns:
            List of corrective actions to take
        """
        actions = []

        # Validate against SYSTEM rules
        all_passed, violations = self.rules_engine.validate(
            system_metrics,
            RuleAppliesTo.SYSTEM
        )

        if not all_passed:
            logger.warning(f"System rule violations detected: {len(violations)}")

            for violation in violations:
                action = self.rules_engine.get_violation_action(violation)

                if action == RuleAction.BLOCK:
                    # Critical violation - escalate immediately
                    actions.append(f"escalate_critical_violation:{violation.rule_id}")

                elif action in [RuleAction.BLOCK_OR_OVERRIDE, RuleAction.WARN_OR_BLOCK]:
                    # Request human review
                    actions.append(f"request_review:{violation.rule_id}")

                elif action == RuleAction.WARN:
                    # Log warning
                    logger.warning(f"System rule violation: {violation.message}")

        self.last_check = datetime.utcnow()

        return actions
