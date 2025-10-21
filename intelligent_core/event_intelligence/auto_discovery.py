"""
Auto-Discovery System for Events
=================================

Automatically discovers services, their event patterns, and builds knowledge base.
"""

import logging
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from shared.event_bus import Event, subscribe_to, publish_event

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Registry of all services and their capabilities.
    """

    def __init__(self):
        self._services: Dict[str, Dict] = {}
        self._event_producers: Dict[str, Set[str]] = defaultdict(set)  # event_type -> {services}
        self._event_consumers: Dict[str, Set[str]] = defaultdict(set)  # event_type -> {services}

    def register_service(
        self,
        service_name: str,
        subscriptions: List[str],
        capabilities: Optional[List[str]] = None
    ):
        """Register a service with its subscriptions."""
        self._services[service_name] = {
            "name": service_name,
            "subscriptions": subscriptions,
            "capabilities": capabilities or [],
            "registered_at": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat()
        }

        # Track consumers
        for pattern in subscriptions:
            self._event_consumers[pattern].add(service_name)

        logger.info(
            f" Registered service: {service_name} "
            f"with {len(subscriptions)} subscriptions"
        )

    def record_event_published(self, event_type: str, source: str):
        """Record that a service published an event type."""
        self._event_producers[event_type].add(source)

    def get_service(self, service_name: str) -> Optional[Dict]:
        """Get service info."""
        return self._services.get(service_name)

    def get_all_services(self) -> List[Dict]:
        """Get all registered services."""
        return list(self._services.values())

    def get_producers(self, event_type: str) -> Set[str]:
        """Get services that produce this event type."""
        return self._event_producers.get(event_type, set())

    def get_consumers(self, pattern: str) -> Set[str]:
        """Get services that consume events matching this pattern."""
        return self._event_consumers.get(pattern, set())

    def get_stats(self) -> Dict:
        """Get registry statistics."""
        return {
            "total_services": len(self._services),
            "total_event_types": len(self._event_producers),
            "total_subscriptions": sum(
                len(s["subscriptions"]) for s in self._services.values()
            ),
            "services": list(self._services.keys()),
            "event_types": list(self._event_producers.keys())
        }


class EventPatternLearner:
    """
    Learns patterns from event sequences.
    """

    def __init__(self):
        self._sequences: List[tuple] = []  # (event1_type, event2_type, time_diff)
        self._patterns: Dict[str, Dict] = {}  # pattern_id -> pattern_data

    def record_sequence(self, event1_type: str, event2_type: str, time_diff_seconds: float):
        """Record an event sequence."""
        self._sequences.append((event1_type, event2_type, time_diff_seconds))

        # Update pattern statistics
        pattern_key = f"{event1_type} → {event2_type}"

        if pattern_key not in self._patterns:
            self._patterns[pattern_key] = {
                "from": event1_type,
                "to": event2_type,
                "occurrences": 0,
                "avg_time_seconds": 0,
                "min_time_seconds": float('inf'),
                "max_time_seconds": 0,
                "confidence": 0.0
            }

        pattern = self._patterns[pattern_key]
        pattern["occurrences"] += 1

        # Update timing statistics
        old_avg = pattern["avg_time_seconds"]
        pattern["avg_time_seconds"] = (
            (old_avg * (pattern["occurrences"] - 1) + time_diff_seconds)
            / pattern["occurrences"]
        )
        pattern["min_time_seconds"] = min(pattern["min_time_seconds"], time_diff_seconds)
        pattern["max_time_seconds"] = max(pattern["max_time_seconds"], time_diff_seconds)

        # Calculate confidence (more occurrences = higher confidence)
        pattern["confidence"] = min(pattern["occurrences"] / 100.0, 1.0)

        logger.debug(
            f" Pattern learned: {pattern_key} "
            f"(occurrences: {pattern['occurrences']}, confidence: {pattern['confidence']:.2f})"
        )

    def get_patterns(self, min_confidence: float = 0.0) -> List[Dict]:
        """Get learned patterns with confidence above threshold."""
        return [
            p for p in self._patterns.values()
            if p["confidence"] >= min_confidence
        ]

    def predict_next_event(
        self,
        current_event_type: str,
        min_confidence: float = 0.5
    ) -> Optional[Dict]:
        """
        Predict the most likely next event.

        Returns:
            {
                "event_type": "workflow.completed",
                "confidence": 0.87,
                "expected_time_seconds": 3600
            }
        """
        # Find patterns starting with current event
        matching_patterns = [
            p for p in self._patterns.values()
            if p["from"] == current_event_type and p["confidence"] >= min_confidence
        ]

        if not matching_patterns:
            return None

        # Return pattern with highest confidence
        best_pattern = max(matching_patterns, key=lambda p: p["confidence"])

        return {
            "event_type": best_pattern["to"],
            "confidence": best_pattern["confidence"],
            "expected_time_seconds": best_pattern["avg_time_seconds"]
        }


class AutoDiscoveryEngine:
    """
    Main auto-discovery engine that coordinates everything.
    """

    def __init__(self):
        self.registry = ServiceRegistry()
        self.pattern_learner = EventPatternLearner()
        self._event_history: List[tuple] = []  # (event_type, timestamp, correlation_id)
        self._max_history = 10000

    async def start(self):
        """Start auto-discovery."""
        logger.info(" Starting Auto-Discovery Engine...")

        # Subscribe to service registration events
        @subscribe_to("service.started")
        async def on_service_started(event: Event):
            await self._handle_service_started(event)

        # Subscribe to all events for pattern learning
        @subscribe_to("*")
        async def on_any_event(event: Event):
            await self._handle_any_event(event)

        logger.info(" Auto-Discovery Engine started")

    async def _handle_service_started(self, event: Event):
        """Handle service registration."""
        service_name = event.data.get("service_name")
        subscriptions = event.data.get("subscriptions", [])
        capabilities = event.data.get("capabilities", [])

        if service_name:
            self.registry.register_service(service_name, subscriptions, capabilities)

            # Publish discovery event
            await publish_event(
                event_type="event_intelligence.service_discovered",
                data={
                    "service_name": service_name,
                    "subscriptions": subscriptions,
                    "capabilities": capabilities
                },
                source="event-intelligence"
            )

    async def _handle_any_event(self, event: Event):
        """Learn from all events."""
        # Skip our own events to avoid loops
        if event.source == "event-intelligence":
            return

        # Record producer
        self.registry.record_event_published(event.type, event.source)

        # Add to history
        self._event_history.append((
            event.type,
            datetime.fromisoformat(event.timestamp),
            event.correlation_id
        ))

        # Trim history if too large
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        # Learn sequences (events with same correlation_id)
        await self._learn_sequences(event)

    async def _learn_sequences(self, current_event: Event):
        """Learn event sequences from correlation chains."""
        if not current_event.correlation_id:
            return

        # Find previous event with same correlation_id
        current_timestamp = datetime.fromisoformat(current_event.timestamp)

        for prev_type, prev_timestamp, prev_correlation in reversed(self._event_history[:-1]):
            if prev_correlation == current_event.correlation_id:
                # Found related event!
                time_diff = (current_timestamp - prev_timestamp).total_seconds()

                self.pattern_learner.record_sequence(
                    prev_type,
                    current_event.type,
                    time_diff
                )

                # Only learn from immediate predecessor
                break

    def get_service_registry(self) -> ServiceRegistry:
        """Get the service registry."""
        return self.registry

    def get_pattern_learner(self) -> EventPatternLearner:
        """Get the pattern learner."""
        return self.pattern_learner

    def get_stats(self) -> Dict:
        """Get comprehensive statistics."""
        return {
            "services": self.registry.get_stats(),
            "patterns": {
                "total_patterns": len(self.pattern_learner._patterns),
                "high_confidence_patterns": len(
                    self.pattern_learner.get_patterns(min_confidence=0.7)
                ),
                "sequences_learned": len(self.pattern_learner._sequences)
            },
            "events": {
                "history_size": len(self._event_history),
                "unique_event_types": len(set(e[0] for e in self._event_history))
            }
        }


# Global instance
_discovery_engine: Optional[AutoDiscoveryEngine] = None


async def init_auto_discovery() -> AutoDiscoveryEngine:
    """Initialize auto-discovery engine."""
    global _discovery_engine

    _discovery_engine = AutoDiscoveryEngine()
    await _discovery_engine.start()

    return _discovery_engine


def get_discovery_engine() -> Optional[AutoDiscoveryEngine]:
    """Get auto-discovery engine instance."""
    return _discovery_engine
