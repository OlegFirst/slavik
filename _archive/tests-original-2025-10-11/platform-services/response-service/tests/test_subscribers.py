"""
Response Module - Event Subscribers Tests
ISO 22301:2019 Clause 8.4 - Incident Response

Unit tests for ResponseEventSubscriber
"""

import pytest
import json
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call

from events.subscribers import ResponseEventSubscriber
from models.domain import (
    Incident, IncidentCreate, IncidentStatus, IncidentSeverity, IncidentType
)


# ============================================================================
# Subscriber Initialization Tests
# ============================================================================

@pytest.mark.asyncio
class TestSubscriberInitialization:
    """Test event subscriber initialization"""

    def test_init_disabled_by_default(self):
        """Test subscriber is disabled by default"""
        # Arrange & Act
        with patch.dict('os.environ', {}, clear=True):
            subscriber = ResponseEventSubscriber()

            # Assert
            assert subscriber.enabled is False
            assert subscriber.broker_connected is False
            assert len(subscriber.handlers) > 0  # Handlers are registered

    def test_init_enabled_via_env(self):
        """Test subscriber enabled via environment variable"""
        # Arrange & Act
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            subscriber = ResponseEventSubscriber()

            # Assert
            assert subscriber.enabled is True

    def test_init_with_service(self, mock_db_session):
        """Test subscriber initialization with service"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)

        # Act
        subscriber = ResponseEventSubscriber(service=service)

        # Assert
        assert subscriber.service is not None

    def test_handlers_registered(self):
        """Test event handlers are registered on init"""
        # Arrange & Act
        subscriber = ResponseEventSubscriber()

        # Assert
        assert "risk.assessment.high_risk_detected" in subscriber.handlers
        assert "risk.assessment.critical_risk" in subscriber.handlers
        assert "impact.analysis.high_impact" in subscriber.handlers
        assert "recovery.failure" in subscriber.handlers
        assert "recovery.rto_exceeded" in subscriber.handlers
        assert "monitoring.alert.critical" in subscriber.handlers
        assert "external.disaster_alert" in subscriber.handlers
        assert "external.security_breach" in subscriber.handlers


# ============================================================================
# Connection Management Tests
# ============================================================================

@pytest.mark.asyncio
class TestSubscriberConnection:
    """Test RabbitMQ connection management for subscriber"""

    async def test_start_success(
        self, mock_rabbitmq_connection, mock_rabbitmq_channel,
        mock_rabbitmq_exchange, mock_rabbitmq_queue
    ):
        """Test successful subscriber start"""
        # Arrange
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}), \
             patch('aio_pika.connect_robust', return_value=mock_rabbitmq_connection):

            mock_rabbitmq_connection.channel.return_value = mock_rabbitmq_channel
            mock_rabbitmq_channel.declare_exchange.return_value = mock_rabbitmq_exchange
            mock_rabbitmq_channel.declare_queue.return_value = mock_rabbitmq_queue

            subscriber = ResponseEventSubscriber()

            # Act
            await subscriber.start()

            # Assert
            assert subscriber.broker_connected is True
            mock_rabbitmq_channel.set_qos.assert_awaited_once()
            mock_rabbitmq_queue.bind.assert_awaited()  # Bound to multiple routing keys
            mock_rabbitmq_queue.consume.assert_awaited_once()

    async def test_start_disabled(self):
        """Test start skipped when disabled"""
        # Arrange
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'false'}):
            subscriber = ResponseEventSubscriber()

            # Act
            await subscriber.start()

            # Assert
            assert subscriber.broker_connected is False

    async def test_start_binds_routing_keys(
        self, mock_rabbitmq_connection, mock_rabbitmq_channel,
        mock_rabbitmq_exchange, mock_rabbitmq_queue
    ):
        """Test subscriber binds to correct routing keys"""
        # Arrange
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}), \
             patch('aio_pika.connect_robust', return_value=mock_rabbitmq_connection):

            mock_rabbitmq_connection.channel.return_value = mock_rabbitmq_channel
            mock_rabbitmq_channel.declare_exchange.return_value = mock_rabbitmq_exchange
            mock_rabbitmq_channel.declare_queue.return_value = mock_rabbitmq_queue

            subscriber = ResponseEventSubscriber()

            # Act
            await subscriber.start()

            # Assert
            bind_calls = mock_rabbitmq_queue.bind.call_args_list
            routing_keys = [call.kwargs['routing_key'] for call in bind_calls]

            assert "risk.*" in routing_keys
            assert "impact.*" in routing_keys
            assert "recovery.*" in routing_keys
            assert "monitoring.*" in routing_keys
            assert "external.*" in routing_keys

    async def test_stop_success(
        self, mock_rabbitmq_connection, mock_rabbitmq_channel
    ):
        """Test successful subscriber stop"""
        # Arrange
        with patch.dict('os.environ', {'EVENT_BUS_ENABLED': 'true'}):
            subscriber = ResponseEventSubscriber()
            subscriber.connection = mock_rabbitmq_connection
            subscriber.channel = mock_rabbitmq_channel
            subscriber.broker_connected = True

            # Act
            await subscriber.stop()

            # Assert
            assert subscriber.broker_connected is False
            mock_rabbitmq_channel.close.assert_awaited_once()
            mock_rabbitmq_connection.close.assert_awaited_once()


# ============================================================================
# Event Handler Tests
# ============================================================================

@pytest.mark.asyncio
class TestEventHandlers:
    """Test individual event handlers"""

    async def test_handle_high_risk_detected(self, mock_db_session, org_id):
        """Test handling high risk detected event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "risk_id": str(uuid4()),
            "risk_level": "high",
            "organization_id": str(org_id),
            "risk_name": "Critical Security Risk",
            "description": "High risk detected in authentication system",
            "affected_systems": ["auth-service"]
        }

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_high_risk_detected(event_data)

            # Assert
            mock_create.assert_awaited_once()

    async def test_handle_critical_risk(self, mock_db_session, org_id):
        """Test handling critical risk event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "risk_id": str(uuid4()),
            "organization_id": str(org_id),
            "risk_name": "Critical Risk",
            "severity": "critical"
        }

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_critical_risk(event_data)

            # Assert
            mock_create.assert_awaited_once()

    async def test_handle_high_impact(self, mock_db_session, org_id):
        """Test handling high impact event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "organization_id": str(org_id),
            "impact_level": "high",
            "event_name": "Service Disruption",
            "description": "Major service disruption detected",
            "affected_systems": ["payment-service", "notification-service"]
        }

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_high_impact(event_data)

            # Assert
            mock_create.assert_awaited_once()

    async def test_handle_recovery_failure(self, mock_db_session, org_id):
        """Test handling recovery failure event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "organization_id": str(org_id),
            "service_name": "Database Service",
            "error_message": "Failover failed",
            "recovery_id": str(uuid4())
        }

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_recovery_failure(event_data)

            # Assert
            mock_create.assert_awaited_once()

    async def test_handle_rto_exceeded(self, mock_db_session, org_id):
        """Test handling RTO exceeded event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "organization_id": str(org_id),
            "service_name": "Production API",
            "target_rto": 4.0,
            "actual_rto": 6.5
        }

        with patch.object(subscriber, '_create_compliance_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_rto_exceeded(event_data)

            # Assert
            mock_create.assert_awaited_once()
            call_args = mock_create.call_args
            assert call_args.kwargs['violation_type'] == "RTO_EXCEEDED"

    async def test_handle_rpo_exceeded(self, mock_db_session, org_id):
        """Test handling RPO exceeded event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "organization_id": str(org_id),
            "service_name": "Database",
            "target_rpo": 1.0,
            "actual_rpo": 2.5
        }

        with patch.object(subscriber, '_create_compliance_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_rpo_exceeded(event_data)

            # Assert
            mock_create.assert_awaited_once()
            call_args = mock_create.call_args
            assert call_args.kwargs['violation_type'] == "RPO_EXCEEDED"

    async def test_handle_critical_alert(self, mock_db_session, org_id):
        """Test handling critical alert event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "organization_id": str(org_id),
            "alert_name": "System Critical",
            "severity": "critical",
            "description": "Critical system alert"
        }

        with patch.object(subscriber, '_create_incident_from_alert', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_critical_alert(event_data)

            # Assert
            mock_create.assert_awaited_once()

    async def test_handle_system_down(self, mock_db_session, org_id):
        """Test handling system down event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "organization_id": str(org_id),
            "system_name": "Payment Gateway",
            "timestamp": datetime.utcnow().isoformat()
        }

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_system_down(event_data)

            # Assert
            mock_create.assert_awaited_once()

    async def test_handle_disaster_alert(self, mock_db_session, org_id):
        """Test handling disaster alert event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "organization_id": str(org_id),
            "disaster_type": "Earthquake",
            "description": "Magnitude 7.0 earthquake detected",
            "affected_locations": ["datacenter-1", "office-sf"]
        }

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_disaster_alert(event_data)

            # Assert
            mock_create.assert_awaited_once()

    async def test_handle_security_breach(self, mock_db_session, org_id):
        """Test handling security breach event"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        event_data = {
            "organization_id": str(org_id),
            "breach_type": "Data Breach",
            "description": "Unauthorized access to customer data",
            "affected_systems": ["customer-db"],
            "breach_id": str(uuid4())
        }

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._handle_security_breach(event_data)

            # Assert
            mock_create.assert_awaited_once()


# ============================================================================
# Message Processing Tests
# ============================================================================

@pytest.mark.asyncio
class TestMessageProcessing:
    """Test message processing functionality"""

    async def test_on_message_routes_to_handler(self):
        """Test message routing to correct handler"""
        # Arrange
        subscriber = ResponseEventSubscriber()

        mock_message = MagicMock()
        mock_message.routing_key = "risk.assessment.high_risk_detected"
        mock_message.body = json.dumps({
            "risk_id": str(uuid4()),
            "risk_level": "high",
            "organization_id": str(uuid4())
        }).encode()
        mock_message.ack = AsyncMock()

        with patch.object(subscriber, '_handle_high_risk_detected', return_value=AsyncMock()) as mock_handler:
            # Act
            await subscriber._on_message(mock_message)

            # Assert
            mock_handler.assert_awaited_once()
            mock_message.ack.assert_awaited_once()

    async def test_on_message_no_handler(self):
        """Test message with no registered handler"""
        # Arrange
        subscriber = ResponseEventSubscriber()

        mock_message = MagicMock()
        mock_message.routing_key = "unknown.event.type"
        mock_message.body = json.dumps({"test": "data"}).encode()
        mock_message.ack = AsyncMock()

        # Act
        await subscriber._on_message(mock_message)

        # Assert
        mock_message.ack.assert_awaited_once()  # Still acknowledged

    async def test_on_message_invalid_json(self):
        """Test message with invalid JSON"""
        # Arrange
        subscriber = ResponseEventSubscriber()

        mock_message = MagicMock()
        mock_message.routing_key = "test.event"
        mock_message.body = b"invalid json"
        mock_message.reject = AsyncMock()

        # Act
        await subscriber._on_message(mock_message)

        # Assert
        mock_message.reject.assert_awaited_once_with(requeue=False)

    async def test_on_message_handler_error(self):
        """Test message processing when handler raises error"""
        # Arrange
        subscriber = ResponseEventSubscriber()

        mock_message = MagicMock()
        mock_message.routing_key = "risk.assessment.high_risk_detected"
        mock_message.body = json.dumps({"test": "data"}).encode()
        mock_message.reject = AsyncMock()

        with patch.object(
            subscriber,
            '_handle_high_risk_detected',
            side_effect=Exception("Handler error")
        ):
            # Act
            await subscriber._on_message(mock_message)

            # Assert
            mock_message.reject.assert_awaited_once_with(requeue=False)


# ============================================================================
# Custom Handler Registration Tests
# ============================================================================

@pytest.mark.asyncio
class TestCustomHandlers:
    """Test custom handler registration"""

    def test_register_handler(self):
        """Test registering custom handler"""
        # Arrange
        subscriber = ResponseEventSubscriber()

        async def custom_handler(event_data):
            pass

        # Act
        subscriber.register_handler("custom.event", custom_handler)

        # Assert
        assert "custom.event" in subscriber.handlers
        assert subscriber.handlers["custom.event"] == custom_handler

    def test_unregister_handler(self):
        """Test unregistering handler"""
        # Arrange
        subscriber = ResponseEventSubscriber()

        async def custom_handler(event_data):
            pass

        subscriber.register_handler("custom.event", custom_handler)

        # Act
        subscriber.unregister_handler("custom.event")

        # Assert
        assert "custom.event" not in subscriber.handlers

    def test_unregister_nonexistent_handler(self):
        """Test unregistering non-existent handler"""
        # Arrange
        subscriber = ResponseEventSubscriber()

        # Act - should not raise exception
        subscriber.unregister_handler("nonexistent.event")

        # Assert
        assert "nonexistent.event" not in subscriber.handlers


# ============================================================================
# Helper Methods Tests
# ============================================================================

@pytest.mark.asyncio
class TestHelperMethods:
    """Test subscriber helper methods"""

    async def test_create_incident_from_risk(self, mock_db_session, org_id):
        """Test creating incident from risk assessment"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        risk_data = {
            "risk_id": str(uuid4()),
            "risk_name": "High Security Risk",
            "description": "Critical vulnerability detected",
            "affected_systems": ["api-gateway"]
        }

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._create_incident_from_risk(
                risk_id=risk_data["risk_id"],
                organization_id=str(org_id),
                severity="high",
                risk_data=risk_data
            )

            # Assert
            mock_create.assert_awaited_once()
            call_args = mock_create.call_args
            incident_data = call_args.kwargs['incident_data']
            assert incident_data.severity == IncidentSeverity.HIGH
            assert incident_data.incident_type == IncidentType.OTHER

    async def test_create_incident_from_alert(self, mock_db_session, org_id):
        """Test creating incident from monitoring alert"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        alert_data = {
            "organization_id": str(org_id),
            "alert_name": "CPU Threshold Exceeded",
            "severity": "critical",
            "description": "Server CPU usage above 95%",
            "affected_systems": ["web-server-01"]
        }

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._create_incident_from_alert(alert_data)

            # Assert
            mock_create.assert_awaited_once()

    async def test_create_compliance_incident(self, mock_db_session, org_id):
        """Test creating compliance violation incident"""
        # Arrange
        from services.business_logic import ResponseService

        service = ResponseService(mock_db_session)
        subscriber = ResponseEventSubscriber(service=service)

        with patch.object(service, 'create_incident', return_value=AsyncMock()) as mock_create:
            # Act
            await subscriber._create_compliance_incident(
                organization_id=str(org_id),
                violation_type="RTO_EXCEEDED",
                service_name="Production Database",
                details={"target_rto": 4.0, "actual_rto": 6.0}
            )

            # Assert
            mock_create.assert_awaited_once()
            call_args = mock_create.call_args
            incident_data = call_args.kwargs['incident_data']
            assert "RTO_EXCEEDED" in incident_data.title
            assert incident_data.severity == IncidentSeverity.HIGH

    async def test_helper_without_service(self, org_id):
        """Test helper methods without service initialized"""
        # Arrange
        subscriber = ResponseEventSubscriber(service=None)

        # Act - should not raise exception
        await subscriber._create_incident_from_risk(
            risk_id=str(uuid4()),
            organization_id=str(org_id),
            severity="high",
            risk_data={}
        )

        # Assert - no exception raised, just logged warning
