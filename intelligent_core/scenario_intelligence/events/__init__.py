"""
Scenario Intelligence Events Module

Provides:
- event_definitions: Event type definitions
- event_handlers: Event handlers for subscribed events
- event_publisher: Event publishing utilities
"""

from .event_definitions import (
    ScenarioEventType,
    SubscribedEventType,
    ScenarioEvent,
    build_scenario_registered_event,
    build_scenario_execution_started_event,
    build_scenario_execution_completed_event,
    build_scenario_execution_failed_event,
    build_scenario_generation_completed_event,
    build_scenario_pattern_detected_event,
    build_scenario_learned_event,
    build_scenario_converted_to_exercise_event,
    get_event_priority
)

from .event_handlers import (
    ScenarioEventHandlers,
    get_event_handlers
)

__all__ = [
    # Event Types
    "ScenarioEventType",
    "SubscribedEventType",
    "ScenarioEvent",

    # Event Builders
    "build_scenario_registered_event",
    "build_scenario_execution_started_event",
    "build_scenario_execution_completed_event",
    "build_scenario_execution_failed_event",
    "build_scenario_generation_completed_event",
    "build_scenario_pattern_detected_event",
    "build_scenario_learned_event",
    "build_scenario_converted_to_exercise_event",
    "get_event_priority",

    # Event Handlers
    "ScenarioEventHandlers",
    "get_event_handlers",
]
