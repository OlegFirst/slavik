"""
Response Module - Event Publishers
ISO 22301:2019 Clause 8.4 - Incident Response

Publishes events for incident response activities
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

import aio_pika
from aio_pika import Message, ExchangeType, DeliveryMode
from aio_pika.exceptions import AMQPException

from models.domain import Incident, IncidentStatus, IncidentEscalation

logger = logging.getLogger(__name__)


class ResponseEventPublisher:
    """
    Event publisher for incident response events

    Publishes events to message broker for event-driven integration
    """

    def __init__(self):
        """
        Initialize event publisher with RabbitMQ configuration

        Connection is established lazily on first publish or explicit connect() call
        """
        # Get configuration from environment
        self.enabled = os.getenv("EVENT_BUS_ENABLED", "false").lower() == "true"
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
        self.exchange_name = os.getenv("RABBITMQ_EXCHANGE", "response_events")

        # RabbitMQ connection objects
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.broker_connected = False

        logger.info(f"Event publisher initialized (enabled={self.enabled})")

    async def publish_incident_created(self, incident: Incident):
        """
        Publish incident created event

        Event: response.incident.created
        """
        event_data = {
            "event_type": "response.incident.created",
            "incident_id": str(incident.id),
            "incident_number": incident.incident_number,
            "organization_id": str(incident.organization_id),
            "title": incident.title,
            "severity": incident.severity.value,
            "incident_type": incident.incident_type.value,
            "affected_systems": incident.affected_systems,
            "detected_at": incident.detected_at.isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._publish_event("response.incident.created", event_data)

        logger.info(f"Published incident.created event for {incident.incident_number}")

    async def publish_incident_updated(self, incident: Incident):
        """
        Publish incident updated event

        Event: response.incident.updated
        """
        event_data = {
            "event_type": "response.incident.updated",
            "incident_id": str(incident.id),
            "incident_number": incident.incident_number,
            "organization_id": str(incident.organization_id),
            "status": incident.status.value,
            "severity": incident.severity.value,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._publish_event("response.incident.updated", event_data)

        logger.debug(f"Published incident.updated event for {incident.incident_number}")

    async def publish_incident_status_changed(
        self,
        incident: Incident,
        old_status: IncidentStatus,
        new_status: IncidentStatus
    ):
        """
        Publish incident status changed event

        Event: response.incident.status_changed
        """
        event_data = {
            "event_type": "response.incident.status_changed",
            "incident_id": str(incident.id),
            "incident_number": incident.incident_number,
            "organization_id": str(incident.organization_id),
            "old_status": old_status.value,
            "new_status": new_status.value,
            "severity": incident.severity.value,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._publish_event("response.incident.status_changed", event_data)

        logger.info(
            f"Published status_changed event for {incident.incident_number}: "
            f"{old_status.value} -> {new_status.value}"
        )

    async def publish_incident_resolved(self, incident: Incident):
        """
        Publish incident resolved event

        Event: response.incident.resolved
        """
        event_data = {
            "event_type": "response.incident.resolved",
            "incident_id": str(incident.id),
            "incident_number": incident.incident_number,
            "organization_id": str(incident.organization_id),
            "severity": incident.severity.value,
            "duration_hours": incident.duration_hours,
            "detected_at": incident.detected_at.isoformat(),
            "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
            "root_cause": incident.root_cause,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._publish_event("response.incident.resolved", event_data)

        logger.info(f"Published incident.resolved event for {incident.incident_number}")

    async def publish_incident_closed(self, incident: Incident):
        """
        Publish incident closed event

        Event: response.incident.closed
        """
        event_data = {
            "event_type": "response.incident.closed",
            "incident_id": str(incident.id),
            "incident_number": incident.incident_number,
            "organization_id": str(incident.organization_id),
            "severity": incident.severity.value,
            "duration_hours": incident.duration_hours,
            "detected_at": incident.detected_at.isoformat(),
            "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._publish_event("response.incident.closed", event_data)

        logger.info(f"Published incident.closed event for {incident.incident_number}")

    async def publish_incident_escalated(
        self,
        incident: Incident,
        escalation_data: IncidentEscalation
    ):
        """
        Publish incident escalated event

        Event: response.incident.escalated
        """
        event_data = {
            "event_type": "response.incident.escalated",
            "incident_id": str(incident.id),
            "incident_number": incident.incident_number,
            "organization_id": str(incident.organization_id),
            "severity": incident.severity.value,
            "escalation_level": escalation_data.escalation_level,
            "escalation_reason": escalation_data.escalation_reason,
            "escalate_to": [str(uid) for uid in escalation_data.escalate_to] if escalation_data.escalate_to else [],
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._publish_event("response.incident.escalated", event_data)

        logger.info(
            f"Published incident.escalated event for {incident.incident_number} "
            f"to level {escalation_data.escalation_level}"
        )

    async def publish_stakeholder_notification(
        self,
        incident: Incident,
        message: str,
        recipients: List[str]
    ):
        """
        Publish stakeholder notification event

        Event: response.stakeholder.notification

        This event triggers external notification services
        """
        event_data = {
            "event_type": "response.stakeholder.notification",
            "incident_id": str(incident.id),
            "incident_number": incident.incident_number,
            "organization_id": str(incident.organization_id),
            "severity": incident.severity.value,
            "message": message,
            "recipients": recipients,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._publish_event("response.stakeholder.notification", event_data)

        logger.info(
            f"Published stakeholder notification event for {incident.incident_number} "
            f"to {len(recipients)} recipients"
        )

    async def publish_metrics_updated(
        self,
        incident_id: UUID,
        service_name: str,
        rto_met: bool,
        rpo_met: bool
    ):
        """
        Publish recovery metrics updated event

        Event: response.metrics.updated
        """
        event_data = {
            "event_type": "response.metrics.updated",
            "incident_id": str(incident_id),
            "service_name": service_name,
            "rto_met": rto_met,
            "rpo_met": rpo_met,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._publish_event("response.metrics.updated", event_data)

        logger.debug(f"Published metrics.updated event for incident {incident_id}")

    async def publish_compliance_violation(
        self,
        incident_id: UUID,
        incident_number: str,
        organization_id: UUID,
        violation_type: str,
        details: Dict[str, Any]
    ):
        """
        Publish compliance violation event

        Event: response.compliance.violation

        Triggered when RTO/RPO objectives are not met
        """
        event_data = {
            "event_type": "response.compliance.violation",
            "incident_id": str(incident_id),
            "incident_number": incident_number,
            "organization_id": str(organization_id),
            "violation_type": violation_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._publish_event("response.compliance.violation", event_data)

        logger.warning(
            f"Published compliance violation event for {incident_number}: {violation_type}"
        )

    # ========================================================================
    # Private Methods
    # ========================================================================

    async def _publish_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Publish event to message broker

        Args:
            event_type: Event type/routing key (e.g., "response.incident.created")
            event_data: Event payload as dictionary
        """
        try:
            # Check if event bus is enabled
            if not self.enabled:
                logger.debug(f"Event bus disabled, skipping: {event_type}")
                return

            # Ensure connection is established
            if not self.broker_connected:
                await self.connect()

            # If still not connected, fall back to logging
            if not self.broker_connected or not self.exchange:
                logger.warning(f"Event bus not connected, logging event: {event_type}")
                logger.debug(f"Event data: {event_data}")
                return

            # Create message
            message_body = json.dumps(event_data, default=str).encode()
            message = Message(
                body=message_body,
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                timestamp=datetime.utcnow(),
                headers={
                    "event_type": event_type,
                    "source": "response-service"
                }
            )

            # Publish to exchange with routing key
            await self.exchange.publish(
                message=message,
                routing_key=event_type
            )

            logger.debug(f"Event published to RabbitMQ: {event_type}")

        except AMQPException as e:
            logger.error(f"AMQP error publishing event {event_type}: {e}")
            # Mark as disconnected to trigger reconnection on next publish
            self.broker_connected = False
            # Don't raise - event publishing should not break main flow

        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            # Don't raise - event publishing should not break main flow

    async def connect(self):
        """
        Connect to RabbitMQ message broker

        Creates connection, channel, and exchange
        Uses robust connection for automatic reconnection
        """
        try:
            # Skip if event bus is disabled
            if not self.enabled:
                logger.info("Event bus disabled, skipping connection")
                return

            # Skip if already connected
            if self.broker_connected and self.connection and not self.connection.is_closed:
                logger.debug("Already connected to RabbitMQ")
                return

            # Build connection URL
            rabbitmq_url = (
                f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
                f"@{self.rabbitmq_host}:{self.rabbitmq_port}/"
            )

            # Create robust connection (auto-reconnect)
            logger.info(f"Connecting to RabbitMQ at {self.rabbitmq_host}:{self.rabbitmq_port}")
            self.connection = await aio_pika.connect_robust(rabbitmq_url)

            # Create channel
            self.channel = await self.connection.channel()

            # Declare exchange (topic type for routing key patterns)
            self.exchange = await self.channel.declare_exchange(
                name=self.exchange_name,
                type=ExchangeType.TOPIC,
                durable=True
            )

            self.broker_connected = True
            logger.info(f"Event publisher connected to RabbitMQ (exchange={self.exchange_name})")

        except AMQPException as e:
            logger.error(f"AMQP error connecting to RabbitMQ: {e}")
            self.broker_connected = False
            # Don't raise - allow service to run without event bus

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.broker_connected = False
            # Don't raise - allow service to run without event bus

    async def disconnect(self):
        """
        Disconnect from RabbitMQ message broker

        Gracefully closes channel and connection
        """
        try:
            # Close channel
            if self.channel and not self.channel.is_closed:
                await self.channel.close()
                logger.debug("RabbitMQ channel closed")

            # Close connection
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.debug("RabbitMQ connection closed")

            # Reset state
            self.channel = None
            self.exchange = None
            self.connection = None
            self.broker_connected = False

            logger.info("Event publisher disconnected from RabbitMQ")

        except AMQPException as e:
            logger.error(f"AMQP error disconnecting from RabbitMQ: {e}")
            # Force reset state even on error
            self.broker_connected = False

        except Exception as e:
            logger.error(f"Failed to disconnect from RabbitMQ: {e}")
            # Force reset state even on error
            self.broker_connected = False
