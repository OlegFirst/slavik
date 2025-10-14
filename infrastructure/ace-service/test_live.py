#!/usr/bin/env python3
"""
Live Test - ACE Service на порту 8060
Тестируем полный workflow: Generate → Execute → Reflect → Curate
"""

import requests
import json

BASE_URL = "http://localhost:8060"

print("\n" + "="*60)
print("🧪 ACE Service Live Test")
print("="*60 + "\n")

# Test 1: Generator
print("1️⃣  Testing Generator (Generate Context)...")
response = requests.post(f"{BASE_URL}/api/v1/ace/generate-context", json={
    "task_type": "test_live_scenario",
    "base_context": {
        "module": "test",
        "operation": "live_test"
    },
    "module_name": "test_module"
})

if response.status_code == 200:
    context_data = response.json()
    enhanced_context = context_data['enhanced_context']
    print(f"✅ Context generated!")
    print(f"   Strategies: {len(enhanced_context.get('playbook_strategies', []))}")
    print(f"   Patterns: {len(enhanced_context.get('known_patterns', []))}")
    print(f"   Playbook ID: {enhanced_context.get('playbook_id')}")
    print(f"   Version: {enhanced_context.get('playbook_version')}\n")
else:
    print(f"❌ Failed: {response.status_code}\n")
    exit(1)

# Test 2: Simulate task execution
print("2️⃣  Simulating Task Execution...")
simulated_result = {
    "success": True,
    "output": "Test scenario generated successfully",
    "effectiveness": 0.85
}
print("✅ Task executed (simulated)\n")

# Test 3: Reflector
print("3️⃣  Testing Reflector (Analyze Trajectory)...")
trajectory = {
    "input_context": enhanced_context,
    "output_result": simulated_result,
    "success": simulated_result["success"],
    "effectiveness": simulated_result["effectiveness"]
}

response = requests.post(f"{BASE_URL}/api/v1/ace/reflect", json={
    "task_type": "test_live_scenario",
    "trajectory": trajectory,
    "module_name": "test_module"
})

if response.status_code == 200:
    insights_data = response.json()
    insights = insights_data['insights']
    print(f"✅ Insights generated!")
    print(f"   Effectiveness: {insights.get('effectiveness_score')}")
    print(f"   Success: {insights.get('success')}")
    print(f"   Patterns found: {len(insights.get('patterns_identified', []))}")
    print(f"   Recommendations: {len(insights.get('recommendations', []))}\n")
else:
    print(f"❌ Failed: {response.status_code}\n")
    exit(1)

# Test 4: Curator
print("4️⃣  Testing Curator (Update Playbook)...")
response = requests.post(f"{BASE_URL}/api/v1/ace/curate", json={
    "task_type": "test_live_scenario",
    "insights": insights,
    "module_name": "test_module"
})

if response.status_code == 200:
    playbook_data = response.json()
    updated_playbook = playbook_data['updated_playbook']
    print(f"✅ Playbook updated!")
    print(f"   New version: {updated_playbook.get('version')}")
    print(f"   Previous version: {updated_playbook.get('previous_version')}")
    print(f"   Strategies: {len(updated_playbook.get('strategies', []))}")
    print(f"   Patterns: {len(updated_playbook.get('patterns', []))}\n")
else:
    print(f"❌ Failed: {response.status_code}\n")
    exit(1)

# Test 5: Check updated stats
print("5️⃣  Checking Updated Stats...")
response = requests.get(f"{BASE_URL}/stats")

if response.status_code == 200:
    stats = response.json()
    print(f"✅ Stats retrieved!")
    print(f"   Total playbooks: {stats['total_playbooks']}")
    print(f"   Total trajectories: {stats['total_trajectories']}")
    print(f"   Active modules: {len(stats['active_modules'])}")
    print(f"   Modules: {', '.join(stats['active_modules'])}\n")
else:
    print(f"❌ Failed: {response.status_code}\n")
    exit(1)

print("="*60)
print("🎉 ALL TESTS PASSED!")
print("="*60)
print("\n✨ ACE Service is fully operational on port 8060!")
print("\n📊 Next steps:")
print("   1. Check data in Supabase")
print("   2. Integrate with intelligent-core modules")
print("   3. Monitor KPIs over time")
print()
