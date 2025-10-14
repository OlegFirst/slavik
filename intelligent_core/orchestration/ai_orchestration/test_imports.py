"""
Import Verification Test
Tests all module imports to ensure no circular dependencies or missing modules
"""

import sys
from typing import List, Tuple

def test_core_imports() -> Tuple[bool, List[str]]:
    """Test core module imports"""
    errors = []
    try:
        from core.base_orchestrator import BaseOrchestrator
        from core.service_registry import ServiceRegistry
        from core.health_monitor import HealthMonitor
        from core.event_coordinator import EventCoordinator
        from core.docker_manager import DockerManager
        print("✅ Core modules imported successfully")
        return True, errors
    except Exception as e:
        errors.append(f"Core import error: {e}")
        print(f"❌ Core import failed: {e}")
        return False, errors

def test_model_imports() -> Tuple[bool, List[str]]:
    """Test model imports"""
    errors = []
    try:
        from models.platform_models import EventPublishRequest, WorkflowStartRequest
        from models.ai_models import AIDecision, Decision
        from models.scenario_models import ScenarioGenerationRequest
        from models.deployment_models import DeploymentPlan
        print("✅ Model modules imported successfully")
        return True, errors
    except Exception as e:
        errors.append(f"Model import error: {e}")
        print(f"❌ Model import failed: {e}")
        return False, errors

def test_platform_imports() -> Tuple[bool, List[str]]:
    """Test platform orchestrator imports"""
    errors = []
    try:
        from platform.service_groups import ServiceGroup
        from platform.platform_orchestrator import PlatformOrchestrator
        from platform.deployment_manager import DeploymentManager
        print("✅ Platform modules imported successfully")
        return True, errors
    except Exception as e:
        errors.append(f"Platform import error: {e}")
        print(f"❌ Platform import failed: {e}")
        return False, errors

def test_ai_imports() -> Tuple[bool, List[str]]:
    """Test AI orchestrator imports"""
    errors = []
    try:
        from ai.ai_orchestrator import AIOrchestrator
        from ai.intelligence_engine import IntelligenceEngine
        from ai.devops_engine import DevOpsEngine
        from ai.claude_engine import ClaudeProEngine
        from ai.agent_router import AIAgentRouter, AgentCapability
        print("✅ AI modules imported successfully")
        return True, errors
    except Exception as e:
        errors.append(f"AI import error: {e}")
        print(f"❌ AI import failed: {e}")
        return False, errors

def test_scenario_imports() -> Tuple[bool, List[str]]:
    """Test scenario orchestrator imports"""
    errors = []
    try:
        from scenario.scenario_orchestrator import ScenarioOrchestrator
        from scenario.learning_engine import LearningEngine
        print("✅ Scenario modules imported successfully")
        return True, errors
    except Exception as e:
        errors.append(f"Scenario import error: {e}")
        print(f"❌ Scenario import failed: {e}")
        return False, errors

def test_control_center_imports() -> Tuple[bool, List[str]]:
    """Test control center imports"""
    errors = []
    try:
        from control_center.unified_controller import UnifiedController
        print("✅ Control center modules imported successfully")
        return True, errors
    except Exception as e:
        errors.append(f"Control center import error: {e}")
        print(f"❌ Control center import failed: {e}")
        return False, errors

def test_integration_imports() -> Tuple[bool, List[str]]:
    """Test integration imports"""
    errors = []
    try:
        from integrations.github_client import GitHubTokenManager
        print("✅ Integration modules imported successfully")
        return True, errors
    except Exception as e:
        errors.append(f"Integration import error: {e}")
        print(f"❌ Integration import failed: {e}")
        return False, errors

def test_main_imports() -> Tuple[bool, List[str]]:
    """Test main application imports"""
    errors = []
    try:
        # Don't actually import main to avoid starting the app
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("✅ Main application module loaded successfully")
            return True, errors
        else:
            errors.append("Could not load main.py spec")
            print("❌ Main application import failed: No spec")
            return False, errors
    except Exception as e:
        errors.append(f"Main import error: {e}")
        print(f"❌ Main import failed: {e}")
        return False, errors

def main():
    """Run all import tests"""
    print("=" * 60)
    print("ORCHESTRATOR IMPORT VERIFICATION TEST")
    print("=" * 60)
    print()

    tests = [
        ("Core Modules", test_core_imports),
        ("Model Modules", test_model_imports),
        ("Platform Modules", test_platform_imports),
        ("AI Modules", test_ai_imports),
        ("Scenario Modules", test_scenario_imports),
        ("Control Center", test_control_center_imports),
        ("Integration Modules", test_integration_imports),
        ("Main Application", test_main_imports),
    ]

    results = []
    all_errors = []

    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        success, errors = test_func()
        results.append((test_name, success))
        all_errors.extend(errors)

    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if all_errors:
        print()
        print("=" * 60)
        print("ERRORS")
        print("=" * 60)
        for error in all_errors:
            print(f"- {error}")

    if passed == total:
        print()
        print("🎉 ALL IMPORTS VERIFIED SUCCESSFULLY!")
        return 0
    else:
        print()
        print("⚠️  SOME IMPORTS FAILED - CHECK ERRORS ABOVE")
        return 1

if __name__ == "__main__":
    sys.exit(main())
