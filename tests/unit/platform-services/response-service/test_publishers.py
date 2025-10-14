"""
Response Module - Event Publishers Tests
ISO 22301:2019 Clause 8.4 - Incident Response

Unit tests for ResponseEventPublisher
"""

import pytest
import json
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call

from events.publishers import ResponseEventPublisher
from models.domain import (
    Incident, IncidentStatus, IncidentSeverity, IncidentType, IncidentEscalation
)


# ============================================================================
# Publisher Initialization Tests
# ============================================================================

@pytest.mark.asyncio
class TestPublisherInitialization:
    """Test event publisher initialization"""

    def test_init_disabled_by_default(self):
        """Test publisher is disabled by default"""
        # Arrange & Act
        with patch.dict('os.environ', {}, clear=True):
            publisher = ResponseEventPublisher()

            # Assert
            assert publisher.enabled is False
            assert publisher.broker_connected is False

    def test_init_enabled_via_env(self):
        """Test publisher enabled via environment variable"""
        # Arrange & Act
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()

            # Assert
            assert publisher.enabled is True

    def test_init_with_custom_config(self):
        """Test publisher initialization with custom config"""
        # Arrange & Act
        with patch.dict('os.environ', {
            'EVENT_BUS_ENABLED': 'true',
            'RABBITMQ_HOST': 'custom-host',
            'RABBITMQ_PORT': '5673',
            'RABBITMQ_USER': 'custom-user',
            'RABBITMQ_EXCHANGE': 'custom-exchange'
        }):
            publisher = ResponseEventPublisher()

            # Assert
            assert publisher.enabled is True
            assert publisher.rabbitmq_host == 'custom-host'
            assert publisher.rabbitmq_port == 5673
            assert publisher.rabbitmq_user == 'custom-user'
            assert publisher.exchange_name == 'custom-exchange'


# ============================================================================
# Connection Management Tests
# ============================================================================

@pytest.mark.asyncio
class TestConnectionManagement:
    """Test RabbitMQ connection management"""

    async def test_connect_success(
        self, mock_rabbitmq_connection, mock_rabbitmq_channel, mock_rabbitmq_exchange
    ):
        """Test successful RabbitMQ connection"""
        # Arrange
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}), \
             patch('aio_pika.connect_robust', return_value=mock_rabbitmq_connection) as mock_connect:

            mock_rabbitmq_connection.channel.return_value = mock_rabbitmq_channel
            mock_rabbitmq_channel.declare_exchange.return_value = mock_rabbitmq_exchange

            publisher = ResponseEventPublisher()

            # Act
            await publisher.connect()

            # Assert
            assert publisher.broker_connected is True
            assert publisher.connection is not None
            assert publisher.channel is not None
            assert publisher.exchange is not None
            mock_connect.assert_awaited_once()

    async def test_connect_disabled(self):
        """Test connect skipped when disabled"""
        # Arrange
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'false'}):
            publisher = ResponseEventPublisher()

            # Act
            await publisher.connect()

            # Assert
            assert publisher.broker_connected is False

    async def test_connect_failure(self):
        """Test connection failure handling"""
        # Arrange
        from aio_pika.exceptions import AMQPException

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}), \
             patch('aio_pika.connect_robust', side_effect=AMQPException("Connection failed")):

            publisher = ResponseEventPublisher()

            # Act
            await publisher.connect()

            # Assert
            assert publisher.broker_connected is False

    async def test_disconnect_success(
        self, mock_rabbitmq_connection, mock_rabbitmq_channel
    ):
        """Test successful disconnect"""
        # Arrange
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()
            publisher.connection = mock_rabbitmq_connection
            publisher.channel = mock_rabbitmq_channel
            publisher.broker_connected = True

            # Act
            await publisher.disconnect()

            # Assert
            assert publisher.broker_connected is False
            assert publisher.connection is None
            assert publisher.channel is None
            mock_rabbitmq_channel.close.assert_awaited_once()
            mock_rabbitmq_connection.close.assert_awaited_once()


# ============================================================================
# Event Publishing Tests
# ============================================================================

@pytest.mark.asyncio
class TestEventPublishing:
    """Test event publishing functionality"""

    async def test_publish_incident_created(
        self, mock_rabbitmq_exchange, org_id
    ):
        """Test publishing incident created event"""
        # Arrange
        incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.DETECTED,
            affected_systems=["api-server"],
            detected_at=datetime.utcnow(),
            detected_by="Test User",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()
            publisher.enabled = True
            publisher.broker_connected = True
            publisher.exchange = mock_rabbitmq_exchange

            # Act
            await publisher.publish_incident_created(incident)

            # Assert
            mock_rabbitmq_exchange.publish.assert_awaited_once()
            call_args = mock_rabbitmq_exchange.publish.call_args
            message = call_args.kwargs['message']
            routing_key = call_args.kwargs['routing_key']

            assert routing_key == "response.incident.created"
            event_data = json.loads(message.body.decode())
            assert event_data['event_type'] == "response.incident.created"
            assert event_data['incident_number'] == "INC-2025-TEST-0001"
            assert event_data['severity'] == "critical"

    async def test_publish_incident_updated(
        self, mock_rabbitmq_exchange, org_id
    ):
        """Test publishing incident updated event"""
        # Arrange
        incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Updated Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.INVESTIGATING,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()
            publisher.enabled = True
            publisher.broker_connected = True
            publisher.exchange = mock_rabbitmq_exchange

            # Act
            await publisher.publish_incident_updated(incident)

            # Assert
            mock_rabbitmq_exchange.publish.assert_awaited_once()
            call_args = mock_rabbitmq_exchange.publish.call_args
            routing_key = call_args.kwargs['routing_key']
            assert routing_key == "response.incident.updated"

    async def test_publish_incident_status_changed(
        self, mock_rabbitmq_exchange, org_id
    ):
        """Test publishing status changed event"""
        # Arrange
        incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.RESOLVED,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()
            publisher.enabled = True
            publisher.broker_connected = True
            publisher.exchange = mock_rabbitmq_exchange

            # Act
            await publisher.publish_incident_status_changed(
                incident,
                IncidentStatus.INVESTIGATING,
                IncidentStatus.RESOLVED
            )

            # Assert
            mock_rabbitmq_exchange.publish.assert_awaited_once()
            call_args = mock_rabbitmq_exchange.publish.call_args
            message = call_args.kwargs['message']
            event_data = json.loads(message.body.decode())
            assert event_data['old_status'] == "investigating"
            assert event_data['new_status'] == "resolved"

    async def test_publish_incident_resolved(
        self, mock_rabbitmq_exchange, org_id
    ):
        """Test publishing incident resolved event"""
        # Arrange
        incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.RESOLVED,
            duration_hours=5.0,
            root_cause="Hardware failure",
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            resolved_at=datetime.utcnow(),
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()
            publisher.enabled = True
            publisher.broker_connected = True
            publisher.exchange = mock_rabbitmq_exchange

            # Act
            await publisher.publish_incident_resolved(incident)

            # Assert
            mock_rabbitmq_exchange.publish.assert_awaited_once()
            call_args = mock_rabbitmq_exchange.publish.call_args
            message = call_args.kwargs['message']
            event_data = json.loads(message.body.decode())
            assert event_data['event_type'] == "response.incident.resolved"
            assert event_data['duration_hours'] == 5.0
            assert event_data['root_cause'] == "Hardware failure"

    async def test_publish_incident_escalated(
        self, mock_rabbitmq_exchange, org_id
    ):
        """Test publishing incident escalated event"""
        # Arrange
        incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.INVESTIGATING,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        escalation_data = IncidentEscalation(
            escalation_reason="Critical issue",
            escalation_level="executive",
            notify_stakeholders=True,
            escalate_to=[uuid4(), uuid4()]
        )

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()
            publisher.enabled = True
            publisher.broker_connected = True
            publisher.exchange = mock_rabbitmq_exchange

            # Act
            await publisher.publish_incident_escalated(incident, escalation_data)

            # Assert
            mock_rabbitmq_exchange.publish.assert_awaited_once()
            call_args = mock_rabbitmq_exchange.publish.call_args
            message = call_args.kwargs['message']
            event_data = json.loads(message.body.decode())
            assert event_data['escalation_level'] == "executive"
            assert event_data['escalation_reason'] == "Critical issue"

    async def test_publish_stakeholder_notification(
        self, mock_rabbitmq_exchange, org_id
    ):
        """Test publishing stakeholder notification event"""
        # Arrange
        incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.INVESTIGATING,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        recipients = ["stakeholder1@example.com", "stakeholder2@example.com"]
        message = "Critical incident requires your attention"

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()
            publisher.enabled = True
            publisher.broker_connected = True
            publisher.exchange = mock_rabbitmq_exchange

            # Act
            await publisher.publish_stakeholder_notification(incident, message, recipients)

            # Assert
            mock_rabbitmq_exchange.publish.assert_awaited_once()
            call_args = mock_rabbitmq_exchange.publish.call_args
            event_data = json.loads(call_args.kwargs['message'].body.decode())
            assert event_data['event_type'] == "response.stakeholder.notification"
            assert event_data['recipients'] == recipients
            assert event_data['message'] == message

    async def test_publish_compliance_violation(
        self, mock_rabbitmq_exchange, org_id, incident_id
    ):
        """Test publishing compliance violation event"""
        # Arrange
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()
            publisher.enabled = True
            publisher.broker_connected = True
            publisher.exchange = mock_rabbitmq_exchange

            # Act
            await publisher.publish_compliance_violation(
                incident_id=incident_id,
                incident_number="INC-2025-TEST-0001",
                organization_id=org_id,
                violation_type="RTO_EXCEEDED",
                details={"target_rto": 4.0, "actual_rto": 6.0}
            )

            # Assert
            mock_rabbitmq_exchange.publish.assert_awaited_once()
            call_args = mock_rabbitmq_exchange.publish.call_args
            event_data = json.loads(call_args.kwargs['message'].body.decode())
            assert event_data['violation_type'] == "RTO_EXCEEDED"
            assert event_data['details']['actual_rto'] == 6.0

    async def test_publish_when_disabled(self, org_id):
        """Test publishing skipped when disabled"""
        # Arrange
        incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.DETECTED,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'false'}):
            publisher = ResponseEventPublisher()

            # Act
            await publisher.publish_incident_created(incident)

            # Assert - no exception should be raised
            assert publisher.enabled is False

    async def test_publish_auto_connects(
        self, mock_rabbitmq_connection, mock_rabbitmq_channel, mock_rabbitmq_exchange, org_id
    ):
        """Test publishing auto-connects if not connected"""
        # Arrange
        incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.DETECTED,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}), \
             patch('aio_pika.connect_robust', return_value=mock_rabbitmq_connection):

            mock_rabbitmq_connection.channel.return_value = mock_rabbitmq_channel
            mock_rabbitmq_channel.declare_exchange.return_value = mock_rabbitmq_exchange

            publisher = ResponseEventPublisher()

            # Act
            await publisher.publish_incident_created(incident)

            # Assert
            assert publisher.broker_connected is True
            mock_rabbitmq_exchange.publish.assert_awaited_once()

    async def test_publish_handles_amqp_error(
        self, mock_rabbitmq_exchange, org_id
    ):
        """Test publishing handles AMQP errors gracefully"""
        # Arrange
        from aio_pika.exceptions import AMQPException

        incident = Incident(
            id=uuid4(),
            organization_id=org_id,
            incident_number="INC-2025-TEST-0001",
            title="Test Incident",
            description="Test",
            incident_type=IncidentType.SYSTEM_FAILURE,
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.DETECTED,
            affected_systems=[],
            detected_at=datetime.utcnow(),
            detected_by="Test",
            response_team=None,
            actions=[],
            communications=[],
            timeline=[],
            metrics=[],
            tags=[]
        )

        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            publisher = ResponseEventPublisher()
            publisher.enabled = True
            publisher.broker_connected = True
            publisher.exchange = mock_rabbitmq_exchange

            mock_rabbitmq_exchange.publish.side_effect = AMQPException("Connection lost")

            # Act - should not raise exception
            await publisher.publish_incident_created(incident)

            # Assert
            assert publisher.broker_connected is False  # Marked as disconnected
