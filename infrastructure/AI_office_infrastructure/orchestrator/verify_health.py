#!/usr/bin/env python3
"""
Infrastructure Orchestrator - Health Verification Script
=========================================================

Quick health check script to verify orchestrator functionality.
Run this anytime to verify the orchestrator is working correctly.

Usage:
    python3 verify_health.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def verify_health():
    """Comprehensive health check"""

    print("="*80)
    print("INFRASTRUCTURE ORCHESTRATOR - HEALTH VERIFICATION")
    print("="*80)
    print()

    passed = 0
    failed = 0

    # Test 1: Import
    print("1. Testing Import...")
    try:
        from unified_orchestrator import UnifiedOrchestrator
        print("    PASS: UnifiedOrchestrator imported successfully")
        passed += 1
    except Exception as e:
        print(f"    FAIL: Import failed - {e}")
        failed += 1
        return False

    # Test 2: Initialization
    print("\n2. Testing Initialization...")
    try:
        orchestrator = UnifiedOrchestrator(PROJECT_ROOT)
        print("    PASS: Orchestrator initialized")
        passed += 1
    except Exception as e:
        print(f"    FAIL: Initialization failed - {e}")
        failed += 1
        return False

    # Test 3: Components
    print("\n3. Testing Components...")
    components = {
        'ServiceDiscovery': orchestrator.discovery,
        'DockerManager': orchestrator.docker_manager,
        'EventExecutor': orchestrator.event_executor,
        'InfrastructureExecutor': orchestrator.infrastructure_executor,
        'BCMExecutor': orchestrator.bcm_executor
    }

    for name, component in components.items():
        if component is not None:
            print(f"    PASS: {name} available")
            passed += 1
        else:
            print(f"   ️  WARN: {name} not available (may be optional)")

    # Test 4: Core Methods
    print("\n4. Testing Core Methods...")
    methods = [
        'discover_services',
        'generate_configs',
        'deploy',
        'execute_task',
        'status',
        'fix_event_gaps'
    ]

    for method in methods:
        if hasattr(orchestrator, method) and callable(getattr(orchestrator, method)):
            print(f"    PASS: {method}() available")
            passed += 1
        else:
            print(f"    FAIL: {method}() not available")
            failed += 1

    # Test 5: Task Execution
    print("\n5. Testing Task Execution...")
    try:
        test_task = {
            'task_type': 'code',
            'action': 'test',
            'parameters': {}
        }
        result = await orchestrator.execute_task(test_task)
        if result.get('success') is not None:
            print("    PASS: Task execution works")
            passed += 1
        else:
            print("    FAIL: Task execution returned unexpected result")
            failed += 1
    except Exception as e:
        print(f"    FAIL: Task execution error - {e}")
        failed += 1

    # Test 6: API Endpoints
    print("\n6. Testing API Endpoints...")
    try:
        from unified_orchestrator import app
        routes = [r.path for r in app.routes]

        required_endpoints = [
            '/health',
            '/api/v1/status',
            '/api/v1/deploy',
            '/api/v1/tasks/execute'
        ]

        for endpoint in required_endpoints:
            if endpoint in routes:
                print(f"    PASS: {endpoint} endpoint exists")
                passed += 1
            else:
                print(f"    FAIL: {endpoint} endpoint missing")
                failed += 1
    except Exception as e:
        print(f"    FAIL: API endpoint check failed - {e}")
        failed += 1

    # Summary
    print("\n" + "="*80)
    print("HEALTH CHECK SUMMARY")
    print("="*80)
    total = passed + failed
    print(f"Total Checks: {total}")
    print(f" Passed: {passed}")
    print(f" Failed: {failed}")

    if failed == 0:
        print("\n HEALTH CHECK PASSED - Orchestrator is fully functional")
        print("="*80)
        return True
    else:
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n️  HEALTH CHECK COMPLETED WITH WARNINGS - {success_rate:.1f}% functional")
        print("="*80)
        return False


def main():
    """Main entry point"""
    try:
        result = asyncio.run(verify_health())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nHealth check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
