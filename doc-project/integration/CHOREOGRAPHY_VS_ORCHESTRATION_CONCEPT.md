# Choreography vs Orchestration в Event-Driven Architecture
## Концептуальная записка

**Дата:** 2025-10-09
**Контекст:** AI-Platform-ISO микросервисная архитектура
**Статус:** Концептуальная фаза (перед реализацией)

---

## 📋 Executive Summary

В процессе проектирования Event-Driven микросервисной архитектуры критически важно понимать **два фундаментальных подхода к управлению взаимодействием сервисов**:

1. **Orchestration (Оркестровка)** - централизованное управление workflow через orchestrator
2. **Choreography (Хореография)** - децентрализованное взаимодействие через события

**Ключевой вывод:** Не существует универсального "правильного" подхода. Для разных бизнес-процессов подходят разные паттерны. Оптимальная архитектура - **гибридная**.

---

## 🎼 1. Orchestration (Оркестровка)

### Концепция

**Центральный координатор** (orchestrator) явно управляет последовательностью вызовов сервисов.

```
                    ┌─────────────────┐
                    │  ORCHESTRATOR   │ ← Центральный мозг
                    │   (Дирижёр)     │
                    └────────┬────────┘
                             │
         ┌──────────────┬────┴────┬──────────────┐
         │              │         │              │
         ▼              ▼         ▼              ▼
    ┌────────┐    ┌────────┐ ┌────────┐    ┌────────┐
    │Service │    │Service │ │Service │    │Service │
    │   A    │    │   B    │ │   C    │    │   D    │
    └────────┘    └────────┘ └────────┘    └────────┘
```

### Характеристики

**Преимущества:**
- ✅ Централизованная логика - весь workflow в одном месте
- ✅ Легко понять поток выполнения целиком
- ✅ Простой debugging - один контроллер
- ✅ Гарантированный порядок выполнения
- ✅ Transactional consistency
- ✅ Простой audit trail для регуляторных требований

**Недостатки:**
- ❌ Single point of failure - если orchestrator упал, всё стоит
- ❌ Tight coupling - orchestrator знает о всех сервисах
- ❌ Сложно масштабировать - bottleneck на orchestrator
- ❌ Сложно добавлять новые сервисы - нужно менять orchestrator
- ❌ Cascading failures - ошибка в одном сервисе блокирует весь процесс

### Пример кода

```python
# ai-orchestration/bia_orchestrator.py

async def execute_bia_workflow(bia_id: str, org_id: str):
    """
    Orchestrator явно управляет всем процессом BIA.
    Знает о всех шагах и их последовательности.
    """

    # Шаг 1: Orchestrator вызывает Service A
    processes = await expertise_center.identify_processes(bia_id, org_id)
    if not processes:
        raise WorkflowError("No processes identified")

    # Шаг 2: Orchestrator вызывает Service B
    impact_analysis = await risk_analyst.assess_impact(processes)
    if impact_analysis.risk_level == "critical":
        # Orchestrator решает добавить шаг
        await compliance_officer.verify_regulatory_requirements(bia_id)

    # Шаг 3: Orchestrator вызывает Service C
    report = await report_generator.generate_bia_report(
        bia_id=bia_id,
        processes=processes,
        impact=impact_analysis
    )

    # Шаг 4: Orchestrator вызывает Service D
    await notification_service.notify_stakeholders(
        report_url=report.url,
        recipients=await get_stakeholders(org_id)
    )

    # Orchestrator отвечает за весь lifecycle
    return {
        "bia_id": bia_id,
        "status": "completed",
        "report_url": report.url,
        "duration": calculate_duration()
    }
```

### Когда использовать Orchestration

✅ **Используйте когда:**

1. **Сложная бизнес-логика с чётким порядком шагов**
   - Пример: BIA Process (10+ последовательных зависимых шагов)
   - Шаг B невозможен без завершения шага A

2. **Transactional consistency критична**
   - Пример: Финансовые транзакции
   - Все шаги должны выполниться или откатиться

3. **Regulatory compliance требует audit trail**
   - Пример: ISO 22301 mandatory processes
   - Нужно доказать регулятору последовательность действий

4. **Понятность flow важнее масштабируемости**
   - Пример: Critical onboarding процесс
   - Важнее не ошибиться, чем обработать 1M запросов/сек

5. **Условная логика и ветвление**
   - Если X, то делаем Y, иначе Z
   - Orchestrator может принимать решения на основе промежуточных результатов

---

## 💃 2. Choreography (Хореография)

### Концепция

**НЕТ центрального координатора.** Каждый сервис - автономный участник, который:
- Слушает интересующие его события
- Выполняет свою работу
- Публикует события о результатах
- НЕ знает о других сервисах

```
    ┌────────┐         ┌────────┐
    │Service │ events  │Service │
    │   A    │────────>│   B    │
    └────────┘         └───┬────┘
         ▲                 │ events
         │                 ▼
    ┌────┴────┐       ┌────────┐
    │Service  │<──────│Service │
    │   D     │events │   C    │
    └─────────┘       └────────┘

    Все общаются через EVENTS (EventBus)
```

### Характеристики

**Преимущества:**
- ✅ Decoupled - сервисы не знают друг о друге
- ✅ Легко добавлять новые сервисы - просто подписываешься на события
- ✅ Fault tolerance - если один упал, остальные продолжают работать
- ✅ Масштабируемость - нет bottleneck
- ✅ Параллельная обработка - несколько сервисов реагируют одновременно
- ✅ Evolution-friendly - можно менять сервисы независимо

**Недостатки:**
- ❌ Сложнее понять полный flow - логика распределена
- ❌ Сложнее debugить - нужны инструменты distributed tracing
- ❌ Eventual consistency - нет гарантии немедленного результата
- ❌ Риск циклических зависимостей событий
- ❌ Сложнее обеспечить transactional guarantees

### Пример кода

```python
# Service A: expertise-center/bia_specialist.py

async def start_bia(org_id: str) -> str:
    """
    BIA Specialist НЕ знает кто будет реагировать на событие.
    Просто делает свою работу и публикует факт.
    """
    bia_id = await self.create_bia(org_id)

    # Публикуем событие (не вызываем никого!)
    await publish_event("bcm.bia.started", {
        "bia_id": bia_id,
        "org_id": org_id,
        "timestamp": datetime.utcnow().isoformat()
    })

    return bia_id


# Service B: event_intelligence/event_subscribers.py

@subscribe_to("bcm.bia.started")
async def on_bia_started(event: Event):
    """
    Event Intelligence НЕ знает кто опубликовал событие.
    Просто реагирует на факт начала BIA.
    """
    bia_id = event.data["bia_id"]

    # Записываем в knowledge graph
    await knowledge_graph.add_node(
        node_type="bia_process",
        node_id=bia_id,
        properties=event.data
    )

    # Предсказываем длительность
    prediction = await predict_duration(event.data["org_id"])

    # Публикуем своё событие
    await publish_event("event_intelligence.prediction", {
        "bia_id": bia_id,
        "predicted_duration_hours": prediction
    })


# Service C: predictive/recommendations_engine.py

@subscribe_to("bcm.bia.started")
async def on_bia_started(event: Event):
    """
    Predictive Service тоже реагирует на то же событие.
    Работает ПАРАЛЛЕЛЬНО с event_intelligence.
    """
    recommendations = await generate_bia_recommendations(
        org_id=event.data["org_id"]
    )

    await publish_event("proactive.bia_recommendations", {
        "bia_id": event.data["bia_id"],
        "recommendations": recommendations
    })


# Service D: notification-service/handlers.py

@subscribe_to("proactive.bia_recommendations")
async def on_recommendations_ready(event: Event):
    """
    Notification Service реагирует на событие от predictive.
    НЕ знает что predictive существует.
    """
    await send_email(
        to=await get_user_email(event.data["bia_id"]),
        subject="Your BIA recommendations are ready",
        body=format_recommendations(event.data["recommendations"])
    )
```

### Когда использовать Choreography

✅ **Используйте когда:**

1. **Loose coupling критичен**
   - Пример: Event Intelligence учится от всех событий платформы
   - Новые сервисы появляются, старые уходят - Event Intelligence не должен меняться

2. **Масштабируемость важна**
   - Пример: Обработка миллионов событий от IoT устройств
   - Нужно горизонтально масштабировать обработку

3. **Новые функции добавляются часто**
   - Пример: Новый AI specialist хочет реагировать на события
   - Просто добавляет @subscribe_to, не меняя существующий код

4. **Fault tolerance критичен**
   - Пример: Один сервис упал, остальные продолжают работать
   - Система degraded, но не полностью down

5. **Независимые реакции на одно событие**
   - Пример: "bcm.bia.completed" → learning, notification, archiving, reporting
   - Все реакции независимы и параллельны

---

## 🎭 3. Hybrid Approach (Рекомендуемый)

### Концепция

**Лучшее из обоих миров:** Orchestration для критичных процессов + Choreography для side-effects и cross-cutting concerns.

```
┌──────────────────────────────────────────────────────────┐
│         AI-ORCHESTRATION (Orchestrator)                  │
│    Управляет критичными multi-step workflows             │
│    Пример: BIA Workflow с 10+ шагами                     │
└────────────────┬─────────────────────────────────────────┘
                 │
                 │ Commands + Events
                 ▼
┌──────────────────────────────────────────────────────────┐
│              EVENTBUS (Choreography Layer)               │
│    Все сервисы публикуют события о своих действиях       │
└────────────────┬─────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬────────────┐
    │            │            │            │
    ▼            ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│Event   │  │Workflow│  │Expert  │  │Predict │
│Intel   │  │Intel   │  │Center  │  │Service │
└────────┘  └────────┘  └────────┘  └────────┘
  (learns)   (indexes)   (assists)   (predicts)
```

### Пример: BIA Process (Hybrid)

**Orchestrated часть** (критичная бизнес-логика):

```python
# ai-orchestration/bia_orchestrator.py

async def execute_bia_workflow(bia_id: str, org_id: str):
    """
    Orchestrator координирует КРИТИЧНЫЕ шаги BIA.
    На каждом шаге публикует события для choreography.
    """

    # ============ ORCHESTRATED MAIN PATH ============

    # Шаг 1: Создать BIA (orchestrated)
    bia = await expertise_center.create_bia(bia_id, org_id)

    # ✅ Публикуем событие (choreography starts)
    await publish_event("bcm.bia.started", {
        "bia_id": bia_id,
        "org_id": org_id
    })

    # Шаг 2: Идентификация процессов (orchestrated)
    processes = await expertise_center.identify_processes(bia_id)

    # ✅ Публикуем событие
    await publish_event("bcm.bia.processes_identified", {
        "bia_id": bia_id,
        "process_count": len(processes)
    })

    # Шаг 3: Оценка воздействия (orchestrated)
    impact = await expertise_center.assess_impact(bia_id, processes)

    # ✅ Публикуем событие
    await publish_event("bcm.bia.impact_assessed", {
        "bia_id": bia_id,
        "critical_processes": impact.critical_count
    })

    # Шаг 4: Генерация отчёта (orchestrated)
    report = await expertise_center.generate_report(bia_id)

    # ✅ Публикуем событие
    await publish_event("bcm.bia.completed", {
        "bia_id": bia_id,
        "report_url": report.url,
        "duration_hours": calculate_duration()
    })

    return report
```

**Choreographed side-effects** (параллельные реакции):

```python
# event_intelligence - УЧИТСЯ от всех событий

@subscribe_to("bcm.bia.*")  # Все BIA события
async def learn_bia_patterns(event: Event):
    """Независимо от orchestrator, учимся от каждого события"""
    await pattern_learner.record(event)
    await knowledge_graph.update(event)
    logger.info(f"✅ Learned from: {event.type}")


# predictive - ПРЕДСКАЗЫВАЕТ на основе событий

@subscribe_to("bcm.bia.started")
async def predict_on_start(event: Event):
    """Независимо генерируем предсказания"""
    predictions = await predict_timeline(event.data["org_id"])
    await publish_event("proactive.bia_timeline_prediction", predictions)


@subscribe_to("bcm.bia.processes_identified")
async def predict_on_processes(event: Event):
    """Обновляем предсказания на основе реальных данных"""
    await update_predictions(event.data["bia_id"], event.data)


# workflow_intelligence - ИНДЕКСИРУЕТ кейсы

@subscribe_to("bcm.bia.completed")
async def index_completed_bia(event: Event):
    """Независимо добавляем в case library"""
    await case_library.add_case(
        module="bia",
        case_data=event.data
    )
    logger.info(f"✅ Indexed case: {event.data['bia_id']}")


# notification-service - УВЕДОМЛЯЕТ

@subscribe_to("bcm.bia.completed")
async def notify_on_completion(event: Event):
    """Независимо отправляем уведомления"""
    await send_email(
        to=await get_stakeholders(event.data["bia_id"]),
        subject=f"BIA {event.data['bia_id']} completed",
        body=f"Report available: {event.data['report_url']}"
    )


# community_intelligence - ДЕЛИТСЯ знаниями

@subscribe_to("bcm.bia.completed")
async def share_anonymized_case(event: Event):
    """Если одобрено - делимся с community"""
    if await check_sharing_consent(event.data["bia_id"]):
        anonymized = await anonymize_case(event.data)
        await publish_to_community(anonymized)
```

### Преимущества Hybrid

✅ **Best of both worlds:**

1. **Orchestrator** гарантирует корректность критичной бизнес-логики
2. **Choreography** обеспечивает гибкость и расширяемость
3. **События** создают audit trail для регуляторов
4. **Loose coupling** между orchestrator и observer services
5. **Параллельная обработка** side-effects (learning, notification, etc.)
6. **Fault tolerance** - если notification упал, BIA всё равно завершится

---

## 🎯 4. Практические рекомендации

### Decision Tree: Как выбрать подход

```
START
  │
  ├─> Есть чёткая последовательность ЗАВИСИМЫХ шагов?
  │   (Шаг B невозможен без завершения шага A)
  │   ├─> ДА → Нужна transactional consistency?
  │   │        ├─> ДА → ORCHESTRATION
  │   │        └─> НЕТ → HYBRID (orchestrate main, choreograph side-effects)
  │   └─> НЕТ → Продолжить
  │
  ├─> Несколько сервисов должны НЕЗАВИСИМО реагировать на событие?
  │   (Например, learning, notification, archiving)
  │   ├─> ДА → CHOREOGRAPHY
  │   └─> НЕТ → Продолжить
  │
  ├─> Новые функции будут добавляться часто?
  │   (Новые AI specialists, новые observers)
  │   ├─> ДА → CHOREOGRAPHY
  │   └─> НЕТ → Продолжить
  │
  ├─> Критична масштабируемость (1M+ events/sec)?
  │   ├─> ДА → CHOREOGRAPHY
  │   └─> НЕТ → ORCHESTRATION (если понятность важнее)
```

### Примеры из AI-Platform-ISO

#### ✅ Orchestration подходит для:

| Workflow | Причина |
|----------|---------|
| **BIA Complete Process** | 10+ зависимых последовательных шагов, regulatory audit trail |
| **Compliance Audit** | Строгая последовательность, ISO требования, transactional consistency |
| **Certification Process** | Формальный процесс с чёткими gates, документация для аудиторов |
| **Tabletop Exercise Execution** | Координация участников, чёткие фазы (prepare → execute → evaluate) |

#### ✅ Choreography подходит для:

| Workflow | Причина |
|----------|---------|
| **Event Learning** | Event Intelligence учится от всех событий, не влияя на источники |
| **Proactive Recommendations** | Predictive публикует - кто хочет, подписывается |
| **Auto-discovery** | Сервисы регистрируются при старте, независимо друг от друга |
| **Notifications** | Многие типы событий → email/SMS, без coupling к источникам |
| **Cross-service analytics** | Monitoring, metrics, logging реагируют на всё, невидимо для бизнес-логики |

#### ✅ Hybrid подходит для:

| Workflow | Orchestrated часть | Choreographed часть |
|----------|-------------------|---------------------|
| **Incident Response** | Create incident → Assign team → Track resolution | Learning, predictions, notifications, community sharing |
| **BIA Process** | Main BIA steps (identify → assess → report) | Learning, indexing, recommendations, notifications |
| **Exercise Execution** | Scenario coordination, inject delivery | Observer reactions, real-time learning, gap detection |

---

## 🚨 5. Критичная разница: Documentation vs Real Event Flow

### ⚠️ Проблема: "Fake Choreography"

**Часто встречается ситуация:**

✅ В документации написано: "Event-driven choreography"
✅ События публикуются: `await publish_event("bcm.bia.started")`
✅ Подписчики зарегистрированы: `@subscribe_to("bcm.bia.started")`

**НО в реальности:**

```python
# event_intelligence/event_subscribers.py

@subscribe_to("bcm.bia.started")
async def on_bia_started(event: Event):
    logger.info(f"📊 BIA Event: {event.type}")
    # ВСЁ! Только лог. Это STUB, не real handler!
```

❌ **Это НЕ Real Event Flow!** Это имитация choreography.

### ✅ Real Event Flow

**Real Event Flow** = События РЕАЛЬНО вызывают действия в системе, end-to-end:

```python
@subscribe_to("bcm.bia.started")
async def on_bia_started(event: Event):
    """РЕАЛЬНАЯ обработка события"""

    # 1. Записываем в knowledge graph
    await knowledge_graph.add_node(
        node_type="bia_process",
        node_id=event.data["bia_id"],
        properties=event.data
    )

    # 2. Обновляем ML patterns
    await pattern_learner.record_sequence(event)

    # 3. Генерируем predictions
    prediction = await predict_duration(event.data["org_id"])

    # 4. Публикуем prediction (downstream event)
    await publish_event("event_intelligence.prediction", {
        "bia_id": event.data["bia_id"],
        "predicted_duration": prediction
    })

    # 5. Логируем результат
    logger.info(f"✅ Processed BIA start: {event.data['bia_id']}")
```

**Признаки Real Event Flow:**

✅ Реальные действия (DB writes, API calls, calculations)
✅ Downstream события (опубликовано → обработано → опубликовано дальше)
✅ End-to-end тестируемость
✅ Measurable impact на систему

### Как проверить Real Event Flow

**Test 1: End-to-End Test**

```python
async def test_bia_real_flow():
    # 1. Создаём BIA
    response = await client.post("/api/bia/start", json={"org_id": "TEST"})
    bia_id = response.json()["bia_id"]

    await asyncio.sleep(2)  # Ждём обработку событий

    # 2. Проверяем что event_intelligence РЕАЛЬНО записал
    knowledge = await get_knowledge_graph()
    assert bia_id in knowledge.nodes  # ✅ Real action!

    # 3. Проверяем что predictive РЕАЛЬНО сгенерировал
    recommendations = await get_recommendations(bia_id)
    assert len(recommendations) > 0  # ✅ Real action!

    # 4. Проверяем что notification РЕАЛЬНО отправил
    emails = await get_sent_emails()
    assert any(bia_id in e.body for e in emails)  # ✅ Real action!
```

**Test 2: Event Tracing**

```python
async def trace_event(event_id: str):
    event = await get_event_from_redis(event_id)
    print(f"📤 Published: {event.type}")

    subscribers = await get_subscribers(event.type)
    print(f"📥 Subscribers: {len(subscribers)}")

    for sub in subscribers:
        actions = await get_service_actions(sub, event_id)
        if not actions:
            print(f"   ⚠️ {sub} - NO ACTIONS (stub?)")
        else:
            print(f"   ✅ {sub} - {len(actions)} ACTIONS")
```

---

## 📊 6. Roadmap для реализации

### Текущий статус (2025-10-09)

✅ **Готово:**
- EventBus 100% integration (13/13 services)
- 14 event subscriptions registered
- Events catalog (126 event types)
- Knowledge Library catalog (320+ flows)
- Architecture documentation

⚠️ **Частично:**
- События публикуются (только 7 calls - мало!)
- Event subscribers зарегистрированы (но большинство - stubs)

❌ **Не готово:**
- Real Event Flow (end-to-end)
- Choreographed workflows в production
- Orchestrators implementation

### Рекомендуемая последовательность

#### Фаза 1: Фундамент (СЕЙЧАС - 2 недели)

1. ✅ Закончить EventBus integration (DONE)
2. 🔄 Qdrant Vector DB integration (IN PROGRESS)
3. ⏳ Knowledge System полностью (RAG, embeddings, standards)
4. ⏳ Все сервисы "живые" (запускаются, health checks, базовые endpoints)

#### Фаза 2: Каталогизация (1 неделя)

1. ⏳ Создать `SERVICES_CATALOG.md`
   - Каждый из 13 сервисов
   - Capabilities, Dependencies, Events (pub/sub), APIs

2. ⏳ Создать `CHOREOGRAPHY_ORCHESTRATION_DISTRIBUTION.md`
   - Анализ всех 320+ flows из Knowledge Library
   - Решение: orchestrated/choreographed/hybrid для каждого
   - Приоритизация: Топ-20 критичных flows

#### Фаза 3: Первый Real Event Flow (Proof of Concept - 1 неделя)

**Цель:** Доказать что choreography работает end-to-end.

**Выбрать 1 flow:** BIA Process (самый важный)

**Реализовать:**
1. Добавить publish_event в expertise-center (5+ events по BIA lifecycle)
2. Реализовать real handlers в event_intelligence (не stubs!)
3. Реализовать real handlers в predictive
4. Реализовать real handlers в workflow_intelligence
5. Реализовать real handlers в notification-service
6. Создать end-to-end тест
7. Трейсинг событий через систему

**Success criteria:**
- ✅ User starts BIA → событие публикуется
- ✅ event_intelligence записывает в knowledge graph
- ✅ predictive генерирует recommendations
- ✅ notification отправляет email
- ✅ User completes BIA → событие публикуется
- ✅ workflow_intelligence индексирует в case library
- ✅ event_intelligence обновляет ML модель
- ✅ End-to-end тест проходит

#### Фаза 4: Orchestrator для BIA (1 неделя)

**Реализовать hybrid approach:**

1. Создать `ai-orchestration/bia_orchestrator.py`
2. Orchestrate критичные шаги BIA (identify → assess → report)
3. Publish events на каждом шаге
4. Choreography продолжает работать (learning, notification, etc.)
5. Тестировать end-to-end

#### Фаза 5: Масштабирование (4-6 недель)

1. Реализовать Топ-20 flows из приоритизации
2. Для каждого: решить orchestration/choreography/hybrid
3. Реализовать orchestrators где нужно
4. Реализовать choreographed reactions где нужно
5. End-to-end тесты для всех flows

---

## 🎓 7. Ключевые выводы

### Для архитекторов

1. **Нет универсального решения** - анализируйте каждый workflow отдельно
2. **Hybrid approach** оптимален для большинства enterprise систем
3. **Events как first-class citizens** - даже orchestrators публикуют события
4. **Real Event Flow важнее документации** - тестируйте end-to-end

### Для разработчиков

1. **Stubs недостаточно** - event handlers должны делать реальную работу
2. **Publish events щедро** - каждое важное действие = событие
3. **Idempotency обязательна** - события могут дублироваться
4. **Distributed tracing необходим** - без него не понять что происходит

### Для бизнеса

1. **Choreography = гибкость** - легко добавлять новые функции
2. **Orchestration = предсказуемость** - важно для compliance
3. **Hybrid = баланс** - контроль + гибкость
4. **Real Event Flow = value** - события должны работать, не просто существовать

---

## 📚 8. Дополнительные ресурсы

### Внутренняя документация

- `FINAL_UNIFIED_ARCHITECTURE_SPECIFICATION.md` - общая архитектура
- `COMPLETE_KNOWLEDGE_LIBRARY_CATALOG.md` - 320+ business flows
- `EVENT_BUS_COMPLETE_INTEGRATION.md` - EventBus integration details
- `infrastructure/eventbus/events/events_catalog.json` - 126 event types

### Код

- **EventBus:** `infrastructure/eventbus/` + `intelligent-core/shared/event_bus/`
- **Orchestration:** `intelligent-core/orchestration/ai-orchestration/`
- **Choreography:** `intelligent-core/event_intelligence/event_subscribers.py`
- **Event Publishers:** Search for `publish_event(` in codebase

### Следующие шаги

1. Закончить фундамент (Qdrant, Knowledge System)
2. Создать SERVICES_CATALOG.md
3. Создать CHOREOGRAPHY_ORCHESTRATION_DISTRIBUTION.md
4. Реализовать первый Real Event Flow для BIA
5. Масштабировать на остальные flows

---

**Конец записки**

*Этот документ будет обновляться по мере реализации и получения практического опыта.*
