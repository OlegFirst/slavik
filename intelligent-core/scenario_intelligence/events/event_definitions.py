"""
Event Definitions for Scenario Intelligence

Defines all EventBus events published and consumed by Scenario Intelligence.
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime


class ScenarioEventType(str, Enum):
    """Event types published by Scenario Intelligence"""

    # Scenario Lifecycle
    SCENARIO_REGISTERED = "scenario.registered"
    SCENARIO_UPDATED = "scenario.updated"
    SCENARIO_DELETED = "scenario.deleted"

    # Scenario Execution
    SCENARIO_EXECUTION_STARTED = "scenario.execution.started"
    SCENARIO_EXECUTION_STEP_COMPLETED = "scenario.execution.step.completed"
    SCENARIO_EXECUTION_COMPLETED = "scenario.execution.completed"
    SCENARIO_EXECUTION_FAILED = "scenario.execution.failed"
    SCENARIO_EXECUTION_TIMEOUT = "scenario.execution.timeout"

    # Scenario Generation (Auto-Generator)
    SCENARIO_GENERATION_STARTED = "scenario.generation.started"
    SCENARIO_GENERATION_COMPLETED = "scenario.generation.completed"
    SCENARIO_GENERATION_FAILED = "scenario.generation.failed"

    # Scenario Learning
    SCENARIO_PATTERN_DETECTED = "scenario.pattern.detected"
    SCENARIO_LEARNED = "scenario.learned"
    SCENARIO_OPTIMIZED = "scenario.optimized"

    # Integration Events
    SCENARIO_CONVERTED_TO_EXERCISE = "scenario.converted.to_exercise"
    SCENARIO_VALIDATED_BY_COMMUNITY = "scenario.validated.by_community"
    SCENARIO_SAFETY_CHECKED = "scenario.safety.checked"


class SubscribedEventType(str, Enum):
    """Event types consumed by Scenario Intelligence"""

    # From Simulation Service
    EXERCISE_CREATED = "exercise.created"
    SIMULATION_STARTED = "simulation.started"
    SIMULATION_COMPLETED = "simulation.completed"
    SIMULATION_FAILED = "simulation.failed"

    # From AI Orchestration
    AI_TASK_COMPLETED = "ai.task.completed"
    AI_TASK_FAILED = "ai.task.failed"
    SAFETY_CHECK_COMPLETED = "safety.check.completed"

    # From Community Intelligence
    COMMUNITY_VALIDATION_COMPLETED = "community.validation.completed"
    CONSENSUS_REACHED = "consensus.reached"

    # From Predictive Intelligence
    PREDICTION_COMPLETED = "prediction.completed"
    ANOMALY_DETECTED = "anomaly.detected"

    # From Event Intelligence
    PATTERN_DETECTED = "event.pattern.detected"
    COMPLEX_EVENT_DETECTED = "complex.event.detected"

    # From Workflow Intelligence
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    PDCA_CYCLE_COMPLETED = "pdca.cycle.completed"

    # From BCM Service
    COMPLIANCE_VALIDATION_COMPLETED = "compliance.validation.completed"
    FRAMEWORK_SCENARIOS_LOADED = "framework.scenarios.loaded"

    # System Events
    SYSTEM_HEALTH_DEGRADED = "system.health.degraded"
    SYSTEM_RECOVERED = "system.recovered"


class ScenarioEvent:
    """Base class for Scenario Intelligence events"""

    def __init__(
        self,
        event_type: ScenarioEventType,
        payload: Dict[str, Any],
        priority: str = "normal",
        correlation_id: Optional[str] = None
    ):
        self.event_type = event_type
        self.payload = payload
        self.priority = priority  # low, normal, high, critical
        self.correlation_id = correlation_id or self._generate_correlation_id()
        self.timestamp = datetime.utcnow().isoformat()

    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID"""
        import uuid
        return f"scenario-{uuid.uuid4()}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for EventBus"""
        return {
            "event_type": self.event_type.value,
            "payload": self.payload,
            "priority": self.priority,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "source": "scenario-intelligence"
        }


# =============================================================================
# Event Builders (Helper functions to create events)
# =============================================================================

def build_scenario_registered_event(
    scenario_id: str,
    scenario_name: str,
    level: int,
    scenario_type: str
) -> ScenarioEvent:
    """Build scenario.registered event"""
    return ScenarioEvent(
        event_type=ScenarioEventType.SCENARIO_REGISTERED,
        payload={
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "level": level,
            "scenario_type": scenario_type
        },
        priority="normal"
    )


def build_scenario_execution_started_event(
    scenario_id: str,
    execution_id: str,
    context: Dict[str, Any]
) -> ScenarioEvent:
    """Build scenario.execution.started event"""
    return ScenarioEvent(
        event_type=ScenarioEventType.SCENARIO_EXECUTION_STARTED,
        payload={
            "scenario_id": scenario_id,
            "execution_id": execution_id,
            "context": context
        },
        priority="normal"
    )


def build_scenario_execution_completed_event(
    scenario_id: str,
    execution_id: str,
    result: str,
    duration_ms: int,
    metrics: Dict[str, Any]
) -> ScenarioEvent:
    """Build scenario.execution.completed event"""
    return ScenarioEvent(
        event_type=ScenarioEventType.SCENARIO_EXECUTION_COMPLETED,
        payload={
            "scenario_id": scenario_id,
            "execution_id": execution_id,
            "result": result,  # "success", "failure", "partial"
            "duration_ms": duration_ms,
            "metrics": metrics
        },
        priority="normal"
    )


def build_scenario_execution_failed_event(
    scenario_id: str,
    execution_id: str,
    error: str,
    error_step: Optional[str] = None
) -> ScenarioEvent:
    """Build scenario.execution.failed event"""
    return ScenarioEvent(
        event_type=ScenarioEventType.SCENARIO_EXECUTION_FAILED,
        payload={
            "scenario_id": scenario_id,
            "execution_id": execution_id,
            "error": error,
            "error_step": error_step
        },
        priority="high"  # Failures are high priority
    )


def build_scenario_generation_completed_event(
    scenario_id: str,
    level: int,
    generation_method: str,
    adapters_used: list[str]
) -> ScenarioEvent:
    """Build scenario.generation.completed event"""
    return ScenarioEvent(
        event_type=ScenarioEventType.SCENARIO_GENERATION_COMPLETED,
        payload={
            "scenario_id": scenario_id,
            "level": level,
            "generation_method": generation_method,  # "auto_generator", "manual", "template"
            "adapters_used": adapters_used
        },
        priority="normal"
    )


def build_scenario_pattern_detected_event(
    scenario_id: str,
    pattern_type: str,
    pattern_data: Dict[str, Any],
    confidence: float
) -> ScenarioEvent:
    """Build scenario.pattern.detected event"""
    return ScenarioEvent(
        event_type=ScenarioEventType.SCENARIO_PATTERN_DETECTED,
        payload={
            "scenario_id": scenario_id,
            "pattern_type": pattern_type,
            "pattern_data": pattern_data,
            "confidence": confidence
        },
        priority="normal"
    )


def build_scenario_learned_event(
    scenario_id: str,
    learning_type: str,
    improvements: list[str],
    new_patterns: int
) -> ScenarioEvent:
    """Build scenario.learned event"""
    return ScenarioEvent(
        event_type=ScenarioEventType.SCENARIO_LEARNED,
        payload={
            "scenario_id": scenario_id,
            "learning_type": learning_type,  # "from_execution", "from_simulation", "from_feedback"
            "improvements": improvements,
            "new_patterns": new_patterns
        },
        priority="normal"
    )


def build_scenario_converted_to_exercise_event(
    scenario_id: str,
    exercise_id: str,
    exercise_type: str
) -> ScenarioEvent:
    """Build scenario.converted.to_exercise event"""
    return ScenarioEvent(
        event_type=ScenarioEventType.SCENARIO_CONVERTED_TO_EXERCISE,
        payload={
            "scenario_id": scenario_id,
            "exercise_id": exercise_id,
            "exercise_type": exercise_type
        },
        priority="normal"
    )


# =============================================================================
# Event Priority Rules
# =============================================================================

EVENT_PRIORITY_MAP = {
    # Critical - System health, security
    ScenarioEventType.SCENARIO_EXECUTION_FAILED: "high",
    ScenarioEventType.SCENARIO_EXECUTION_TIMEOUT: "high",
    ScenarioEventType.SCENARIO_SAFETY_CHECKED: "high",

    # High - Important operations
    ScenarioEventType.SCENARIO_GENERATION_FAILED: "high",
    ScenarioEventType.SCENARIO_EXECUTION_COMPLETED: "normal",

    # Normal - Regular operations
    ScenarioEventType.SCENARIO_REGISTERED: "normal",
    ScenarioEventType.SCENARIO_EXECUTION_STARTED: "normal",
    ScenarioEventType.SCENARIO_GENERATION_STARTED: "normal",
    ScenarioEventType.SCENARIO_GENERATION_COMPLETED: "normal",
    ScenarioEventType.SCENARIO_PATTERN_DETECTED: "normal",
    ScenarioEventType.SCENARIO_LEARNED: "normal",
    ScenarioEventType.SCENARIO_CONVERTED_TO_EXERCISE: "normal",

    # Low - Informational
    ScenarioEventType.SCENARIO_UPDATED: "low",
    ScenarioEventType.SCENARIO_OPTIMIZED: "low",
}


def get_event_priority(event_type: ScenarioEventType) -> str:
    """Get priority for event type"""
    return EVENT_PRIORITY_MAP.get(event_type, "normal")
