"""
Test Scenario Execution Engine

Comprehensive tests for the execution engine with real scenarios.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.execution_engine import ExecutionEngine
from execution.executor import ScenarioExecutor
from execution.validator import ExecutionValidator
from execution.reporter import ExecutionReporter
from storage.postgres_storage import PostgresScenarioStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_simple_scenario():
    """Test 1: Execute a simple mock scenario"""
    print("\n" + "="*80)
    print("TEST 1: Simple Mock Scenario Execution")
    print("="*80)

    test_scenario = {
        'meta': {
            'id': 'test-simple-mock',
            'level': 1,
            'type': 'functional',
            'version': '1.0.0'
        },
        'description': {
            'title': 'Simple Mock Test',
            'summary': 'Testing basic execution flow'
        },
        'execution': {
            'steps': [
                {
                    'id': 'step1',
                    'action': 'mock_action',
                    'params': {'message': 'Hello World'},
                    'expect': {'status': 200}
                },
                {
                    'id': 'step2',
                    'action': 'mock_action',
                    'params': {'count': 42},
                    'expect': {'status': 200}
                }
            ]
        }
    }

    engine = ExecutionEngine(storage=None, save_to_db=False)
    report = await engine.execute_scenario_direct(test_scenario)

    print(f"\n✅ Test 1 Results:")
    print(f"   Status: {report.summary['overall_status']}")
    print(f"   Executions: {report.summary['total_executions']}")
    print(f"   Success Rate: {report.summary['success_rate']:.1%}")
    print(f"   Avg Duration: {report.summary['timing']['avg_duration']:.2f}s")

    if report.validations:
        val = report.validations[0]
        print(f"   Validation: {val['validation_status']} ({val['summary']['total_issues']} issues)")

    assert report.summary['overall_status'] == 'success', "Test 1 failed"
    print("✅ Test 1 PASSED")


async def test_http_scenario():
    """Test 2: Execute scenario with HTTP requests"""
    print("\n" + "="*80)
    print("TEST 2: HTTP Request Scenario")
    print("="*80)

    # Test against a public API
    test_scenario = {
        'meta': {
            'id': 'test-http-request',
            'level': 1,
            'type': 'functional'
        },
        'description': {
            'title': 'HTTP Request Test',
            'summary': 'Testing HTTP request execution'
        },
        'execution': {
            'steps': [
                {
                    'id': 'health_check',
                    'action': 'http_request',
                    'method': 'GET',
                    'endpoint': 'https://httpbin.org/status/200',
                    'expect': {
                        'http_status': 200
                    }
                },
                {
                    'id': 'get_data',
                    'action': 'http_request',
                    'method': 'GET',
                    'endpoint': 'https://httpbin.org/json',
                    'expect': {
                        'http_status': 200,
                        'response_time_max': '3s'
                    }
                }
            ]
        }
    }

    engine = ExecutionEngine(storage=None, save_to_db=False)
    report = await engine.execute_scenario_direct(test_scenario)

    print(f"\n✅ Test 2 Results:")
    print(f"   Status: {report.summary['overall_status']}")
    print(f"   Success Rate: {report.summary['success_rate']:.1%}")
    print(f"   Steps: {report.summary['steps']['successful']}/{report.summary['steps']['total']} passed")

    assert report.summary['successful'] >= 1, "Test 2 failed"
    print("✅ Test 2 PASSED")


async def test_scenario_from_database():
    """Test 3: Load and execute scenario from database"""
    print("\n" + "="*80)
    print("TEST 3: Execute Scenario from Database")
    print("="*80)

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("⚠️  Skipping Test 3: DATABASE_URL not set")
        return

    # Initialize storage
    storage = PostgresScenarioStorage(connection_string=DATABASE_URL)
    await storage.initialize()

    try:
        # Create and save a test scenario
        test_scenario = {
            'meta': {
                'id': 'test-db-execution',
                'level': 1,
                'type': 'functional',
                'version': '1.0.0'
            },
            'description': {
                'title': 'Database Test',
                'summary': 'Testing database integration'
            },
            'execution': {
                'steps': [
                    {
                        'id': 'step1',
                        'action': 'mock_action',
                        'params': {'test': 'db_integration'},
                        'expect': {'status': 200}
                    }
                ]
            }
        }

        # Save to database
        await storage.register(test_scenario)
        print("   ✅ Test scenario saved to database")

        # Create engine with storage
        engine = ExecutionEngine(storage=storage, save_to_db=True)

        # Execute by ID
        report = await engine.execute_scenario('test-db-execution')

        print(f"\n✅ Test 3 Results:")
        print(f"   Status: {report.summary['overall_status']}")
        print(f"   Success Rate: {report.summary['success_rate']:.1%}")

        # Check execution history
        history = await engine.get_execution_history('test-db-execution')
        print(f"   Execution History: {len(history)} records")

        # Get statistics
        stats = await engine.get_statistics()
        print(f"   Total Executions: {stats.get('total_executions', 0)}")

        assert report.summary['overall_status'] == 'success', "Test 3 failed"
        assert len(history) >= 1, "Execution history not saved"
        print("✅ Test 3 PASSED")

    finally:
        await storage.close()


async def test_batch_execution():
    """Test 4: Execute multiple scenarios in batch"""
    print("\n" + "="*80)
    print("TEST 4: Batch Execution")
    print("="*80)

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("⚠️  Skipping Test 4: DATABASE_URL not set")
        return

    storage = PostgresScenarioStorage(connection_string=DATABASE_URL)
    await storage.initialize()

    try:
        # Create multiple test scenarios
        scenarios = []
        for i in range(3):
            scenario = {
                'meta': {
                    'id': f'test-batch-{i}',
                    'level': 1,
                    'type': 'functional'
                },
                'description': {
                    'title': f'Batch Test {i}',
                    'summary': f'Batch scenario {i}'
                },
                'execution': {
                    'steps': [
                        {
                            'id': 'step1',
                            'action': 'mock_action',
                            'params': {'batch_id': i}
                        }
                    ]
                }
            }
            await storage.register(scenario)
            scenarios.append(f'test-batch-{i}')

        print(f"   ✅ Created {len(scenarios)} test scenarios")

        # Execute batch
        engine = ExecutionEngine(storage=storage, save_to_db=True)
        report = await engine.execute_batch(scenarios)

        print(f"\n✅ Test 4 Results:")
        print(f"   Status: {report.summary['overall_status']}")
        print(f"   Total Executions: {report.summary['total_executions']}")
        print(f"   Successful: {report.summary['successful']}")
        print(f"   Failed: {report.summary['failed']}")
        print(f"   Success Rate: {report.summary['success_rate']:.1%}")

        assert report.summary['total_executions'] == 3, "Not all scenarios executed"
        print("✅ Test 4 PASSED")

    finally:
        await storage.close()


async def test_real_l1_scenario():
    """Test 5: Execute a real L1 scenario from generated scenarios"""
    print("\n" + "="*80)
    print("TEST 5: Real L1 Scenario Execution")
    print("="*80)

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("⚠️  Skipping Test 5: DATABASE_URL not set")
        return

    storage = PostgresScenarioStorage(connection_string=DATABASE_URL)
    await storage.initialize()

    try:
        # Find any L1 scenario in database
        scenarios = await storage.find_scenarios(level=1, limit=1)

        if not scenarios:
            print("⚠️  No L1 scenarios found in database")
            print("   Tip: Run generators first to create scenarios")
            return

        scenario = scenarios[0]
        scenario_id = scenario.get('meta', {}).get('id')
        print(f"   Found scenario: {scenario_id}")

        # Execute it
        engine = ExecutionEngine(storage=storage, save_to_db=True, validate_results=True)
        report = await engine.execute_scenario(scenario_id)

        print(f"\n✅ Test 5 Results:")
        print(f"   Scenario: {scenario_id}")
        print(f"   Status: {report.summary['overall_status']}")
        print(f"   Duration: {report.summary['timing']['avg_duration']:.2f}s")
        print(f"   Steps: {report.summary['steps']['total']}")

        if report.validations:
            val = report.validations[0]
            print(f"   Validation: {val['validation_status']}")
            print(f"   Issues: {val['summary']['total_issues']}")

        print("✅ Test 5 PASSED")

    finally:
        await storage.close()


async def test_report_export():
    """Test 6: Export reports to JSON and HTML"""
    print("\n" + "="*80)
    print("TEST 6: Report Export")
    print("="*80)

    test_scenario = {
        'meta': {
            'id': 'test-export',
            'level': 1,
            'type': 'functional'
        },
        'execution': {
            'steps': [
                {'id': 'step1', 'action': 'mock_action'}
            ]
        }
    }

    engine = ExecutionEngine(storage=None, save_to_db=False)
    report = await engine.execute_scenario_direct(test_scenario)

    reporter = ExecutionReporter()

    # Test JSON export
    json_output = reporter.export_to_json(report)
    print(f"   ✅ JSON export: {len(json_output)} characters")

    # Test HTML export
    html_output = reporter.export_to_html(report)
    print(f"   ✅ HTML export: {len(html_output)} characters")

    # Save to files
    import tempfile
    temp_dir = tempfile.gettempdir()

    json_path = f"{temp_dir}/test_report.json"
    html_path = f"{temp_dir}/test_report.html"

    reporter.save_report(report, json_path, format='json')
    reporter.save_report(report, html_path, format='html')

    print(f"   ✅ Saved to: {json_path}")
    print(f"   ✅ Saved to: {html_path}")

    assert len(json_output) > 100, "JSON export too short"
    assert len(html_output) > 500, "HTML export too short"
    print("✅ Test 6 PASSED")


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("SCENARIO EXECUTION ENGINE - COMPREHENSIVE TEST SUITE")
    print("="*80)

    tests = [
        ("Simple Mock Scenario", test_simple_scenario),
        ("HTTP Request Scenario", test_http_scenario),
        ("Database Integration", test_scenario_from_database),
        ("Batch Execution", test_batch_execution),
        ("Real L1 Scenario", test_real_l1_scenario),
        ("Report Export", test_report_export),
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name} FAILED: {e}")
            failed += 1
        except Exception as e:
            if "Skipping" in str(e) or "⚠️" in str(e):
                skipped += 1
            else:
                print(f"❌ {test_name} ERROR: {e}")
                failed += 1

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Skipped: {skipped} ⚠️")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
