# ТЗ: Автоматическая Генерация Сценариев + Цикл Самообучения
## Интеграция через СУЩЕСТВУЮЩУЮ Архитектуру

**Date:** 2025-10-09
**Priority:** High (Critical Path!)
**Time:** 6-8 hours (Phase 1: System Level)

---

## 🎯 ГЛАВНАЯ ЦЕЛЬ

Запустить **полный цикл самообучения** через **практическое применение BCM на СЕБЕ**:

```
┌─────────────────────────────────────────────────────────────┐
│  КЛЮЧЕВОЙ ПРИНЦИП:                                          │
│  "Применяя BCM на СЕБЕ → становимся ЭКСПЕРТАМИ"             │
│                                                             │
│  1. Система ЖИВЁТ BCM на практике (для себя)                │
│  2. Учится через ПРАКТИКУ (не теорию)                       │
│  3. Становится ЭКСПЕРТОМ в устойчивости                     │
│  4. ПОТОМ применяет к любым доменам (healthcare, finance)   │
└─────────────────────────────────────────────────────────────┘
```

### Цикл самообучения:

```
СИСТЕМНЫЙ уровень (Priority #1):
Анализ платформы → Сценарии для СЕБЯ → BCM для ПЛАТФОРМЫ →
Learning через ПРАКТИКУ → Улучшения СЕБЯ → ЦИКЛ

ПРОГРАММНЫЙ уровень (когда встали):
Те же модули → Сценарии для пользователей → BCM для организаций →
Обучение пользователей → ЦИКЛ
```

---

## ✅ ЧТО УЖЕ ЕСТЬ (НЕ СОЗДАВАТЬ!)

| Компонент | Где | Роль |
|-----------|-----|------|
| `system_behavior_analyzer.py` | `/infrastructure/AI-office-infrastructure/analytics-specialist/tools/` | Анализ системного поведения |
| `intelligent_module_analyzer.py` | `/infrastructure/AI-office-infrastructure/analytics-specialist/tools/` | Глубокий анализ модулей |
| `analytics_integration_loader.py` | `/intelligent-core/ai-foundation/learning-knowledge/loaders/` | Загрузка в Qdrant |
| `pattern_detector.py` | `/intelligent-core/ai-foundation/learning-knowledge/learning/engines/` | Детекция паттернов |
| `self_learning_engine.py` | `/intelligent-core/ai-foundation/learning/` | Самообучение |
| `rule_generator.py` | `/intelligent-core/ai-foundation/learning/` | Генерация правил |

---

## 🔄 ДВА УРОВНЯ СЦЕНАРИЕВ

### 🎯 Разделение на Системный + Программный

```
┌──────────────────────────────────────────────────────────┐
│  СИСТЕМНЫЙ УРОВЕНЬ (запускаем СЕЙЧАС!)                   │
│  ════════════════════════════════════                     │
│  Target: AI-Platform-ISO (САМА ПЛАТФОРМА)                │
│  Цель: Выживание, устойчивость, эффективность            │
│                                                          │
│  Сценарии:                                               │
│  ├─ BIA для платформы (API Gateway, Event Bus, DB)      │
│  ├─ Risk assessment своих рисков (memory leak, etc)     │
│  ├─ Recovery procedures (auto-restart, failover)        │
│  └─ Resource management (приоритеты, limits)            │
│                                                          │
│  Применение: ПРЯМО СЕЙЧАС на себе                        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  ПРОГРАММНЫЙ УРОВЕНЬ (когда встали)                      │
│  ═══════════════════════════════                         │
│  Target: User Organizations (больницы, банки, заводы)    │
│  Цель: Помощь пользователям в их доменах                │
│                                                          │
│  Сценарии:                                               │
│  ├─ BIA для больниц (Emergency, Patient Records)        │
│  ├─ Risk для банков (Trading, Transactions)             │
│  ├─ ISO 22301 compliance                                │
│  └─ Миллион BCM сценариев                               │
│                                                          │
│  Применение: После системного уровня                     │
└──────────────────────────────────────────────────────────┘
```

**ВАЖНО:** Используем **ТЕ ЖЕ модули** (BIA, Risk, Planning) для обоих уровней!
Отличие только в **target** и **сценариях**.

---

## 🔄 ЦИКЛ (8 Шагов)

### Шаг 1: Анализ кода (analytics-specialist)

**Файл:** `analytics-specialist/workflows/scenario_generation_workflow.py` (создать)

```python
from tools.system_behavior_analyzer import SystemBehaviorAnalyzer
from tools.intelligent_module_analyzer import IntelligentModuleAnalyzer

async def scenario_generation_workflow(level="system"):
    """
    Генерация сценариев для ДВУХ уровней:
    - level="system" → сценарии для ПЛАТФОРМЫ (приоритет!)
    - level="domain" → сценарии для пользователей (потом)
    """

    behavior = SystemBehaviorAnalyzer()
    module_analyzer = IntelligentModuleAnalyzer()

    if level == "system":
        # СИСТЕМНЫЙ: Анализируем ПЛАТФОРМУ для СЕБЯ
        results = await behavior.analyze_platform_for_self()
        scenarios = {
            "platform_bia": {
                "target": "AI-Platform-ISO",
                "processes": ["API Gateway", "Event Bus", "Database", "RAG", "Analytics"],
                "goal": "self_survival"
            },
            "platform_risks": {
                "target": "AI-Platform-ISO",
                "risks": ["memory_leak", "cascade_failure", "self_ddos"],
                "goal": "resilience"
            }
        }
    else:
        # ПРОГРАММНЫЙ: Генерируем для пользователей
        results = await module_analyzer.analyze_all_modules()
        scenarios = {
            "healthcare_bia": {...},
            "finance_risk": {...},
            # ... миллион сценариев
        }

    await publish_event("platform.scenarios.generated", {
        "level": level,
        "scenarios": scenarios,
        "patterns": results["patterns"]
    })
```

---

### Шаг 2: Загрузка в Qdrant (ai-foundation)

**Файл:** `analytics_integration_loader.py` (расширить)

```python
@subscribe_to("platform.scenarios.generated")
async def load_scenarios(event):
    level = event.data["level"]  # "system" или "domain"

    # Разные коллекции для разных уровней
    collection = "system_scenarios" if level == "system" else "domain_scenarios"

    await qdrant.upsert(
        collection=collection,
        documents=event.data["scenarios"],
        metadata={"level": level, "priority": "critical" if level == "system" else "normal"}
    )

    await publish_event("platform.knowledge.updated", {
        "level": level,
        "collection": collection
    })
```

---

### Шаг 3: Детекция паттернов (ai-foundation)

**Файл:** `pattern_detector.py` (расширить)

```python
@subscribe_to("platform.knowledge.updated")
async def detect_patterns(event):
    base_flows = detect_base_flows(scenarios)
    await save_rules(base_flows)
    await publish_event("platform.patterns.detected", {...})
```

---

### Шаг 4: Самообучение (ai-foundation)

**Файл:** `self_learning_engine.py` (расширить)

```python
@subscribe_to("platform.patterns.detected")
async def learn(event):
    await update_ml_models(event.data["patterns"])
    templates = await generate_code_templates(event.data["base_flows"])
    await publish_event("platform.learning.completed", {...})
```

---

### Шаг 5: Генерация улучшений (ai-foundation)

**Файл:** `rule_generator.py` (расширить)

```python
@subscribe_to("platform.learning.completed")
async def generate_improvements(event):
    violations = await find_rule_violations()
    improvements = [await generate_fix(v) for v in violations]
    await publish_event("platform.improvements.generated", {...})
```

---

### Шаг 6: Применение улучшений (workflow_intelligence)

**Файл:** `workflow_intelligence/event_subscribers.py` (расширить)

```python
@subscribe_to("platform.improvements.generated")
async def apply_improvements(event):
    """
    КЛЮЧЕВОЙ ШАГ: Применяем BCM на ПРАКТИКЕ!
    """
    level = event.data.get("level", "system")

    if level == "system":
        # СИСТЕМНЫЙ: Применяем К СЕБЕ прямо сейчас!
        for improvement in event.data["improvements"]:
            if improvement["type"] == "resource_priority":
                # Применяем приоритеты ресурсов
                await resource_manager.set_priority(
                    service=improvement["service"],
                    priority=improvement["priority"]
                )
            elif improvement["type"] == "recovery_procedure":
                # Настраиваем auto-recovery
                await health_monitor.configure(
                    service=improvement["service"],
                    rto=improvement["rto"],
                    action="auto_restart"
                )
            elif improvement["type"] == "circuit_breaker":
                # Добавляем circuit breaker
                await circuit_breaker.add(
                    service=improvement["service"],
                    threshold=improvement["threshold"]
                )

        # УЧИМСЯ от применения
        await learning_engine.learn_from_practice({
            "applied": event.data["improvements"],
            "results": "measured_after_24h"
        })
    else:
        # ПРОГРАММНЫЙ: Сохраняем как рекомендации для пользователей
        await recommendations_db.save(event.data["improvements"])

    await publish_event("platform.cycle.completed", {
        "level": level,
        "applied": len(event.data["improvements"])
    })
```

---

### Шаг 7: Повтор цикла (EventBus)

```python
@subscribe_to("platform.cycle.completed")
async def schedule_next(event):
    await asyncio.sleep(86400)  # 24 hours
    await publish_event("platform.analysis.trigger", {...})
```

---

## 📝 ЗАДАЧИ (ПРИОРИТИЗИРОВАННЫЕ)

### 🔥 PHASE 1: СИСТЕМНЫЙ УРОВЕНЬ (СЕЙЧАС!)

**Цель:** Платформа применяет BCM к СЕБЕ

#### Task 1.1: Системные сценарии
- [ ] Создать `/learning-knowledge/scenarios/system_scenarios/`
  - [ ] `platform_bia.json` - BIA для платформы
  - [ ] `platform_risks.json` - Риски платформы
  - [ ] `recovery_procedures.json` - Процедуры восстановления
  - [ ] `resource_priorities.json` - Приоритеты ресурсов

#### Task 1.2: Применение к СЕБЕ
- [ ] Создать `/learning-knowledge/system_bcm/system_bcm.py`
  - [ ] `execute_self_bia()` - BIA для платформы
  - [ ] `assess_own_risks()` - Risk assessment себя
  - [ ] `setup_recovery()` - Настройка auto-recovery
  - [ ] `apply_priorities()` - Приоритизация ресурсов

#### Task 1.3: Практическое обучение
- [ ] Создать `learning-knowledge/learning/practice_learning.py`
  - [ ] `learn_from_self_application()` - Учимся применяя к себе
  - [ ] `measure_effectiveness()` - Измеряем результаты
  - [ ] `improve_based_on_practice()` - Улучшаемся на основе практики

#### Task 1.4: Workflow интеграция
- [ ] Расширить `analytics-specialist/workflows/scenario_generation_workflow.py`
  - [ ] Добавить `level="system"` mode
  - [ ] Генерация системных сценариев

#### Task 1.5: EventBus subscribers (системный уровень)
- [ ] `analytics_integration_loader.py` → обработка `level="system"`
- [ ] `pattern_detector.py` → детекция системных паттернов
- [ ] `self_learning_engine.py` → обучение от практики
- [ ] `workflow_intelligence` → применение к СЕБЕ

#### Task 1.6: Тестирование Phase 1
- [ ] Запустить системный цикл end-to-end
- [ ] Проверить что платформа применила BIA к себе
- [ ] Проверить что приоритеты ресурсов настроены
- [ ] Проверить что recovery procedures работают
- [ ] **ГЛАВНОЕ:** Измерить что система стала УСТОЙЧИВЕЕ

---

### 🎯 PHASE 2: ПРОГРАММНЫЙ УРОВЕНЬ (После Phase 1)

**Цель:** Применяем те же модули для пользователей

#### Task 2.1: Доменные сценарии
- [ ] Создать `/learning-knowledge/scenarios/domain_scenarios/`
  - [ ] `healthcare_bia.json` - BIA для больниц
  - [ ] `finance_risk.json` - Risk для банков
  - [ ] ... миллион сценариев через AI

#### Task 2.2: Адаптация для пользователей
- [ ] Та же логика, другой target
- [ ] Интеграция с UI для пользователей
- [ ] Обучение пользователей на примере платформы

---

### 🔄 PHASE 3: ПОЛНЫЙ ЦИКЛ

#### Task 3.1: Virtuous Cycle
- [ ] Система практикует → учится → улучшается
- [ ] Пользователи видят пример → учатся → применяют
- [ ] Система учится от пользователей → улучшается
- [ ] ЦИКЛ ПОВТОРЯЕТСЯ ♻️

---

## ✅ КРИТЕРИИ УСПЕХА

### Phase 1 (Системный уровень):
- ✅ Платформа ПРИМЕНИЛА BIA к себе (приоритеты настроены)
- ✅ Recovery procedures РАБОТАЮТ (auto-restart при сбоях)
- ✅ Circuit breakers УСТАНОВЛЕНЫ (защита от перегрузки)
- ✅ Resource priorities ПРИМЕНЕНЫ (критичное защищено)
- ✅ Система УЧИТСЯ от практики (измеряем результаты)
- ✅ **ГЛАВНОЕ:** Платформа стала УСТОЙЧИВЕЕ (метрики улучшились)

### Phase 2 (Программный уровень):
- ✅ 570+ доменных сценариев сгенерированы
- ✅ Пользователи используют те же модули
- ✅ Обучение пользователей на примере платформы

### Phase 3 (Полный цикл):
- ✅ Virtuous cycle работает (система ↔ пользователи)
- ✅ Цикл повторяется автоматически
- ✅ ML модели обновляются
- ✅ Постоянное улучшение

---

## 🎯 КЛЮЧЕВЫЕ ПРИНЦИПЫ

1. **Применение на СЕБЕ первично**
   - Сначала платформа ЖИВЁТ BCM
   - Потом пользователи учатся у платформы

2. **Разделение уровней**
   - Системный (для себя) = Priority #1
   - Программный (для пользователей) = После системного

3. **Обучение через ПРАКТИКУ**
   - Не теория → а реальное применение
   - Измеряем результаты → улучшаемся

4. **Использование существующих модулей**
   - БЕЗ дублирования
   - ТЕ ЖЕ BIA/Risk/Planning для обоих уровней
   - Отличие только в target и scenarios

---

## 📊 TIMELINE

```
Week 1: Phase 1 (Системный)
├─ Day 1-2: Системные сценарии
├─ Day 3-4: Применение к СЕБЕ
├─ Day 5-6: Обучение от практики
└─ Day 7: Измерение результатов

Week 2: Phase 2 (Программный) - параллельно с Phase 1
├─ Доменные сценарии
├─ Адаптация для пользователей
└─ Интеграция

Week 3+: Phase 3 (Полный цикл)
└─ Virtuous cycle автоматизирован
```

---

**Результат:**

Платформа становится **самообучающейся системой**, которая:
1. **ЖИВЁТ** BCM на практике (применяет к себе)
2. **УЧИТСЯ** через практику (не теорию)
3. **СТАНОВИТСЯ ЭКСПЕРТОМ** в устойчивости
4. **ПОМОГАЕТ пользователям** применять ту же логику
5. **ПОСТОЯННО УЛУЧШАЕТСЯ** через virtuous cycle

**Используем:** ТОЛЬКО существующую архитектуру
- `analytics-specialist` = анализ и генерация сценариев
- `ai-foundation/learning-knowledge` = хранение знаний + обучение
- `platform-services` = BCM модули (BIA, Risk, Planning)
- `workflow_intelligence` = координация и применение
- `EventBus` = связь между всеми компонентами
