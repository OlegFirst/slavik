"""
Test Orchestrator Execution Methods
====================================

Tests for auto_resolve, escalate_to_human, emergency_stop, and service registry.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from .orchestrator import AIOrchestrator
from .service_registry import ServiceRegistry, ServiceInfo, ServiceStatus
from .models import (
    Decision, Strategy, ActionType, PriorityLevel
)


class TestServiceRegistry:
    """Test ServiceRegistry functionality."""

    @pytest.fixture
    async def registry(self):
        """Create service registry."""
        registry = ServiceRegistry()
        await registry.initialize()
        yield registry
        await registry.shutdown()

    @pytest.mark.asyncio
    async def test_register_service(self, registry):
        """Test service registration."""
        await registry.register_service(
            'test-service',
            'http://localhost:8000',
            '/health'
        )

        assert 'test-service' in registry.services
        service = registry.services['test-service']
        assert service.name == 'test-service'
        assert service.url == 'http://localhost:8000'

    @pytest.mark.asyncio
    async def test_get_healthy_service(self, registry):
        """Test getting healthy service."""
        # Register and mark as healthy
        await registry.register_service(
            'test-service',
            'http://localhost:8000',
            '/health'
        )
        registry.services['test-service'].status = ServiceStatus.HEALTHY

        service = await registry.get_service('test-service')
        assert service is not None
        assert service.name == 'test-service'

    @pytest.mark.asyncio
    async def test_get_unavailable_service(self, registry):
        """Test getting unavailable service."""
        # Register and mark as unhealthy
        await registry.register_service(
            'test-service',
            'http://localhost:8000',
            '/health'
        )
        registry.services['test-service'].status = ServiceStatus.UNHEALTHY

        service = await registry.get_service('test-service')
        assert service is None

    @pytest.mark.asyncio
    async def test_call_service_success(self, registry):
        """Test successful service call."""
        await registry.register_service(
            'test-service',
            'http://localhost:8000',
            '/health'
        )
        registry.services['test-service'].status = ServiceStatus.HEALTHY

        # Mock HTTP session
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'success': True})

        with patch.object(registry._session, 'request') as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response

            result = await registry.call_service(
                'test-service',
                'POST',
                '/api/test',
                {'data': 'test'}
            )

            assert result == {'success': True}
            assert registry.services['test-service'].failure_count == 0

    @pytest.mark.asyncio
    async def test_call_service_with_retry(self, registry):
        """Test service call with retry on failure."""
        await registry.register_service(
            'test-service',
            'http://localhost:8000',
            '/health'
        )
        registry.services['test-service'].status = ServiceStatus.HEALTHY
        registry.retry_delay = 0.1  # Speed up test

        # Mock first call fails, second succeeds
        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            mock_response = AsyncMock()
            if call_count == 1:
                raise asyncio.TimeoutError("Timeout")
            else:
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={'success': True})
                return mock_response

        with patch.object(registry._session, 'request', side_effect=mock_request):
            result = await registry.call_service(
                'test-service',
                'GET',
                '/api/test'
            )

            assert result == {'success': True}
            assert call_count == 2  # First failed, second succeeded

    @pytest.mark.asyncio
    async def test_call_service_all_retries_fail(self, registry):
        """Test service call when all retries fail."""
        await registry.register_service(
            'test-service',
            'http://localhost:8000',
            '/health'
        )
        registry.services['test-service'].status = ServiceStatus.HEALTHY
        registry.max_retries = 2
        registry.retry_delay = 0.1

        # Mock all calls fail
        with patch.object(registry._session, 'request', side_effect=asyncio.TimeoutError):
            with pytest.raises(RuntimeError) as exc_info:
                await registry.call_service(
                    'test-service',
                    'GET',
                    '/api/test'
                )

            assert "failed after 2 attempts" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_check(self, registry):
        """Test health check updates service status."""
        await registry.register_service(
            'test-service',
            'http://localhost:8000',
            '/health'
        )
        service = registry.services['test-service']

        # Mock healthy response
        mock_response = AsyncMock()
        mock_response.status = 200

        with patch.object(registry._session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            await registry._check_service_health(service)

            assert service.status == ServiceStatus.HEALTHY
            assert service.failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker(self, registry):
        """Test circuit breaker opens after threshold."""
        await registry.register_service(
            'test-service',
            'http://localhost:8000',
            '/health'
        )
        registry.circuit_breaker_threshold = 3
        service = registry.services['test-service']

        # Mock failed health checks
        with patch.object(registry._session, 'get', side_effect=Exception("Connection failed")):
            # Fail multiple times
            for _ in range(3):
                await registry._check_service_health(service)

            assert service.status == ServiceStatus.UNHEALTHY
            assert service.failure_count >= 3


class TestOrchestratorExecution:
    """Test orchestrator execution methods."""

    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator for testing."""
        # Create with memory backend to avoid Redis dependency
        orchestrator = AIOrchestrator(event_bus_backend='memory')

        # Mock components to avoid initialization issues
        orchestrator.memory = AsyncMock()
        orchestrator.memory.working_memory = AsyncMock()
        orchestrator.memory.short_term_memory = AsyncMock()
        orchestrator.memory.get_stats = MagicMock(return_value={})
        orchestrator.memory.initialize = AsyncMock()
        orchestrator.memory.close = AsyncMock()

        orchestrator.context_aggregator = AsyncMock()
        orchestrator.context_aggregator.initialize = AsyncMock()

        orchestrator.strategy_selector = AsyncMock()
        orchestrator.strategy_selector.initialize = AsyncMock()

        orchestrator.delegation_manager = AsyncMock()
        orchestrator.delegation_manager.initialize = AsyncMock()

        orchestrator.safety_monitor = None
        orchestrator.evolution_engine = None

        orchestrator.service_registry = AsyncMock()
        orchestrator.service_registry.initialize = AsyncMock()
        orchestrator.service_registry.shutdown = AsyncMock()
        orchestrator.service_registry.call_service = AsyncMock()

        orchestrator.event_bus = AsyncMock()
        orchestrator.event_bus.close = AsyncMock()
        orchestrator.event_bus.publish = AsyncMock()
        orchestrator.event_bus.subscribe = AsyncMock()

        await orchestrator.initialize()

        yield orchestrator

        await orchestrator.shutdown()

    @pytest.mark.asyncio
    async def test_auto_resolve_with_service_call(self, orchestrator):
        """Test auto_resolve makes service calls."""
        # Create decision with action details
        strategy = Strategy(
            action="Create BIA process",
            rationale="Business impact analysis needed",
            confidence=0.95,
            source="ai_generated",
            metadata={
                'service': 'bia',
                'method': 'POST',
                'endpoint': '/api/v1/processes',
                'data': {'name': 'Test Process'}
            }
        )

        decision = Decision(
            action=ActionType.AUTO_RESOLVE,
            rationale="Creating BIA process",
            priority=PriorityLevel.HIGH,
            confidence=0.95,
            strategies_considered=[strategy],
            metadata={
                'situation': {'process_name': 'Test Process'},
                'tenant_id': 'test-tenant'
            }
        )

        # Mock service call success
        orchestrator.service_registry.call_service.return_value = {
            'id': 123,
            'name': 'Test Process',
            'status': 'created'
        }

        result = await orchestrator._auto_resolve(decision)

        assert result['success'] is True
        assert result['action'] == 'auto_resolve'
        assert result['service'] == 'bia'
        assert 'result' in result

        # Verify service was called
        orchestrator.service_registry.call_service.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_resolve_service_unavailable(self, orchestrator):
        """Test auto_resolve handles service unavailable."""
        strategy = Strategy(
            action="Create risk assessment",
            rationale="Risk analysis needed",
            confidence=0.9,
            source="ai_generated",
            metadata={
                'service': 'risk',
                'method': 'POST',
                'endpoint': '/api/v1/assessments',
                'data': {}
            }
        )

        decision = Decision(
            action=ActionType.AUTO_RESOLVE,
            rationale="Creating risk assessment",
            priority=PriorityLevel.HIGH,
            confidence=0.9,
            strategies_considered=[strategy],
            metadata={'situation': {}}
        )

        # Mock service unavailable
        orchestrator.service_registry.call_service.side_effect = ValueError("Service 'risk' not available")

        result = await orchestrator._auto_resolve(decision)

        assert result['success'] is False
        assert result['fallback'] == 'escalate_to_human'
        assert 'error' in result

    @pytest.mark.asyncio
    async def test_auto_resolve_generic_resolution(self, orchestrator):
        """Test auto_resolve with no specific action."""
        decision = Decision(
            action=ActionType.AUTO_RESOLVE,
            rationale="Generic resolution",
            priority=PriorityLevel.MEDIUM,
            confidence=0.8,
            metadata={'situation': {}}
        )

        result = await orchestrator._auto_resolve(decision)

        assert result['success'] is True
        assert result['resolution_type'] == 'generic'

        # Should not call service
        orchestrator.service_registry.call_service.assert_not_called()

    @pytest.mark.asyncio
    async def test_escalate_to_human(self, orchestrator):
        """Test escalate_to_human creates incident and sends notifications."""
        decision = Decision(
            action=ActionType.ESCALATE_HUMAN,
            rationale="Low confidence - human review needed",
            priority=PriorityLevel.HIGH,
            confidence=0.6,
            safety_approved=True,
            metadata={
                'situation': {'workflow_id': 'wf_123'},
                'tenant_id': 'test-tenant'
            }
        )

        result = await orchestrator._escalate_to_human(decision)

        assert result['success'] is True
        assert result['action'] == 'escalate_to_human'
        assert result['requires_human_intervention'] is True
        assert 'escalation_id' in result
        assert 'ticket_id' in result
        assert result['notification_sent'] is True

        # Verify event was published
        orchestrator.event_bus.publish.assert_called()

    @pytest.mark.asyncio
    async def test_escalate_to_human_critical_priority(self, orchestrator):
        """Test critical escalation sends critical notifications."""
        decision = Decision(
            action=ActionType.ESCALATE_HUMAN,
            rationale="Critical safety concern",
            priority=PriorityLevel.CRITICAL,
            confidence=0.3,
            safety_approved=False,
            metadata={'situation': {}}
        )

        result = await orchestrator._escalate_to_human(decision)

        assert result['priority'] == 'CRITICAL'
        assert result['incident_ticket']['priority'] == 'CRITICAL'

    @pytest.mark.asyncio
    async def test_emergency_stop(self, orchestrator):
        """Test emergency_stop triggers shutdown procedures."""
        decision = Decision(
            action=ActionType.EMERGENCY_STOP,
            rationale="Critical system failure detected",
            priority=PriorityLevel.CRITICAL,
            confidence=1.0,
            metadata={
                'situation': {'error': 'System malfunction'},
                'tenant_id': 'test-tenant'
            }
        )

        result = await orchestrator._emergency_stop(decision)

        assert result['success'] is True
        assert result['action'] == 'emergency_stop'
        assert result['critical'] is True
        assert 'emergency_id' in result
        assert result['requires_manual_intervention'] is True
        assert 'recovery_instructions' in result
        assert len(result['recovery_instructions']) > 0

        # Verify emergency event was published
        assert orchestrator.event_bus.publish.call_count >= 2  # Emergency stop + workflow stop

        # Verify stats updated
        assert 'emergency_stops' in orchestrator.stats

    @pytest.mark.asyncio
    async def test_emergency_stop_stops_workflows(self, orchestrator):
        """Test emergency_stop sends workflow stop command."""
        decision = Decision(
            action=ActionType.EMERGENCY_STOP,
            rationale="Emergency shutdown required",
            priority=PriorityLevel.CRITICAL,
            confidence=1.0,
            metadata={'situation': {}, 'tenant_id': 'test'}
        )

        result = await orchestrator._emergency_stop(decision)

        assert 'all_workflows' in result['stopped_workflows']

    @pytest.mark.asyncio
    async def test_parse_action_from_decision_bia(self, orchestrator):
        """Test parsing BIA action from decision."""
        strategy = Strategy(
            action="Create BIA process for IT systems",
            rationale="Need BIA",
            confidence=0.9,
            source="ai_generated"
        )

        decision = Decision(
            action=ActionType.AUTO_RESOLVE,
            rationale="Create BIA",
            priority=PriorityLevel.MEDIUM,
            confidence=0.9,
            strategies_considered=[strategy],
            metadata={'situation': {'process_name': 'IT Systems'}}
        )

        action_details = orchestrator._parse_action_from_decision(decision)

        assert action_details['service'] == 'bia'
        assert action_details['method'] == 'POST'
        assert action_details['endpoint'] == '/api/v1/processes'

    @pytest.mark.asyncio
    async def test_parse_action_from_decision_risk(self, orchestrator):
        """Test parsing risk action from decision."""
        strategy = Strategy(
            action="Create risk assessment",
            rationale="Risk analysis needed",
            confidence=0.9,
            source="ai_generated"
        )

        decision = Decision(
            action=ActionType.AUTO_RESOLVE,
            rationale="Assess risk",
            priority=PriorityLevel.HIGH,
            confidence=0.9,
            strategies_considered=[strategy],
            metadata={'situation': {}}
        )

        action_details = orchestrator._parse_action_from_decision(decision)

        assert action_details['service'] == 'risk'
        assert action_details['method'] == 'POST'
        assert action_details['endpoint'] == '/api/v1/assessments'

    @pytest.mark.asyncio
    async def test_parse_action_from_decision_workflow(self, orchestrator):
        """Test parsing workflow restart action."""
        strategy = Strategy(
            action="Restart workflow",
            rationale="Resume stuck workflow",
            confidence=0.95,
            source="procedural_memory"
        )

        decision = Decision(
            action=ActionType.AUTO_RESOLVE,
            rationale="Resume workflow",
            priority=PriorityLevel.HIGH,
            confidence=0.95,
            strategies_considered=[strategy],
            metadata={'situation': {'workflow_id': 'wf_123'}}
        )

        action_details = orchestrator._parse_action_from_decision(decision)

        assert action_details['service'] == 'planning'
        assert action_details['method'] == 'POST'
        assert 'wf_123' in action_details['endpoint']


@pytest.mark.asyncio
async def test_orchestrator_integration():
    """Integration test for full execution flow."""
    orchestrator = AIOrchestrator(event_bus_backend='memory')

    # Mock components
    orchestrator.memory = AsyncMock()
    orchestrator.memory.working_memory = AsyncMock()
    orchestrator.memory.short_term_memory = AsyncMock()
    orchestrator.memory.get_stats = MagicMock(return_value={})
    orchestrator.memory.initialize = AsyncMock()
    orchestrator.memory.close = AsyncMock()

    orchestrator.context_aggregator = AsyncMock()
    orchestrator.context_aggregator.initialize = AsyncMock()

    orchestrator.strategy_selector = AsyncMock()
    orchestrator.strategy_selector.initialize = AsyncMock()

    orchestrator.delegation_manager = AsyncMock()
    orchestrator.delegation_manager.initialize = AsyncMock()

    orchestrator.safety_monitor = None
    orchestrator.evolution_engine = None

    orchestrator.event_bus.close = AsyncMock()
    orchestrator.event_bus.publish = AsyncMock()
    orchestrator.event_bus.subscribe = AsyncMock()

    # Initialize
    await orchestrator.initialize()

    # Verify service registry initialized
    assert orchestrator.service_registry is not None
    assert orchestrator.service_registry._initialized

    # Verify services registered
    assert len(orchestrator.service_registry.services) == 5
    assert 'bia' in orchestrator.service_registry.services
    assert 'risk' in orchestrator.service_registry.services

    # Cleanup
    await orchestrator.shutdown()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
