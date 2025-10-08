"""
Complete real tests for Service Discovery with actual scenarios
Tests service registration, health monitoring, and ISO service mapping
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime


@pytest.mark.asyncio
class TestServiceRegistryInitialization:
    """Test service registry initialization"""

    async def test_service_registry_initializes_empty(self):
        """Test service registry starts with no registered services"""
        # ARRANGE & ACT
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        # ASSERT
        assert registry is not None
        services = await registry.get_all_services()
        assert isinstance(services, list)
        assert len(services) == 0


    async def test_service_registry_initializes_with_storage_backend(self):
        """Test registry can initialize with storage backend"""
        # ARRANGE
        with patch('infrastructure.runtime.service_discovery.service_registry.RedisClient') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis.return_value = mock_redis_instance

            from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

            # ACT
            registry = ServiceRegistry(storage="redis")

            # ASSERT
            assert registry is not None


@pytest.mark.asyncio
class TestServiceRegistration:
    """Test service registration functionality"""

    async def test_register_bia_workflow_service(self):
        """Test registering BIA workflow service"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        service_info = {
            "service_id": "bia-workflow-service",
            "service_name": "BIA Workflow Service",
            "host": "localhost",
            "port": 8001,
            "protocol": "http",
            "health_endpoint": "/health",
            "metadata": {
                "module": "workflow_intelligence",
                "domain": "bcm",
                "version": "1.0.0"
            }
        }

        # ACT
        result = await registry.register(service_info)

        # ASSERT
        assert result is True
        services = await registry.get_all_services()
        assert len(services) == 1
        assert services[0]["service_id"] == "bia-workflow-service"


    async def test_register_multiple_services(self):
        """Test registering multiple different services"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        services_to_register = [
            {
                "service_id": "bia-service",
                "service_name": "BIA Service",
                "host": "localhost",
                "port": 8001
            },
            {
                "service_id": "risk-service",
                "service_name": "Risk Assessment Service",
                "host": "localhost",
                "port": 8002
            },
            {
                "service_id": "compliance-service",
                "service_name": "Compliance Service",
                "host": "localhost",
                "port": 8003
            }
        ]

        # ACT
        for service in services_to_register:
            await registry.register(service)

        # ASSERT
        all_services = await registry.get_all_services()
        assert len(all_services) == 3


    async def test_register_duplicate_service_updates(self):
        """Test registering same service ID updates existing registration"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        service_v1 = {
            "service_id": "test-service",
            "service_name": "Test Service",
            "host": "localhost",
            "port": 8000,
            "metadata": {"version": "1.0.0"}
        }

        service_v2 = {
            "service_id": "test-service",
            "service_name": "Test Service",
            "host": "localhost",
            "port": 9000,  # Different port
            "metadata": {"version": "2.0.0"}  # Updated version
        }

        # ACT
        await registry.register(service_v1)
        await registry.register(service_v2)

        # ASSERT
        all_services = await registry.get_all_services()
        assert len(all_services) == 1
        assert all_services[0]["port"] == 9000
        assert all_services[0]["metadata"]["version"] == "2.0.0"


@pytest.mark.asyncio
class TestServiceDiscovery:
    """Test service discovery functionality"""

    async def test_discover_service_by_name(self):
        """Test discovering service by service name"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        await registry.register({
            "service_id": "bia-001",
            "service_name": "BIA Service",
            "host": "localhost",
            "port": 8001
        })

        # ACT
        service = await registry.discover("BIA Service")

        # ASSERT
        assert service is not None
        assert service["service_name"] == "BIA Service"
        assert service["port"] == 8001


    async def test_discover_service_by_id(self):
        """Test discovering service by service ID"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        await registry.register({
            "service_id": "compliance-copilot-001",
            "service_name": "Compliance Copilot",
            "host": "localhost",
            "port": 8003
        })

        # ACT
        service = await registry.discover_by_id("compliance-copilot-001")

        # ASSERT
        assert service is not None
        assert service["service_id"] == "compliance-copilot-001"


    async def test_discover_nonexistent_service_returns_none(self):
        """Test discovering service that doesn't exist returns None"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        # ACT
        service = await registry.discover("NonExistent Service")

        # ASSERT
        assert service is None


@pytest.mark.asyncio
class TestHealthMonitoring:
    """Test service health monitoring"""

    async def test_check_service_health_healthy(self):
        """Test health check for healthy service"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        service_info = {
            "service_id": "test-service",
            "host": "localhost",
            "port": 8000,
            "health_endpoint": "/health"
        }

        # Mock HTTP client
        with patch('infrastructure.runtime.service_discovery.health_monitor.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}

            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock()

            # ACT
            health_status = await monitor.check_health(service_info)

            # ASSERT
            assert health_status is not None
            assert health_status["healthy"] is True


    async def test_check_service_health_unhealthy(self):
        """Test health check for unhealthy service"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        service_info = {
            "service_id": "failing-service",
            "host": "localhost",
            "port": 8000,
            "health_endpoint": "/health"
        }

        # Mock HTTP client with connection error
        with patch('infrastructure.runtime.service_discovery.health_monitor.httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(
                side_effect=ConnectionError("Service unreachable")
            )
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock()

            # ACT
            health_status = await monitor.check_health(service_info)

            # ASSERT
            assert health_status is not None
            assert health_status["healthy"] is False


    async def test_health_monitor_tracks_multiple_services(self):
        """Test monitoring health of multiple services"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.health_monitor import HealthMonitor

        monitor = HealthMonitor()

        services = [
            {"service_id": "service-1", "host": "localhost", "port": 8001, "health_endpoint": "/health"},
            {"service_id": "service-2", "host": "localhost", "port": 8002, "health_endpoint": "/health"},
            {"service_id": "service-3", "host": "localhost", "port": 8003, "health_endpoint": "/health"}
        ]

        # Mock HTTP responses
        with patch('infrastructure.runtime.service_discovery.health_monitor.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}

            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock()

            # ACT
            health_results = []
            for service in services:
                result = await monitor.check_health(service)
                health_results.append(result)

            # ASSERT
            assert len(health_results) == 3
            assert all(result["healthy"] for result in health_results)


@pytest.mark.asyncio
class TestISOServiceMapping:
    """Test ISO 22301 service mapping"""

    async def test_map_iso_clause_to_services(self):
        """Test mapping ISO 22301 clauses to responsible services"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.iso_service_map import ISOServiceMapper

        mapper = ISOServiceMapper()

        # ACT
        bia_services = await mapper.get_services_for_clause("8.2.2")  # BIA clause

        # ASSERT
        assert bia_services is not None
        assert isinstance(bia_services, list)
        # Should return BIA-related services


    async def test_get_all_iso_mappings(self):
        """Test retrieving all ISO clause to service mappings"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.iso_service_map import ISOServiceMapper

        mapper = ISOServiceMapper()

        # ACT
        all_mappings = await mapper.get_all_mappings()

        # ASSERT
        assert all_mappings is not None
        assert isinstance(all_mappings, dict)
        # Should contain mappings for various clauses
        assert len(all_mappings) > 0


@pytest.mark.asyncio
class TestServiceRegistryRealScenarios:
    """Test real-world service registry scenarios"""

    async def test_bcm_platform_service_registration(self):
        """Test registering all BCM platform services"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        bcm_services = [
            {
                "service_id": "bia-workflow",
                "service_name": "BIA Workflow Service",
                "host": "localhost",
                "port": 8001,
                "metadata": {"iso_clause": "8.2.2", "module": "workflow_intelligence"}
            },
            {
                "service_id": "risk-assessment",
                "service_name": "Risk Assessment Service",
                "host": "localhost",
                "port": 8002,
                "metadata": {"iso_clause": "8.2.1", "module": "expertise_center"}
            },
            {
                "service_id": "compliance-monitoring",
                "service_name": "Compliance Monitoring Service",
                "host": "localhost",
                "port": 8003,
                "metadata": {"iso_clause": "9.1", "module": "governance"}
            },
            {
                "service_id": "incident-response",
                "service_name": "Incident Response Service",
                "host": "localhost",
                "port": 8004,
                "metadata": {"iso_clause": "8.4", "module": "response"}
            }
        ]

        # ACT
        for service in bcm_services:
            await registry.register(service)

        # ASSERT
        all_services = await registry.get_all_services()
        assert len(all_services) == 4

        # Verify each service registered correctly
        bia_service = await registry.discover_by_id("bia-workflow")
        assert bia_service is not None
        assert bia_service["metadata"]["iso_clause"] == "8.2.2"


    async def test_service_deregistration(self):
        """Test deregistering services"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry

        registry = ServiceRegistry()

        await registry.register({
            "service_id": "temp-service",
            "service_name": "Temporary Service",
            "host": "localhost",
            "port": 9999
        })

        # ACT
        await registry.deregister("temp-service")

        # ASSERT
        service = await registry.discover_by_id("temp-service")
        assert service is None


    async def test_service_registry_with_health_monitoring(self):
        """Test complete service registry with health monitoring"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry
        from infrastructure.runtime.service_discovery.health_monitor import HealthMonitor

        registry = ServiceRegistry()
        monitor = HealthMonitor()

        service_info = {
            "service_id": "monitored-service",
            "service_name": "Monitored Service",
            "host": "localhost",
            "port": 8000,
            "health_endpoint": "/health"
        }

        # ACT - Register service
        await registry.register(service_info)

        # Mock health check
        with patch('infrastructure.runtime.service_discovery.health_monitor.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}

            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock()

            # Check health
            health = await monitor.check_health(service_info)

        # ASSERT
        assert health["healthy"] is True

        service = await registry.discover_by_id("monitored-service")
        assert service is not None


@pytest.mark.integration
@pytest.mark.asyncio
class TestServiceDiscoveryIntegration:
    """Integration tests for service discovery"""

    async def test_end_to_end_service_lifecycle(self):
        """Test complete service lifecycle: register → discover → health check → deregister"""
        # ARRANGE
        from infrastructure.runtime.service_discovery.service_registry import ServiceRegistry
        from infrastructure.runtime.service_discovery.health_monitor import HealthMonitor

        registry = ServiceRegistry()
        monitor = HealthMonitor()

        service_info = {
            "service_id": "lifecycle-test-service",
            "service_name": "Lifecycle Test Service",
            "host": "localhost",
            "port": 8888,
            "health_endpoint": "/health"
        }

        # ACT & ASSERT - Step 1: Register
        registered = await registry.register(service_info)
        assert registered is True

        # ACT & ASSERT - Step 2: Discover
        discovered = await registry.discover_by_id("lifecycle-test-service")
        assert discovered is not None
        assert discovered["service_id"] == "lifecycle-test-service"

        # ACT & ASSERT - Step 3: Health check (mocked)
        with patch('infrastructure.runtime.service_discovery.health_monitor.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}

            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client.return_value.__aexit__ = AsyncMock()

            health = await monitor.check_health(service_info)
            assert health["healthy"] is True

        # ACT & ASSERT - Step 4: Deregister
        await registry.deregister("lifecycle-test-service")
        deregistered = await registry.discover_by_id("lifecycle-test-service")
        assert deregistered is None
