#!/usr/bin/env python3
"""
Quick Test - Verify All Imports Work
=====================================

This script quickly verifies that all modules can be imported.
Run this before running the full test suite.
"""

import sys
import traceback


def test_imports():
    """Test all critical imports."""
    errors = []

    print("Testing imports...")
    print("=" * 60)

    # Test main module
    try:
        from intelligent_core.ai_orchestration import AIOrchestrator
        print("✅ Main module: AIOrchestrator")
    except Exception as e:
        errors.append(f"❌ Main module: {e}")
        traceback.print_exc()

    # Test models
    try:
        from intelligent_core.ai_orchestration.models import (
            Decision, Strategy, Priority, FullContext, SafetyResult,
            ActionType, PriorityLevel, MemoryType
        )
        print("✅ Models: All data models")
    except Exception as e:
        errors.append(f"❌ Models: {e}")
        traceback.print_exc()

    # Test decision center
    try:
        from intelligent_core.ai_orchestration.decision_center import (
            ContextAggregator, PriorityEngine, StrategySelector, DelegationManager
        )
        print("✅ Decision Center: All components")
    except Exception as e:
        errors.append(f"❌ Decision Center: {e}")
        traceback.print_exc()

    # Test memory
    try:
        from intelligent_core.ai_orchestration.memory import (
            DistributedMemory, WorkingMemory, ShortTermMemory,
            LongTermMemory, ProceduralMemory
        )
        print("✅ Memory: All memory layers")
    except Exception as e:
        errors.append(f"❌ Memory: {e}")
        traceback.print_exc()

    # Test safety
    try:
        from intelligent_core.ai_orchestration.safety import (
            SafetyMonitor, ConstitutionEnforcer, LoopDetector,
            HallucinationDetector, ControlMonitor
        )
        print("✅ Safety: All safety components")
    except Exception as e:
        errors.append(f"❌ Safety: {e}")
        traceback.print_exc()

    # Test evolution
    try:
        from intelligent_core.ai_orchestration.evolution import (
            EvolutionEngine, DataEvolution, ModelEvolution, CodeEvolution
        )
        print("✅ Evolution: All evolution components")
    except Exception as e:
        errors.append(f"❌ Evolution: {e}")
        traceback.print_exc()

    print("=" * 60)

    # Summary
    if errors:
        print(f"\n❌ FAILED: {len(errors)} import errors")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("\n✅ SUCCESS: All imports working!")
        print(f"\nModule is ready for use.")
        print(f"Run tests with: pytest tests/ -v")
        return True


if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
