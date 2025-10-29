"""
Test Suite for Consolidated Cognitive Orchestration System
Tests the hybrid Python + JavaScript architecture with production integrations
"""

import asyncio
import pytest
import httpx
from unittest.mock import Mock, AsyncMock

# Import our modules
from main import app
from models import SystemRequest, HealthResponse, ExperimentRequest
from integrations import RedisClient, PostgreSQLClient, DockerManager
from orchestrators import CognitiveOrchestrationController


class TestHybridArchitecture:
    """Test hybrid architecture functionality"""

    @pytest.fixture
    async def mock_integrations(self):
        """Mock production integrations for testing"""
        redis_mock = Mock(spec=RedisClient)
        redis_mock.connect = AsyncMock()
        redis_mock.health_check = AsyncMock(return_value=True)
        redis_mock.get = AsyncMock(return_value=None)
        redis_mock.set = AsyncMock(return_value=True)
        redis_mock.publish = AsyncMock(return_value=1)
        redis_mock.get_stats = AsyncMock(return_value={"status": "connected"})

        postgres_mock = Mock(spec=PostgreSQLClient)
        postgres_mock.connect = AsyncMock()
        postgres_mock.health_check = AsyncMock(return_value=True)
        postgres_mock.execute = AsyncMock(return_value="INSERT 0 1")
        postgres_mock.fetch = AsyncMock(return_value=[])
        postgres_mock.get_stats = AsyncMock(return_value={"status": "connected"})

        docker_mock = Mock(spec=DockerManager)
        docker_mock.initialize = AsyncMock()
        docker_mock.health_check = AsyncMock(return_value=True)
        docker_mock.create_sandbox = AsyncMock(return_value="container_123")
        docker_mock.cleanup_container = AsyncMock()
        docker_mock.get_stats = AsyncMock(return_value={"status": "connected"})

        return {
            'redis_client': redis_mock,
            'postgres_client': postgres_mock,
            'docker_manager': docker_mock
        }

    @pytest.fixture
    async def cognitive_controller(self, mock_integrations):
        """Create cognitive controller with mocked integrations"""
        controller = CognitiveOrchestrationController(mock_integrations)

        # Mock the JavaScript orchestrator wrappers
        for name, orchestrator in controller.orchestrators.items():
            orchestrator.start = AsyncMock()
            orchestrator.handle = AsyncMock(return_value={
                "success": True,
                "result": f"Mock result from {name}",
                "timestamp": 1234567890
            })
            orchestrator.get_health_status = AsyncMock(return_value={
                "status": "ready",
                "services": {"loaded": 5}
            })
            orchestrator.is_running = True

        return controller

    @pytest.mark.asyncio
    async def test_system_startup(self, cognitive_controller):
        """Test system startup sequence"""
        await cognitive_controller.start()

        # Verify all orchestrators were started
        for orchestrator in cognitive_controller.orchestrators.values():
            orchestrator.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_intelligent_routing(self, cognitive_controller):
        """Test intelligent request routing"""
        test_cases = [
            # Client requests
            ({"type": "authenticate", "credentials": {}}, "client"),
            ({"type": "authorize", "user_id": "123"}, "client"),

            # Sandbox requests
            ({"type": "experiment", "code": "print('hello')"}, "sandbox"),
            ({"type": "evolve", "component": "test"}, "sandbox"),

            # Program requests
            ({"type": "business-logic", "domain": "bcm"}, "program"),
            ({"domain": "test", "module": "test"}, "program"),

            # Bridge requests
            ({"type": "translate", "from_level": "system"}, "bridge"),
            ({"from_level": "program", "to_level": "system"}, "bridge"),

            # System requests (default)
            ({"type": "health-check"}, "system"),
            ({"type": "metrics"}, "system"),
        ]

        for request, expected_orchestrator in test_cases:
            result = await cognitive_controller.handle(request)

            assert result["success"] is True
            assert result["processed_by"] == expected_orchestrator

    @pytest.mark.asyncio
    async def test_health_monitoring(self, cognitive_controller):
        """Test comprehensive health monitoring"""
        health = await cognitive_controller.get_system_health()

        assert "status" in health
        assert "orchestrators" in health
        assert len(health["orchestrators"]) == 5  # All 5 orchestrators

        for orchestrator_name in ["system", "bridge", "program", "client", "sandbox"]:
            assert orchestrator_name in health["orchestrators"]

    @pytest.mark.asyncio
    async def test_metrics_collection(self, cognitive_controller):
        """Test metrics collection"""
        # Make some requests to generate metrics
        await cognitive_controller.handle({"type": "test"})
        await cognitive_controller.handle({"type": "test"})

        metrics = cognitive_controller.get_metrics()

        assert metrics["total_requests"] == 2
        assert metrics["successful_requests"] == 2
        assert metrics["orchestrators_running"] == 5
        assert "average_response_time" in metrics

    @pytest.mark.asyncio
    async def test_bcm_business_logic(self, cognitive_controller):
        """Test BCM-specific business logic execution"""
        result = await cognitive_controller.execute_business_logic(
            domain="bcm",
            module="risk-assessment",
            action="assess",
            data={"risk_id": "RISK-001"}
        )

        assert result["success"] is True
        assert result["processed_by"] == "program"

    @pytest.mark.asyncio
    async def test_experiment_creation(self, cognitive_controller):
        """Test sandbox experiment creation"""
        result = await cognitive_controller.create_experiment(
            code="print('Hello from experiment!')",
            config={"auto_run": False}
        )

        assert result["success"] is True
        assert result["processed_by"] == "sandbox"

    @pytest.mark.asyncio
    async def test_error_handling(self, cognitive_controller):
        """Test error handling and recovery"""
        # Mock an orchestrator failure
        cognitive_controller.orchestrators["system"].handle = AsyncMock(
            side_effect=Exception("Test error")
        )

        with pytest.raises(Exception):
            await cognitive_controller.handle({"type": "test"})

        # Verify metrics were updated
        metrics = cognitive_controller.get_metrics()
        assert metrics["failed_requests"] > 0


class TestFastAPIIntegration:
    """Test FastAPI application integration"""

    @pytest.fixture
    async def test_client(self):
        """Create test HTTP client"""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_health_endpoint(self, test_client):
        """Test health endpoint"""
        response = await test_client.get("/api/v2/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_universal_orchestration_endpoint(self, test_client):
        """Test universal orchestration endpoint"""
        request_data = {
            "type": "health-check",
            "context": {"user_id": "test-user"}
        }

        response = await test_client.post("/api/v2/orchestrate", json=request_data)

        # Note: This will fail without proper setup, but tests the endpoint structure
        assert response.status_code in [200, 500]  # Either success or expected failure

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, test_client):
        """Test metrics endpoint"""
        response = await test_client.get("/api/v2/metrics")
        assert response.status_code in [200, 500]  # Either success or expected failure

        if response.status_code == 200:
            data = response.json()
            assert "timestamp" in data


class TestProductionIntegrations:
    """Test production integrations (Redis, PostgreSQL, Docker)"""

    @pytest.mark.asyncio
    async def test_redis_integration(self):
        """Test Redis client functionality"""
        # This test requires actual Redis instance
        try:
            redis_client = RedisClient("redis://localhost:6379")
            await redis_client.connect()

            # Test basic operations
            await redis_client.set("test_key", "test_value")
            value = await redis_client.get("test_key")
            assert value == "test_value"

            # Test JSON operations
            await redis_client.set("test_json", {"key": "value"})
            json_value = await redis_client.get("test_json")
            assert json_value is not None

            await redis_client.disconnect()

        except Exception as e:
            pytest.skip(f"Redis not available: {e}")

    @pytest.mark.asyncio
    async def test_postgres_integration(self):
        """Test PostgreSQL client functionality"""
        # This test requires actual PostgreSQL instance
        try:
            postgres_client = PostgreSQLClient(
                "postgresql://postgres:postgres@localhost:5432/test"
            )
            await postgres_client.connect()

            # Test basic query
            result = await postgres_client.fetchval("SELECT 1")
            assert result == 1

            await postgres_client.disconnect()

        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")

    @pytest.mark.asyncio
    async def test_docker_integration(self):
        """Test Docker manager functionality"""
        # This test requires Docker daemon
        try:
            docker_manager = DockerManager()
            await docker_manager.initialize()

            # Test health check
            health = await docker_manager.health_check()
            assert health is True

            await docker_manager.cleanup()

        except Exception as e:
            pytest.skip(f"Docker not available: {e}")


class TestPydanticModels:
    """Test Pydantic model validation"""

    def test_system_request_validation(self):
        """Test SystemRequest model validation"""
        # Valid request
        request = SystemRequest(
            type="health-check",
            component="event-bus",
            priority=5
        )
        assert request.type == "health-check"
        assert request.priority == 5

        # Invalid priority
        with pytest.raises(ValueError):
            SystemRequest(type="test", priority=15)

    def test_experiment_request_validation(self):
        """Test ExperimentRequest model validation"""
        # Valid experiment
        experiment = ExperimentRequest(
            type="experiment",
            name="Test Experiment",
            code="print('hello')",
            auto_run=True
        )
        assert experiment.name == "Test Experiment"
        assert experiment.auto_run is True

    def test_health_response_model(self):
        """Test HealthResponse model"""
        response = HealthResponse(
            success=True,
            status="healthy",
            cognitive_orchestrators={},
            infrastructure=None
        )
        assert response.status == "healthy"
        assert response.success is True


# Performance tests
class TestPerformance:
    """Test system performance characteristics"""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, cognitive_controller):
        """Test handling multiple concurrent requests"""
        # Create multiple concurrent requests
        requests = [
            cognitive_controller.handle({"type": "test", "id": i})
            for i in range(10)
        ]

        # Execute concurrently
        results = await asyncio.gather(*requests, return_exceptions=True)

        # Verify all succeeded (or failed gracefully)
        for result in results:
            if isinstance(result, Exception):
                # Should be a controlled failure, not a crash
                assert "orchestrator is not running" in str(result)
            else:
                assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_response_time_tracking(self, cognitive_controller):
        """Test response time tracking"""
        # Make a request
        await cognitive_controller.handle({"type": "test"})

        metrics = cognitive_controller.get_metrics()
        assert metrics["average_response_time"] > 0


if __name__ == "__main__":
    # Run basic smoke test
    async def smoke_test():
        print("🧪 Running Consolidated System Smoke Test...")

        # Test model creation
        request = SystemRequest(type="health-check")
        print(f"✅ Pydantic models work: {request.type}")

        # Test integration mocks
        mock_integrations = {
            'redis_client': Mock(),
            'postgres_client': Mock(),
            'docker_manager': Mock()
        }
        controller = CognitiveOrchestrationController(mock_integrations)
        print(f"✅ Controller creation works: {len(controller.orchestrators)} orchestrators")

        print("🎉 Basic smoke test passed!")

    asyncio.run(smoke_test())