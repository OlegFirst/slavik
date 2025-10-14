"""
Goals Engine - Positive guidance system for Workflow Intelligence
===================================================================

Complements RulesEngine with proactive optimization toward targets.

Key Concepts:
- Rules = NEGATIVE (what you can't do) → Blocking
- Goals = POSITIVE (what to strive for) → Guiding

Goals Engine:
1. Tracks progress toward goals
2. Suggests optimizations when falling behind
3. Reports achievement metrics
4. Triggers proactive actions (auto-scale, template suggestions, etc.)

Applies recursively:
- User goals (BIA completion time, quality)
- System goals (performance, accuracy)
- Component goals (AI Foundation, BIA Service)
- Platform goals (MTTR, user satisfaction)

Created: 2025-10-09
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import yaml
from pathlib import Path


class GoalStatus(Enum):
    """Status of goal achievement"""
    ON_TRACK = "on_track"          # Progress >= expected
    AT_RISK = "at_risk"            # Progress < expected but recoverable
    BEHIND = "behind"              # Progress significantly behind
    ACHIEVED = "achieved"          # Goal met or exceeded
    FAILED = "failed"              # Goal missed, no longer achievable


class GoalLevel(Enum):
    """Level at which goal applies"""
    USER = "user"                  # User-created workflows
    SYSTEM = "system"              # Workflow Intelligence itself
    COMPONENT = "component"        # Other platform components
    PLATFORM = "platform"          # Entire AI-Platform-ISO


@dataclass
class Goal:
    """Represents a single goal with metrics and optimization strategy"""
    goal_id: str
    name: str
    description: str
    level: GoalLevel
    metrics: Dict[str, Any]        # Target values
    optimization_strategy: str
    current_values: Dict[str, Any] = field(default_factory=dict)
    status: GoalStatus = GoalStatus.ON_TRACK
    progress_percent: float = 0.0
    last_updated: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GoalProgress:
    """Tracks progress toward a goal"""
    goal_id: str
    current_value: Any
    target_value: Any
    progress_percent: float
    status: GoalStatus
    time_remaining: Optional[float] = None  # seconds
    time_elapsed: Optional[float] = None    # seconds
    estimated_completion: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)


@dataclass
class OptimizationSuggestion:
    """Suggestion to help achieve a goal"""
    goal_id: str
    goal_name: str
    strategy: str
    priority: str  # high, medium, low
    actions: List[str]
    expected_impact: str
    timestamp: str


class GoalsEngine:
    """
    Engine for tracking and optimizing toward goals

    Features:
    - Load goals from YAML configuration
    - Track progress against targets
    - Suggest optimizations when at risk
    - Trigger proactive actions
    - Report achievement metrics
    - Recursive application (user, system, component, platform)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Goals Engine

        Args:
            config_path: Path to goals.yaml config file
        """
        self.goals: Dict[str, Goal] = {}
        self.progress_history: List[GoalProgress] = []
        self.suggestions_history: List[OptimizationSuggestion] = []
        self.config: Dict[str, Any] = {}

        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str):
        """Load goals configuration from YAML file"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Goals config not found: {config_path}")

        with open(path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Parse goals from config
        self._parse_user_goals()
        self._parse_system_goals()
        self._parse_component_goals()
        self._parse_platform_goals()

    def _parse_user_goals(self):
        """Parse user-level goals from config"""
        user_goals = self.config.get('goals', {}).get('user_goals', {})

        for goal_key, goal_data in user_goals.items():
            goal = Goal(
                goal_id=f"user_{goal_key}",
                name=goal_data.get('description', goal_key),
                description=goal_data.get('description', ''),
                level=GoalLevel.USER,
                metrics=goal_data.get('metrics', {}),
                optimization_strategy=goal_data.get('optimization_strategy', 'default'),
                metadata=goal_data
            )
            self.goals[goal.goal_id] = goal

    def _parse_system_goals(self):
        """Parse system-level goals from config"""
        system_goals = self.config.get('goals', {}).get('system_goals', {})

        for goal_key, goal_data in system_goals.items():
            goal = Goal(
                goal_id=f"system_{goal_key}",
                name=goal_data.get('description', goal_key),
                description=goal_data.get('description', ''),
                level=GoalLevel.SYSTEM,
                metrics=goal_data.get('metrics', {}),
                optimization_strategy=goal_data.get('optimization_strategy', 'default'),
                metadata=goal_data
            )
            self.goals[goal.goal_id] = goal

    def _parse_component_goals(self):
        """Parse component-level goals from config"""
        component_goals = self.config.get('goals', {}).get('component_goals', {})

        for component_name, goal_data in component_goals.items():
            goal = Goal(
                goal_id=f"component_{component_name}",
                name=goal_data.get('description', component_name),
                description=goal_data.get('description', ''),
                level=GoalLevel.COMPONENT,
                metrics=goal_data.get('metrics', {}),
                optimization_strategy=goal_data.get('optimization_strategy', 'default'),
                metadata={'component': component_name, **goal_data}
            )
            self.goals[goal.goal_id] = goal

    def _parse_platform_goals(self):
        """Parse platform-level goals from config"""
        platform_goals = self.config.get('goals', {}).get('platform_goals', {})

        for goal_key, goal_data in platform_goals.items():
            goal = Goal(
                goal_id=f"platform_{goal_key}",
                name=goal_data.get('description', goal_key),
                description=goal_data.get('description', ''),
                level=GoalLevel.PLATFORM,
                metrics=goal_data.get('metrics', {}),
                optimization_strategy=goal_data.get('optimization_strategy', 'default'),
                metadata=goal_data
            )
            self.goals[goal.goal_id] = goal

    def track_progress(
        self,
        goal_id: str,
        current_values: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> GoalProgress:
        """
        Track progress toward a goal

        Args:
            goal_id: ID of goal to track
            current_values: Current metric values
            context: Additional context (start_time, etc.)

        Returns:
            GoalProgress object with status and suggestions
        """
        if goal_id not in self.goals:
            raise ValueError(f"Goal not found: {goal_id}")

        goal = self.goals[goal_id]
        goal.current_values = current_values
        goal.last_updated = datetime.utcnow().isoformat()

        # Calculate progress for each metric
        progress_scores = []

        for metric_key, target_value in goal.metrics.items():
            current_value = current_values.get(metric_key)

            if current_value is not None:
                # Calculate progress percentage
                progress_pct = self._calculate_progress(
                    metric_key, current_value, target_value
                )
                progress_scores.append(progress_pct)

        # Overall progress is average of all metrics
        if progress_scores:
            overall_progress = sum(progress_scores) / len(progress_scores)
        else:
            overall_progress = 0.0

        goal.progress_percent = overall_progress

        # Determine status based on progress and time
        status = self._determine_status(goal, overall_progress, context)
        goal.status = status

        # Generate suggestions if at risk
        suggestions = []
        if status in [GoalStatus.AT_RISK, GoalStatus.BEHIND]:
            suggestions = self._generate_suggestions(goal, context)

        # Create progress object
        progress = GoalProgress(
            goal_id=goal_id,
            current_value=current_values,
            target_value=goal.metrics,
            progress_percent=overall_progress,
            status=status,
            suggested_actions=suggestions
        )

        # Add time estimates if context provided
        if context and 'start_time' in context:
            start_time = datetime.fromisoformat(context['start_time'])
            now = datetime.utcnow()
            elapsed = (now - start_time).total_seconds()

            progress.time_elapsed = elapsed

            # Estimate completion time
            if overall_progress > 0:
                estimated_total_time = elapsed / (overall_progress / 100)
                estimated_completion = start_time + timedelta(seconds=estimated_total_time)
                progress.estimated_completion = estimated_completion.isoformat()
                progress.time_remaining = estimated_total_time - elapsed

        self.progress_history.append(progress)

        return progress

    def _calculate_progress(
        self,
        metric_key: str,
        current_value: Any,
        target_value: Any
    ) -> float:
        """
        Calculate progress percentage for a metric

        Returns:
            Progress percentage (0-100)
        """
        # Handle different metric types

        # Percentage metrics (e.g., target_uptime_percent)
        if 'percent' in metric_key.lower():
            if target_value == 0:
                return 100.0 if current_value == 0 else 0.0
            return min(100.0, (current_value / target_value) * 100)

        # Time-based metrics (e.g., target_completion_days)
        if 'days' in metric_key.lower() or 'time' in metric_key.lower():
            # For time metrics, less is better
            if current_value <= target_value:
                return 100.0
            else:
                # Penalize being over target
                return max(0.0, 100.0 - ((current_value - target_value) / target_value * 100))

        # Count metrics (e.g., target_risks_identified_min)
        if 'count' in metric_key.lower() or 'min' in metric_key.lower():
            if target_value == 0:
                return 100.0
            return min(100.0, (current_value / target_value) * 100)

        # Score metrics (0.0 - 1.0 scale)
        if 'score' in metric_key.lower():
            if target_value == 0:
                return 100.0 if current_value == 0 else 0.0
            return min(100.0, (current_value / target_value) * 100)

        # Default: linear progress
        if target_value == 0:
            return 100.0 if current_value == 0 else 0.0
        return min(100.0, (current_value / target_value) * 100)

    def _determine_status(
        self,
        goal: Goal,
        progress_percent: float,
        context: Optional[Dict[str, Any]]
    ) -> GoalStatus:
        """
        Determine goal status based on progress and time

        Returns:
            GoalStatus
        """
        # Check if goal achieved
        if progress_percent >= 100.0:
            return GoalStatus.ACHIEVED

        # If no time context, use progress thresholds
        if not context or 'start_time' not in context:
            if progress_percent >= 80:
                return GoalStatus.ON_TRACK
            elif progress_percent >= 50:
                return GoalStatus.AT_RISK
            else:
                return GoalStatus.BEHIND

        # Calculate time progress
        start_time = datetime.fromisoformat(context['start_time'])
        now = datetime.utcnow()
        elapsed = (now - start_time).total_seconds()

        # Get target duration from goal metadata
        target_duration = self._get_target_duration(goal)

        if target_duration:
            time_progress_percent = (elapsed / target_duration) * 100

            # Compare time progress vs work progress
            if progress_percent >= time_progress_percent:
                return GoalStatus.ON_TRACK
            elif progress_percent >= time_progress_percent * 0.7:
                return GoalStatus.AT_RISK
            elif elapsed < target_duration:
                return GoalStatus.BEHIND
            else:
                # Time exceeded and not complete
                return GoalStatus.FAILED

        # Fallback to progress-only thresholds
        if progress_percent >= 70:
            return GoalStatus.ON_TRACK
        elif progress_percent >= 40:
            return GoalStatus.AT_RISK
        else:
            return GoalStatus.BEHIND

    def _get_target_duration(self, goal: Goal) -> Optional[float]:
        """
        Extract target duration in seconds from goal metrics

        Returns:
            Duration in seconds, or None if not found
        """
        metrics = goal.metrics

        # Check for common time metrics
        if 'target_completion_days' in metrics:
            return metrics['target_completion_days'] * 86400  # days to seconds

        if 'target_completion_hours' in metrics:
            return metrics['target_completion_hours'] * 3600

        if 'target_response_minutes' in metrics:
            return metrics['target_response_minutes'] * 60

        # Check metadata for fallback duration
        if 'fallback_days' in goal.metadata:
            return goal.metadata['fallback_days'] * 86400

        return None

    def _generate_suggestions(
        self,
        goal: Goal,
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate optimization suggestions for at-risk goal

        Returns:
            List of actionable suggestions
        """
        suggestions = []
        strategy = goal.optimization_strategy

        # Get strategy configuration from config
        strategy_config = self.config.get('coordination', {}).get(
            'goal_driven_optimization', {}
        ).get('strategies', {}).get(strategy, {})

        if not strategy_config:
            # Fallback generic suggestions
            suggestions.append(f"Review progress on '{goal.name}' - currently behind target")
            return suggestions

        # Check if strategy trigger condition met
        trigger = strategy_config.get('trigger', '')
        action = strategy_config.get('action', '')

        # Parse trigger condition
        if self._evaluate_trigger(trigger, goal, context):
            suggestions.append(f"Trigger: {trigger}")
            suggestions.append(f"Action: {action}")

            # Add strategy-specific suggestions
            if strategy == 'suggest_faster_path':
                suggestions.append("Consider using ML recommendations for similar cases")
                suggestions.append("Review Case Library for successful shortcuts")

            elif strategy == 'template_based_acceleration':
                suggestions.append("Use pre-built templates to accelerate workflow")
                suggestions.append("Import best-practice configurations from Case Library")

            elif strategy == 'auto_scale_if_slow':
                suggestions.append("System performance below target - consider auto-scaling")
                suggestions.append("Review resource utilization metrics")

            elif strategy == 'self_healing':
                suggestions.append("Governance rule violation detected - attempting auto-remediation")
                suggestions.append("Check audit log for violation details")

        return suggestions

    def _evaluate_trigger(
        self,
        trigger: str,
        goal: Goal,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Evaluate trigger condition string

        Args:
            trigger: Condition string (e.g., "goal_progress < 50% && time_remaining < 50%")
            goal: Goal to evaluate
            context: Context data

        Returns:
            True if trigger condition met
        """
        # Simple evaluation - in production, use safer eval or AST parser
        try:
            # Replace variables with actual values
            trigger_eval = trigger
            trigger_eval = trigger_eval.replace('goal_progress', str(goal.progress_percent))

            if context and 'start_time' in context:
                start_time = datetime.fromisoformat(context['start_time'])
                now = datetime.utcnow()
                elapsed = (now - start_time).total_seconds()
                target_duration = self._get_target_duration(goal) or 1
                time_remaining_pct = ((target_duration - elapsed) / target_duration) * 100
                trigger_eval = trigger_eval.replace('time_remaining', str(time_remaining_pct))

            # Replace operators
            trigger_eval = trigger_eval.replace('&&', ' and ')
            trigger_eval = trigger_eval.replace('||', ' or ')
            trigger_eval = trigger_eval.replace('%', '')

            # Safe evaluation (only allow comparison operators)
            allowed_chars = set('0123456789.<>= ()andornot')
            if all(c in allowed_chars or c.isspace() for c in trigger_eval):
                return eval(trigger_eval)
            else:
                return False

        except Exception:
            return False

    def get_optimization_suggestions(
        self,
        level: Optional[GoalLevel] = None
    ) -> List[OptimizationSuggestion]:
        """
        Get all active optimization suggestions

        Args:
            level: Filter by goal level (user, system, component, platform)

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        for goal in self.goals.values():
            if level and goal.level != level:
                continue

            if goal.status in [GoalStatus.AT_RISK, GoalStatus.BEHIND]:
                suggestion_actions = self._generate_suggestions(goal, None)

                if suggestion_actions:
                    # Determine priority based on status
                    priority = 'high' if goal.status == GoalStatus.BEHIND else 'medium'

                    suggestion = OptimizationSuggestion(
                        goal_id=goal.goal_id,
                        goal_name=goal.name,
                        strategy=goal.optimization_strategy,
                        priority=priority,
                        actions=suggestion_actions,
                        expected_impact=f"Improve progress from {goal.progress_percent:.1f}% toward 100%",
                        timestamp=datetime.utcnow().isoformat()
                    )
                    suggestions.append(suggestion)

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 999))

        return suggestions

    def get_goal_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of all goal statuses

        Returns:
            Summary dict with counts and overall health
        """
        total = len(self.goals)
        achieved = sum(1 for g in self.goals.values() if g.status == GoalStatus.ACHIEVED)
        on_track = sum(1 for g in self.goals.values() if g.status == GoalStatus.ON_TRACK)
        at_risk = sum(1 for g in self.goals.values() if g.status == GoalStatus.AT_RISK)
        behind = sum(1 for g in self.goals.values() if g.status == GoalStatus.BEHIND)
        failed = sum(1 for g in self.goals.values() if g.status == GoalStatus.FAILED)

        # Overall health score (0-100)
        health_score = ((achieved * 100 + on_track * 80 + at_risk * 50 + behind * 20) / total) if total > 0 else 0

        return {
            'total_goals': total,
            'achieved': achieved,
            'on_track': on_track,
            'at_risk': at_risk,
            'behind': behind,
            'failed': failed,
            'overall_health_score': health_score,
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_goals_by_level(self, level: GoalLevel) -> List[Goal]:
        """Get all goals for a specific level"""
        return [g for g in self.goals.values() if g.level == level]

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get specific goal by ID"""
        return self.goals.get(goal_id)


# ============= SYSTEM SELF-MONITORING =============

class SystemGoalsMonitor:
    """
    Monitor system-level goals (Workflow Intelligence monitoring itself)

    This is the "eat own dog food" implementation - the system tracks
    its own performance against goals and takes corrective action.
    """

    def __init__(self, goals_engine: GoalsEngine):
        self.goals_engine = goals_engine
        self.last_check: Optional[datetime] = None

    async def check_system_performance(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Check Workflow Intelligence performance against system goals

        Args:
            metrics: Current system metrics (response_time_ms, ml_accuracy, etc.)

        Returns:
            List of actions to take (e.g., ["scale_up", "trigger_retraining"])
        """
        actions = []

        # Track performance goal
        perf_goal_id = "system_performance"
        if perf_goal_id in self.goals_engine.goals:
            progress = self.goals_engine.track_progress(
                perf_goal_id,
                metrics,
                context={'start_time': datetime.utcnow().isoformat()}
            )

            if progress.status == GoalStatus.BEHIND:
                actions.append("escalate_performance_issue")
                actions.extend(progress.suggested_actions)

        # Track accuracy goal
        accuracy_goal_id = "system_accuracy"
        if accuracy_goal_id in self.goals_engine.goals:
            progress = self.goals_engine.track_progress(
                accuracy_goal_id,
                metrics,
                context={'start_time': datetime.utcnow().isoformat()}
            )

            if progress.status in [GoalStatus.AT_RISK, GoalStatus.BEHIND]:
                actions.append("trigger_model_retraining")

        self.last_check = datetime.utcnow()

        return actions
