"""
Response Module - Event Subscribers
ISO 22301:2019 Clause 8.4 - Incident Response

Subscribes to events from other services
"""

import logging
import json
import os
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from uuid import UUID

import aio_pika
from aio_pika import ExchangeType, IncomingMessage
from aio_pika.exceptions import AMQPException

logger = logging.getLogger(__name__)


class ResponseEventSubscriber:
    """
    Event subscriber for incident response

    Listens to events from other services and triggers appropriate actions
    """

    def __init__(self, service=None):
        """
        Initialize event subscriber with RabbitMQ configuration

        Args:
            service: ResponseService instance for creating incidents
        """
        # Store service reference for incident creation
        self.service = service

        # Get configuration from environment
        self.enabled = os.getenv("EVENT_BUS_ENABLED", "false").lower() == "true"
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_password = os.getenv("RABBITMQ_PASSWORD", "guest")
        self.exchange_name = os.getenv("RABBITMQ_EXCHANGE", "response_events")
        self.queue_name = os.getenv("RABBITMQ_QUEUE", "response_queue")

        # RabbitMQ connection objects
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.queue: Optional[aio_pika.Queue] = None
        self.broker_connected = False

        # Event handlers registry
        self.handlers: Dict[str, Callable] = {}
        self._register_handlers()

        logger.info(f"Event subscriber initialized (enabled={self.enabled})")

    def _register_handlers(self):
        """Register event handlers"""
        # Risk assessment events
        self.handlers["risk.assessment.high_risk_detected"] = self._handle_high_risk_detected
        self.handlers["risk.assessment.critical_risk"] = self._handle_critical_risk

        # Impact analysis events
        self.handlers["impact.analysis.high_impact"] = self._handle_high_impact

        # BIA events
        self.handlers["bia.process.critical_identified"] = self._handle_critical_process

        # Recovery events
        self.handlers["recovery.failure"] = self._handle_recovery_failure
        self.handlers["recovery.rto_exceeded"] = self._handle_rto_exceeded
        self.handlers["recovery.rpo_exceeded"] = self._handle_rpo_exceeded

        # Monitoring/Alert events
        self.handlers["monitoring.alert.critical"] = self._handle_critical_alert
        self.handlers["monitoring.system_down"] = self._handle_system_down

        # External events
        self.handlers["external.disaster_alert"] = self._handle_disaster_alert
        self.handlers["external.security_breach"] = self._handle_security_breach

    # ========================================================================
    # Event Handlers
    # ========================================================================

    async def _handle_high_risk_detected(self, event_data: Dict[str, Any]):
        """
        Handle high risk detected event from Risk module

        May trigger automatic incident creation or alert
        """
        try:
            logger.info(f"High risk detected: {event_data}")

            risk_id = event_data.get("risk_id")
            risk_level = event_data.get("risk_level", "high")
            organization_id = event_data.get("organization_id")

            # Create incident for high risks only if critical or high
            if risk_level in ["critical", "high"] and risk_id and organization_id:
                await self._create_incident_from_risk(
                    risk_id=risk_id,
                    organization_id=organization_id,
                    severity=risk_level,
                    risk_data=event_data
                )

            logger.info(f"Processed high risk event: {risk_id}")

        except Exception as e:
            logger.error(f"Failed to handle high risk event: {e}")

    async def _handle_critical_risk(self, event_data: Dict[str, Any]):
        """
        Handle critical risk event

        Should trigger automatic incident creation
        """
        try:
            logger.warning(f"Critical risk detected: {event_data}")

            # Auto-create incident for critical risk
            risk_id = event_data.get("risk_id")
            organization_id = event_data.get("organization_id")

            if risk_id and organization_id:
                await self._create_incident_from_risk(
                    risk_id=risk_id,
                    organization_id=organization_id,
                    severity="critical",
                    risk_data=event_data
                )

        except Exception as e:
            logger.error(f"Failed to handle critical risk event: {e}")

    async def _handle_high_impact(self, event_data: Dict[str, Any]):
        """
        Handle high impact event from Impact Analysis module
        """
        try:
            logger.info(f"High impact detected: {event_data}")

            # Create incident for high impact events
            organization_id = event_data.get("organization_id")
            impact_level = event_data.get("impact_level", "high")

            if organization_id and self.service and impact_level in ["critical", "high"]:
                from models.domain import IncidentCreate, IncidentType, IncidentSeverity

                severity_mapping = {
                    "critical": IncidentSeverity.CRITICAL,
                    "high": IncidentSeverity.HIGH
                }

                incident_data = IncidentCreate(
                    title=f"High Impact Event: {event_data.get('event_name', 'Unknown Event')}",
                    description=f"High impact detected: {event_data.get('description', 'N/A')}",
                    incident_type=IncidentType.SERVICE_DISRUPTION,
                    severity=severity_mapping.get(impact_level, IncidentSeverity.HIGH),
                    affected_systems=event_data.get("affected_systems", []),
                    affected_locations=event_data.get("affected_locations", []),
                    detected_by="Event Subscriber (Auto)",
                    external_reference=event_data.get("impact_id")
                )

                await self.service.create_incident(
                    organization_id=UUID(organization_id),
                    incident_data=incident_data
                )
                logger.info("Auto-created incident for high impact event")

        except Exception as e:
            logger.error(f"Failed to handle high impact event: {e}")

    async def _handle_critical_process(self, event_data: Dict[str, Any]):
        """
        Handle critical process identified event from BIA module

        Note: This is informational - doesn't create incidents but logs for awareness
        """
        try:
            logger.info(f"Critical process identified: {event_data}")

            process_name = event_data.get("process_name", "Unknown Process")
            criticality = event_data.get("criticality_level", "N/A")

            # Log critical process information for incident response planning
            logger.info(
                f"Critical process registered: {process_name} "
                f"(criticality: {criticality}). This information will be used "
                f"to prioritize incident response activities."
            )

            # In a full implementation, you might:
            # - Update a cache of critical processes
            # - Adjust response team assignments
            # - Update escalation policies
            # For now, we just log the information

        except Exception as e:
            logger.error(f"Failed to handle critical process event: {e}")

    async def _handle_recovery_failure(self, event_data: Dict[str, Any]):
        """
        Handle recovery failure event from Recovery module

        Should create or escalate incident
        """
        try:
            logger.error(f"Recovery failure detected: {event_data}")

            # Create incident for recovery failure
            organization_id = event_data.get("organization_id")
            service_name = event_data.get("service_name", "Unknown Service")

            if organization_id and self.service:
                from models.domain import IncidentCreate, IncidentType, IncidentSeverity

                incident_data = IncidentCreate(
                    title=f"Recovery Failure: {service_name}",
                    description=f"Recovery operation failed for {service_name}. Details: {event_data.get('error_message', 'N/A')}",
                    incident_type=IncidentType.SERVICE_DISRUPTION,
                    severity=IncidentSeverity.HIGH,
                    affected_systems=[service_name],
                    detected_by="Event Subscriber (Auto)",
                    external_reference=event_data.get("recovery_id")
                )

                await self.service.create_incident(
                    organization_id=UUID(organization_id),
                    incident_data=incident_data
                )
                logger.info(f"Auto-created incident for recovery failure: {service_name}")

        except Exception as e:
            logger.error(f"Failed to handle recovery failure event: {e}")

    async def _handle_rto_exceeded(self, event_data: Dict[str, Any]):
        """
        Handle RTO exceeded event

        Should create compliance violation incident
        """
        try:
            logger.warning(f"RTO exceeded: {event_data}")

            service_name = event_data.get("service_name")
            target_rto = event_data.get("target_rto")
            actual_rto = event_data.get("actual_rto")
            organization_id = event_data.get("organization_id")

            # Create compliance violation incident
            if organization_id and service_name:
                await self._create_compliance_incident(
                    organization_id=organization_id,
                    violation_type="RTO_EXCEEDED",
                    service_name=service_name,
                    details={
                        "target_rto": target_rto,
                        "actual_rto": actual_rto,
                        "difference": actual_rto - target_rto if (actual_rto and target_rto) else None
                    }
                )

            logger.warning(f"RTO exceeded for {service_name}: {actual_rto} > {target_rto}")

        except Exception as e:
            logger.error(f"Failed to handle RTO exceeded event: {e}")

    async def _handle_rpo_exceeded(self, event_data: Dict[str, Any]):
        """
        Handle RPO exceeded event

        Should create compliance violation incident
        """
        try:
            logger.warning(f"RPO exceeded: {event_data}")

            service_name = event_data.get("service_name")
            target_rpo = event_data.get("target_rpo")
            actual_rpo = event_data.get("actual_rpo")
            organization_id = event_data.get("organization_id")

            # Create compliance violation incident
            if organization_id and service_name:
                await self._create_compliance_incident(
                    organization_id=organization_id,
                    violation_type="RPO_EXCEEDED",
                    service_name=service_name,
                    details={
                        "target_rpo": target_rpo,
                        "actual_rpo": actual_rpo,
                        "difference": actual_rpo - target_rpo if (actual_rpo and target_rpo) else None
                    }
                )

        except Exception as e:
            logger.error(f"Failed to handle RPO exceeded event: {e}")

    async def _handle_critical_alert(self, event_data: Dict[str, Any]):
        """
        Handle critical alert from monitoring system

        Should create incident automatically
        """
        try:
            logger.critical(f"Critical alert received: {event_data}")

            # Auto-create incident from critical alert
            organization_id = event_data.get("organization_id")
            if organization_id:
                await self._create_incident_from_alert(event_data)

        except Exception as e:
            logger.error(f"Failed to handle critical alert: {e}")

    async def _handle_system_down(self, event_data: Dict[str, Any]):
        """
        Handle system down event

        Should create high-severity incident
        """
        try:
            logger.critical(f"System down event: {event_data}")

            system_name = event_data.get("system_name", "Unknown System")
            down_since = event_data.get("timestamp")
            organization_id = event_data.get("organization_id")

            # Auto-create incident for system down
            if organization_id and self.service:
                from models.domain import IncidentCreate, IncidentType, IncidentSeverity

                incident_data = IncidentCreate(
                    title=f"System Down: {system_name}",
                    description=f"System {system_name} is down since {down_since}. Immediate attention required.",
                    incident_type=IncidentType.SYSTEM_FAILURE,
                    severity=IncidentSeverity.CRITICAL,
                    affected_systems=[system_name],
                    detected_by="Event Subscriber (Auto)",
                    detected_at=datetime.fromisoformat(down_since) if down_since else None
                )

                await self.service.create_incident(
                    organization_id=UUID(organization_id),
                    incident_data=incident_data
                )
                logger.info(f"Auto-created incident for system down: {system_name}")

        except Exception as e:
            logger.error(f"Failed to handle system down event: {e}")

    async def _handle_disaster_alert(self, event_data: Dict[str, Any]):
        """
        Handle external disaster alert

        Should create critical incident and activate response teams
        """
        try:
            logger.critical(f"Disaster alert received: {event_data}")

            # Auto-create critical incident and activate all response teams
            organization_id = event_data.get("organization_id")
            disaster_type = event_data.get("disaster_type", "Unknown Disaster")

            if organization_id and self.service:
                from models.domain import IncidentCreate, IncidentType, IncidentSeverity

                incident_data = IncidentCreate(
                    title=f"Disaster Alert: {disaster_type}",
                    description=f"Disaster alert received: {event_data.get('description', 'External disaster detected')}",
                    incident_type=IncidentType.NATURAL_DISASTER,
                    severity=IncidentSeverity.CRITICAL,
                    affected_systems=event_data.get("affected_systems", []),
                    affected_locations=event_data.get("affected_locations", []),
                    detected_by="Event Subscriber (Auto)"
                )

                await self.service.create_incident(
                    organization_id=UUID(organization_id),
                    incident_data=incident_data
                )
                logger.info(f"Auto-created incident for disaster alert: {disaster_type}")

        except Exception as e:
            logger.error(f"Failed to handle disaster alert: {e}")

    async def _handle_security_breach(self, event_data: Dict[str, Any]):
        """
        Handle security breach event

        Should create critical incident immediately
        """
        try:
            logger.critical(f"Security breach detected: {event_data}")

            # Auto-create critical security incident
            organization_id = event_data.get("organization_id")
            breach_type = event_data.get("breach_type", "Security Breach")

            if organization_id and self.service:
                from models.domain import IncidentCreate, IncidentType, IncidentSeverity

                incident_data = IncidentCreate(
                    title=f"Security Breach: {breach_type}",
                    description=f"Security breach detected: {event_data.get('description', 'Unauthorized access or data breach detected')}",
                    incident_type=IncidentType.SECURITY_BREACH,
                    severity=IncidentSeverity.CRITICAL,
                    affected_systems=event_data.get("affected_systems", []),
                    detected_by="Event Subscriber (Auto)",
                    external_reference=event_data.get("breach_id")
                )

                await self.service.create_incident(
                    organization_id=UUID(organization_id),
                    incident_data=incident_data
                )
                logger.info(f"Auto-created incident for security breach: {breach_type}")
                # Note: Stakeholder notification will be triggered by auto-escalation

        except Exception as e:
            logger.error(f"Failed to handle security breach event: {e}")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    async def _create_incident_from_risk(
        self,
        risk_id: str,
        organization_id: str,
        severity: str,
        risk_data: Dict[str, Any]
    ):
        """
        Create incident from risk assessment

        Args:
            risk_id: Risk assessment ID
            organization_id: Organization UUID
            severity: Risk severity (maps to incident severity)
            risk_data: Full risk event data
        """
        if not self.service:
            logger.warning("Service not initialized, cannot create incident")
            return

        try:
            from models.domain import IncidentCreate, IncidentType, IncidentSeverity

            # Map risk severity to incident severity
            severity_mapping = {
                "critical": IncidentSeverity.CRITICAL,
                "high": IncidentSeverity.HIGH,
                "medium": IncidentSeverity.MEDIUM,
                "low": IncidentSeverity.LOW
            }
            incident_severity = severity_mapping.get(severity.lower(), IncidentSeverity.MEDIUM)

            # Create incident
            incident_data = IncidentCreate(
                title=f"High Risk Detected: {risk_data.get('risk_name', 'Unknown Risk')}",
                description=f"Risk assessment identified: {risk_data.get('description', 'N/A')}",
                incident_type=IncidentType.OTHER,
                severity=incident_severity,
                affected_systems=risk_data.get("affected_systems", []),
                detected_by="Event Subscriber (Auto)",
                external_reference=risk_id
            )

            await self.service.create_incident(
                organization_id=UUID(organization_id),
                incident_data=incident_data
            )
            logger.info(f"Created incident from risk {risk_id}")

        except Exception as e:
            logger.error(f"Failed to create incident from risk: {e}")

    async def _create_incident_from_alert(
        self,
        alert_data: Dict[str, Any]
    ):
        """
        Create incident from monitoring alert

        Args:
            alert_data: Alert event data
        """
        if not self.service:
            logger.warning("Service not initialized, cannot create incident")
            return

        try:
            from models.domain import IncidentCreate, IncidentType, IncidentSeverity

            organization_id = alert_data.get("organization_id")
            alert_name = alert_data.get("alert_name", "Critical Alert")
            alert_severity = alert_data.get("severity", "high")

            # Map alert severity to incident severity
            severity_mapping = {
                "critical": IncidentSeverity.CRITICAL,
                "high": IncidentSeverity.HIGH,
                "medium": IncidentSeverity.MEDIUM,
                "low": IncidentSeverity.LOW
            }
            incident_severity = severity_mapping.get(alert_severity.lower(), IncidentSeverity.HIGH)

            # Create incident
            incident_data = IncidentCreate(
                title=f"Alert: {alert_name}",
                description=f"Monitoring alert triggered: {alert_data.get('description', 'N/A')}",
                incident_type=IncidentType.SERVICE_DISRUPTION,
                severity=incident_severity,
                affected_systems=alert_data.get("affected_systems", []),
                detected_by="Event Subscriber (Auto)",
                external_reference=alert_data.get("alert_id")
            )

            await self.service.create_incident(
                organization_id=UUID(organization_id),
                incident_data=incident_data
            )
            logger.info(f"Created incident from alert: {alert_name}")

        except Exception as e:
            logger.error(f"Failed to create incident from alert: {e}")

    async def _create_compliance_incident(
        self,
        organization_id: str,
        violation_type: str,
        service_name: str,
        details: Dict[str, Any]
    ):
        """
        Create compliance violation incident

        Args:
            organization_id: Organization UUID
            violation_type: Type of compliance violation (RTO_EXCEEDED, RPO_EXCEEDED, etc.)
            service_name: Service name
            details: Additional violation details
        """
        if not self.service:
            logger.warning("Service not initialized, cannot create incident")
            return

        try:
            from models.domain import IncidentCreate, IncidentType, IncidentSeverity

            # Create incident
            incident_data = IncidentCreate(
                title=f"Compliance Violation: {violation_type} - {service_name}",
                description=(
                    f"Compliance violation detected for {service_name}. "
                    f"Type: {violation_type}. Details: {json.dumps(details)}"
                ),
                incident_type=IncidentType.SERVICE_DISRUPTION,
                severity=IncidentSeverity.HIGH,
                affected_systems=[service_name],
                detected_by="Event Subscriber (Auto)"
            )

            await self.service.create_incident(
                organization_id=UUID(organization_id),
                incident_data=incident_data
            )
            logger.info(f"Created compliance incident: {violation_type} for {service_name}")

        except Exception as e:
            logger.error(f"Failed to create compliance incident: {e}")

    # ========================================================================
    # Subscriber Management
    # ========================================================================

    async def start(self):
        """
        Start listening to events from RabbitMQ

        Connects to broker, declares queue, binds to exchange, and starts consuming
        """
        try:
            # Skip if event bus is disabled
            if not self.enabled:
                logger.info("Event bus disabled, skipping subscriber start")
                return

            # Build connection URL
            rabbitmq_url = (
                f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
                f"@{self.rabbitmq_host}:{self.rabbitmq_port}/"
            )

            # Create robust connection (auto-reconnect)
            logger.info(f"Connecting subscriber to RabbitMQ at {self.rabbitmq_host}:{self.rabbitmq_port}")
            self.connection = await aio_pika.connect_robust(rabbitmq_url)

            # Create channel
            self.channel = await self.connection.channel()

            # Set prefetch count to process one message at a time
            await self.channel.set_qos(prefetch_count=1)

            # Declare exchange (same as publisher)
            self.exchange = await self.channel.declare_exchange(
                name=self.exchange_name,
                type=ExchangeType.TOPIC,
                durable=True
            )

            # Declare queue
            self.queue = await self.channel.declare_queue(
                name=self.queue_name,
                durable=True
            )

            # Bind queue to exchange with routing patterns
            # Subscribe to various event types
            routing_keys = [
                "risk.*",              # All risk events
                "impact.*",            # All impact events
                "bia.*",               # All BIA events
                "recovery.*",          # All recovery events
                "monitoring.*",        # All monitoring events
                "external.*"           # All external events
            ]

            for routing_key in routing_keys:
                await self.queue.bind(
                    exchange=self.exchange,
                    routing_key=routing_key
                )
                logger.debug(f"Bound queue to routing key: {routing_key}")

            # Start consuming messages
            await self.queue.consume(self._on_message)

            self.broker_connected = True
            logger.info(f"Event subscriber started and listening on queue: {self.queue_name}")

        except AMQPException as e:
            logger.error(f"AMQP error starting event subscriber: {e}")
            self.broker_connected = False
            # Don't raise - allow service to run without event bus

        except Exception as e:
            logger.error(f"Failed to start event subscriber: {e}")
            self.broker_connected = False
            # Don't raise - allow service to run without event bus

    async def stop(self):
        """
        Stop listening to events

        Gracefully disconnects from RabbitMQ
        """
        try:
            # Close channel
            if self.channel and not self.channel.is_closed:
                await self.channel.close()
                logger.debug("Subscriber channel closed")

            # Close connection
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.debug("Subscriber connection closed")

            # Reset state
            self.channel = None
            self.exchange = None
            self.queue = None
            self.connection = None
            self.broker_connected = False

            logger.info("Event subscriber stopped")

        except AMQPException as e:
            logger.error(f"AMQP error stopping event subscriber: {e}")
            # Force reset state even on error
            self.broker_connected = False

        except Exception as e:
            logger.error(f"Failed to stop event subscriber: {e}")
            # Force reset state even on error
            self.broker_connected = False

    async def _on_message(self, message: IncomingMessage):
        """
        Handle incoming message from RabbitMQ broker

        Args:
            message: Incoming message from RabbitMQ
        """
        try:
            # Parse message
            event_type = message.routing_key
            event_data = json.loads(message.body.decode())

            logger.debug(f"Received event: {event_type}")
            logger.debug(f"Event data: {event_data}")

            # Route to appropriate handler
            handler = self.handlers.get(event_type)
            if handler:
                # Execute handler
                await handler(event_data)
                # Acknowledge message after successful processing
                await message.ack()
                logger.debug(f"Successfully processed event: {event_type}")
            else:
                # No handler registered - acknowledge anyway to prevent requeue
                logger.debug(f"No handler for event type: {event_type}")
                await message.ack()

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message JSON: {e}")
            # Reject malformed messages (don't requeue)
            await message.reject(requeue=False)

        except Exception as e:
            logger.error(f"Failed to process message {message.routing_key}: {e}")
            # Reject message but don't requeue to prevent infinite loops
            # In production, you might want to send to a dead letter queue
            await message.reject(requeue=False)

    def register_handler(self, event_type: str, handler: Callable):
        """
        Register custom event handler

        Args:
            event_type: Event type to handle
            handler: Async function to handle the event
        """
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")

    def unregister_handler(self, event_type: str):
        """
        Unregister event handler

        Args:
            event_type: Event type to unregister
        """
        if event_type in self.handlers:
            del self.handlers[event_type]
            logger.info(f"Unregistered handler for event type: {event_type}")
