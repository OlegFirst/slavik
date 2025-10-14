"""
Unit tests for Scenario Intelligence Monitoring

Tests:
- Prometheus metrics
- Context managers
- MIO Manager integration
"""

import pytest
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "intelligent-core/scenario-intelligence"))


def test_metrics_import():
    """Test that metrics can be imported"""
    from monitoring import (
        GenerationMetricsContext,
        ExecutionMetricsContext,
        record_scenario_generated,
        record_scenario_executed
    )
    assert GenerationMetricsContext is not None
    assert ExecutionMetricsContext is not None


def test_generation_metrics_context():
    """Test generation metrics context manager"""
    from monitoring import GenerationMetricsContext

    with GenerationMetricsContext(level='l1', generator='test'):
        pass  # Should not raise


def test_execution_metrics_context():
    """Test execution metrics context manager"""
    from monitoring import ExecutionMetricsContext

    with ExecutionMetricsContext(level='l1'):
        pass  # Should not raise


def test_record_functions():
    """Test metric recording functions"""
    from monitoring import (
        record_scenario_generated,
        record_scenario_executed
    )

    # Should not raise
    record_scenario_generated('l1', 'test', 'manual', count=1)
    record_scenario_executed('l1', 'success', 1.0, 5, 0)


def test_mio_manager_client():
    """Test MIO Manager client"""
    from monitoring.mio_integration import MIOManagerClient

    client = MIOManagerClient(enabled=False)  # Disabled for test
    assert client is not None
    assert not client.enabled


@pytest.mark.asyncio
async def test_mio_manager_operations():
    """Test MIO Manager async operations"""
    from monitoring.mio_integration import MIOManagerClient

    client = MIOManagerClient(enabled=False)

    # Should not raise even though disabled
    await client.report_scenarios_generated('l1', 10, 'test')
    await client.report_scenarios_executed('l1', 5, 100.0)
    await client.alert_generation_failure('l4', 'test error')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
