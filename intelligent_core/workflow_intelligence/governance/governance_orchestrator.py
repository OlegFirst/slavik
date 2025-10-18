"""
Governance Orchestrator - Coordinates Goals + Rules Together
==============================================================

Unified governance system that coordinates:
- Goals Engine: Positive targets (what to strive for)
- Rules Engine: Constraints (what not to violate)

Decision Priority (when goals conflict with rules):
1. Constitution Rules (always enforced)
2. Compliance Rules (enforced unless overridden)
3. Goals (guide optimization)
4. Organization Rules (enforced based on config)
5. Best Practice Rules (suggestions)
6. ML-Driven Rules (adaptive guidance)

Recursive Application:
- User Level: User-created workflows
- System Level: Workflow Intelligence itself
- Component Level: Other platform components (AI Foundation, BCM Domain BIA Service)
- Platform Level: Entire AI-Platform-ISO

Created: 2025-10-09
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .goals_engine import (
    GoalsEngine,
    Goal,
    GoalProgress,
    GoalStatus,
    GoalLevel,
    OptimizationSuggestion,
    SystemGoalsMonitor
)

from .rules_engine_v2 import (
    RulesEngineV2,
    Rule,
    RuleViolation,
    RuleCategory,
    RuleSeverity,
    RuleAppliesTo,
    RuleAction,
    SystemRulesValidator
)

logger = logging.getLogger(__name__)


@dataclass
class GovernanceDecision:
    """
    Decision made by governance orchestrator

    Combines goal progress and rule violations to make
    actionable decisions.
    """
    decision_id: str
    decision_type: str  # "allow", "block", "warn", "suggest_optimization"
    rationale: str
    goal_status: Optional[Dict[str, Any]] = None
    rule_violations: List[RuleViolation] = field(default_factory=list)
    optimization_suggestions: List[OptimizationSuggestion] = field(default_factory=list)
    actions_to_take: List[str] = field(default_factory=list)
    escalate_to_human: bool = False
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class GovernanceContext:
    """
    Context for governance evaluation

    Combines workflow data with metadata about which level
    is being evaluated.
    """
    target_level: RuleAppliesTo          # USER, SYSTEM, COMPONENT, PLATFORM
    data: Dict[str, Any]                 # Data to evaluate
    current_stage: Optional[str] = None  # Workflow stage (if applicable)
    workflow_id: Optional[str] = None
    start_time: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class GovernanceOrchestrator:
    """
    Orchestrates Goals + Rules for unified governance

    Features:
    - Coordinates goals and rules evaluation
    - Resolves conflicts (rules take precedence)
    - Generates actionable decisions
    - Triggers optimization suggestions
    - Handles escalation to humans
    - Recursive application across levels
    """

    def __init__(self, config_path: str):
        """
        Initialize Governance Orchestrator

        Args:
            config_path: Path to goals.yaml configuration file
        """
        self.goals_engine = GoalsEngine(config_path)
        self.rules_engine = RulesEngineV2(config_path)

        # System self-monitoring components
        self.system_goals_monitor = SystemGoalsMonitor(self.goals_engine)
        self.system_rules_validator = SystemRulesValidator(self.rules_engine)

        self.decisions_history: List[GovernanceDecision] = []

        logger.info(
            f"Governance Orchestrator initialized: "
            f"{len(self.goals_engine.goals)} goals, "
            f"{len(self.rules_engine.rules)} rules"
        )

    def evaluate(self, context: GovernanceContext) -> GovernanceDecision:
        """
        Evaluate governance for given context

        This is the main entry point that coordinates goals and rules.

        Decision Priority:
        1. Check rules (blocking if violated)
        2. Check goals (suggest optimizations if behind)
        3. Make decision based on combined analysis

        Args:
            context: GovernanceContext with data and metadata

        Returns:
            GovernanceDecision with action to take
        """
        decision_id = f"dec_{datetime.utcnow().timestamp()}"

        # Step 1: Validate against rules
        rules_passed, rule_violations = self.rules_engine.validate(
            context.data,
            context.target_level,
            context.current_stage
        )

        # Step 2: Check goal progress (if applicable)
        goal_progress_list = self._check_goal_progress(context)

        # Step 3: Determine decision based on priority
        decision = self._make_decision(
            decision_id,
            context,
            rules_passed,
            rule_violations,
            goal_progress_list
        )

        self.decisions_history.append(decision)

        logger.info(
            f"Governance decision: {decision.decision_type} "
            f"(rules_passed={rules_passed}, goals_tracked={len(goal_progress_list)})"
        )

        return decision

    def _check_goal_progress(
        self,
        context: GovernanceContext
    ) -> List[GoalProgress]:
        """
        Check progress against relevant goals

        Args:
            context: GovernanceContext

        Returns:
            List of GoalProgress for relevant goals
        """
        progress_list = []

        # Map RuleAppliesTo to GoalLevel
        level_map = {
            RuleAppliesTo.USER: GoalLevel.USER,
            RuleAppliesTo.SYSTEM: GoalLevel.SYSTEM,
            RuleAppliesTo.COMPONENT: GoalLevel.COMPONENT,
            RuleAppliesTo.PLATFORM: GoalLevel.PLATFORM
        }

        goal_level = level_map.get(context.target_level)
        if not goal_level:
            return progress_list

        # Get goals for this level
        relevant_goals = self.goals_engine.get_goals_by_level(goal_level)

        for goal in relevant_goals:
            try:
                # Extract current values for goal metrics
                current_values = {}
                for metric_key in goal.metrics.keys():
                    if metric_key in context.data:
                        current_values[metric_key] = context.data[metric_key]

                if current_values:
                    # Build context for goal tracking
                    goal_context = {}
                    if context.start_time:
                        goal_context['start_time'] = context.start_time

                    progress = self.goals_engine.track_progress(
                        goal.goal_id,
                        current_values,
                        goal_context
                    )
                    progress_list.append(progress)

            except Exception as e:
                logger.error(f"Error tracking goal {goal.goal_id}: {e}")

        return progress_list

    def _make_decision(
        self,
        decision_id: str,
        context: GovernanceContext,
        rules_passed: bool,
        rule_violations: List[RuleViolation],
        goal_progress_list: List[GoalProgress]
    ) -> GovernanceDecision:
        """
        Make governance decision based on rules and goals

        Decision Priority:
        1. Constitution rules → BLOCK
        2. Compliance rules → BLOCK or OVERRIDE
        3. Goals at risk → SUGGEST optimization
        4. Organization rules → WARN or BLOCK
        5. Best practice rules → SUGGEST
        6. ML-driven rules → SUGGEST

        Args:
            decision_id: Unique decision ID
            context: GovernanceContext
            rules_passed: Whether all rules passed
            rule_violations: List of rule violations
            goal_progress_list: List of goal progress

        Returns:
            GovernanceDecision
        """
        # Categorize violations by severity
        critical_violations = [
            v for v in rule_violations
            if v.severity == RuleSeverity.CRITICAL
        ]

        high_violations = [
            v for v in rule_violations
            if v.severity == RuleSeverity.HIGH
        ]

        medium_violations = [
            v for v in rule_violations
            if v.severity == RuleSeverity.MEDIUM
        ]

        low_violations = [
            v for v in rule_violations
            if v.severity == RuleSeverity.LOW
        ]

        # Categorize goal status
        goals_behind = [
            p for p in goal_progress_list
            if p.status == GoalStatus.BEHIND
        ]

        goals_at_risk = [
            p for p in goal_progress_list
            if p.status == GoalStatus.AT_RISK
        ]

        # ===== DECISION LOGIC =====

        # Case 1: Constitution violations → BLOCK immediately
        constitution_violations = self.rules_engine.get_constitution_violations(rule_violations)
        if constitution_violations:
            return GovernanceDecision(
                decision_id=decision_id,
                decision_type="block",
                rationale=(
                    f"Constitution rule violated: {constitution_violations[0].rule_name}. "
                    "This is a critical platform principle that cannot be overridden."
                ),
                rule_violations=constitution_violations,
                actions_to_take=[
                    "escalate_to_platform_team",
                    "log_security_incident"
                ],
                escalate_to_human=True
            )

        # Case 2: Critical violations → BLOCK
        if critical_violations:
            return GovernanceDecision(
                decision_id=decision_id,
                decision_type="block",
                rationale=f"Critical rule violation: {critical_violations[0].rule_name}",
                rule_violations=critical_violations,
                actions_to_take=["escalate_to_ops", "notify_security_team"],
                escalate_to_human=True
            )

        # Case 3: High violations that can't be overridden → BLOCK
        blocking_high_violations = [
            v for v in high_violations if not v.can_override
        ]
        if blocking_high_violations:
            return GovernanceDecision(
                decision_id=decision_id,
                decision_type="block",
                rationale=f"High-severity rule violation: {blocking_high_violations[0].rule_name}",
                rule_violations=blocking_high_violations,
                actions_to_take=["escalate_to_compliance_officer"],
                escalate_to_human=True
            )

        # Case 4: High violations that CAN be overridden → WARN and request override
        overridable_high_violations = [
            v for v in high_violations if v.can_override and not v.override_approved
        ]
        if overridable_high_violations:
            return GovernanceDecision(
                decision_id=decision_id,
                decision_type="warn",
                rationale=(
                    f"High-severity rule violation: {overridable_high_violations[0].rule_name}. "
                    "Override is possible with justification."
                ),
                rule_violations=overridable_high_violations,
                actions_to_take=[
                    "request_override_approval",
                    "notify_compliance_officer"
                ],
                escalate_to_human=True
            )

        # Case 5: Goals significantly behind → SUGGEST optimization
        if goals_behind:
            optimization_suggestions = self.goals_engine.get_optimization_suggestions()

            return GovernanceDecision(
                decision_id=decision_id,
                decision_type="suggest_optimization",
                rationale=(
                    f"{len(goals_behind)} goal(s) significantly behind target. "
                    "Optimization recommended."
                ),
                goal_status={
                    'goals_behind': len(goals_behind),
                    'goals_at_risk': len(goals_at_risk)
                },
                optimization_suggestions=optimization_suggestions,
                actions_to_take=[
                    f"apply_optimization:{s.strategy}"
                    for s in optimization_suggestions[:3]  # Top 3
                ]
            )

        # Case 6: Medium violations → WARN
        if medium_violations:
            return GovernanceDecision(
                decision_id=decision_id,
                decision_type="warn",
                rationale=f"Medium-severity violation: {medium_violations[0].rule_name}",
                rule_violations=medium_violations,
                actions_to_take=["log_warning", "notify_bcm_manager"]
            )

        # Case 7: Goals at risk → SUGGEST optimization
        if goals_at_risk:
            optimization_suggestions = self.goals_engine.get_optimization_suggestions()

            return GovernanceDecision(
                decision_id=decision_id,
                decision_type="suggest_optimization",
                rationale=(
                    f"{len(goals_at_risk)} goal(s) at risk. "
                    "Proactive optimization suggested."
                ),
                goal_status={
                    'goals_at_risk': len(goals_at_risk)
                },
                optimization_suggestions=optimization_suggestions,
                actions_to_take=[
                    f"suggest_optimization:{s.strategy}"
                    for s in optimization_suggestions
                ]
            )

        # Case 8: Low violations or best practice → SUGGEST
        if low_violations:
            return GovernanceDecision(
                decision_id=decision_id,
                decision_type="suggest",
                rationale=f"Best practice suggestion: {low_violations[0].rule_name}",
                rule_violations=low_violations,
                actions_to_take=["show_recommendation_to_user"]
            )

        # Case 9: All good → ALLOW
        return GovernanceDecision(
            decision_id=decision_id,
            decision_type="allow",
            rationale="All rules passed and goals on track",
            goal_status={
                'goals_tracked': len(goal_progress_list),
                'all_on_track': True
            }
        )

    def validate_user_workflow(
        self,
        workflow_data: Dict[str, Any],
        workflow_id: str,
        current_stage: str,
        start_time: Optional[str] = None
    ) -> GovernanceDecision:
        """
        Validate user-created workflow against governance

        Args:
            workflow_data: Workflow data to validate
            workflow_id: Workflow ID
            current_stage: Current workflow stage
            start_time: Workflow start time (ISO format)

        Returns:
            GovernanceDecision
        """
        context = GovernanceContext(
            target_level=RuleAppliesTo.USER,
            data=workflow_data,
            current_stage=current_stage,
            workflow_id=workflow_id,
            start_time=start_time
        )

        return self.evaluate(context)

    async def validate_system_health(
        self,
        system_metrics: Dict[str, Any]
    ) -> GovernanceDecision:
        """
        Validate Workflow Intelligence system against governance (self-monitoring)

        This is the "eat own dog food" implementation - the system validates
        itself against rules and goals.

        Args:
            system_metrics: Current system metrics (performance, accuracy, etc.)

        Returns:
            GovernanceDecision with corrective actions
        """
        context = GovernanceContext(
            target_level=RuleAppliesTo.SYSTEM,
            data=system_metrics,
            metadata={'self_monitoring': True}
        )

        decision = self.evaluate(context)

        # If system violations detected, take corrective action
        if decision.decision_type in ['block', 'warn']:
            logger.warning(
                f"System self-monitoring detected issues: {decision.rationale}"
            )

            # Execute corrective actions
            for action in decision.actions_to_take:
                try:
                    await self._execute_system_corrective_action(action, system_metrics)
                except Exception as e:
                    logger.error(f"Error executing system corrective action {action}: {e}")

        return decision

    async def _execute_system_corrective_action(
        self,
        action: str,
        system_metrics: Dict[str, Any]
    ):
        """
        Execute corrective action for system-level issue

        Args:
            action: Action to execute (e.g., "escalate_performance_issue")
            system_metrics: Current system metrics
        """
        if action.startswith("escalate_"):
            issue_type = action.replace("escalate_", "")
            logger.error(f"ESCALATION: System issue detected - {issue_type}")
            # In production, trigger escalation workflow

        elif action.startswith("request_review:"):
            rule_id = action.split(":")[1]
            logger.warning(f"REVIEW REQUESTED: System rule {rule_id} violated")
            # In production, create review ticket

        elif action.startswith("apply_optimization:"):
            strategy = action.split(":")[1]
            logger.info(f"OPTIMIZATION: Applying strategy - {strategy}")
            # In production, trigger optimization workflow

    def validate_component_health(
        self,
        component_name: str,
        component_metrics: Dict[str, Any]
    ) -> GovernanceDecision:
        """
        Validate platform component against governance

        Args:
            component_name: Component name (e.g., "ai_foundation", "bia_service")
            component_metrics: Current component metrics

        Returns:
            GovernanceDecision
        """
        context = GovernanceContext(
            target_level=RuleAppliesTo.COMPONENT,
            data=component_metrics,
            metadata={'component': component_name}
        )

        return self.evaluate(context)

    def validate_platform_health(
        self,
        platform_metrics: Dict[str, Any]
    ) -> GovernanceDecision:
        """
        Validate entire platform against governance

        Args:
            platform_metrics: Platform-wide metrics (MTTR, user satisfaction, etc.)

        Returns:
            GovernanceDecision
        """
        context = GovernanceContext(
            target_level=RuleAppliesTo.PLATFORM,
            data=platform_metrics
        )

        return self.evaluate(context)

    def get_governance_summary(self) -> Dict[str, Any]:
        """
        Get overall governance health summary

        Returns:
            Summary dict with goals status, rules compliance, decisions
        """
        goals_summary = self.goals_engine.get_goal_status_summary()

        # Rules compliance
        total_violations = len(self.rules_engine.violations_history)
        recent_violations = [
            v for v in self.rules_engine.violations_history
            if (datetime.utcnow() - datetime.fromisoformat(v.timestamp)).total_seconds() < 3600
        ]

        critical_violations = [
            v for v in recent_violations
            if v.severity == RuleSeverity.CRITICAL
        ]

        # Decisions
        recent_decisions = [
            d for d in self.decisions_history
            if (datetime.utcnow() - datetime.fromisoformat(d.timestamp)).total_seconds() < 3600
        ]

        blocked_decisions = [
            d for d in recent_decisions
            if d.decision_type == 'block'
        ]

        # Calculate governance maturity score
        governance_maturity = self._calculate_governance_maturity(
            goals_summary,
            len(critical_violations),
            len(blocked_decisions)
        )

        return {
            'goals': goals_summary,
            'rules': {
                'total_violations': total_violations,
                'recent_violations': len(recent_violations),
                'critical_violations': len(critical_violations)
            },
            'decisions': {
                'total_decisions': len(self.decisions_history),
                'recent_decisions': len(recent_decisions),
                'blocked_decisions': len(blocked_decisions)
            },
            'governance_maturity_score': governance_maturity,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _calculate_governance_maturity(
        self,
        goals_summary: Dict[str, Any],
        critical_violations: int,
        blocked_decisions: int
    ) -> int:
        """
        Calculate governance maturity score (0-100)

        Factors:
        - Goal achievement rate (40%)
        - Rule compliance (30%)
        - Decision quality (30%)

        Args:
            goals_summary: Goals status summary
            critical_violations: Number of critical violations
            blocked_decisions: Number of blocked decisions

        Returns:
            Maturity score (0-100)
        """
        # Goals score (40%)
        goals_health = goals_summary.get('overall_health_score', 0)
        goals_score = goals_health * 0.4

        # Rules compliance score (30%)
        if critical_violations == 0:
            rules_score = 30
        elif critical_violations <= 2:
            rules_score = 20
        elif critical_violations <= 5:
            rules_score = 10
        else:
            rules_score = 0

        # Decision quality score (30%)
        if blocked_decisions == 0:
            decisions_score = 30
        elif blocked_decisions <= 3:
            decisions_score = 20
        elif blocked_decisions <= 10:
            decisions_score = 10
        else:
            decisions_score = 0

        total_score = int(goals_score + rules_score + decisions_score)

        return min(100, max(0, total_score))


# ============= CONVENIENCE FUNCTIONS =============

def create_governance_orchestrator(config_path: str) -> GovernanceOrchestrator:
    """
    Factory function to create governance orchestrator

    Args:
        config_path: Path to goals.yaml configuration

    Returns:
        GovernanceOrchestrator instance
    """
    return GovernanceOrchestrator(config_path)
