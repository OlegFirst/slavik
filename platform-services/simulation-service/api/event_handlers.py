"""
EventBus Event Handlers for Simulation Service

Handles incoming events from other services:
- scenario.execution.requested - Request to execute a scenario
- digital_twin.state.changed - Digital twin state updates for simulations
- bia.analysis.requested - BIA analysis requests
- workflow.scenario.required - Workflow intelligence needs scenario
"""

import asyncio
import logging
from typing import Dict, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class SimulationEventHandlers:
    """Event handlers for simulation service EventBus subscriptions"""

    def __init__(
        self,
        simulation_service,
        scenario_service,
        bia_service,
        eventbus_client
    ):
        self.simulation_service = simulation_service
        self.scenario_service = scenario_service
        self.bia_service = bia_service
        self.eventbus_client = eventbus_client

    # ============================================================================
    # EVENT HANDLER: scenario.execution.requested
    # ============================================================================

    async def handle_scenario_execution_requested(self, event: Dict[str, Any]):
        """
        Handle scenario execution request from other services

        Event payload:
        {
            "scenario_id": "string",
            "tenant_id": "string",
            "requested_by": "string",
            "parameters": {...},
            "priority": "high|normal|low"
        }
        """
        try:
            logger.info(f"Received scenario.execution.requested: {event}")

            scenario_id = event.get("scenario_id")
            tenant_id = event.get("tenant_id")
            parameters = event.get("parameters", {})

            if not scenario_id or not tenant_id:
                logger.error("Missing scenario_id or tenant_id in event")
                return

            # Create simulation from scenario
            simulation = await self.simulation_service.create_from_scenario(
                scenario_id=scenario_id,
                tenant_id=tenant_id,
                parameters=parameters
            )

            # Execute simulation
            execution = await self.simulation_service.execute(
                simulation_id=simulation["id"],
                tenant_id=tenant_id
            )

            # Publish result event
            await self.eventbus_client.publish(
                "simulation.started",
                {
                    "simulation_id": simulation["id"],
                    "scenario_id": scenario_id,
                    "execution_id": execution["id"],
                    "tenant_id": tenant_id,
                    "requested_by": event.get("requested_by")
                }
            )

            logger.info(f"Scenario execution started: {execution['id']}")

        except Exception as e:
            logger.error(f"Error handling scenario.execution.requested: {e}", exc_info=True)
            await self.eventbus_client.publish(
                "simulation.failed",
                {
                    "scenario_id": event.get("scenario_id"),
                    "error": str(e),
                    "event_type": "scenario.execution.requested"
                }
            )

    # ============================================================================
    # EVENT HANDLER: digital_twin.state.changed
    # ============================================================================

    async def handle_digital_twin_state_changed(self, event: Dict[str, Any]):
        """
        Handle digital twin state changes for simulation updates

        Event payload:
        {
            "twin_id": "string",
            "tenant_id": "string",
            "state": {...},
            "changed_fields": [...],
            "timestamp": "ISO8601"
        }
        """
        try:
            logger.info(f"Received digital_twin.state.changed: {event}")

            twin_id = event.get("twin_id")
            tenant_id = event.get("tenant_id")
            state = event.get("state", {})

            if not twin_id or not tenant_id:
                logger.error("Missing twin_id or tenant_id in event")
                return

            # Find active simulations using this digital twin
            active_simulations = await self.simulation_service.find_active_by_twin(
                twin_id=twin_id,
                tenant_id=tenant_id
            )

            if not active_simulations:
                logger.debug(f"No active simulations for twin {twin_id}")
                return

            # Update simulation parameters based on new state
            for simulation in active_simulations:
                await self.simulation_service.update_from_twin_state(
                    simulation_id=simulation["id"],
                    twin_state=state
                )

                logger.info(f"Updated simulation {simulation['id']} with twin state")

        except Exception as e:
            logger.error(f"Error handling digital_twin.state.changed: {e}", exc_info=True)

    # ============================================================================
    # EVENT HANDLER: bia.analysis.requested
    # ============================================================================

    async def handle_bia_analysis_requested(self, event: Dict[str, Any]):
        """
        Handle BIA analysis request - run BIA simulation

        Event payload:
        {
            "analysis_id": "string",
            "tenant_id": "string",
            "resources": [...],
            "scenario": {...},
            "requested_by": "string"
        }
        """
        try:
            logger.info(f"Received bia.analysis.requested: {event}")

            analysis_id = event.get("analysis_id")
            tenant_id = event.get("tenant_id")
            resources = event.get("resources", [])
            scenario = event.get("scenario", {})

            if not analysis_id or not tenant_id:
                logger.error("Missing analysis_id or tenant_id in event")
                return

            # Create BIA simulation
            simulation = await self.bia_service.create_bia_simulation(
                analysis_id=analysis_id,
                tenant_id=tenant_id,
                resources=resources,
                scenario=scenario
            )

            # Execute BIA simulation
            results = await self.bia_service.execute_bia(
                simulation_id=simulation["id"],
                tenant_id=tenant_id
            )

            # Publish results
            await self.eventbus_client.publish(
                "bia.analysis.completed",
                {
                    "analysis_id": analysis_id,
                    "simulation_id": simulation["id"],
                    "results": results,
                    "tenant_id": tenant_id,
                    "completed_at": datetime.utcnow().isoformat()
                }
            )

            logger.info(f"BIA analysis completed: {analysis_id}")

        except Exception as e:
            logger.error(f"Error handling bia.analysis.requested: {e}", exc_info=True)
            await self.eventbus_client.publish(
                "bia.analysis.failed",
                {
                    "analysis_id": event.get("analysis_id"),
                    "error": str(e),
                    "tenant_id": event.get("tenant_id")
                }
            )

    # ============================================================================
    # EVENT HANDLER: workflow.scenario.required
    # ============================================================================

    async def handle_workflow_scenario_required(self, event: Dict[str, Any]):
        """
        Handle request from workflow intelligence for scenario generation

        Event payload:
        {
            "workflow_id": "string",
            "tenant_id": "string",
            "scenario_requirements": {...},
            "context": {...}
        }
        """
        try:
            logger.info(f"Received workflow.scenario.required: {event}")

            workflow_id = event.get("workflow_id")
            tenant_id = event.get("tenant_id")
            requirements = event.get("scenario_requirements", {})
            context = event.get("context", {})

            if not workflow_id or not tenant_id:
                logger.error("Missing workflow_id or tenant_id in event")
                return

            # Generate scenario using AI
            scenario = await self.scenario_service.generate_ai_scenario(
                tenant_id=tenant_id,
                requirements=requirements,
                context=context
            )

            # Publish scenario to workflow intelligence
            await self.eventbus_client.publish(
                "scenario.generated",
                {
                    "workflow_id": workflow_id,
                    "scenario_id": scenario["id"],
                    "scenario": scenario,
                    "tenant_id": tenant_id,
                    "generated_at": datetime.utcnow().isoformat()
                }
            )

            logger.info(f"Scenario generated for workflow {workflow_id}: {scenario['id']}")

        except Exception as e:
            logger.error(f"Error handling workflow.scenario.required: {e}", exc_info=True)
            await self.eventbus_client.publish(
                "scenario.generation.failed",
                {
                    "workflow_id": event.get("workflow_id"),
                    "error": str(e),
                    "tenant_id": event.get("tenant_id")
                }
            )


# ============================================================================
# REGISTRATION FUNCTION
# ============================================================================

async def register_event_handlers(
    eventbus_client,
    simulation_service,
    scenario_service,
    bia_service
):
    """
    Register all event handlers with EventBus

    Args:
        eventbus_client: EventBus client instance
        simulation_service: Simulation service instance
        scenario_service: Scenario service instance
        bia_service: BIA service instance
    """

    handlers = SimulationEventHandlers(
        simulation_service=simulation_service,
        scenario_service=scenario_service,
        bia_service=bia_service,
        eventbus_client=eventbus_client
    )

    # Subscribe to events
    subscriptions = [
        {
            "pattern": "scenario.execution.requested",
            "handler": handlers.handle_scenario_execution_requested
        },
        {
            "pattern": "digital_twin.state.changed",
            "handler": handlers.handle_digital_twin_state_changed
        },
        {
            "pattern": "bia.analysis.requested",
            "handler": handlers.handle_bia_analysis_requested
        },
        {
            "pattern": "workflow.scenario.required",
            "handler": handlers.handle_workflow_scenario_required
        }
    ]

    for sub in subscriptions:
        try:
            await eventbus_client.subscribe(
                pattern=sub["pattern"],
                handler=sub["handler"]
            )
            logger.info(f"✅ Subscribed to: {sub['pattern']}")
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to {sub['pattern']}: {e}")

    logger.info("EventBus event handlers registered successfully")

    return handlers
