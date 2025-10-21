"""
Scenario Intelligence Client for MIO Manager

Subscribes to scenario events and monitors scenario health.
"""

import logging
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class ScenarioIntelligenceClient:
    """
    Client for monitoring Scenario Intelligence events

    Subscribes to:
    - scenario.generated
    - scenario.executed
    - scenario.regeneration.triggered
    - scenario.regeneration.completed
    """

    def __init__(self, eventbus_client):
        """
        Initialize Scenario Intelligence client

        Args:
            eventbus_client: EventBus client instance
        """
        self.eventbus = eventbus_client
        self._subscriptions_active = False

        # Metrics tracking
        self.metrics = {
            "scenarios_generated": 0,
            "scenarios_executed": 0,
            "scenarios_failed": 0,
            "regenerations_triggered": 0,
            "regenerations_completed": 0,
            "last_generation": None,
            "last_execution": None,
            "last_regeneration": None
        }

        logger.info("ScenarioIntelligenceClient initialized")

    async def subscribe_to_events(self):
        """Subscribe to Scenario Intelligence events"""
        if self._subscriptions_active:
            logger.warning("Already subscribed to scenario events")
            return

        try:
            # Subscribe to scenario generation events
            await self.eventbus.subscribe(
                'scenario.generated',
                self.handle_scenario_generated
            )

            # Subscribe to scenario execution events
            await self.eventbus.subscribe(
                'scenario.executed',
                self.handle_scenario_executed
            )

            # Subscribe to regeneration events
            await self.eventbus.subscribe(
                'scenario.regeneration.triggered',
                self.handle_regeneration_triggered
            )

            await self.eventbus.subscribe(
                'scenario.regeneration.completed',
                self.handle_regeneration_completed
            )

            # Subscribe to pattern detection
            await self.eventbus.subscribe(
                'scenario.pattern.detected',
                self.handle_pattern_detected
            )

            self._subscriptions_active = True
            logger.info(" Subscribed to Scenario Intelligence events")

        except Exception as e:
            logger.error(f"Failed to subscribe to scenario events: {e}", exc_info=True)
            raise

    async def handle_scenario_generated(self, event):
        """
        Handle scenario.generated event

        Args:
            event: EventBus event
        """
        try:
            data = event.data if hasattr(event, 'data') else event

            scenario_ids = data.get('scenario_ids', [])
            level = data.get('level')
            generator = data.get('generator')
            count = data.get('count', len(scenario_ids))
            trigger = data.get('trigger', 'unknown')

            logger.info(
                f" Scenarios Generated: level={level}, generator={generator}, "
                f"count={count}, trigger={trigger}"
            )

            # Update metrics
            self.metrics["scenarios_generated"] += count
            self.metrics["last_generation"] = {
                "level": level,
                "generator": generator,
                "count": count,
                "trigger": trigger,
                "timestamp": data.get('timestamp')
            }

            # Alert if many scenarios generated (potential issue)
            if count > 100:
                logger.warning(
                    f"️  Large batch of scenarios generated: {count} scenarios "
                    f"(level={level}, generator={generator})"
                )

        except Exception as e:
            logger.error(f"Error handling scenario.generated event: {e}", exc_info=True)

    async def handle_scenario_executed(self, event):
        """
        Handle scenario.executed event

        Args:
            event: EventBus event
        """
        try:
            data = event.data if hasattr(event, 'data') else event

            scenario_id = data.get('scenario_id')
            execution_id = data.get('execution_id')
            status = data.get('status')
            duration_ms = data.get('duration_ms', 0)
            steps_executed = data.get('steps_executed', 0)
            steps_failed = data.get('steps_failed', 0)
            error = data.get('error')

            logger.info(
                f" Scenario Executed: id={scenario_id}, status={status}, "
                f"duration={duration_ms}ms, steps={steps_executed}/{steps_executed + steps_failed}"
            )

            # Update metrics
            self.metrics["scenarios_executed"] += 1
            if status == 'failed':
                self.metrics["scenarios_failed"] += 1

            self.metrics["last_execution"] = {
                "scenario_id": scenario_id,
                "execution_id": execution_id,
                "status": status,
                "duration_ms": duration_ms,
                "timestamp": data.get('timestamp')
            }

            # Alert on failures
            if status == 'failed':
                logger.error(
                    f" Scenario Execution Failed: id={scenario_id}, "
                    f"execution={execution_id}, error={error}"
                )

                # TODO: Trigger remediation action
                # - Alert DevOps Agent
                # - Create incident ticket
                # - Add to investigation queue

            # Alert on slow executions
            if duration_ms > 30000:  # > 30 seconds
                logger.warning(
                    f"️  Slow Scenario Execution: id={scenario_id}, "
                    f"duration={duration_ms}ms ({duration_ms / 1000:.1f}s)"
                )

        except Exception as e:
            logger.error(f"Error handling scenario.executed event: {e}", exc_info=True)

    async def handle_regeneration_triggered(self, event):
        """
        Handle scenario.regeneration.triggered event

        Args:
            event: EventBus event
        """
        try:
            data = event.data if hasattr(event, 'data') else event

            regeneration_id = data.get('regeneration_id')
            trigger_event = data.get('trigger_event')
            affected_services = data.get('affected_services', [])
            affected_levels = data.get('affected_levels', [])

            logger.info(
                f" Regeneration Triggered: id={regeneration_id}, "
                f"trigger={trigger_event}, services={len(affected_services)}, "
                f"levels={affected_levels}"
            )

            # Update metrics
            self.metrics["regenerations_triggered"] += 1
            self.metrics["last_regeneration"] = {
                "regeneration_id": regeneration_id,
                "trigger_event": trigger_event,
                "affected_services": affected_services,
                "affected_levels": affected_levels,
                "status": "triggered",
                "timestamp": data.get('timestamp')
            }

        except Exception as e:
            logger.error(f"Error handling regeneration.triggered event: {e}", exc_info=True)

    async def handle_regeneration_completed(self, event):
        """
        Handle scenario.regeneration.completed event

        Args:
            event: EventBus event
        """
        try:
            data = event.data if hasattr(event, 'data') else event

            regeneration_id = data.get('regeneration_id')
            status = data.get('status')
            scenarios_generated = data.get('scenarios_generated', 0)
            scenarios_updated = data.get('scenarios_updated', 0)
            scenarios_deprecated = data.get('scenarios_deprecated', 0)
            duration_ms = data.get('duration_ms', 0)
            errors = data.get('errors', [])

            logger.info(
                f" Regeneration Completed: id={regeneration_id}, status={status}, "
                f"generated={scenarios_generated}, updated={scenarios_updated}, "
                f"deprecated={scenarios_deprecated}, duration={duration_ms}ms"
            )

            # Update metrics
            self.metrics["regenerations_completed"] += 1
            if self.metrics["last_regeneration"] and \
               self.metrics["last_regeneration"]["regeneration_id"] == regeneration_id:
                self.metrics["last_regeneration"].update({
                    "status": status,
                    "scenarios_generated": scenarios_generated,
                    "scenarios_updated": scenarios_updated,
                    "scenarios_deprecated": scenarios_deprecated,
                    "duration_ms": duration_ms,
                    "completed_at": data.get('timestamp')
                })

            # Alert on failures
            if status == 'failed' or errors:
                logger.error(
                    f" Regeneration Failed: id={regeneration_id}, errors={errors}"
                )

            # Alert on slow regenerations
            if duration_ms > 60000:  # > 1 minute
                logger.warning(
                    f"️  Slow Regeneration: id={regeneration_id}, "
                    f"duration={duration_ms}ms ({duration_ms / 1000:.1f}s)"
                )

        except Exception as e:
            logger.error(f"Error handling regeneration.completed event: {e}", exc_info=True)

    async def handle_pattern_detected(self, event):
        """
        Handle scenario.pattern.detected event

        Args:
            event: EventBus event
        """
        try:
            data = event.data if hasattr(event, 'data') else event

            pattern_type = data.get('pattern_type')
            scenario_ids = data.get('scenario_ids', [])
            confidence = data.get('confidence', 0.0)

            logger.info(
                f" Pattern Detected: type={pattern_type}, "
                f"scenarios={len(scenario_ids)}, confidence={confidence:.2f}"
            )

            # High confidence patterns are worth investigating
            if confidence > 0.8:
                logger.info(
                    f" High-Confidence Pattern: type={pattern_type}, "
                    f"confidence={confidence:.2f} - Consider creating template"
                )

        except Exception as e:
            logger.error(f"Error handling pattern.detected event: {e}", exc_info=True)

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics

        Returns:
            Metrics dictionary
        """
        return self.metrics.copy()

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of Scenario Intelligence

        Returns:
            Health status dictionary
        """
        failure_rate = 0.0
        if self.metrics["scenarios_executed"] > 0:
            failure_rate = (
                self.metrics["scenarios_failed"] / self.metrics["scenarios_executed"]
            ) * 100

        return {
            "status": "healthy" if failure_rate < 10 else "degraded",
            "metrics": self.get_metrics(),
            "failure_rate_percent": failure_rate,
            "subscriptions_active": self._subscriptions_active
        }

    async def close(self):
        """Close client"""
        self._subscriptions_active = False
        logger.info(" ScenarioIntelligenceClient closed")
