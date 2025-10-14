"""
End-to-End tests for BCM workflows

Tests complete BCM cycle workflows including:
- Full BCM cycle (Analyze → Plan → Do → Check → Act)
- BIA workflow with resource monitoring
- Strategy selection and validation
- Recovery plan generation
- Exercise execution
- Continuous improvement
"""

import pytest
import asyncio
import httpx
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Test configuration
BCM_SERVICE_URL = "http://localhost:8050"
API_TIMEOUT = 30.0


@pytest.mark.e2e
class TestBCMFullCycle:
    """Test complete BCM cycle workflow"""

    @pytest.mark.asyncio
    async def test_full_bcm_cycle_workflow(self):
        """
        Test complete BCM cycle: Analyze → Plan → Do → Check → Act

        This is the primary E2E test for System BCM Service.
        """
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Step 1: Check service health
            response = await client.get(f"{BCM_SERVICE_URL}/health")
            assert response.status_code == 200
            health = response.json()
            assert health['status'] == 'healthy'

            # Step 2: Start BCM cycle
            cycle_request = {
                "trigger": "scheduled",
                "config": {
                    "enable_resource_monitoring": True,
                    "bia_depth": "full"
                }
            }

            response = await client.post(
                f"{BCM_SERVICE_URL}/bcm/cycle/start",
                json=cycle_request
            )
            assert response.status_code == 200
            cycle_data = response.json()
            cycle_id = cycle_data.get('cycle_id')
            assert cycle_id is not None

            # Step 3: Monitor cycle progress
            max_polls = 60  # 60 seconds max
            poll_interval = 1.0

            for _ in range(max_polls):
                response = await client.get(f"{BCM_SERVICE_URL}/bcm/cycle/{cycle_id}/status")
                assert response.status_code == 200
                status = response.json()

                current_phase = status.get('current_phase')
                state = status.get('state')

                if state == 'completed':
                    break
                elif state == 'failed':
                    pytest.fail(f"BCM cycle failed: {status.get('error')}")

                await asyncio.sleep(poll_interval)

            # Step 4: Verify cycle completion
            response = await client.get(f"{BCM_SERVICE_URL}/bcm/cycle/{cycle_id}/status")
            assert response.status_code == 200
            final_status = response.json()

            assert final_status['state'] == 'completed'
            assert 'phases_completed' in final_status
            assert 'analyze' in final_status['phases_completed']
            assert 'plan' in final_status['phases_completed']

            # Step 5: Get cycle results
            response = await client.get(f"{BCM_SERVICE_URL}/bcm/cycle/{cycle_id}/results")
            assert response.status_code == 200
            results = response.json()

            # Validate results structure
            assert 'bia_results' in results or 'summary' in results
            assert 'timestamp' in results

    @pytest.mark.asyncio
    async def test_bcm_cycle_with_resource_monitoring(self):
        """Test BCM cycle includes resource monitoring"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Start cycle with resource monitoring enabled
            cycle_request = {
                "trigger": "scheduled",
                "config": {
                    "enable_resource_monitoring": True
                }
            }

            response = await client.post(
                f"{BCM_SERVICE_URL}/bcm/cycle/start",
                json=cycle_request
            )
            assert response.status_code == 200
            cycle_data = response.json()
            cycle_id = cycle_data.get('cycle_id')

            # Wait a bit for monitoring to collect data
            await asyncio.sleep(2.0)

            # Check resource status
            response = await client.get(f"{BCM_SERVICE_URL}/resources/status")
            assert response.status_code == 200
            resource_status = response.json()

            # Validate resource monitoring data
            assert 'available' in resource_status
            assert 'state' in resource_status
            assert 'stats' in resource_status
            assert resource_status['state'] in ['deficit', 'normal', 'surplus']


@pytest.mark.e2e
class TestBIAWorkflow:
    """Test Business Impact Analysis workflow"""

    @pytest.mark.asyncio
    async def test_bia_workflow_complete(self):
        """Test complete BIA workflow"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Step 1: Initiate BIA
            bia_request = {
                "scope": "platform",
                "include_resource_analysis": True
            }

            response = await client.post(
                f"{BCM_SERVICE_URL}/bcm/bia/start",
                json=bia_request
            )
            assert response.status_code in [200, 201]
            bia_data = response.json()
            bia_id = bia_data.get('bia_id') or bia_data.get('id')

            # Step 2: Wait for BIA completion
            max_polls = 30
            for _ in range(max_polls):
                response = await client.get(f"{BCM_SERVICE_URL}/bcm/bia/{bia_id}/status")
                if response.status_code == 200:
                    status = response.json()
                    if status.get('state') == 'completed':
                        break
                await asyncio.sleep(1.0)

            # Step 3: Get BIA results
            response = await client.get(f"{BCM_SERVICE_URL}/bcm/bia/{bia_id}/results")
            assert response.status_code == 200
            results = response.json()

            # Validate BIA results structure
            assert 'critical_functions' in results or 'summary' in results

    @pytest.mark.asyncio
    async def test_bia_with_resource_constraints(self):
        """Test BIA considers resource constraints"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Get current resource status
            response = await client.get(f"{BCM_SERVICE_URL}/resources/status")
            assert response.status_code == 200
            resource_status = response.json()

            # Initiate BIA
            bia_request = {
                "scope": "platform",
                "include_resource_analysis": True,
                "resource_constraints": {
                    "max_cpu_percent": 80.0,
                    "max_memory_mb": 4096.0
                }
            }

            response = await client.post(
                f"{BCM_SERVICE_URL}/bcm/bia/start",
                json=bia_request
            )
            assert response.status_code in [200, 201]

            # Verify resource monitoring during BIA
            await asyncio.sleep(2.0)
            response = await client.get(f"{BCM_SERVICE_URL}/resources/status")
            assert response.status_code == 200
            updated_status = response.json()

            # Should have collected more snapshots
            assert updated_status['stats']['total_snapshots'] >= resource_status['stats']['total_snapshots']


@pytest.mark.e2e
class TestStrategyWorkflow:
    """Test BCM strategy selection and validation"""

    @pytest.mark.asyncio
    async def test_strategy_selection_workflow(self):
        """Test strategy selection based on BIA results"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Step 1: Get available strategies
            response = await client.get(f"{BCM_SERVICE_URL}/bcm/strategies")
            assert response.status_code == 200
            strategies = response.json()

            assert 'strategies' in strategies or isinstance(strategies, list)

            # Step 2: Select strategy
            if isinstance(strategies, dict) and 'strategies' in strategies:
                strategy_list = strategies['strategies']
            else:
                strategy_list = strategies

            if len(strategy_list) > 0:
                selected_strategy = strategy_list[0]
                strategy_id = selected_strategy.get('id') or selected_strategy.get('name')

                # Validate strategy
                response = await client.post(
                    f"{BCM_SERVICE_URL}/bcm/strategy/validate",
                    json={"strategy_id": strategy_id}
                )
                assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_strategy_with_resource_awareness(self):
        """Test strategy selection considers resource availability"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Get resource status
            response = await client.get(f"{BCM_SERVICE_URL}/resources/status")
            assert response.status_code == 200
            resource_status = response.json()

            # Request resource-aware strategy
            strategy_request = {
                "criteria": "resource_optimized",
                "available_resources": resource_status['available']
            }

            response = await client.post(
                f"{BCM_SERVICE_URL}/bcm/strategy/recommend",
                json=strategy_request
            )
            assert response.status_code in [200, 201]
            recommendation = response.json()

            # Should provide strategy recommendation
            assert 'recommended_strategy' in recommendation or 'strategy' in recommendation


@pytest.mark.e2e
class TestRecoveryWorkflow:
    """Test recovery plan and execution workflow"""

    @pytest.mark.asyncio
    async def test_recovery_plan_generation(self):
        """Test recovery plan generation"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Generate recovery plan
            plan_request = {
                "scenario": "service_outage",
                "critical_functions": ["database", "api_gateway"]
            }

            response = await client.post(
                f"{BCM_SERVICE_URL}/bcm/recovery/plan",
                json=plan_request
            )
            assert response.status_code in [200, 201]
            plan = response.json()

            # Validate plan structure
            assert 'steps' in plan or 'plan_id' in plan

    @pytest.mark.asyncio
    async def test_recovery_exercise_execution(self):
        """Test recovery exercise execution"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Start recovery exercise
            exercise_request = {
                "type": "tabletop",
                "scenario": "database_failure"
            }

            response = await client.post(
                f"{BCM_SERVICE_URL}/bcm/exercise/start",
                json=exercise_request
            )
            assert response.status_code in [200, 201]
            exercise = response.json()

            exercise_id = exercise.get('exercise_id') or exercise.get('id')

            if exercise_id:
                # Monitor exercise
                await asyncio.sleep(2.0)

                response = await client.get(
                    f"{BCM_SERVICE_URL}/bcm/exercise/{exercise_id}/status"
                )
                assert response.status_code == 200


@pytest.mark.e2e
class TestContinuousImprovementWorkflow:
    """Test continuous improvement workflow (Act phase)"""

    @pytest.mark.asyncio
    async def test_lessons_learned_capture(self):
        """Test capturing lessons learned"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Submit lesson learned
            lesson = {
                "category": "resource_management",
                "description": "Resource monitoring improved incident detection",
                "impact": "positive",
                "recommendation": "Continue resource tracking in all BCM phases"
            }

            response = await client.post(
                f"{BCM_SERVICE_URL}/bcm/lessons",
                json=lesson
            )
            assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_improvement_actions_workflow(self):
        """Test improvement actions tracking"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Create improvement action
            action = {
                "title": "Enhance resource monitoring",
                "priority": "high",
                "owner": "platform_team"
            }

            response = await client.post(
                f"{BCM_SERVICE_URL}/bcm/improvements",
                json=action
            )
            assert response.status_code in [200, 201]

            # Get all improvements
            response = await client.get(f"{BCM_SERVICE_URL}/bcm/improvements")
            assert response.status_code == 200


@pytest.mark.e2e
class TestResourceMonitoringIntegration:
    """Test resource monitoring integration across BCM workflows"""

    @pytest.mark.asyncio
    async def test_resource_status_endpoint(self):
        """Test /resources/status endpoint availability"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            response = await client.get(f"{BCM_SERVICE_URL}/resources/status")
            assert response.status_code == 200

            resource_status = response.json()

            # Validate response structure
            assert 'available' in resource_status
            assert 'state' in resource_status
            assert 'stats' in resource_status

            # Validate available resources
            available = resource_status['available']
            assert 'cpu_percent' in available
            assert 'memory_mb' in available
            assert available['cpu_percent'] >= 0
            assert available['memory_mb'] >= 0

            # Validate state
            assert resource_status['state'] in ['deficit', 'normal', 'surplus']

            # Validate stats
            stats = resource_status['stats']
            assert 'total_snapshots' in stats
            assert 'resource_state' in stats

    @pytest.mark.asyncio
    async def test_resource_predictions(self):
        """Test resource deficit predictions"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            response = await client.get(f"{BCM_SERVICE_URL}/resources/status")
            assert response.status_code == 200

            resource_status = response.json()

            # Should include predictions
            if 'predictions' in resource_status:
                predictions = resource_status['predictions']

                # cpu_deficit_seconds can be None or float
                if predictions.get('cpu_deficit_seconds') is not None:
                    assert predictions['cpu_deficit_seconds'] >= 0

                # memory_deficit_seconds can be None or float
                if predictions.get('memory_deficit_seconds') is not None:
                    assert predictions['memory_deficit_seconds'] >= 0

    @pytest.mark.asyncio
    async def test_resource_trends(self):
        """Test resource trend analysis"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Wait for some monitoring data
            await asyncio.sleep(2.0)

            response = await client.get(f"{BCM_SERVICE_URL}/resources/status")
            assert response.status_code == 200

            resource_status = response.json()

            # Should include trends
            if 'trends' in resource_status:
                trends = resource_status['trends']

                # Trends should be between -1.0 and 1.0
                if 'cpu_trend' in trends:
                    assert -1.0 <= trends['cpu_trend'] <= 1.0

                if 'memory_trend' in trends:
                    assert -1.0 <= trends['memory_trend'] <= 1.0


@pytest.mark.e2e
class TestPrometheusMetricsIntegration:
    """Test Prometheus metrics exposure"""

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self):
        """Test /metrics endpoint for Prometheus"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            response = await client.get(f"{BCM_SERVICE_URL}/metrics")
            assert response.status_code == 200

            metrics_text = response.text

            # Validate Prometheus format
            assert 'system_bcm_' in metrics_text or '# HELP' in metrics_text

    @pytest.mark.asyncio
    async def test_resource_metrics_exposed(self):
        """Test resource-specific metrics are exposed"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            response = await client.get(f"{BCM_SERVICE_URL}/metrics")
            assert response.status_code == 200

            metrics_text = response.text

            # Check for expected metrics
            expected_metrics = [
                'system_bcm_resource_snapshots_total',
                'system_bcm_resource_deficit_events',
                'system_bcm_resource_surplus_events',
                'system_bcm_resource_state',
                'system_bcm_cpu_available_percent',
                'system_bcm_memory_available_mb'
            ]

            # At least some metrics should be present
            metrics_found = sum(1 for metric in expected_metrics if metric in metrics_text)
            assert metrics_found >= 3  # At least 3 metrics should be exposed


@pytest.mark.e2e
@pytest.mark.slow
class TestBCMStressScenarios:
    """Test BCM under stress/load conditions"""

    @pytest.mark.asyncio
    async def test_concurrent_bcm_cycles(self):
        """Test multiple concurrent BCM cycles"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Start multiple cycles concurrently
            cycle_requests = [
                {"trigger": f"test_{i}", "config": {"enable_resource_monitoring": True}}
                for i in range(3)
            ]

            tasks = [
                client.post(f"{BCM_SERVICE_URL}/bcm/cycle/start", json=req)
                for req in cycle_requests
            ]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # At least one should succeed
            successful = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
            assert len(successful) >= 1

    @pytest.mark.asyncio
    async def test_resource_monitoring_under_load(self):
        """Test resource monitoring remains functional under load"""
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:

            # Generate load
            tasks = [
                client.get(f"{BCM_SERVICE_URL}/resources/status")
                for _ in range(10)
            ]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # All should succeed
            successful = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
            assert len(successful) >= 8  # At least 80% success rate


# Fixtures

@pytest.fixture(scope="session")
async def bcm_service():
    """Ensure BCM service is running"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{BCM_SERVICE_URL}/health")
            if response.status_code == 200:
                return True
        except Exception:
            pytest.skip("BCM service not running")
    return False


@pytest.fixture(autouse=True)
async def wait_for_service(bcm_service):
    """Wait for service to be ready before each test"""
    await asyncio.sleep(0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
