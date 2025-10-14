#!/usr/bin/env python3
"""
ACE Service Integration Test
Tests the complete ACE workflow: Generate → Execute → Reflect → Curate
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from ace_client import ACEClient
    print("✅ ACE Client import successful")
except ImportError as e:
    print(f"❌ Failed to import ACE Client: {e}")
    sys.exit(1)


async def test_full_workflow():
    """Test complete ACE workflow"""
    print("\n" + "="*60)
    print("ACE SERVICE INTEGRATION TEST")
    print("="*60 + "\n")

    # Initialize client
    print("1️⃣  Initializing ACE Client...")
    ace = ACEClient(base_url="http://localhost:8050")

    try:
        await ace.connect()
        print("✅ Connected to ACE Service\n")
    except Exception as e:
        print(f"❌ Failed to connect to ACE Service: {e}")
        print("\n💡 Make sure ACE Service is running:")
        print("   cd /Users/MD/AI-Platform-ISO/infrastructure/ace-service")
        print("   python3 main.py")
        return False

    # Test 1: Generator
    print("2️⃣  Testing Generator (Generate Context)...")
    task_type = "test_scenario_generation"
    base_context = {
        "operation": "emergency_response",
        "module": "scenario_intelligence",
        "framework": "ISO_22301"
    }

    try:
        enhanced_context = await ace.generate_context(
            task_type=task_type,
            base_context=base_context,
            module_name="test_module"
        )
        print(f"✅ Generated enhanced context")
        print(f"   Strategies: {len(enhanced_context.get('playbook_strategies', []))}")
        print(f"   Patterns: {len(enhanced_context.get('known_patterns', []))}")
        print(f"   Domain knowledge: {len(enhanced_context.get('domain_expertise', []))}\n")
    except Exception as e:
        print(f"❌ Generator failed: {e}\n")
        return False

    # Test 2: Execute (simulated)
    print("3️⃣  Simulating Task Execution...")
    result = {
        "success": True,
        "output": "Emergency response scenario generated successfully",
        "effectiveness": 0.85,
        "steps": ["Analyze", "Generate", "Validate"]
    }
    print("✅ Task executed (simulated)\n")

    # Test 3: Reflector
    print("4️⃣  Testing Reflector (Analyze Trajectory)...")
    trajectory = {
        "input_context": enhanced_context,
        "output_result": result,
        "steps": result["steps"],
        "success": result["success"],
        "effectiveness": result["effectiveness"]
    }

    try:
        insights = await ace.reflect_on_trajectory(
            task_type=task_type,
            trajectory=trajectory,
            module_name="test_module"
        )
        print(f"✅ Generated insights")
        print(f"   Effectiveness: {insights.get('effectiveness_score', 'N/A')}")
        print(f"   Patterns found: {len(insights.get('patterns_identified', []))}")
        print(f"   Recommendations: {len(insights.get('recommendations', []))}\n")
    except Exception as e:
        print(f"❌ Reflector failed: {e}\n")
        return False

    # Test 4: Curator
    print("5️⃣  Testing Curator (Update Playbook)...")
    try:
        updated_playbook = await ace.curate_playbook(
            task_type=task_type,
            insights=insights,
            module_name="test_module"
        )
        print(f"✅ Playbook updated")
        print(f"   New version: {updated_playbook.get('version', 'N/A')}")
        print(f"   Total strategies: {len(updated_playbook.get('strategies', []))}")
        print(f"   Total patterns: {len(updated_playbook.get('patterns', []))}\n")
    except Exception as e:
        print(f"❌ Curator failed: {e}\n")
        return False

    # Test 5: Analytics
    print("6️⃣  Testing Analytics Endpoint...")
    try:
        analytics = await ace.get_analytics()
        print(f"✅ Analytics retrieved")
        print(f"   Total playbooks: {analytics.get('total_playbooks', 0)}")
        print(f"   Total trajectories: {analytics.get('total_trajectories', 0)}")
        print(f"   Avg effectiveness: {analytics.get('avg_effectiveness', 0):.2%}\n")
    except Exception as e:
        print(f"❌ Analytics failed: {e}\n")
        return False

    # Cleanup
    await ace.close()

    print("="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print("\n✨ ACE Service is ready for platform integration")
    print("\n📖 Next steps:")
    print("   1. Review INTEGRATION_GUIDE.md")
    print("   2. Integrate with intelligent-core modules")
    print("   3. Monitor playbook evolution in Supabase")

    return True


async def test_convenience_workflow():
    """Test the convenience ace_workflow function"""
    print("\n" + "="*60)
    print("TESTING CONVENIENCE WORKFLOW")
    print("="*60 + "\n")

    ace = ACEClient(base_url="http://localhost:8050")

    try:
        await ace.connect()
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False

    # Define a simple task execution function
    async def execute_task(context, **kwargs):
        print("   → Executing task with enhanced context...")
        await asyncio.sleep(0.5)  # Simulate work
        return {
            "success": True,
            "output": f"Task completed with {len(context.get('playbook_strategies', []))} strategies",
            "effectiveness": 0.90
        }

    print("Testing ace_workflow helper function...")
    try:
        result = await ace.ace_workflow(
            task_type="test_convenience_workflow",
            base_context={"test": "data"},
            execute_task_fn=execute_task,
            module_name="test_module"
        )
        print(f"✅ Convenience workflow completed")
        print(f"   Result: {result.get('output', 'N/A')}\n")
    except Exception as e:
        print(f"❌ Convenience workflow failed: {e}\n")
        await ace.close()
        return False

    await ace.close()
    print("✅ Convenience workflow test passed!\n")
    return True


async def main():
    """Run all tests"""
    # Test 1: Full workflow
    test1_passed = await test_full_workflow()

    if not test1_passed:
        print("\n❌ Integration tests failed")
        sys.exit(1)

    # Test 2: Convenience workflow
    test2_passed = await test_convenience_workflow()

    if not test2_passed:
        print("\n❌ Convenience workflow test failed")
        sys.exit(1)

    print("\n" + "🚀"*30)
    print("ACE SERVICE IS FULLY OPERATIONAL!")
    print("🚀"*30 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
