"""
Unit Tests for Scenario Learner
"""
import pytest
from learning.scenario_learner import ScenarioLearner


class TestScenarioLearner:
    """Tests for ScenarioLearner"""

    @pytest.mark.asyncio
    async def test_learner_initialization(self):
        """Test that Learner initializes correctly"""
        learner = ScenarioLearner()
        assert learner.executions == []
        assert learner.statistics == {}

    @pytest.mark.asyncio
    async def test_record_execution(self):
        """Test recording an execution"""
        learner = ScenarioLearner()
        scenario = {"meta": {"id": "test-scenario"}}
        result = {"status": "success", "duration": 100}
        context = {}

        await learner.record_execution("test-scenario", scenario, result, context)
        assert len(learner.executions) == 1
        assert "test-scenario" in learner.statistics

    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """Test getting statistics for a scenario"""
        learner = ScenarioLearner()
        scenario = {"meta": {"id": "test-scenario"}}

        # Record successful execution
        result1 = {"status": "success", "duration": 100}
        await learner.record_execution("test-scenario", scenario, result1, {})

        # Record failed execution
        result2 = {"status": "failed", "duration": 50}
        await learner.record_execution("test-scenario", scenario, result2, {})

        stats = await learner.get_statistics("test-scenario")
        assert stats is not None
        assert stats["total_executions"] == 2
        assert stats["successful_executions"] == 1
        assert stats["failed_executions"] == 1
        # Check avg_duration instead of success_rate
        assert stats["avg_duration"] == 75.0  # (100 + 50) / 2

    @pytest.mark.asyncio
    async def test_get_all_statistics(self):
        """Test getting statistics for all scenarios"""
        learner = ScenarioLearner()
        scenario1 = {"meta": {"id": "s1"}}
        scenario2 = {"meta": {"id": "s2"}}

        await learner.record_execution("s1", scenario1, {"status": "success", "duration": 100}, {})
        await learner.record_execution("s2", scenario2, {"status": "success", "duration": 200}, {})

        all_stats = await learner.get_all_statistics()
        assert "s1" in all_stats
        assert "s2" in all_stats
        assert all_stats["s1"]["total_executions"] == 1
        assert all_stats["s2"]["total_executions"] == 1

    @pytest.mark.asyncio
    async def test_get_recent_executions(self):
        """Test getting execution history"""
        learner = ScenarioLearner()
        scenario = {"meta": {"id": "test-scenario"}}

        await learner.record_execution("test-scenario", scenario, {"status": "success", "duration": 100}, {})
        await learner.record_execution("test-scenario", scenario, {"status": "success", "duration": 150}, {})

        # Use get_recent_executions instead of get_executions
        executions = await learner.get_recent_executions("test-scenario")
        assert len(executions) == 2
        assert executions[0]["scenario_id"] == "test-scenario"
        assert executions[1]["scenario_id"] == "test-scenario"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
