"""
Scenario Intelligence Events for EventBus Integration

Defines events for scenario generation, execution, and auto-regeneration.
Extends existing event_definitions.py with generation-specific events.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class ScenarioGenerationTrigger(str, Enum):
    """What triggered scenario generation"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    SERVICE_ADDED = "service_added"
    SERVICE_UPDATED = "service_updated"
    SERVICE_REMOVED = "service_removed"
    CATALOG_REFRESH = "catalog_refresh"


class ScenarioLevel(str, Enum):
    """Scenario levels"""
    L1_PLATFORM = "l1_platform"
    L1_APPLICATION = "l1_application"
    L2_SUBSYSTEM = "l2"
    L3_SYSTEM = "l3"
    L4_WORKFLOW = "l4"


@dataclass
class ScenarioGeneratedEvent:
    """Published when new scenarios are generated"""
    scenario_ids: List[str]
    level: str  # ScenarioLevel
    generator: str  # "l1_platform", "l2", etc.
    count: int
    trigger: str  # ScenarioGenerationTrigger
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioUpdatedEvent:
    """Published when scenario is updated"""
    scenario_id: str
    old_version: str
    new_version: str
    changes: Dict[str, Any]
    reason: str  # "auto_regeneration", "manual_edit", "service_updated"
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioExecutedEvent:
    """Published when scenario is executed"""
    scenario_id: str
    execution_id: str
    status: str  # success, failed, timeout, partial
    duration_ms: float
    steps_executed: int
    steps_failed: int
    timestamp: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ServiceCatalogUpdatedEvent:
    """Subscribed to - triggers regeneration"""
    service_name: str
    change_type: str  # added, removed, updated
    service_data: Dict[str, Any]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioRegenerationTriggeredEvent:
    """Published when auto-regeneration is triggered"""
    trigger_event: str  # Original event type that triggered regeneration
    affected_services: List[str]
    affected_levels: List[str]
    regeneration_id: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioRegenerationCompletedEvent:
    """Published when auto-regeneration completes"""
    regeneration_id: str
    trigger_event: str
    scenarios_generated: int
    scenarios_updated: int
    scenarios_deprecated: int
    duration_ms: float
    timestamp: str
    status: str  # success, partial, failed
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioDeprecatedEvent:
    """Published when scenario is deprecated (service removed)"""
    scenario_id: str
    reason: str
    replaced_by: Optional[str]  # New scenario ID if replaced
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScenarioPatternDetectedEvent:
    """Published when pattern is detected across scenarios"""
    pattern_type: str
    scenario_ids: List[str]
    confidence: float
    pattern_data: Dict[str, Any]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Event type constants for EventBus routing
class ScenarioEventTypes:
    """Event types for EventBus routing"""

    # Generation events
    SCENARIO_GENERATED = "scenario.generated"
    SCENARIO_UPDATED = "scenario.updated"
    SCENARIO_EXECUTED = "scenario.executed"
    SCENARIO_DEPRECATED = "scenario.deprecated"

    # Regeneration events
    REGENERATION_TRIGGERED = "scenario.regeneration.triggered"
    REGENERATION_COMPLETED = "scenario.regeneration.completed"

    # Pattern detection
    PATTERN_DETECTED = "scenario.pattern.detected"

    # Subscribed events (from other services)
    SERVICE_CATALOG_UPDATED = "service.catalog.updated"
    SERVICE_ADDED = "service.added"
    SERVICE_REMOVED = "service.removed"
    SERVICE_UPDATED = "service.updated"
    SERVICE_HEALTH_CHANGED = "service.health.changed"


# Helper functions to create events
def create_scenario_generated_event(
    scenario_ids: List[str],
    level: str,
    generator: str,
    trigger: str = ScenarioGenerationTrigger.MANUAL,
    metadata: Optional[Dict[str, Any]] = None
) -> ScenarioGeneratedEvent:
    """Create a scenario generated event"""
    return ScenarioGeneratedEvent(
        scenario_ids=scenario_ids,
        level=level,
        generator=generator,
        count=len(scenario_ids),
        trigger=trigger,
        timestamp=datetime.utcnow().isoformat(),
        metadata=metadata
    )


def create_scenario_updated_event(
    scenario_id: str,
    old_version: str,
    new_version: str,
    changes: Dict[str, Any],
    reason: str = "manual_edit",
    metadata: Optional[Dict[str, Any]] = None
) -> ScenarioUpdatedEvent:
    """Create a scenario updated event"""
    return ScenarioUpdatedEvent(
        scenario_id=scenario_id,
        old_version=old_version,
        new_version=new_version,
        changes=changes,
        reason=reason,
        timestamp=datetime.utcnow().isoformat(),
        metadata=metadata
    )


def create_scenario_executed_event(
    scenario_id: str,
    execution_id: str,
    status: str,
    duration_ms: float,
    steps_executed: int = 0,
    steps_failed: int = 0,
    error: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ScenarioExecutedEvent:
    """Create a scenario executed event"""
    return ScenarioExecutedEvent(
        scenario_id=scenario_id,
        execution_id=execution_id,
        status=status,
        duration_ms=duration_ms,
        steps_executed=steps_executed,
        steps_failed=steps_failed,
        timestamp=datetime.utcnow().isoformat(),
        error=error,
        metadata=metadata
    )


def create_regeneration_triggered_event(
    trigger_event: str,
    affected_services: List[str],
    affected_levels: List[str],
    regeneration_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> ScenarioRegenerationTriggeredEvent:
    """Create a regeneration triggered event"""
    return ScenarioRegenerationTriggeredEvent(
        trigger_event=trigger_event,
        affected_services=affected_services,
        affected_levels=affected_levels,
        regeneration_id=regeneration_id,
        timestamp=datetime.utcnow().isoformat(),
        metadata=metadata
    )


def create_regeneration_completed_event(
    regeneration_id: str,
    trigger_event: str,
    scenarios_generated: int,
    scenarios_updated: int,
    scenarios_deprecated: int,
    duration_ms: float,
    status: str = "success",
    errors: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ScenarioRegenerationCompletedEvent:
    """Create a regeneration completed event"""
    return ScenarioRegenerationCompletedEvent(
        regeneration_id=regeneration_id,
        trigger_event=trigger_event,
        scenarios_generated=scenarios_generated,
        scenarios_updated=scenarios_updated,
        scenarios_deprecated=scenarios_deprecated,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow().isoformat(),
        status=status,
        errors=errors,
        metadata=metadata
    )
