"""
Unit Tests for Scenario Registry
"""
import pytest
from storage.registry import ScenarioRegistry


class TestScenarioRegistry:
    """Tests for ScenarioRegistry"""

    @pytest.mark.asyncio
    async def test_registry_initialization(self):
        """Test that Registry initializes correctly"""
        registry = ScenarioRegistry()
        assert registry.scenarios == {}
        assert registry.index_by_level == {}
        assert registry.index_by_type == {}
        assert registry.index_by_module == {}

    @pytest.mark.asyncio
    async def test_register_scenario(self):
        """Test scenario registration"""
        registry = ScenarioRegistry()
        scenario = {
            "meta": {
                "id": "test-scenario",
                "version": "1.0.0",
                "level": 1,
                "type": "functional",
                "module": "test"
            }
        }
        success = await registry.register(scenario)
        assert success is True
        assert "test-scenario" in registry.scenarios

    @pytest.mark.asyncio
    async def test_get_scenario_by_id(self):
        """Test getting scenario by ID"""
        registry = ScenarioRegistry()
        scenario = {
            "meta": {
                "id": "test-scenario",
                "version": "1.0.0",
                "level": 1,
                "type": "functional"
            }
        }
        await registry.register(scenario)
        retrieved = await registry.get_scenario_by_id("test-scenario")
        assert retrieved is not None
        assert retrieved["meta"]["id"] == "test-scenario"

    @pytest.mark.asyncio
    async def test_find_scenarios_by_level(self):
        """Test finding scenarios by level"""
        registry = ScenarioRegistry()
        scenario1 = {
            "meta": {"id": "s1", "version": "1.0.0", "level": 1, "type": "functional"}
        }
        scenario2 = {
            "meta": {"id": "s2", "version": "1.0.0", "level": 2, "type": "functional"}
        }
        await registry.register(scenario1)
        await registry.register(scenario2)

        level1_scenarios = await registry.find_scenarios(level=1)
        assert len(level1_scenarios) == 1
        assert level1_scenarios[0]["meta"]["id"] == "s1"

    @pytest.mark.asyncio
    async def test_find_scenarios_by_type(self):
        """Test finding scenarios by type"""
        registry = ScenarioRegistry()
        scenario1 = {
            "meta": {"id": "s1", "version": "1.0.0", "level": 1, "type": "functional"}
        }
        scenario2 = {
            "meta": {"id": "s2", "version": "1.0.0", "level": 1, "type": "chaos"}
        }
        await registry.register(scenario1)
        await registry.register(scenario2)

        functional_scenarios = await registry.find_scenarios(type="functional")
        assert len(functional_scenarios) == 1
        assert functional_scenarios[0]["meta"]["type"] == "functional"

    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """Test getting registry statistics"""
        registry = ScenarioRegistry()
        scenario1 = {
            "meta": {"id": "s1", "version": "1.0.0", "level": 1, "type": "functional"}
        }
        scenario2 = {
            "meta": {"id": "s2", "version": "1.0.0", "level": 2, "type": "chaos"}
        }
        await registry.register(scenario1)
        await registry.register(scenario2)

        stats = await registry.get_statistics()
        assert stats["total_scenarios"] == 2
        assert stats["by_level"][1] == 1
        assert stats["by_level"][2] == 1
        assert stats["by_type"]["functional"] == 1
        assert stats["by_type"]["chaos"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
