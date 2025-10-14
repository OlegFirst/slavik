"""
EventBus Integration for Process Framework

Publishes process lifecycle events to EventBus for:
- Real-time notifications
- Workflow orchestration
- Audit logging
- System integration

Events published:
- process.started
- process.step_completed
- process.completed
- process.suspended
- process.resumed
- process.approval_required
- document.generated
- validation.failed

Author: AI Platform Team
Date: 2025-10-11
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


# =====================================================
# Event Publisher
# =====================================================

class ProcessEventPublisher:
    """
    Publishes Process Framework events to EventBus

    Handles:
    - Event formatting
    - Async publishing
    - Error handling
    - Retry logic
    """

    def __init__(self, eventbus_client):
        """
        Initialize with EventBus client

        Args:
            eventbus_client: EventBusClient instance from infrastructure
        """
        self.eventbus = eventbus_client
        self.enabled = eventbus_client is not None

        if self.enabled:
            logger.info("ProcessEventPublisher initialized with EventBus")
        else:
            logger.warning("ProcessEventPublisher initialized without EventBus (events disabled)")

    async def publish_process_started(
        self,
        instance_id: str,
        process_id: str,
        started_by: str,
        initial_data: Optional[Dict] = None
    ):
        """
        Publish process.started event

        Triggered when: New process instance is created
        """
        event = {
            "event_type": "process.started",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "instance_id": instance_id,
                "process_id": process_id,
                "started_by": started_by,
                "initial_data": initial_data or {},
                "status": "active"
            }
        }

        await self._publish("process.started", event)
        logger.info(f"Published process.started for {instance_id}")

    async def publish_step_completed(
        self,
        instance_id: str,
        process_id: str,
        step_id: str,
        next_step_id: Optional[str],
        executed_by: str,
        duration_ms: Optional[int] = None,
        result: str = "success"
    ):
        """
        Publish process.step_completed event

        Triggered when: Step execution completes (success or failure)
        """
        event = {
            "event_type": "process.step_completed",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "instance_id": instance_id,
                "process_id": process_id,
                "step_id": step_id,
                "next_step_id": next_step_id,
                "executed_by": executed_by,
                "duration_ms": duration_ms,
                "result": result
            }
        }

        await self._publish("process.step_completed", event)
        logger.debug(f"Published step_completed for {instance_id}/{step_id}")

    async def publish_process_completed(
        self,
        instance_id: str,
        process_id: str,
        started_by: str,
        total_duration_seconds: Optional[float] = None,
        final_status: str = "completed"
    ):
        """
        Publish process.completed event

        Triggered when: Process reaches END step
        """
        event = {
            "event_type": "process.completed",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "instance_id": instance_id,
                "process_id": process_id,
                "started_by": started_by,
                "total_duration_seconds": total_duration_seconds,
                "final_status": final_status,
                "completed_at": datetime.now().isoformat()
            }
        }

        await self._publish("process.completed", event)
        logger.info(f"Published process.completed for {instance_id}")

    async def publish_process_suspended(
        self,
        instance_id: str,
        process_id: str,
        suspended_by: str,
        reason: Optional[str] = None
    ):
        """
        Publish process.suspended event

        Triggered when: Process is manually suspended
        """
        event = {
            "event_type": "process.suspended",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "instance_id": instance_id,
                "process_id": process_id,
                "suspended_by": suspended_by,
                "reason": reason,
                "previous_status": "active"
            }
        }

        await self._publish("process.suspended", event)
        logger.info(f"Published process.suspended for {instance_id}")

    async def publish_process_resumed(
        self,
        instance_id: str,
        process_id: str,
        resumed_by: str
    ):
        """
        Publish process.resumed event

        Triggered when: Suspended process is resumed
        """
        event = {
            "event_type": "process.resumed",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "instance_id": instance_id,
                "process_id": process_id,
                "resumed_by": resumed_by,
                "new_status": "active"
            }
        }

        await self._publish("process.resumed", event)
        logger.info(f"Published process.resumed for {instance_id}")

    async def publish_approval_required(
        self,
        instance_id: str,
        process_id: str,
        step_id: str,
        approvers: list,
        approval_data: Optional[Dict] = None
    ):
        """
        Publish process.approval_required event

        Triggered when: Process reaches APPROVAL step
        Used for: Sending notifications to approvers
        """
        event = {
            "event_type": "process.approval_required",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "instance_id": instance_id,
                "process_id": process_id,
                "step_id": step_id,
                "approvers": approvers,
                "approval_data": approval_data or {},
                "requires_action": True
            }
        }

        await self._publish("process.approval_required", event)
        logger.info(f"Published approval_required for {instance_id}/{step_id} to {len(approvers)} approvers")

    async def publish_document_generated(
        self,
        instance_id: str,
        process_id: str,
        document_path: str,
        template_id: str,
        format: str,
        generated_by: str,
        ai_enriched: bool = False
    ):
        """
        Publish document.generated event

        Triggered when: Document is generated from template
        """
        event = {
            "event_type": "document.generated",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "instance_id": instance_id,
                "process_id": process_id,
                "document_path": document_path,
                "template_id": template_id,
                "format": format,
                "generated_by": generated_by,
                "ai_enriched": ai_enriched,
                "generated_at": datetime.now().isoformat()
            }
        }

        await self._publish("document.generated", event)
        logger.info(f"Published document.generated for {instance_id}: {document_path}")

    async def publish_validation_failed(
        self,
        instance_id: str,
        process_id: str,
        step_id: str,
        executed_by: str,
        errors: Dict[str, list]
    ):
        """
        Publish validation.failed event

        Triggered when: Form validation fails
        """
        event = {
            "event_type": "validation.failed",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "instance_id": instance_id,
                "process_id": process_id,
                "step_id": step_id,
                "executed_by": executed_by,
                "errors": errors,
                "error_count": sum(len(errs) for errs in errors.values())
            }
        }

        await self._publish("validation.failed", event)
        logger.warning(f"Published validation.failed for {instance_id}/{step_id}")

    # =====================================================
    # Helper Methods
    # =====================================================

    async def _publish(self, topic: str, event: Dict[str, Any]):
        """
        Publish event to EventBus with error handling

        Args:
            topic: Event topic/channel
            event: Event data
        """
        if not self.enabled:
            logger.debug(f"EventBus disabled, skipping event: {topic}")
            return

        try:
            await self.eventbus.publish(topic, event)
        except Exception as e:
            logger.error(f"Failed to publish event {topic}: {e}")
            # Don't raise - event publishing should not block process execution

    def publish_sync(self, topic: str, event: Dict[str, Any]):
        """
        Synchronous wrapper for event publishing

        Usage:
            publisher.publish_sync("process.started", event_data)
        """
        try:
            # Create new event loop if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Run async publish in sync context
            loop.run_until_complete(self._publish(topic, event))
        except Exception as e:
            logger.error(f"Failed to publish event synchronously {topic}: {e}")


# =====================================================
# Convenience Functions for ProcessFramework Integration
# =====================================================

async def emit_process_event(
    publisher: ProcessEventPublisher,
    event_type: str,
    **event_data
):
    """
    Generic event emitter

    Usage:
        await emit_process_event(
            publisher,
            "process.started",
            instance_id="123",
            process_id="bia_v1"
        )
    """
    event = {
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": event_data
    }

    await publisher._publish(event_type, event)


# =====================================================
# Event Listener (for testing/monitoring)
# =====================================================

class ProcessEventListener:
    """
    Listens to Process Framework events

    Useful for:
    - Testing
    - Monitoring
    - Debugging
    - Building dashboards
    """

    def __init__(self, eventbus_client):
        self.eventbus = eventbus_client
        self.handlers = {}
        self.enabled = eventbus_client is not None

    def on(self, event_type: str, handler: callable):
        """
        Register event handler

        Usage:
            listener.on("process.started", handle_process_started)
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)
        logger.debug(f"Registered handler for {event_type}")

    async def start_listening(self, topics: list):
        """
        Start listening to specified topics

        Usage:
            await listener.start_listening([
                "process.started",
                "process.completed"
            ])
        """
        if not self.enabled:
            logger.warning("EventBus not available, cannot listen to events")
            return

        logger.info(f"Starting to listen to {len(topics)} topics")

        for topic in topics:
            await self.eventbus.subscribe(topic, self._handle_event)

    async def _handle_event(self, topic: str, event: Dict):
        """Internal event handler"""
        event_type = event.get("event_type", topic)

        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")


# =====================================================
# Event Schema Validation
# =====================================================

def validate_event_schema(event: Dict) -> bool:
    """
    Validate event has required fields

    Required:
    - event_type
    - timestamp
    - data (dict)
    """
    required_fields = ["event_type", "timestamp", "data"]

    for field in required_fields:
        if field not in event:
            logger.error(f"Event missing required field: {field}")
            return False

    if not isinstance(event["data"], dict):
        logger.error("Event data must be a dictionary")
        return False

    return True


# =====================================================
# Event Serialization
# =====================================================

def serialize_event(event: Dict) -> str:
    """Serialize event to JSON string"""
    try:
        return json.dumps(event, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to serialize event: {e}")
        return "{}"


def deserialize_event(event_str: str) -> Dict:
    """Deserialize event from JSON string"""
    try:
        return json.loads(event_str)
    except Exception as e:
        logger.error(f"Failed to deserialize event: {e}")
        return {}
