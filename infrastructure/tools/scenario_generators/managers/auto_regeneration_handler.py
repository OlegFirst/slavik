"""
Auto-Regeneration Handler for Scenario Intelligence

Handles automatic regeneration of scenarios when service catalog changes.
Subscribes to EventBus events and triggers regeneration as needed.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import uuid
import asyncio

# Add intelligent-core to path
intelligent_core_path = Path(__file__).parent.parent.parent.parent.parent / "intelligent-core" / "scenario-intelligence"
sys.path.insert(0, str(intelligent_core_path))

from generation_manager import GenerationManager

# Import EventBus integration
try:
    from integrations.eventbus_client import ScenarioEventBusClient
    from events.scenario_events import (
        create_regeneration_triggered_event,
        create_regeneration_completed_event,
        create_scenario_deprecated_event,
        ScenarioGenerationTrigger,
    )
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class AutoRegenerationHandler:
    """
    Handles automatic regeneration when service catalog changes

    Features:
    - Service added: Generate new scenarios for that service
    - Service updated: Regenerate affected scenarios
    - Service removed: Mark scenarios as deprecated
    - Batch processing: Handle multiple changes efficiently
    """

    def __init__(
        self,
        generation_manager: GenerationManager,
        eventbus_client: Optional[ScenarioEventBusClient] = None,
        batch_window_seconds: int = 30
    ):
        """
        Initialize auto-regeneration handler

        Args:
            generation_manager: GenerationManager instance
            eventbus_client: EventBus client (creates new if None)
            batch_window_seconds: Time window for batching changes (default: 30s)
        """
        self.manager = generation_manager
        self.eventbus_client = eventbus_client or ScenarioEventBusClient()
        self.batch_window_seconds = batch_window_seconds

        # Batch tracking
        self._pending_changes: List[Dict[str, Any]] = []
        self._batch_task: Optional[asyncio.Task] = None
        self._processing = False

        # Service -> Level mapping
        self.service_level_map = self._build_service_level_map()

        logger.info("AutoRegenerationHandler initialized")

    def _build_service_level_map(self) -> Dict[str, str]:
        """
        Build mapping of service names to generation levels

        Returns:
            Dict mapping service names to levels (l1_platform, l2, etc.)
        """
        # This mapping should ideally come from service catalog
        # For now, use simple heuristics
        return {
            # L1 Platform Services
            "gateway": "l1_platform",
            "eventbus": "l1_platform",
            "database-gateway": "l1_platform",
            "balancer-service": "l1_platform",
            "service-discovery": "l1_platform",

            # L1 Applications
            "scenario-intelligence": "l1_application",
            "simulation-service": "l1_application",
            "workflow-intelligence": "l1_application",

            # L2 Subsystems
            "ai-office": "l2",
            "expertise-center": "l2",
            "community-intelligence": "l2",

            # Default to L1 platform for unknown services
        }

    def get_level_for_service(self, service_name: str) -> str:
        """Get generation level for service"""
        return self.service_level_map.get(service_name, "l1_platform")

    async def initialize(self):
        """Initialize handler and subscribe to events"""
        if not self.eventbus_client.is_connected():
            await self.eventbus_client.initialize()

        # Subscribe to service catalog events
        await self.eventbus_client.subscribe_to_catalog_updates(
            self.handle_catalog_event
        )

        logger.info(" AutoRegenerationHandler subscribed to catalog events")

    async def handle_catalog_event(self, event: Any):
        """
        Handle service catalog event

        Args:
            event: EventBus event
        """
        try:
            event_type = event.type
            data = event.data

            logger.info(f" Received catalog event: {event_type}")

            # Add to pending changes
            self._pending_changes.append({
                "event_type": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Start batch timer if not already running
            if not self._batch_task or self._batch_task.done():
                self._batch_task = asyncio.create_task(
                    self._process_batch_after_delay()
                )

        except Exception as e:
            logger.error(f"Error handling catalog event: {e}", exc_info=True)

    async def _process_batch_after_delay(self):
        """Wait for batch window, then process all pending changes"""
        await asyncio.sleep(self.batch_window_seconds)

        if self._pending_changes:
            await self._process_batch()

    async def _process_batch(self):
        """Process all pending changes as a batch"""
        if self._processing or not self._pending_changes:
            return

        self._processing = True
        changes = self._pending_changes.copy()
        self._pending_changes.clear()

        regeneration_id = f"regen-{uuid.uuid4()}"
        start_time = datetime.utcnow()

        try:
            logger.info(f" Processing batch of {len(changes)} changes (id={regeneration_id})")

            # Analyze changes
            affected_services = self._extract_affected_services(changes)
            affected_levels = self._determine_affected_levels(affected_services)

            # Publish regeneration triggered event
            if self.eventbus_client and EVENTBUS_AVAILABLE:
                trigger_event = create_regeneration_triggered_event(
                    trigger_event="service.catalog.updated",
                    affected_services=list(affected_services),
                    affected_levels=affected_levels,
                    regeneration_id=regeneration_id,
                    metadata={"changes_count": len(changes)}
                )
                await self.eventbus_client.publish_regeneration_triggered(trigger_event)

            # Perform regeneration
            result = await self._regenerate_for_levels(affected_levels, regeneration_id)

            # Publish completion event
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            if self.eventbus_client and EVENTBUS_AVAILABLE:
                completion_event = create_regeneration_completed_event(
                    regeneration_id=regeneration_id,
                    trigger_event="service.catalog.updated",
                    scenarios_generated=result.get("generated", 0),
                    scenarios_updated=result.get("updated", 0),
                    scenarios_deprecated=result.get("deprecated", 0),
                    duration_ms=duration_ms,
                    status=result.get("status", "success"),
                    errors=result.get("errors", [])
                )
                await self.eventbus_client.publish_regeneration_completed(completion_event)

            logger.info(f" Batch regeneration completed (id={regeneration_id})")

        except Exception as e:
            logger.error(f"Batch regeneration failed: {e}", exc_info=True)

            # Publish failed completion event
            if self.eventbus_client and EVENTBUS_AVAILABLE:
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                completion_event = create_regeneration_completed_event(
                    regeneration_id=regeneration_id,
                    trigger_event="service.catalog.updated",
                    scenarios_generated=0,
                    scenarios_updated=0,
                    scenarios_deprecated=0,
                    duration_ms=duration_ms,
                    status="failed",
                    errors=[str(e)]
                )
                await self.eventbus_client.publish_regeneration_completed(completion_event)

        finally:
            self._processing = False

    def _extract_affected_services(self, changes: List[Dict[str, Any]]) -> Set[str]:
        """Extract unique service names from changes"""
        services = set()
        for change in changes:
            data = change.get("data", {})
            service_name = data.get("service_name")
            if service_name:
                services.add(service_name)
        return services

    def _determine_affected_levels(self, services: Set[str]) -> List[str]:
        """Determine which generation levels are affected"""
        levels = set()
        for service in services:
            level = self.get_level_for_service(service)
            levels.add(level)
        return sorted(list(levels))

    async def _regenerate_for_levels(
        self,
        levels: List[str],
        regeneration_id: str
    ) -> Dict[str, Any]:
        """
        Regenerate scenarios for affected levels

        Args:
            levels: List of levels to regenerate
            regeneration_id: Unique regeneration ID

        Returns:
            Result dict with stats
        """
        logger.info(f" Regenerating scenarios for levels: {levels}")

        result = {
            "status": "success",
            "generated": 0,
            "updated": 0,
            "deprecated": 0,
            "errors": []
        }

        try:
            # Run generation for affected levels
            report = await self.manager.generate_all(levels=levels)

            # Extract stats
            result["generated"] = report.get("total_scenarios_generated", 0)
            result["status"] = report.get("status", "success")
            result["errors"] = report.get("errors", [])

            logger.info(
                f" Regeneration complete: "
                f"{result['generated']} scenarios generated"
            )

        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            logger.error(f"Regeneration failed: {e}", exc_info=True)

        return result

    async def handle_service_added(self, service_name: str, service_data: Dict[str, Any]):
        """
        Handle when new service is added

        Args:
            service_name: Name of the service
            service_data: Service metadata
        """
        logger.info(f"🆕 Service added: {service_name}")

        # Determine which generator handles this service
        level = self.get_level_for_service(service_name)

        # Trigger regeneration for that level
        regeneration_id = f"add-{uuid.uuid4()}"

        try:
            result = await self._regenerate_for_levels([level], regeneration_id)
            logger.info(f" Generated scenarios for new service: {service_name}")
            return result

        except Exception as e:
            logger.error(f"Failed to generate scenarios for {service_name}: {e}")
            raise

    async def handle_service_updated(
        self,
        service_name: str,
        changes: Dict[str, Any]
    ):
        """
        Handle when service is updated

        Args:
            service_name: Name of the service
            changes: What changed
        """
        logger.info(f" Service updated: {service_name}")

        # Determine affected scenarios
        level = self.get_level_for_service(service_name)

        # Regenerate only affected level
        regeneration_id = f"update-{uuid.uuid4()}"

        try:
            result = await self._regenerate_for_levels([level], regeneration_id)
            logger.info(f" Updated scenarios for: {service_name}")
            return result

        except Exception as e:
            logger.error(f"Failed to update scenarios for {service_name}: {e}")
            raise

    async def handle_service_removed(self, service_name: str):
        """
        Handle when service is removed

        Args:
            service_name: Name of the service
        """
        logger.info(f"️  Service removed: {service_name}")

        # Find scenarios for this service
        # Mark them as deprecated

        try:
            # TODO: Query registry for scenarios using this service
            # For now, just log
            logger.warning(f"Service removed but scenario deprecation not implemented: {service_name}")

            # Publish deprecated event
            if self.eventbus_client and EVENTBUS_AVAILABLE:
                deprecated_event = create_scenario_deprecated_event(
                    scenario_id=f"scenarios-for-{service_name}",
                    reason=f"Service removed: {service_name}",
                    replaced_by=None
                )
                await self.eventbus_client.publish_scenario_deprecated(deprecated_event)

        except Exception as e:
            logger.error(f"Failed to deprecate scenarios for {service_name}: {e}")
            raise

    async def close(self):
        """Cleanup handler"""
        if self._batch_task and not self._batch_task.done():
            self._batch_task.cancel()

        if self.eventbus_client:
            await self.eventbus_client.close()

        logger.info(" AutoRegenerationHandler closed")


# =========================================================================
# Standalone Usage Example
# =========================================================================

async def main():
    """Example usage"""
    from generation_manager import GenerationManager

    # Initialize generation manager
    manager = GenerationManager()

    # Initialize auto-regeneration handler
    handler = AutoRegenerationHandler(manager)
    await handler.initialize()

    logger.info(" Auto-regeneration handler running")
    logger.info("   Listening for service catalog changes...")

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await handler.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
