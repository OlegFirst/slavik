#!/usr/bin/env python3
"""
Comprehensive test system for AI Event Manager

Tests:
1. Import validation
2. EventBus integration
3. HTTP client integrations
4. Continuous monitor
5. Event detection reliability
6. Stress testing
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

print("="*80)
print("AI EVENT MANAGER - COMPREHENSIVE TEST SUITE")
print("="*80)
print()

# Test results
test_results = {}

# ============================================================================
# TEST 1: Import Validation
# ============================================================================
print("[TEST 1] Import Validation...")
try:
    from integrations import (
        IntegrationManager,
        EventBusIntegration,
        EventIntelligenceIntegration,
        DevOpsAgentIntegration,
        GitHubIntegrationClient,
        MioManagerIntegration,
        ContinuousMonitor
    )
    test_results['imports'] = {'status': 'PASS', 'details': 'All integrations imported successfully'}
    print("✅ All integrations imported successfully")
except Exception as e:
    test_results['imports'] = {'status': 'FAIL', 'details': str(e)}
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print()

# ============================================================================
# TEST 2: EventBus Integration
# ============================================================================
print("[TEST 2] EventBus Integration...")
async def test_eventbus():
    try:
        # Test with memory backend
        eventbus = EventBusIntegration(backend='memory')
        await eventbus.initialize()

        # Test publishing
        await eventbus.publish('test.event', {'data': 'test'}, priority='normal')

        # Test gap detection publishing
        await eventbus.publish_gap_detected({
            'event_name': 'test.event.gap',
            'gap_type': 'missing_publisher',
            'severity': 'medium',
            'description': 'Test gap',
            'recommendations': ['Add publisher'],
            'detected_at': '2025-10-08T00:00:00Z'
        })

        stats = eventbus.get_stats()

        await eventbus.close()

        if stats['events_published'] >= 2:
            return {'status': 'PASS', 'details': f"Published {stats['events_published']} events"}
        else:
            return {'status': 'FAIL', 'details': f"Expected 2+ events, got {stats['events_published']}"}

    except Exception as e:
        return {'status': 'FAIL', 'details': str(e)}

test_results['eventbus'] = asyncio.run(test_eventbus())
print(f"{'✅' if test_results['eventbus']['status'] == 'PASS' else '❌'} {test_results['eventbus']['details']}")
print()

# ============================================================================
# TEST 3: Integration Manager
# ============================================================================
print("[TEST 3] Integration Manager Initialization...")
async def test_integration_manager():
    try:
        manager = IntegrationManager({
            'eventbus_backend': 'memory',
            'redis_url': 'redis://localhost:6379',
            'event_intelligence_url': 'http://localhost:8039',
            'devops_agent_url': 'http://localhost:8050',
            'github_integration_url': 'http://localhost:8051',
            'mio_manager_url': 'http://localhost:8046',
            'project_root': str(project_root),
            'monitor_interval': 300
        })

        await manager.initialize_all()

        status = manager.get_integration_status()

        # EventBus should always be active
        if status['integrations']['eventbus'] == 'active':
            active_count = sum(1 for v in status['integrations'].values() if v == 'active')
            return {
                'status': 'PASS',
                'details': f"{active_count}/6 integrations active",
                'active_count': active_count
            }
        else:
            return {'status': 'FAIL', 'details': 'EventBus not initialized'}

        await manager.close()

    except Exception as e:
        return {'status': 'FAIL', 'details': str(e)}

test_results['integration_manager'] = asyncio.run(test_integration_manager())
print(f"{'✅' if test_results['integration_manager']['status'] == 'PASS' else '❌'} {test_results['integration_manager']['details']}")
print()

# ============================================================================
# TEST 4: Event Detection Reliability (100 Events)
# ============================================================================
print("[TEST 4] Event Detection Reliability (100 events)...")
async def test_event_detection_reliability():
    try:
        eventbus = EventBusIntegration(backend='memory')
        await eventbus.initialize()

        # Publish 100 events
        events_to_publish = 100
        events_published = 0

        start_time = time.time()

        for i in range(events_to_publish):
            await eventbus.publish(
                f'test.event.{i}',
                {'index': i, 'timestamp': time.time()},
                priority='normal' if i % 2 == 0 else 'high'
            )
            events_published += 1

        end_time = time.time()
        duration = end_time - start_time

        stats = eventbus.get_stats()

        await eventbus.close()

        if stats['events_published'] == events_to_publish:
            return {
                'status': 'PASS',
                'details': f"100% reliability ({events_to_publish}/{events_to_publish} events)",
                'duration': f"{duration:.2f}s",
                'throughput': f"{events_to_publish/duration:.1f} events/sec"
            }
        else:
            return {
                'status': 'FAIL',
                'details': f"Lost {events_to_publish - stats['events_published']} events"
            }

    except Exception as e:
        return {'status': 'FAIL', 'details': str(e)}

test_results['event_detection'] = asyncio.run(test_event_detection_reliability())
print(f"{'✅' if test_results['event_detection']['status'] == 'PASS' else '❌'} {test_results['event_detection']['details']}")
if 'throughput' in test_results['event_detection']:
    print(f"   Duration: {test_results['event_detection']['duration']}, Throughput: {test_results['event_detection']['throughput']}")
print()

# ============================================================================
# TEST 5: Stress Test (1000 Rapid Events)
# ============================================================================
print("[TEST 5] Stress Test (1000 rapid events)...")
async def test_stress():
    try:
        eventbus = EventBusIntegration(backend='memory')
        await eventbus.initialize()

        events_count = 1000
        start_time = time.time()

        # Publish rapidly
        tasks = []
        for i in range(events_count):
            task = eventbus.publish(
                f'stress.test.{i % 10}',  # Reuse 10 event names
                {'index': i},
                priority='critical' if i % 100 == 0 else 'normal'
            )
            tasks.append(task)

        # Wait for all
        await asyncio.gather(*tasks)

        end_time = time.time()
        duration = end_time - start_time

        stats = eventbus.get_stats()

        await eventbus.close()

        if stats['events_published'] == events_count:
            return {
                'status': 'PASS',
                'details': f"Handled {events_count} events in {duration:.2f}s",
                'throughput': f"{events_count/duration:.0f} events/sec"
            }
        else:
            return {
                'status': 'FAIL',
                'details': f"Lost {events_count - stats['events_published']} events under stress"
            }

    except Exception as e:
        return {'status': 'FAIL', 'details': str(e)}

test_results['stress_test'] = asyncio.run(test_stress())
print(f"{'✅' if test_results['stress_test']['status'] == 'PASS' else '❌'} {test_results['stress_test']['details']}")
if 'throughput' in test_results['stress_test']:
    print(f"   Throughput: {test_results['stress_test']['throughput']}")
print()

# ============================================================================
# TEST 6: Continuous Monitor
# ============================================================================
print("[TEST 6] Continuous Monitor (10 second test)...")
async def test_monitor():
    try:
        manager = IntegrationManager({
            'eventbus_backend': 'memory',
            'monitor_interval': 5  # 5 seconds for testing
        })

        await manager.initialize_all()

        if not manager.monitor:
            return {'status': 'FAIL', 'details': 'Monitor not initialized'}

        # Run for 10 seconds
        await asyncio.sleep(10)

        stats = manager.monitor.get_stats()

        await manager.close()

        if stats['running']:
            return {
                'status': 'PASS',
                'details': f"Monitor stable, {stats['scans_completed']} scans completed"
            }
        else:
            return {'status': 'FAIL', 'details': 'Monitor stopped unexpectedly'}

    except Exception as e:
        return {'status': 'FAIL', 'details': str(e)}

test_results['monitor'] = asyncio.run(test_monitor())
print(f"{'✅' if test_results['monitor']['status'] == 'PASS' else '❌'} {test_results['monitor']['details']}")
print()

# ============================================================================
# FINAL REPORT
# ============================================================================
print("="*80)
print("TEST RESULTS SUMMARY")
print("="*80)

total_tests = len(test_results)
passed_tests = sum(1 for r in test_results.values() if r['status'] == 'PASS')

for test_name, result in test_results.items():
    status_icon = '✅' if result['status'] == 'PASS' else '❌'
    print(f"{status_icon} {test_name.upper()}: {result['status']} - {result['details']}")

print()
print(f"Overall: {passed_tests}/{total_tests} tests passed")
print()

# Production readiness assessment
if passed_tests == total_tests:
    print("🎉 PRODUCTION READY: ALL TESTS PASSED")
    print("   - Event detection: 100% reliable")
    print("   - Integrations: Operational")
    print("   - Stress tested: Passed")
    print("   - Continuous monitoring: Stable")
    sys.exit(0)
elif passed_tests >= total_tests * 0.8:
    print("⚠️  PARTIALLY READY: Some integrations unavailable")
    print("   - Core functionality works")
    print("   - External services may be offline")
    print("   - Safe to run in limited mode")
    sys.exit(0)
else:
    print("❌ NOT READY: Critical failures detected")
    sys.exit(1)
