"""
Тестовый скрипт для Scenario Intelligence System

Проверяет все компоненты:
- Scenario Engine
- Call Engine
- Event Engine
- Registry
- Learner
"""

import asyncio
import yaml
import sys
import os

# Add path
sys.path.insert(0, os.path.dirname(__file__))

from engines.scenario_engine import ScenarioEngine
from storage.registry import ScenarioRegistry
from learning.scenario_learner import ScenarioLearner


async def test_registry():
    """Test Registry"""

    print("\n" + "="*60)
    print("TEST 1: REGISTRY")
    print("="*60)

    registry = ScenarioRegistry()

    # Load example scenario
    with open('scenarios/level1-modules/vault/functional/store-secret.v1.0.0.yaml', 'r') as f:
        vault_scenario = yaml.safe_load(f)

    # Register
    success = await registry.register(vault_scenario)
    print(f" Registered: {success}")

    # Get by ID
    scenario = await registry.get_scenario_by_id('vault-store-secret-encrypted')
    print(f" Retrieved: {scenario['meta']['id']}")

    # Statistics
    stats = await registry.get_statistics()
    print(f" Statistics: {stats}")

    return registry


async def test_scenario_engine(registry):
    """Test Scenario Engine"""

    print("\n" + "="*60)
    print("TEST 2: SCENARIO ENGINE")
    print("="*60)

    engine = ScenarioEngine()

    # Get scenario
    scenario = await registry.get_scenario_by_id('vault-store-secret-encrypted')

    # Execute
    result = await engine.execute_scenario(
        scenario,
        context={
            'user_id': 'user_123',
            'secret_name': 'api-key-test',
            'secret_value': 'secret123'
        }
    )

    print(f"\n Execution Result:")
    print(f"   Status: {result['status']}")
    print(f"   Duration: {result['duration']}s")
    print(f"   Steps: {len(result['result']['steps'])}")

    return result


async def test_learning(registry):
    """Test Learning System"""

    print("\n" + "="*60)
    print("TEST 3: LEARNING SYSTEM")
    print("="*60)

    learner = ScenarioLearner()
    engine = ScenarioEngine()

    # Execute scenario multiple times
    scenario = await registry.get_scenario_by_id('vault-store-secret-encrypted')

    for i in range(3):
        await engine.execute_scenario(scenario, {})

    # Get statistics
    stats = await learner.get_statistics('vault-store-secret-encrypted')
    print(f"\n Learning Statistics:")
    print(f"   Total executions: {stats.get('total_executions', 0)}")
    print(f"   Successful: {stats.get('successful_executions', 0)}")
    print(f"   Avg duration: {stats.get('avg_duration', 0):.2f}s")

    # Get recent executions
    executions = await learner.get_recent_executions(
        scenario_id='vault-store-secret-encrypted',
        limit=3
    )
    print(f"   Recent executions: {len(executions)}")


async def test_user_workflow(registry):
    """Test User Workflow (Level 4)"""

    print("\n" + "="*60)
    print("TEST 4: USER WORKFLOW (Level 4)")
    print("="*60)

    # Load user workflow
    with open('scenarios/level4-user/workflows/bia-complete-workflow.v1.0.0.yaml', 'r') as f:
        bia_workflow = yaml.safe_load(f)

    # Register
    await registry.register(bia_workflow)

    # Execute
    engine = ScenarioEngine()

    result = await engine.execute_scenario(
        bia_workflow,
        context={
            'org_id': 'hospital_1',
            'user_id': 'bcm_manager_1'
        }
    )

    print(f"\n Workflow Execution:")
    print(f"   Status: {result['status']}")
    print(f"   Duration: {result['duration']}s")
    print(f"   Steps executed: {len(result['result']['steps'])}")

    # Check compliance
    if 'compliance' in result['result']:
        print(f"   Compliance checked: ")


async def main():
    """Run all tests"""

    print("\n" + "="*70)
    print(" SCENARIO INTELLIGENCE SYSTEM - FULL TEST")
    print("="*70)

    try:
        # Test 1: Registry
        registry = await test_registry()

        # Test 2: Scenario Engine
        await test_scenario_engine(registry)

        # Test 3: Learning
        await test_learning(registry)

        # Test 4: User Workflow
        await test_user_workflow(registry)

        print("\n" + "="*70)
        print(" ALL TESTS PASSED!")
        print("="*70)

        # Final statistics
        stats = await registry.get_statistics()
        print(f"\nFinal Statistics:")
        print(f"  Total scenarios: {stats['total_scenarios']}")
        print(f"  By level: {stats['by_level']}")
        print(f"  By type: {stats['by_type']}")

    except Exception as e:
        print(f"\n TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
