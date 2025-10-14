# 🚀 INTEGRATION QUICK START GUIDE
## Как начать использовать интеграцию между компонентами

**Дата:** 2025-10-13
**Версия:** 1.0.0
**Для:** Разработчиков

---

## 📖 Оглавление

1. [Быстрый старт за 5 минут](#быстрый-старт-за-5-минут)
2. [Примеры использования](#примеры-использования)
3. [Полная документация](#полная-документация)

---

## ⚡ Быстрый старт за 5 минут

### Scenario Intelligence → Simulation Service

**Задача:** Конвертировать L3 сценарий в BCM exercise

```python
# 1. Импортировать adapter
from scenario_intelligence.integration import get_simulation_adapter

# 2. Получить global instance
adapter = get_simulation_adapter()

# 3. Конвертировать сценарий в exercise
exercise = await adapter.convert_scenario_to_exercise(
    scenario_id="scenario-123",
    exercise_type="bcm_drill",
    duration_minutes=240
)

print(f"Exercise created: {exercise['exercise_id']}")
print(f"Success: {exercise['success']}")
```

**Результат:**
```json
{
    "exercise_id": "exercise-456",
    "success": true,
    "exercise_type": "bcm_drill",
    "estimated_duration_ms": 14400000
}
```

---

### Simulation Service → Scenario Intelligence

**Задача:** Получить сценарий и отправить результаты обратно

```python
# 1. Импортировать client
from simulation_service.integration.scenario_client import get_scenario_client

# 2. Получить global instance
client = get_scenario_client()

# 3. Получить сценарий
scenario = await client.get_scenario("scenario-123")
print(f"Got scenario: {scenario['name']}, Level: {scenario['level']}")

# 4. Запустить симуляцию (ваш код)
simulation_result = {
    "simulation_id": "sim-789",
    "effectiveness": 0.85,
    "duration_ms": 12000,
    "metrics": {...}
}

# 5. Отправить результат обратно для обучения
result = await client.submit_simulation_result(
    scenario_id="scenario-123",
    simulation_result=simulation_result
)

print(f"Result accepted: {result['accepted']}")
print(f"Learning ID: {result['learning_id']}")
```

**Результат:**
```json
{
    "accepted": true,
    "learning_id": "learning-101"
}
```

---

## 🎯 Примеры использования

### Пример 1: Predictive Intelligence

**Предсказать вероятность ошибки сценария:**

```python
from scenario_intelligence.integration import get_predictive_adapter

adapter = get_predictive_adapter()

# Предсказать ошибку
prediction = await adapter.predict_scenario_failure(
    scenario_id="scenario-123",
    historical_data={
        "previous_failures": 2,
        "total_executions": 10
    }
)

print(f"Failure probability: {prediction['probability']:.2%}")
print(f"Confidence: {prediction['confidence']:.2%}")

if prediction['probability'] > 0.5:
    print("⚠️ High failure risk!")
    print(f"Factors: {prediction['factors']}")
    print(f"Recommendation: {prediction['recommendation']}")
```

**Вывод:**
```
Failure probability: 65.00%
Confidence: 85.00%
⚠️ High failure risk!
Factors: ['insufficient_timeout', 'missing_error_handling', 'external_dependency']
Recommendation: Add retry logic and increase timeout to 60 seconds
```

---

### Пример 2: Community Intelligence

**Получить коллективную рекомендацию:**

```python
from scenario_intelligence.integration import get_community_adapter

adapter = get_community_adapter()

# Коллективное решение
recommendation = await adapter.get_community_recommendation(
    scenario_id="scenario-123",
    context={
        "organization_type": "hospital",
        "size": "large",
        "region": "EU"
    },
    agents=["all"]  # Все агенты
)

print(f"Consensus: {recommendation['consensus']}")
print(f"Confidence: {recommendation['confidence']:.2%}")
print(f"Votes: {recommendation['votes']}")

for agent_vote in recommendation['reasoning']:
    print(f"  - {agent_vote['agent']}: {agent_vote['vote']} ({agent_vote['reason']})")
```

**Вывод:**
```
Consensus: approve
Confidence: 92.00%
Votes: {'approve': 11, 'reject': 1}
  - Analytics Specialist: approve (Well structured scenario)
  - DevOps Agent: approve (Realistic timeouts)
  - BIA Expert: reject (Missing business context)
  ...
```

---

### Пример 3: Workflow Intelligence

**Process mining и оптимизация:**

```python
from scenario_intelligence.integration import get_workflow_intel_adapter

adapter = get_workflow_intel_adapter()

# Анализ execution flow
flow = await adapter.analyze_execution_flow(
    scenario_id="scenario-123",
    time_window="7d"
)

print(f"Average duration: {flow['average_duration_ms']}ms")
print(f"Bottlenecks found: {len(flow['bottlenecks'])}")

for bottleneck in flow['bottlenecks']:
    print(f"  ⚠️ {bottleneck['step_id']}: {bottleneck['avg_duration_ms']}ms")

# Получить рекомендации по оптимизации
optimizations = await adapter.optimize_scenario("scenario-123")

print("\n🚀 Optimization recommendations:")
for opt in optimizations['optimizations']:
    print(f"  - {opt['type']}: {opt['description']}")
    print(f"    Impact: {opt['impact']}")
```

**Вывод:**
```
Average duration: 3500ms
Bottlenecks found: 2
  ⚠️ step_3_database_query: 1200ms
  ⚠️ step_5_external_api: 800ms

🚀 Optimization recommendations:
  - parallelize_steps: Execute steps 3 and 4 in parallel
    Impact: -600ms (-17%)
  - add_caching: Cache database query results
    Impact: -900ms (-26%)
```

---

### Пример 4: AI Orchestration

**Делегировать задачу AI агенту:**

```python
from scenario_intelligence.integration import get_orchestration_adapter

adapter = get_orchestration_adapter()

# Делегировать BIA analysis
task = await adapter.delegate_to_ai(
    task_type="bia_analysis",
    scenario_context={
        "scenario_id": "scenario-123",
        "organization_type": "hospital",
        "business_processes": ["patient_care", "emergency_services"]
    },
    priority="high"
)

print(f"Task delegated: {task['task_id']}")
print(f"Assigned to: {task['assigned_agent']}")

# Ждать результата (с таймаутом)
result = await adapter.wait_for_result(
    task_id=task['task_id'],
    timeout=300  # 5 минут
)

if result['completed']:
    print(f"\n✅ Task completed in {result['duration_ms']}ms")
    print(f"Critical processes: {result['result']['critical_processes']}")
    print(f"RTO recommendations: {result['result']['rto_recommendations']}")
else:
    print(f"❌ Task failed or timed out")
```

**Вывод:**
```
Task delegated: task-456
Assigned to: BIA Specialist Agent

✅ Task completed in 12500ms
Critical processes: ['patient_care', 'emergency_services', 'pharmacy']
RTO recommendations: {
    'patient_care': {'rto': 0, 'priority': 'critical'},
    'emergency_services': {'rto': 0, 'priority': 'critical'},
    'pharmacy': {'rto': 4, 'priority': 'high'}
}
```

---

### Пример 5: BCM Service

**Загрузить ISO 22301 сценарии:**

```python
from scenario_intelligence.integration import get_bcm_adapter

adapter = get_bcm_adapter()

# Загрузить сценарии для ISO 22301
iso_scenarios = await adapter.load_framework_scenarios("ISO_22301")

print(f"Loaded {len(iso_scenarios)} ISO 22301 scenarios")

for scenario in iso_scenarios[:3]:  # Первые 3
    print(f"  - {scenario['name']} (Clause: {scenario['iso_clause']})")

# Валидация compliance
compliance = await adapter.validate_bcm_compliance(
    scenario_id="scenario-123",
    iso_clause="8.2.2"  # Business Continuity Strategy
)

print(f"\nCompliance check:")
print(f"  Compliant: {compliance['compliant']}")
print(f"  Score: {compliance['score']:.2%}")

if not compliance['compliant']:
    print(f"  Gaps found:")
    for gap in compliance['gaps']:
        print(f"    - {gap}")
```

**Вывод:**
```
Loaded 24 ISO 22301 scenarios
  - BIA Process Test (Clause: 8.2.2)
  - Crisis Communication Plan (Clause: 8.4.2)
  - Recovery Strategy Validation (Clause: 8.3.3)

Compliance check:
  Compliant: False
  Score: 72.00%
  Gaps found:
    - Missing documentation of business impact
    - RTO not defined for critical processes
    - No escalation procedures documented
```

---

### Пример 6: Event Intelligence

**Анализ событий и обнаружение аномалий:**

```python
from scenario_intelligence.integration import get_event_intelligence_adapter

adapter = get_event_intelligence_adapter()

# Анализ событий за последние 24 часа
analysis = await adapter.analyze_scenario_events(
    scenario_id="scenario-123",
    time_window="24h"
)

print(f"Events analyzed: {analysis['events_count']}")
print(f"Patterns found: {len(analysis['patterns'])}")
print(f"Anomalies: {len(analysis['anomalies'])}")

# Обнаружение аномалий
anomalies = await adapter.detect_anomalies(
    scenario_ids=["scenario-123", "scenario-124", "scenario-125"],
    time_window="24h"
)

print(f"\n🚨 Anomalies detected: {len(anomalies)}")
for anomaly in anomalies:
    severity_icon = "🔴" if anomaly['severity'] == "critical" else "🟡"
    print(f"{severity_icon} {anomaly['scenario_id']}: {anomaly['description']}")
```

**Вывод:**
```
Events analyzed: 1247
Patterns found: 3
Anomalies: 2

🚨 Anomalies detected: 2
🔴 scenario-123: Execution time 3x higher than normal (avg: 1200ms, actual: 3600ms)
🟡 scenario-124: Unusual error rate spike (5% → 15%)
```

---

## 📚 Полная документация

### Основные документы:

1. **[PLATFORM_INTEGRATION_MAP.md](PLATFORM_INTEGRATION_MAP.md)**
   - Полная карта интеграций
   - 4 архитектурных слоя
   - Integration patterns
   - Service dependency map
   - Best practices

2. **[ADAPTERS_COMPLETE_SUMMARY.md](../intelligent-core/scenario-intelligence/ADAPTERS_COMPLETE_SUMMARY.md)**
   - Все 8 adapters (7 + simulation)
   - API reference
   - Usage examples
   - Statistics

3. **[COMPLETE_CONTEXT_SUMMARY.md](../intelligent-core/scenario-intelligence/COMPLETE_CONTEXT_SUMMARY.md)**
   - Scenario Generation System
   - 652 scenarios capacity
   - Simulation integration
   - Complete metrics

4. **[Simulation Service README](../platform-services/simulation/simulation-service/README.md)**
   - 4 simulation engines
   - TheHive integration
   - Platform integrations
   - API documentation

---

## 🔗 Все доступные adapters

### scenario-intelligence → Other Services:

| Adapter | Service | Port | Purpose |
|---------|---------|------|---------|
| `get_predictive_adapter()` | Predictive Intelligence | 8030 | Предсказания ошибок |
| `get_community_adapter()` | Community Intelligence | 8040 | Коллективные решения |
| `get_workflow_adapter()` | Workflow Engine (Temporal) | 8020 | Durable workflows |
| `get_orchestration_adapter()` | AI Orchestration | 8026 | Делегирование AI задач |
| `get_event_intelligence_adapter()` | Event Intelligence | 8035 | Event analysis |
| `get_bcm_adapter()` | System BCM Service | 8050 | BCM compliance |
| `get_workflow_intel_adapter()` | Workflow Intelligence | 8037 | Process mining |
| `get_simulation_adapter()` | Simulation Service | 8095 | BCM exercises |

### simulation-service → Other Services:

| Client | Service | Port | Purpose |
|--------|---------|------|---------|
| `get_scenario_client()` | Scenario Intelligence | 8060 | Получение сценариев |
| `get_orchestrator_client()` | AI Orchestration | 8026 | AI задачи |
| `get_workflow_client()` | Workflow Intelligence | 8037 | PDCA cycles |
| `get_foundation_client()` | AI Foundation | 8025 | RAG, LLM |
| `get_knowledge_client()` | Knowledge Center | 8038 | Best practices |
| `get_community_client()` | Community Intelligence | 8040 | Peer review |

---

## 🎓 Tutorial: Создание полного workflow

**Задача:** Создать L3 сценарий → Конвертировать в exercise → Запустить → Получить результаты → Обучиться

### Шаг 1: Scenario Intelligence создает сценарий

```python
# В scenario-intelligence
from scenario_intelligence.core import ScenarioRegistry

registry = ScenarioRegistry()

# Создать L3 сценарий
scenario = await registry.register({
    "level": 3,
    "type": "functional",
    "name": "BIA Process Resilience Test",
    "steps": [
        {"id": "step_1", "action": "start_bia_process"},
        {"id": "step_2", "action": "collect_business_data"},
        {"id": "step_3", "action": "calculate_impact"},
        {"id": "step_4", "action": "generate_report"}
    ],
    "metadata": {
        "organization_type": "hospital",
        "criticality": "high"
    }
})

print(f"✅ Scenario created: {scenario['scenario_id']}")
```

### Шаг 2: Конвертировать в BCM exercise

```python
# Scenario Intelligence конвертирует
from scenario_intelligence.integration import get_simulation_adapter

adapter = get_simulation_adapter()

exercise = await adapter.convert_scenario_to_exercise(
    scenario_id=scenario['scenario_id'],
    exercise_type="bcm_drill",
    duration_minutes=240
)

print(f"✅ Exercise created: {exercise['exercise_id']}")
```

### Шаг 3: Simulation Service запускает exercise

```python
# В simulation-service
from simulation_service.engines import get_scenario_engine

engine = get_scenario_engine()

# Запустить exercise
result = await engine.execute_exercise(
    exercise_id=exercise['exercise_id'],
    participants=["team_lead", "bia_analyst"],
    real_time=False  # Fast simulation
)

print(f"✅ Exercise completed: effectiveness={result['effectiveness']:.2%}")
```

### Шаг 4: Отправить результаты обратно

```python
# simulation-service отправляет результаты
from simulation_service.integration.scenario_client import get_scenario_client

client = get_scenario_client()

learning = await client.submit_simulation_result(
    scenario_id=scenario['scenario_id'],
    simulation_result={
        "exercise_id": exercise['exercise_id'],
        "effectiveness": result['effectiveness'],
        "duration_ms": result['duration_ms'],
        "issues_found": result['issues'],
        "recommendations": result['recommendations']
    }
)

print(f"✅ Learning submitted: {learning['learning_id']}")
```

### Шаг 5: Scenario Intelligence обучается

```python
# scenario-intelligence обновляет паттерны
from scenario_intelligence.learning import PatternDetector, AutoGenerator

# Pattern Detector анализирует результат
detector = PatternDetector()
patterns = await detector.detect_patterns(
    scenario_id=scenario['scenario_id'],
    execution_result=result
)

print(f"✅ Patterns detected: {len(patterns)}")

# Auto-Generator использует паттерны для улучшения
generator = AutoGenerator()
improved_scenario = await generator.improve_scenario(
    scenario_id=scenario['scenario_id'],
    patterns=patterns,
    simulation_result=result
)

print(f"✅ Scenario improved: {improved_scenario['version']}")
```

**Результат:** Полный цикл обучения! 🎉

---

## 🚦 Что дальше?

### Для начинающих:
1. Прочитать [PLATFORM_INTEGRATION_MAP.md](PLATFORM_INTEGRATION_MAP.md)
2. Запустить примеры из этого guide
3. Изучить [ADAPTERS_COMPLETE_SUMMARY.md](../intelligent-core/scenario-intelligence/ADAPTERS_COMPLETE_SUMMARY.md)

### Для продвинутых:
1. Создать собственный adapter для нового сервиса
2. Настроить EventBus subscriptions
3. Реализовать E2E тесты интеграции
4. Добавить distributed tracing

### Для архитекторов:
1. Изучить Service Dependency Map
2. Оптимизировать integration patterns
3. Настроить monitoring & alerting
4. Документировать новые интеграции

---

## 💡 Tips & Tricks

### Tip 1: Всегда используйте global instances

```python
# ✅ Правильно
adapter = get_predictive_adapter()

# ❌ Неправильно
adapter = ScenarioPredictiveAdapter()  # Создаст новый instance
```

### Tip 2: Graceful error handling

```python
try:
    result = await adapter.predict_scenario_failure(scenario_id)
except Exception as e:
    logger.error(f"Prediction failed: {e}")
    # Fallback
    result = {"probability": 0.0, "confidence": 0.0}
```

### Tip 3: Используйте EventBus для async

```python
# Для асинхронной связи - EventBus
await eventbus.publish("scenario.completed", payload)

# Для синхронной связи - Adapter
result = await adapter.predict_scenario_failure(scenario_id)
```

### Tip 4: Timeouts везде

```python
result = await adapter.wait_for_result(
    task_id=task_id,
    timeout=300  # ВСЕГДА указывать timeout!
)
```

---

**Версия:** 1.0.0
**Дата:** 2025-10-13
**Автор:** Claude + MD collaboration
**Статус:** ✅ Ready for Use

**Поддержка:** [GitHub Issues](https://github.com/your-org/ai-platform-iso/issues)
