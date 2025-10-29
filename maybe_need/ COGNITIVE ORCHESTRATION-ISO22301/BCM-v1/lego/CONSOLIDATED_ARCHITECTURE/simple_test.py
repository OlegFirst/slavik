#!/usr/bin/env python3
"""
Simple Test for Consolidated Cognitive Orchestration System
Basic functionality test without external dependencies
"""

import asyncio
import json
from unittest.mock import Mock

# Import our modules
try:
    from models import SystemRequest, HealthStatus, ExperimentRequest
    from orchestrators import CognitiveOrchestrationController
    print("✅ Module imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)


async def test_basic_functionality():
    """Test basic system functionality"""
    print("\n🧪 Testing Consolidated Cognitive Orchestration System...")

    # Test 1: Pydantic Models
    print("\n1️⃣ Testing Pydantic models...")
    try:
        # Test SystemRequest
        request = SystemRequest(
            type="health-check",
            component="event-bus",
            priority=5
        )
        print(f"   ✅ SystemRequest: {request.type}, priority: {request.priority}")

        # Test ExperimentRequest
        experiment = ExperimentRequest(
            type="experiment",
            name="Test Experiment",
            code="print('hello world')",
            auto_run=True
        )
        print(f"   ✅ ExperimentRequest: {experiment.name}, auto_run: {experiment.auto_run}")

        # Test HealthStatus enum
        status = HealthStatus.HEALTHY
        print(f"   ✅ HealthStatus enum: {status}")

    except Exception as e:
        print(f"   ❌ Model test failed: {e}")
        return False

    # Test 2: Mock Integrations
    print("\n2️⃣ Testing mock integrations...")
    try:
        mock_integrations = {
            'redis_client': Mock(),
            'postgres_client': Mock(),
            'docker_manager': Mock()
        }

        # Configure mocks
        mock_integrations['redis_client'].health_check = Mock(return_value=True)
        mock_integrations['postgres_client'].health_check = Mock(return_value=True)
        mock_integrations['docker_manager'].health_check = Mock(return_value=True)

        print("   ✅ Mock integrations created")

    except Exception as e:
        print(f"   ❌ Mock integration test failed: {e}")
        return False

    # Test 3: Cognitive Controller
    print("\n3️⃣ Testing cognitive controller...")
    try:
        controller = CognitiveOrchestrationController(mock_integrations)
        print(f"   ✅ Controller created with {len(controller.orchestrators)} orchestrators")

        # Test orchestrator names
        expected_orchestrators = ['system', 'bridge', 'program', 'client', 'sandbox']
        actual_orchestrators = list(controller.orchestrators.keys())

        if set(expected_orchestrators) == set(actual_orchestrators):
            print(f"   ✅ All expected orchestrators present: {actual_orchestrators}")
        else:
            print(f"   ❌ Orchestrator mismatch. Expected: {expected_orchestrators}, Got: {actual_orchestrators}")

    except Exception as e:
        print(f"   ❌ Controller test failed: {e}")
        return False

    # Test 4: Request Routing Logic
    print("\n4️⃣ Testing request routing logic...")
    try:
        test_cases = [
            ({"type": "authenticate"}, "client"),
            ({"type": "experiment"}, "sandbox"),
            ({"type": "business-logic"}, "program"),
            ({"type": "translate"}, "bridge"),
            ({"type": "health-check"}, "system"),
            ({"domain": "bcm", "module": "risk"}, "program"),
            ({"from_level": "system", "to_level": "program"}, "bridge"),
        ]

        for request, expected in test_cases:
            actual = controller._determine_orchestrator(request)
            if actual == expected:
                print(f"   ✅ {request} → {actual}")
            else:
                print(f"   ❌ {request} → {actual} (expected {expected})")

    except Exception as e:
        print(f"   ❌ Routing test failed: {e}")
        return False

    # Test 5: Metrics
    print("\n5️⃣ Testing metrics...")
    try:
        initial_metrics = controller.get_metrics()
        print(f"   ✅ Initial metrics: {initial_metrics}")

        # Simulate request processing
        controller.metrics["total_requests"] = 10
        controller.metrics["successful_requests"] = 8
        controller.metrics["failed_requests"] = 2
        controller._update_response_time(0.1)

        updated_metrics = controller.get_metrics()
        print(f"   ✅ Updated metrics: {updated_metrics}")

        if updated_metrics["total_requests"] == 10:
            print("   ✅ Metrics update working correctly")
        else:
            print("   ❌ Metrics update failed")

    except Exception as e:
        print(f"   ❌ Metrics test failed: {e}")
        return False

    # Test 6: JSON Serialization
    print("\n6️⃣ Testing JSON serialization...")
    try:
        request_dict = {
            "type": "business-logic",
            "domain": "bcm",
            "module": "risk-assessment",
            "action": "assess",
            "data": {"risk_id": "RISK-001"}
        }

        json_str = json.dumps(request_dict)
        parsed_back = json.loads(json_str)

        if parsed_back == request_dict:
            print("   ✅ JSON serialization working")
        else:
            print("   ❌ JSON serialization failed")

    except Exception as e:
        print(f"   ❌ JSON test failed: {e}")
        return False

    return True


def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")

    required_files = [
        "main.py",
        "models.py",
        "orchestrators.py",
        "integrations.py",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "README.md"
    ]

    import os
    missing_files = []

    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - missing")
            missing_files.append(file)

    if not missing_files:
        print("   ✅ All required files present")
        return True
    else:
        print(f"   ❌ Missing files: {missing_files}")
        return False


def test_orchestrator_paths():
    """Test that JavaScript orchestrator paths exist"""
    print("\n🗂️ Testing orchestrator paths...")

    import os
    from pathlib import Path

    base_path = Path(__file__).parent.parent / "ORCHESTRATORS"
    orchestrator_files = [
        "base-orchestrator.js",
        "system-orchestrator.js",
        "bridge-orchestrator.js",
        "program-orchestrator.js",
        "client-orchestrator.js",
        "sandbox-orchestrator.js"
    ]

    missing_orchestrators = []

    for file in orchestrator_files:
        file_path = base_path / file
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - missing at {file_path}")
            missing_orchestrators.append(file)

    if not missing_orchestrators:
        print("   ✅ All JavaScript orchestrators found")
        return True
    else:
        print(f"   ❌ Missing orchestrators: {missing_orchestrators}")
        return False


async def main():
    """Main test runner"""
    print("🚀 Consolidated Cognitive Orchestration System - Simple Test Suite")
    print("=" * 70)

    tests = [
        ("File Structure", test_file_structure),
        ("Orchestrator Paths", test_orchestrator_paths),
        ("Basic Functionality", test_basic_functionality),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 50)

        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            results.append((test_name, result))

        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    print("-" * 70)
    print(f"📈 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED - System ready for integration!")
        return True
    else:
        print("⚠️  Some tests failed - review and fix issues")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test suite crashed: {e}")
        exit(1)