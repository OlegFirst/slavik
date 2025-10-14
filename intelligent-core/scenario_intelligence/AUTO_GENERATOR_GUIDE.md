# 🤖 Auto-Generator Guide
## AI-powered Scenario Generation (L1-L4)

**Дата:** 2025-10-13
**Версия:** 1.0.0
**Статус:** ✅ **READY**

---

## 🎯 Что такое Auto-Generator?

**Auto-Generator** - это AI-powered система автоматической генерации сценариев на всех 4 уровнях, которая использует **ВСЕ 8 integration adapters** для создания оптимальных, валидированных и безопасных сценариев.

### Используемые adapters:

1. **predictive** - Предсказание оптимальных параметров
2. **community** - Валидация через consensus
3. **workflow** - Temporal для long-running generation
4. **orchestration** - Делегирование AI задач
5. **event_intelligence** - Pattern detection
6. **bcm** - Domain expertise (ISO 22301, NIST, WHO)
7. **workflow_intel** - Process optimization
8. **simulation** - Testing generated scenarios

---

## 🚀 Quick Start

### Установка:

```python
from scenario_intelligence.learning import get_auto_generator

# Get global instance
auto_gen = get_auto_generator()
```

### Level 1 - Module Scenario:

```python
# Generate L1 scenario for a module
scenario = await auto_gen.generate_module_scenario(
    module_name="notification-service",
    operation="send_notification",
    framework="ISO_22301"
)

print(f"✅ Generated: {scenario['scenario']['name']}")
print(f"Level: {scenario['level']}")
print(f"Predicted duration: {scenario['predicted_duration_ms']}ms")
print(f"Community approved: {scenario['validation']['approved']}")
print(f"Safety check: {scenario['safety']['safe']}")
```

**Output:**
```
✅ Generated: Notification Service - Send Notification Test
Level: 1
Predicted duration: 2500ms
Community approved: True
Safety check: True
```

---

## 📚 Complete Examples

### Example 1: Level 1 - Module Scenario

**Use case:** Test individual service functionality

```python
from scenario_intelligence.learning import get_auto_generator

auto_gen = get_auto_generator()

# Generate L1 scenario
result = await auto_gen.generate_module_scenario(
    module_name="bia-service",
    operation="create_bia",
    framework="ISO_22301"
)

if result["success"]:
    scenario = result["scenario"]

    print("📋 Scenario Details:")
    print(f"  Name: {scenario['name']}")
    print(f"  Steps: {len(scenario['steps'])}")
    print(f"  Timeout: {scenario['timeout_ms']}ms")

    print("\n🔮 Predictive Analysis:")
    print(f"  Predicted duration: {result['predicted_duration_ms']}ms")
    print(f"  Confidence: {result['validation']['confidence']:.2%}")

    print("\n👥 Community Validation:")
    print(f"  Approved: {result['validation']['approved']}")
    print(f"  Score: {result['validation']['score']:.2f}")

    if result["validation"]["feedback"]:
        print("\n💡 Feedback:")
        for feedback in result["validation"]["feedback"]:
            print(f"  - {feedback}")

    print("\n🛡️ Safety Check:")
    print(f"  Safe: {result['safety']['safe']}")

    if result["safety"].get("risks"):
        print("  Risks:")
        for risk in result["safety"]["risks"]:
            print(f"  - {risk}")
```

---

### Example 2: Level 2 - Subsystem Scenario

**Use case:** Test integration between modules

```python
# Generate L2 scenario for subsystem
result = await auto_gen.generate_subsystem_scenario(
    subsystem_name="notification-subsystem",
    modules=["email-service", "sms-service", "push-service"],
    interaction_type="cross_module_communication"
)

if result["success"]:
    print("📋 Subsystem Scenario Generated:")
    print(f"  Name: {result['scenario']['name']}")
    print(f"  Modules: {len(result['scenario']['modules'])}")

    print("\n📊 Pattern Analysis:")
    print(f"  Patterns found: {len(result['patterns'])}")
    for pattern in result["patterns"][:3]:
        print(f"  - {pattern.get('type')}: {pattern.get('description')}")

    print("\n🚀 Optimizations:")
    print(f"  Recommendations: {len(result['optimizations']['optimizations'])}")
    for opt in result["optimizations"]["optimizations"][:3]:
        print(f"  - {opt.get('type')}: {opt.get('impact')}")

    print("\n⚠️ Failure Prediction:")
    pred = result["failure_prediction"]
    print(f"  Probability: {pred['probability']:.2%}")
    print(f"  Confidence: {pred['confidence']:.2%}")

    if pred.get("factors"):
        print("  Risk factors:")
        for factor in pred["factors"]:
            print(f"  - {factor}")
```

---

### Example 3: Level 3 - Inter-system Scenario

**Use case:** Test functional workflows between systems

```python
# Generate L3 scenario for inter-system integration
result = await auto_gen.generate_intersystem_scenario(
    system_a="ai-office",
    system_b="platform-services",
    interaction_type="ai_assisted_workflow",
    use_temporal=True  # Use Temporal workflow
)

if result["success"]:
    print("📋 Inter-system Scenario Generated:")
    print(f"  Name: {result['scenario']['name']}")
    print(f"  Systems: {result['scenario']['systems']}")

    print("\n👥 Community Recommendation:")
    rec = result["community_recommendation"]
    print(f"  Consensus: {rec['consensus']}")
    print(f"  Confidence: {rec['confidence']:.2%}")
    print(f"  Votes: {rec['votes']}")

    print("\n✅ BCM Compliance:")
    compliance_a = result["compliance"]["system_a"]
    compliance_b = result["compliance"]["system_b"]
    print(f"  System A: {compliance_a['score']:.2%} compliant")
    print(f"  System B: {compliance_b['score']:.2%} compliant")

    print("\n🔄 Temporal Workflow:")
    if result.get("temporal_workflow_id"):
        print(f"  Workflow ID: {result['temporal_workflow_id']}")
        print("  Durable execution enabled ✅")

    print("\n🎬 Simulation Exercise:")
    exercise = result["exercise"]
    print(f"  Exercise ID: {exercise['exercise_id']}")
    print(f"  Type: {exercise['exercise_type']}")
    print(f"  Duration: {exercise.get('estimated_duration_ms', 0) / 60000:.0f} minutes")
```

---

### Example 4: Level 4 - E2E User Workflow

**Use case:** Complete end-to-end business workflow

```python
# Generate L4 E2E workflow
result = await auto_gen.generate_user_workflow(
    user_persona="Risk Manager",
    workflow_name="Complete Risk Assessment",
    business_goal="Identify and mitigate organizational risks",
    framework="ISO_22301"
)

if result["success"]:
    print("📋 E2E Workflow Generated:")
    print(f"  Name: {result['scenario']['name']}")
    print(f"  Persona: {result['scenario']['user_persona']}")
    print(f"  Goal: {result['scenario']['business_goal']}")

    print("\n✅ BCM Compliance:")
    compliance = result["compliance"]
    print(f"  Compliant: {compliance['compliant']}")
    print(f"  Score: {compliance['score']:.2%}")
    print(f"  Clause coverage: {len(compliance['clause_coverage'])} clauses")

    print("\n💡 Best Practices:")
    for practice in result["best_practices"][:3]:
        print(f"  - {practice.get('practice')}")
        print(f"    Adoption: {practice.get('adoption_rate', 0):.0%}")

    print("\n🔄 PDCA Cycle:")
    pdca = result["pdca"]
    print(f"  Plan: {len(pdca.get('plan', {}))} items")
    print(f"  Do: {len(pdca.get('do', {}))} items")
    print(f"  Check: {len(pdca.get('check', {}))} items")
    print(f"  Act: {len(pdca.get('act', {}))} items")

    print("\n🔄 Temporal Workflow:")
    print(f"  Workflow ID: {result['temporal_workflow_id']}")

    print("\n🎬 Simulation Exercise:")
    exercise = result["exercise"]
    print(f"  Exercise ID: {exercise['exercise_id']}")
    print(f"  Duration: {exercise.get('estimated_duration_ms', 0) / 3600000:.1f} hours")

    print("\n📊 Generation Stats:")
    stats = result["stats"]
    print(f"  Total generated: {stats['total_generated']}")
    print(f"  By level: L1={stats['by_level']['l1']}, L2={stats['by_level']['l2']}, "
          f"L3={stats['by_level']['l3']}, L4={stats['by_level']['l4']}")
    print(f"  Success rate: {stats['success_rate']:.2%}")
```

---

## 🔄 Batch Generation

### Generate multiple scenarios at once:

```python
# Batch generation for L1 scenarios
specifications = [
    {
        "module_name": "email-service",
        "operation": "send_email",
        "framework": "ISO_22301"
    },
    {
        "module_name": "sms-service",
        "operation": "send_sms",
        "framework": "ISO_22301"
    },
    {
        "module_name": "push-service",
        "operation": "send_push",
        "framework": "ISO_22301"
    }
]

results = await auto_gen.generate_batch(
    level=1,
    specifications=specifications
)

print(f"✅ Generated {len(results)} L1 scenarios")

for i, result in enumerate(results, 1):
    if result["success"]:
        print(f"{i}. {result['scenario']['name']} - "
              f"Duration: {result['predicted_duration_ms']}ms")
```

---

## 🎯 How Auto-Generator Uses All 8 Adapters

### Level 1 Generation Flow:

```
1. BCM Adapter → Get domain expertise (ISO 22301, NIST, WHO)
2. Orchestration Adapter → Delegate AI task for scenario generation
3. Predictive Adapter → Forecast optimal timeout
4. Community Adapter → Validate scenario through consensus
5. Orchestration Adapter → Safety check before approval
```

### Level 2 Generation Flow:

```
1. Event Intelligence Adapter → Analyze patterns in subsystem
2. Workflow Intelligence Adapter → Get optimization recommendations
3. Orchestration Adapter → Delegate AI task with patterns + optimizations
4. Community Adapter → Validate integration scenario
5. Predictive Adapter → Predict failure probability
```

### Level 3 Generation Flow:

```
1. Workflow Intelligence Adapter → Analyze flow for both systems
2. BCM Adapter → Validate compliance for both systems
3. Community Adapter → Get recommendation for integration approach
4. Orchestration Adapter → Delegate AI task with all context
5. Workflow Adapter → Register as Temporal workflow (if use_temporal=True)
6. Simulation Adapter → Convert to BCM exercise for testing
```

### Level 4 Generation Flow:

```
1. BCM Adapter → Load framework scenarios (ISO 22301, etc.)
2. Community Adapter → Get best practices for persona
3. Event Intelligence Adapter → Detect anomalies in L3 scenarios
4. Orchestration Adapter → Delegate complex E2E generation
5. Community Adapter → Validate with ALL agents
6. BCM Adapter → Validate full compliance
7. Workflow Adapter → Register as Temporal workflow (always)
8. Workflow Intelligence Adapter → Apply PDCA cycle
9. Simulation Adapter → Convert to long BCM exercise
```

---

## 📊 Statistics

Get generation statistics:

```python
stats = auto_gen.get_stats()

print("📊 Auto-Generator Statistics:")
print(f"Total generated: {stats['total_generated']}")
print(f"Success rate: {stats['success_rate']:.2%}")
print("\nBy level:")
for level, count in stats["by_level"].items():
    print(f"  {level.upper()}: {count}")
```

---

## 🛡️ Safety & Validation

Auto-Generator включает multiple layers of safety and validation:

### 1. AI Safety Check (Orchestration)

```python
# Every scenario passes through safety check
safety = await orchestration.check_safety(
    scenario_id=scenario_id,
    planned_actions=actions
)

if not safety["safe"]:
    # Scenario rejected or modified
    scenario["safety_warnings"] = safety["risks"]
```

### 2. Community Consensus (Community Intelligence)

```python
# Scenarios validated by community of agents
validation = await community.validate_scenario(
    scenario_yaml=yaml.dump(scenario),
    validators=["all"]
)

if not validation["approved"]:
    # Feedback provided for improvement
    scenario["validation_warnings"] = validation["feedback"]
```

### 3. BCM Compliance (BCM Service)

```python
# L4 scenarios checked for BCM compliance
compliance = await bcm.validate_bcm_compliance(
    scenario_id=scenario_id,
    iso_clause=None  # Check all clauses
)

if not compliance["compliant"]:
    # Gaps identified and recommendations provided
    gaps = compliance["gaps"]
```

### 4. Predictive Analysis (Predictive Intelligence)

```python
# Predict failure probability
prediction = await predictive.predict_scenario_failure(
    scenario_id=scenario_id,
    historical_data=history
)

if prediction["probability"] > 0.5:
    # High failure risk - optimization recommended
    optimizations = await predictive.get_optimization_suggestions(scenario_id)
```

---

## 💡 Best Practices

### 1. Always use framework parameter for L1

```python
# ✅ Good
scenario = await auto_gen.generate_module_scenario(
    module_name="bia-service",
    operation="create_bia",
    framework="ISO_22301"  # Provides domain expertise
)

# ❌ Bad
scenario = await auto_gen.generate_module_scenario(
    module_name="bia-service",
    operation="create_bia"
    # No framework - generic scenario
)
```

### 2. Use Temporal for long-running L3/L4

```python
# ✅ Good - L3 with Temporal
scenario = await auto_gen.generate_intersystem_scenario(
    system_a="ai-office",
    system_b="platform-services",
    interaction_type="complex_workflow",
    use_temporal=True  # Durable execution
)

# ✅ Good - L4 always uses Temporal
scenario = await auto_gen.generate_user_workflow(...)  # Temporal by default
```

### 3. Check validation and safety results

```python
result = await auto_gen.generate_module_scenario(...)

if not result["validation"]["approved"]:
    print("⚠️ Community feedback:")
    for feedback in result["validation"]["feedback"]:
        print(f"  - {feedback}")

if not result["safety"]["safe"]:
    print("🛡️ Safety risks:")
    for risk in result["safety"]["risks"]:
        print(f"  - {risk}")
```

### 4. Use batch generation for multiple L1 scenarios

```python
# ✅ Good - Efficient batch generation
results = await auto_gen.generate_batch(level=1, specifications=specs)

# ❌ Bad - Sequential generation
for spec in specs:
    result = await auto_gen.generate_module_scenario(**spec)
```

---

## 🔧 Advanced Usage

### Custom Framework Scenarios

```python
# Generate scenario for custom framework
scenario = await auto_gen.generate_module_scenario(
    module_name="healthcare-bcm",
    operation="pandemic_response",
    framework="WHO_Healthcare"  # WHO-specific guidelines
)
```

### Integration with Simulation

```python
# Generate L3 scenario and immediately test it
result = await auto_gen.generate_intersystem_scenario(
    system_a="bia-module",
    system_b="risk-module",
    interaction_type="risk_based_bia"
)

if result["success"]:
    # Exercise automatically created
    exercise_id = result["exercise"]["exercise_id"]

    # Run simulation
    from scenario_intelligence.integration import get_simulation_adapter

    sim_adapter = get_simulation_adapter()
    sim_result = await sim_adapter.get_exercise_results(exercise_id)

    print(f"Exercise effectiveness: {sim_result['effectiveness']:.2%}")
```

---

## 📚 API Reference

### `generate_module_scenario(module_name, operation, framework="ISO_22301")`

Generate Level 1 module scenario.

**Returns:**
```python
{
    "success": bool,
    "scenario": Dict,  # Generated scenario
    "level": 1,
    "validation": Dict,  # Community validation
    "safety": Dict,  # Safety check
    "predicted_duration_ms": int
}
```

### `generate_subsystem_scenario(subsystem_name, modules, interaction_type="health_check")`

Generate Level 2 subsystem scenario.

**Returns:**
```python
{
    "success": bool,
    "scenario": Dict,
    "level": 2,
    "validation": Dict,
    "failure_prediction": Dict,
    "patterns": List[Dict],
    "optimizations": Dict
}
```

### `generate_intersystem_scenario(system_a, system_b, interaction_type, use_temporal=False)`

Generate Level 3 inter-system scenario.

**Returns:**
```python
{
    "success": bool,
    "scenario": Dict,
    "level": 3,
    "community_recommendation": Dict,
    "compliance": {"system_a": Dict, "system_b": Dict},
    "exercise": Dict,
    "temporal_workflow_id": str (optional)
}
```

### `generate_user_workflow(user_persona, workflow_name, business_goal, framework="ISO_22301")`

Generate Level 4 E2E workflow.

**Returns:**
```python
{
    "success": bool,
    "scenario": Dict,
    "level": 4,
    "validation": Dict,
    "compliance": Dict,
    "best_practices": List[Dict],
    "temporal_workflow_id": str,
    "exercise": Dict,
    "pdca": Dict,
    "stats": Dict
}
```

### `generate_batch(level, specifications)`

Generate multiple scenarios at once.

### `get_stats()`

Get generation statistics.

---

## 🎓 Learning Resources

1. **[PLATFORM_INTEGRATION_MAP.md](../../doc-project/PLATFORM_INTEGRATION_MAP.md)** - How all adapters integrate
2. **[INTEGRATION_QUICK_START.md](../../doc-project/INTEGRATION_QUICK_START.md)** - Adapter usage examples
3. **[ADAPTERS_COMPLETE_SUMMARY.md](ADAPTERS_COMPLETE_SUMMARY.md)** - All 8 adapters documentation

---

**Версия:** 1.0.0
**Дата:** 2025-10-13
**Автор:** Claude + MD collaboration
**Статус:** ✅ **READY FOR USE**
