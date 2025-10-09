# 🔄 PDCA Platform Integration Architecture

**Date**: 2025-10-09
**Status**: Complete Integration Map

---

## 🎯 КРАТКИЙ ОТВЕТ

PDCA Rules Engine **интегрирован со всей платформой** через:

1. **EventBus** - слушает события workflows
2. **Case Library** - берёт данные из прошлых кейсов
3. **Knowledge Base** - сохраняет lessons и patterns
4. **Predictive Engine** - использует предсказания для PLAN фазы
5. **PostgreSQL** - хранит cycle data
6. **AI Foundation** - использует RAG и LLM для recommendations

---

## 📊 ПОЛНАЯ АРХИТЕКТУРА ИНТЕГРАЦИИ

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            PLATFORM ECOSYSTEM                                 │
└──────────────────────────────────────────────────────────────────────────────┘
                                     ↓
                                 EventBus
                       (infrastructure/eventbus/)
                                     │
                    ┌────────────────┼────────────────┐
                    ↓                ↓                ↓
        [workflow.started]  [workflow.stage]  [workflow.completed]
                    │                │                │
                    └────────────────┼────────────────┘
                                     ↓
            ┌─────────────────────────────────────────────────┐
            │      PDCA Rules Engine (СЛУШАЕТ СОБЫТИЯ)        │
            │  workflow_intelligence/core/pdca_rules.py       │
            │                                                 │
            │  Подписки:                                      │
            │  • event_bus.subscribe("workflow.started")     │
            │  • event_bus.subscribe("workflow.stage.*")     │
            │  • event_bus.subscribe("workflow.completed")   │
            └─────────────────────────────────────────────────┘
                    │                │                │
          ┌─────────┴────────┐  ┌───┴────┐  ┌───────┴────────┐
          ↓                  ↓  ↓        ↓  ↓                ↓
      [PLAN]              [DO] │    [CHECK]│              [ACT]
                               │           │
                               ↓           ↓
            ┌──────────────────────────────────────────────────────┐
            │            DATA SOURCES (ОТКУДА БЕРЁТ)               │
            └──────────────────────────────────────────────────────┘
                    │                │                 │
         ┌──────────┴────┐    ┌─────┴──────┐   ┌─────┴──────────┐
         ↓               ↓    ↓            ↓   ↓                ↓
   Case Library   Knowledge  Predictive  Pattern     PostgreSQL
   (collective)     Base     Engine      Detector    (storage)
         │            │         │           │              │
         ↓            ↓         ↓           ↓              ↓
   Similar cases  Lessons   Forecasts   Patterns    Cycle history
   (anonymized)   Standards  Timelines   Success     Benchmarks
   k≥5 orgs       ISO/BCI    Risks       Anti-pat.   Metrics


            ┌──────────────────────────────────────────────────────┐
            │         DATA DESTINATIONS (КУДА ПУБЛИКУЕТ)           │
            └──────────────────────────────────────────────────────┘
                    │                │                 │
         ┌──────────┴────┐    ┌─────┴──────┐   ┌─────┴──────────┐
         ↓               ↓    ↓            ↓   ↓                ↓
   Knowledge Base  EventBus  PostgreSQL  Metrics      Predictive
   (rag/vector)    (events)  (cycles)    (Prometheus) Learning
         │            │         │           │              │
         ↓            ↓         ↓           ↓              ↓
   Lessons saved  pdca.plan  Benchmarks  Accuracy    Pattern storage
   Patterns       pdca.check Deviations  Duration    Forecast tuning
   Improvements   pdca.act   Quality     Success%    Timeline adjust


            ┌──────────────────────────────────────────────────────┐
            │         AI FOUNDATION (КАК ИСПОЛЬЗУЕТ)               │
            └──────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ↓                   ↓
              RAG Pipeline         LLM Router
              (retrieval)          (generation)
                    │                   │
         ┌──────────┴────┐    ┌─────────┴──────┐
         ↓               ↓    ↓                ↓
   Similar cases    Lessons  Generate      Predict
   Vector search    Context  Recommendations Outcomes
   Semantic match   Enrich   Next actions   Risks


            ┌──────────────────────────────────────────────────────┐
            │              КТО ВЛИЯЕТ НА PDCA                      │
            └──────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ↓                    ↓                    ↓
   Workflow Engine      Case Library      Predictive Engine
   (triggers cycles)   (quality data)    (predictions)
         │                    │                    │
         ↓                    ↓                    ↓
   workflow.started    find_cases()      predict_milestones()
   workflow.completed  success_rate≥0.8  upcoming_risks
   stage.changed       k-anonymity       timeline_forecast


            ┌──────────────────────────────────────────────────────┐
            │           КОМУ PDCA ПОДОТЧЁТНА                       │
            └──────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ↓                    ↓                    ↓
   Workflow Engine      Monitoring         Governance
   (context owner)      (observability)    (compliance)
         │                    │                    │
         ↓                    ↓                    ↓
   WorkflowContext     Prometheus          Audit trail
   get_context()       pdca_cycles_total   PDCACycleData
   gap analysis        accuracy_score      completed_cycles
```

---

## 🔍 ДЕТАЛЬНАЯ ИНТЕГРАЦИЯ ПО ФАЗАМ

### 📋 PLAN PHASE

```python
async def plan_workflow(workflow_id, module, workflow_data):
    """
    ГДЕ БЕРЁТ ДАННЫЕ:
    """

    # 1. Case Library - похожие прошлые workflows
    similar_cases = await case_library.find_cases(
        problem_type=module,
        min_success_rate=0.8,
        exclude_org_id=current_org,
        limit=10
    )
    # Источник: intelligent-core/collective/services/case_library.py
    # База: community_intelligence.case_contributions (PostgreSQL)
    # Критерий: k-anonymity (минимум 5 организаций)

    # 2. Knowledge Base - best practices и lessons
    knowledge = await knowledge_base.search(
        query=f"{module} best practices",
        sources=["standards", "lessons", "patterns"]
    )
    # Источник: intelligent-core/ai-foundation/learning-knowledge/
    # База: Qdrant (vector DB) + PostgreSQL
    # Данные: ISO/BCI/WHO standards, накопленные lessons

    # 3. Predictive Engine - прогнозы
    predictions = await predictive.predict_timeline(
        org_context=workflow_data.get("organization_context"),
        module=module
    )
    # Источник: intelligent-core/predictive/services/
    # ML модели: Temporal patterns, risk forecasts

    # 4. Pattern Detector - успешные паттерны
    success_patterns = await pattern_detector.get_patterns(
        module=module,
        pattern_type="success"
    )
    # Источник: intelligent-core/ai-foundation/learning-knowledge/

    """
    ЧТО СОЗДАЁТ:
    """

    # Создаёт PDCACycleData
    cycle = PDCACycleData(
        workflow_id=workflow_id,
        module=module,
        plan_data={
            "workflow_data": workflow_data,
            "expected_outcomes": predicted_outcomes,
            "estimated_duration": avg_duration_from_similar_cases
        },
        plan_recommendations=[
            "Based on 12 similar cases: Use stakeholder workshops",
            "ISO 22301 §8.2.2 recommends: Document dependencies",
            "Pattern detected: Organizations your size complete in 5 days"
        ]
    )

    """
    КУДА ПУБЛИКУЕТ:
    """

    # EventBus event
    await event_bus.publish(Event(
        event_type="pdca.plan.completed",
        data={
            "workflow_id": workflow_id,
            "recommendations_count": len(recommendations),
            "similar_cases_used": len(similar_cases)
        }
    ))

    # Metrics
    pdca_plan_recommendations_total.inc()
    pdca_plan_similar_cases.observe(len(similar_cases))
```

---

### ⚙️ DO PHASE

```python
async def track_execution(workflow_id, execution_data):
    """
    ГДЕ БЕРЁТ ДАННЫЕ:
    """

    # 1. Workflow Engine - текущее состояние
    workflow = await workflow_engine.get_context(workflow_id)
    # Источник: intelligent-core/workflow_intelligence/core/workflow_engine.py
    # Данные: current_stage, progress_percentage, gaps, issues

    # 2. Active cycle - PLAN data
    cycle = self.active_cycles.get(workflow_id)
    # In-memory state для быстрого доступа

    """
    ЧТО ДЕЛАЕТ:
    """

    # Обновляет DO data
    cycle.do_data = {
        **execution_data,
        "current_stage": workflow.current_stage,
        "progress": workflow.progress_percentage,
        "gaps_count": len(workflow.gaps),
        "issues_count": len(workflow.issues)
    }

    cycle.do_duration = (datetime.utcnow() - cycle.cycle_started_at).total_seconds()

    """
    КУДА ПУБЛИКУЕТ:
    """

    # EventBus (для мониторинга)
    await event_bus.publish(Event(
        event_type="pdca.do.progress",
        data={
            "workflow_id": workflow_id,
            "duration_so_far": cycle.do_duration,
            "progress": workflow.progress_percentage
        }
    ))

    # Metrics
    pdca_do_duration_seconds.set(cycle.do_duration)
    pdca_do_progress_percentage.set(workflow.progress_percentage)
```

---

### ✅ CHECK PHASE

```python
async def check_workflow(workflow_id, final_data):
    """
    ГДЕ БЕРЁТ ДАННЫЕ:
    """

    # 1. Cycle data - PLAN vs DO
    cycle = self.active_cycles.get(workflow_id)
    planned = cycle.plan_data
    actual = final_data

    # 2. Benchmarks - из истории
    benchmarks = await self._get_benchmarks(cycle.module, final_data)
    # Источник: self.completed_cycles (PostgreSQL в будущем)
    # Данные: avg_duration, min_duration, max_duration по модулю

    # 3. Quality standards - из Knowledge Base
    quality_criteria = await knowledge_base.get_quality_criteria(
        module=cycle.module
    )
    # ISO standards, best practices

    """
    ЧТО ДЕЛАЕТ:
    """

    # Находит отклонения
    deviations = []

    # Duration deviation
    if actual.duration > planned.estimated_duration * 1.2:
        deviations.append(
            f"Duration exceeded: {actual.duration}s vs {planned.estimated_duration}s"
        )

    # Quality deviation
    if actual.quality_score < quality_criteria.minimum:
        deviations.append(
            f"Quality below standard: {actual.quality_score} < {quality_criteria.minimum}"
        )

    # Benchmark comparison
    if actual.duration > benchmarks.avg_duration * 1.5:
        deviations.append(
            f"Slower than average: {actual.duration}s vs {benchmarks.avg_duration}s avg"
        )

    # Сохраняет CHECK data
    cycle.check_data = final_data
    cycle.deviations = deviations
    cycle.benchmarks = benchmarks

    # Рассчитывает score
    score = 100 - (len(deviations) * 10)  # -10 за каждое отклонение

    """
    КУДА ПУБЛИКУЕТ:
    """

    # EventBus
    await event_bus.publish(Event(
        event_type="pdca.check.completed",
        data={
            "workflow_id": workflow_id,
            "score": score,
            "deviations_count": len(deviations),
            "benchmark_comparison": {
                "vs_avg": actual.duration / benchmarks.avg_duration,
                "vs_best": actual.duration / benchmarks.min_duration
            }
        }
    ))

    # Metrics
    pdca_check_score.observe(score)
    pdca_check_deviations.observe(len(deviations))

    return {"deviations": deviations, "benchmarks": benchmarks, "score": score}
```

---

### 🎯 ACT PHASE

```python
async def complete_cycle(workflow_id):
    """
    ГДЕ БЕРЁТ ДАННЫЕ:
    """

    # 1. Complete cycle data
    cycle = self.active_cycles.pop(workflow_id)
    # PLAN, DO, CHECK data

    # 2. Pattern Detector - для извлечения lessons
    if self.pattern_detector:
        patterns = await self.pattern_detector.detect_patterns({
            "plan": cycle.plan_data,
            "do": cycle.do_data,
            "check": cycle.check_data
        })
    # Источник: intelligent-core/ai-foundation/learning-knowledge/
    # ML модели: Anomaly detection, success pattern recognition

    # 3. Recent cycles - для recurring issues
    recent_cycles = self.completed_cycles[-10:]
    # История для trend analysis

    """
    ЧТО ДЕЛАЕТ:
    """

    # Извлекает lessons
    lessons = []

    if cycle.deviations:
        for deviation in cycle.deviations:
            lessons.append(f"Issue found: {deviation}")
            lessons.append(f"Root cause: [analysis needed]")

    if not cycle.deviations:
        lessons.append("Workflow completed successfully with no deviations")
        lessons.append(f"Success pattern: {cycle.module}_optimal_flow")

    # Детектирует паттерны
    patterns = []

    # Успешный паттерн
    if len(cycle.deviations or []) == 0:
        patterns.append(f"{cycle.module}_success_pattern")

    # Повторяющиеся проблемы
    common_deviations = set()
    for c in recent_cycles:
        if c.module == cycle.module:
            for dev in (c.deviations or []):
                if dev in (cycle.deviations or []):
                    common_deviations.add(dev)

    if common_deviations:
        patterns.append(f"Recurring issue: {list(common_deviations)[0]}")

    # Предлагает улучшения
    improvements = []

    if cycle.deviations:
        improvements.append("Review and update estimated timelines")

    if cycle.do_duration > benchmarks.avg_duration * 1.5:
        improvements.append("Optimize workflow execution time")
        improvements.append(f"Target: Reduce by {((cycle.do_duration / benchmarks.avg_duration) - 1) * 100:.0f}%")

    # Сохраняет в cycle
    cycle.lessons_learned = lessons
    cycle.patterns_detected = patterns
    cycle.improvements = improvements
    cycle.cycle_completed_at = datetime.utcnow()

    """
    КУДА ПУБЛИКУЕТ/СОХРАНЯЕТ:
    """

    # 1. Архивирует в памяти
    self.completed_cycles.append(cycle)

    # 2. Knowledge Base - lessons и patterns
    if self.knowledge_base:
        await self.knowledge_base.save_lesson({
            "source": "workflow_pdca",
            "module": cycle.module,
            "lessons": lessons,
            "patterns": patterns,
            "improvements": improvements,
            "metadata": {
                "workflow_id": workflow_id,
                "duration": cycle.do_duration,
                "deviations_count": len(cycle.deviations or []),
                "score": cycle.check_data.get("score", 0)
            }
        })
    # Destination: ai-foundation/learning-knowledge/
    # Storage: Qdrant (vectors) + PostgreSQL (metadata)

    # 3. PostgreSQL - cycle history (для benchmarks)
    await postgres.save_pdca_cycle({
        "workflow_id": workflow_id,
        "module": cycle.module,
        "started_at": cycle.cycle_started_at,
        "completed_at": cycle.cycle_completed_at,
        "duration": cycle.do_duration,
        "deviations_count": len(cycle.deviations or []),
        "score": cycle.check_data.get("score", 0),
        "lessons_count": len(lessons),
        "patterns_count": len(patterns)
    })
    # Table: pdca_cycles (workflow_intelligence schema)

    # 4. Predictive Learning - feedback loop
    if self.predictive_engine:
        await self.predictive_engine.store_successful_prediction(
            org_context=cycle.plan_data.get("organization_context"),
            predicted_duration=cycle.plan_data.get("estimated_duration"),
            actual_duration=cycle.do_duration,
            accuracy=1.0 if not cycle.deviations else 0.7
        )
    # Destination: predictive/services/ai_foundation_integration.py
    # Updates ML models для лучших прогнозов

    # 5. EventBus - completion event
    await event_bus.publish(Event(
        event_type="pdca.act.completed",
        data={
            "workflow_id": workflow_id,
            "cycle_duration": cycle.do_duration,
            "lessons_count": len(lessons),
            "patterns_count": len(patterns),
            "improvements_count": len(improvements),
            "quality_score": cycle.check_data.get("score", 0)
        }
    ))

    # 6. Metrics (Prometheus)
    pdca_act_lessons_total.inc(len(lessons))
    pdca_act_patterns_total.inc(len(patterns))
    pdca_cycle_duration_seconds.observe(cycle.do_duration)
    pdca_cycle_quality_score.observe(cycle.check_data.get("score", 0))

    return {
        "lessons": lessons,
        "patterns": patterns,
        "improvements": improvements,
        "cycle_duration": cycle.do_duration
    }
```

---

## 🗄️ ХРАНЕНИЕ ДАННЫХ

### In-Memory (Runtime)
```python
class PDCARulesEngine:
    def __init__(self):
        # Активные циклы (в процессе выполнения)
        self.active_cycles: Dict[str, PDCACycleData] = {}

        # Завершённые циклы (последние 1000)
        self.completed_cycles: List[PDCACycleData] = []
        # LRU cache для быстрых benchmarks
```

### PostgreSQL (Persistent)
```sql
-- Table: workflow_intelligence.pdca_cycles
CREATE TABLE pdca_cycles (
    id UUID PRIMARY KEY,
    workflow_id VARCHAR NOT NULL,
    module VARCHAR NOT NULL,
    tenant_id UUID NOT NULL,

    -- Timing
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds FLOAT,

    -- PLAN phase
    plan_data JSONB,
    recommendations TEXT[],
    expected_outcomes JSONB,

    -- DO phase
    do_data JSONB,
    execution_events JSONB[],

    -- CHECK phase
    check_data JSONB,
    deviations TEXT[],
    benchmarks JSONB,
    quality_score FLOAT,

    -- ACT phase
    lessons_learned TEXT[],
    patterns_detected TEXT[],
    improvements TEXT[],

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),

    -- Indexes
    INDEX idx_module (module),
    INDEX idx_tenant (tenant_id),
    INDEX idx_completed (completed_at)
);
```

### Qdrant (Vector DB)
```python
# Lessons и patterns сохраняются как vectors
{
    "collection": "workflow_lessons",
    "vectors": embedding_of_lesson_text,
    "payload": {
        "lesson_text": "Based on 12 similar cases...",
        "source": "pdca_cycle",
        "module": "bia",
        "workflow_id": "wf-123",
        "quality_score": 95,
        "patterns": ["success_pattern", "optimal_flow"]
    }
}
```

---

## 📡 EVENT FLOW

### События которые слушает PDCA:

```python
# 1. Workflow Started
event_bus.subscribe("workflow.started")
→ Triggers: plan_workflow()
→ Source: workflow_intelligence/core/workflow_engine.py:271

# 2. Stage Changed
event_bus.subscribe("workflow.stage.changed")
→ Triggers: track_execution()
→ Source: workflow_intelligence/core/workflow_engine.py:363

# 3. Workflow Completed
event_bus.subscribe("workflow.completed")
→ Triggers: check_workflow() + complete_cycle()
→ Source: workflow_intelligence/core/workflow_engine.py:399
```

### События которые публикует PDCA:

```python
# 1. Plan completed
Event(event_type="pdca.plan.completed", data={...})
→ Consumers: Monitoring, Analytics

# 2. Do progress
Event(event_type="pdca.do.progress", data={...})
→ Consumers: Real-time dashboards

# 3. Check completed
Event(event_type="pdca.check.completed", data={...})
→ Consumers: Quality monitoring, Alerts

# 4. Act completed
Event(event_type="pdca.act.completed", data={...})
→ Consumers: Knowledge Base, Predictive Learning, Metrics
```

---

## 🎯 ВЛИЯНИЕ НА PDCA

### 1. Workflow Engine (Основной триггер)
```python
# Location: workflow_intelligence/core/workflow_engine.py
class WorkflowEngine:
    async def start(self, workflow_id, initial_data):
        # ... create workflow ...

        # Публикует событие → PDCA начинает PLAN
        await self.event_bus.publish(WorkflowEvent(
            event_type=f"{self.module}.workflow.started",
            workflow_id=workflow_id,
            data={"initial_state": ...}
        ))
```

**Влияние**: Запускает PDCA cycle, определяет module и workflow_id

---

### 2. Case Library (Качество данных)
```python
# Location: collective/services/case_library.py
class CaseLibrary:
    async def find_cases(self, problem_type, min_success_rate=0.8):
        # k-anonymity: минимум 5 организаций
        # success_rate >= 0.8
        # quality_score >= 7.0

        return anonymized_cases
```

**Влияние**:
- Качество recommendations зависит от качества cases
- k-anonymity ≥ 5 → более надёжные паттерны
- success_rate ≥ 0.8 → только проверенные подходы

---

### 3. Predictive Engine (Прогнозы)
```python
# Location: predictive/services/ai_foundation_integration.py
class PredictiveAIFoundation:
    async def retrieve_similar_journeys(self, org_context, current_milestone):
        # RAG retrieval + ML predictions
        return {
            "predicted_timeline": ...,
            "upcoming_risks": ...,
            "resource_needs": ...
        }
```

**Влияние**:
- PLAN phase использует predictions для expected_outcomes
- Точность прогнозов → точность планирования
- Улучшается через feedback loop в ACT phase

---

### 4. Pattern Detector (ML Intelligence)
```python
# Location: ai-foundation/learning-knowledge/learning/engines/pattern_detector.py
class PatternDetector:
    async def detect_patterns(self, cycle_data):
        # Anomaly detection
        # Success pattern recognition
        # Trend analysis

        return patterns
```

**Влияние**:
- ACT phase использует для извлечения lessons
- Автоматически находит recurring issues
- Обучается на каждом цикле

---

## 📊 ПОДОТЧЁТНОСТЬ PDCA

### 1. Workflow Engine (Владелец контекста)
```python
# PDCA запрашивает контекст у Workflow Engine
context = await workflow_engine.get_context(workflow_id)

# Context включает:
# - current_stage, progress_percentage
# - gaps (что не хватает)
# - issues (проблемы)
# - available_actions
# - can_proceed_to_next_stage
```

**Подотчётность**: PDCA не может изменять workflow state, только анализировать

---

### 2. Monitoring (Observability)
```python
# Prometheus metrics
pdca_cycles_total = Counter("pdca_cycles_total", ["module", "status"])
pdca_cycle_duration_seconds = Histogram("pdca_cycle_duration_seconds", ["module"])
pdca_cycle_quality_score = Histogram("pdca_cycle_quality_score", ["module"])
pdca_deviations_total = Counter("pdca_deviations_total", ["module", "deviation_type"])
pdca_lessons_learned_total = Counter("pdca_lessons_learned_total", ["module"])
```

**Подотчётность**: Все действия PDCA логируются и мониторятся

---

### 3. Governance (Compliance)
```python
# Audit trail
{
    "audit_event": "pdca.cycle.completed",
    "workflow_id": "wf-123",
    "module": "bia",
    "tenant_id": "tenant-456",
    "timestamp": "2025-10-09T10:30:00Z",
    "data": {
        "duration": 3600,
        "deviations": 2,
        "lessons": 5,
        "quality_score": 85
    }
}
```

**Подотчётность**: Полный audit trail для compliance (ISO 22301, SOC2)

---

## 🔄 РЕАКЦИЯ НА СОСТОЯНИЯ

### Workflow State Changes

```python
# ПЛАН: workflow = "started"
@event_bus.subscribe("workflow.started")
async def on_workflow_started(event):
    # PDCA реагирует: начинает PLAN phase
    await pdca_rules.plan_workflow(
        workflow_id=event.workflow_id,
        module=event.module,
        workflow_data=event.data
    )

    # Возвращает recommendations пользователю
    # "Based on 12 similar cases: Use workshops"

# ВЫПОЛНЕНИЕ: workflow = "in_progress"
@event_bus.subscribe("workflow.stage.changed")
async def on_stage_changed(event):
    # PDCA реагирует: обновляет DO phase
    await pdca_rules.track_execution(
        workflow_id=event.workflow_id,
        execution_data={
            "stage": event.data.to_state,
            "progress": event.data.progress
        }
    )

    # Мониторит прогресс vs план

# ЗАВЕРШЕНИЕ: workflow = "completed"
@event_bus.subscribe("workflow.completed")
async def on_workflow_completed(event):
    # PDCA реагирует: CHECK + ACT phases

    # CHECK: Validation
    check_result = await pdca_rules.check_workflow(
        workflow_id=event.workflow_id,
        final_data=event.data
    )
    # Находит deviations, сравнивает с benchmarks

    # ACT: Learning
    lessons = await pdca_rules.complete_cycle(
        workflow_id=event.workflow_id
    )
    # Извлекает lessons, сохраняет в Knowledge Base
```

### Quality Thresholds

```python
# НИЗКИЙ SCORE: score < 70
if check_result.score < 70:
    # Публикует alert event
    await event_bus.publish(Event(
        event_type="pdca.quality.low",
        data={"workflow_id": workflow_id, "score": check_result.score}
    ))

    # Consumers: Alerting system, Team notifications

# МНОГО DEVIATIONS: deviations > 5
if len(deviations) > 5:
    # Публикует event для root cause analysis
    await event_bus.publish(Event(
        event_type="pdca.deviations.high",
        data={"workflow_id": workflow_id, "deviations": deviations}
    ))

    # Triggers: AI-powered RCA analysis

# УСПЕХ: score >= 90
if check_result.score >= 90:
    # Сохраняет как success pattern
    await knowledge_base.save_success_pattern({
        "module": cycle.module,
        "approach": cycle.do_data,
        "score": check_result.score
    })
```

---

## 🔗 СВЯЗЬ С PREDICTIVE MODULE

### 1. PLAN Phase → Predictive Input

```python
# PDCA использует Predictive для планирования
async def plan_workflow(workflow_id, module, workflow_data):
    # Запрашивает прогноз
    predictions = await predictive_engine.predict_timeline(
        org_context=workflow_data.get("organization_context"),
        module=module,
        current_state="initial"
    )

    # Predictive возвращает:
    {
        "estimated_duration": 14400,  # seconds
        "upcoming_milestones": [
            {"name": "stakeholder_interviews", "eta_days": 2},
            {"name": "dependency_mapping", "eta_days": 5}
        ],
        "potential_risks": [
            "Limited stakeholder availability",
            "Complex supply chain"
        ],
        "confidence": 0.85
    }

    # PDCA использует для expected_outcomes
    cycle.plan_data["expected_outcomes"] = predictions
```

### 2. ACT Phase → Predictive Feedback

```python
# PDCA обучает Predictive модель
async def complete_cycle(workflow_id):
    # ... extract lessons ...

    # Отправляет feedback в Predictive
    if self.predictive_engine:
        await self.predictive_engine.store_successful_prediction(
            org_context=cycle.plan_data.get("organization_context"),
            predicted_milestone="dependency_mapping",
            actual_milestone="dependency_mapping",  # Совпало!
            predicted_duration=14400,
            actual_duration=cycle.do_duration,
            accuracy=_calculate_accuracy(predicted, actual)
        )

    # Predictive сохраняет в RAG для обучения
    # Future predictions станут точнее!
```

### 3. Continuous Improvement Loop

```
┌─────────────────────────────────────────────┐
│         PDCA ↔ Predictive Loop              │
└─────────────────────────────────────────────┘

Day 1: PDCA PLAN
├── Predictive: "Based on 50 cases, duration = 4h"
└── User starts workflow

Day 1: PDCA DO
├── Tracks: Actual progress
└── Real-time comparison vs prediction

Day 1: PDCA CHECK
├── Result: Actual duration = 3.5h
└── Deviation: -12% (faster than predicted!)

Day 1: PDCA ACT
├── Lesson: "Workshop method faster for small orgs"
└── → Sends to Predictive

Day 2: Predictive Learning
├── Updates ML model
├── New prediction for similar org: 3.5h
└── Accuracy improved: 85% → 90%

Day 7: PDCA PLAN (new workflow)
├── Predictive: "Based on 51 cases, duration = 3.5h"
└── More accurate prediction! ✅

RESULT: Сетевой эффект - каждый workflow улучшает predictions
```

---

## 🔗 СВЯЗЬ С LEARNING MODULE

### 1. Knowledge Base Integration

```python
# PDCA читает из Knowledge Base (PLAN)
async def plan_workflow(workflow_id, module, workflow_data):
    # Semantic search в Knowledge Base
    knowledge = await knowledge_base.search(
        query=f"{module} best practices ISO 22301",
        sources=["standards", "lessons", "patterns"],
        top_k=5
    )

    # Knowledge Base возвращает:
    [
        {
            "source": "iso_22301",
            "section": "8.2.2",
            "content": "BIA should identify critical processes...",
            "relevance": 0.95
        },
        {
            "source": "lesson",
            "text": "Organizations with workshop approach succeed 90%",
            "metadata": {"from_cases": 25, "avg_score": 88},
            "relevance": 0.87
        }
    ]

    # PDCA использует для recommendations
    recommendations.append(
        f"ISO 22301 §8.2.2: {knowledge[0].content}"
    )

# PDCA пишет в Knowledge Base (ACT)
async def complete_cycle(workflow_id):
    # Сохраняет lessons
    await knowledge_base.save_lesson({
        "source": "workflow_pdca",
        "module": cycle.module,
        "lesson_text": "Workshop method effective for orgs < 100 employees",
        "evidence": {
            "from_workflow": workflow_id,
            "duration": cycle.do_duration,
            "quality_score": 95,
            "deviations": 0
        },
        "patterns": ["small_org_success", "workshop_method"],
        "metadata": {
            "org_size": "small",
            "industry": "healthcare",
            "success": True
        }
    })

    # Сохраняется в:
    # - Qdrant (vector embedding для semantic search)
    # - PostgreSQL (metadata для filtering)
```

### 2. Pattern Detection Integration

```python
# Pattern Detector анализирует PDCA cycles
class PatternDetector:
    async def detect_patterns(self, pdca_cycle_data):
        """
        Анализирует PLAN → DO → CHECK data
        """

        # Success patterns
        if pdca_cycle_data["deviations_count"] == 0:
            return {
                "pattern_type": "success",
                "pattern_name": f"{pdca_cycle_data['module']}_optimal_flow",
                "characteristics": {
                    "approach": pdca_cycle_data["plan"]["recommendations"][0],
                    "duration": pdca_cycle_data["do_duration"],
                    "org_context": pdca_cycle_data["org_context"]
                },
                "confidence": 0.9
            }

        # Failure patterns
        if pdca_cycle_data["deviations_count"] > 3:
            return {
                "pattern_type": "anti_pattern",
                "root_cause": _analyze_root_cause(pdca_cycle_data["deviations"]),
                "recommendation": "Avoid this approach for similar contexts"
            }

        # Trend patterns
        recent_cycles = get_recent_cycles(module=pdca_cycle_data["module"], limit=10)
        if _detect_trend(recent_cycles):
            return {
                "pattern_type": "trend",
                "trend": "duration_increasing",
                "alert": "Module complexity growing - review process"
            }

# PDCA использует Pattern Detector в ACT phase
async def complete_cycle(workflow_id):
    patterns = await pattern_detector.detect_patterns({
        "plan": cycle.plan_data,
        "do": cycle.do_data,
        "check": cycle.check_data,
        "deviations_count": len(cycle.deviations),
        "module": cycle.module
    })

    cycle.patterns_detected = patterns
```

### 3. Competency Tracking Integration

```python
# Learning System отслеживает competency через PDCA
class CompetencyTracker:
    async def update_from_pdca(self, pdca_cycle):
        """
        Обновляет competency пользователя на основе PDCA results
        """

        user_id = pdca_cycle.metadata.get("user_id")
        module = pdca_cycle.module

        # Quality score → Competency level
        if pdca_cycle.quality_score >= 90:
            await self.increase_competency(
                user_id=user_id,
                skill=f"{module}_expert",
                points=10
            )
        elif pdca_cycle.quality_score >= 70:
            await self.increase_competency(
                user_id=user_id,
                skill=f"{module}_proficient",
                points=5
            )

        # No deviations → Badge
        if len(pdca_cycle.deviations) == 0:
            await self.award_badge(
                user_id=user_id,
                badge=f"{module}_flawless_execution"
            )

        # Gamification event
        await event_bus.publish(Event(
            event_type="competency.updated",
            data={
                "user_id": user_id,
                "module": module,
                "new_level": "expert"
            }
        ))
```

### 4. Cross-Learning (AI ↔ Human)

```python
# PDCA создаёт training materials из patterns
class ArticleCreator:
    async def create_from_pdca_pattern(self, pattern_id):
        """
        Автоматически создаёт обучающую статью из PDCA pattern
        """

        # Получить pattern data
        pattern = await pattern_detector.get_pattern(pattern_id)

        # Pattern пример:
        {
            "pattern_type": "success",
            "pattern_name": "bia_workshop_small_org",
            "characteristics": {
                "approach": "Stakeholder workshops",
                "duration": 3.5h,
                "org_size": "small",
                "quality_score": 95
            },
            "from_pdca_cycles": [
                {"workflow_id": "wf-123", "score": 95},
                {"workflow_id": "wf-234", "score": 92},
                {"workflow_id": "wf-345", "score": 97}
            ],
            "confidence": 0.9
        }

        # LLM генерирует статью
        article = await llm_router.generate(
            prompt=f"""
            Create a best practice article from this success pattern:

            Pattern: {pattern.pattern_name}
            Success Rate: {len(pattern.from_pdca_cycles)} workflows, avg score {avg_score}
            Approach: {pattern.characteristics.approach}
            Context: {pattern.characteristics.org_size} organizations

            Write a practical guide for other users.
            """,
            temperature=0.7,
            max_tokens=1500
        )

        # Сохраняет в Knowledge Base
        await knowledge_base.save_article({
            "title": f"Best Practice: {pattern.pattern_name}",
            "content": article,
            "source": "ai_generated_from_pdca",
            "evidence": pattern.from_pdca_cycles,
            "tags": [pattern.pattern_type, pattern.module],
            "metadata": {
                "pattern_id": pattern_id,
                "confidence": pattern.confidence,
                "generated_at": datetime.utcnow()
            }
        })

        # Теперь другие users найдут эту статью через search!
        # Human learns from AI analysis of PDCA cycles

# Virtuous cycle:
# 1. Users complete workflows → PDCA cycles
# 2. Pattern Detector finds success patterns
# 3. Article Creator makes training material
# 4. Other users learn from article
# 5. More users succeed → Better patterns
# 6. Platform gets smarter ♻️
```

---

## 📈 МЕТРИКИ И OBSERVABILITY

### Prometheus Metrics

```python
# PDCA cycle metrics
pdca_cycles_total = Counter(
    "pdca_cycles_total",
    "Total PDCA cycles",
    ["module", "status"]  # status: completed, failed, timeout
)

pdca_cycle_duration_seconds = Histogram(
    "pdca_cycle_duration_seconds",
    "PDCA cycle duration",
    ["module"],
    buckets=[60, 300, 900, 1800, 3600, 7200, 14400]  # 1m to 4h
)

pdca_cycle_quality_score = Histogram(
    "pdca_cycle_quality_score",
    "PDCA cycle quality score",
    ["module"],
    buckets=[0, 50, 70, 80, 90, 95, 100]
)

# Phase-specific metrics
pdca_plan_similar_cases = Histogram(
    "pdca_plan_similar_cases",
    "Similar cases found in PLAN phase",
    buckets=[0, 1, 3, 5, 10, 20]
)

pdca_check_deviations = Histogram(
    "pdca_check_deviations",
    "Deviations found in CHECK phase",
    ["module", "deviation_type"]
)

pdca_act_lessons_total = Counter(
    "pdca_act_lessons_total",
    "Lessons learned in ACT phase",
    ["module"]
)

# Integration metrics
pdca_knowledge_base_saves = Counter(
    "pdca_knowledge_base_saves",
    "Items saved to Knowledge Base"
)

pdca_predictive_accuracy = Gauge(
    "pdca_predictive_accuracy",
    "Prediction accuracy from feedback loop",
    ["module"]
)
```

### Grafana Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│               PDCA LIVING SYSTEM DASHBOARD                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Overview (Last 24h)                                     │
│  ├── Total Cycles: 847                                      │
│  ├── Avg Duration: 2.3h                                     │
│  ├── Avg Quality Score: 87                                  │
│  └── Lessons Learned: 1,294                                 │
│                                                             │
│  🔄 Cycle Distribution                                      │
│  [Graph: Cycles by module - BIA 45%, Risk 30%, Planning 25%]│
│                                                             │
│  ⏱️  Duration Trends                                        │
│  [Graph: Average duration decreasing over time - Learning!] │
│                                                             │
│  ✅ Quality Trends                                          │
│  [Graph: Quality score increasing - Platform getting better]│
│                                                             │
│  📚 Knowledge Growth                                        │
│  ├── Lessons in KB: 15,847                                  │
│  ├── Patterns Detected: 234                                 │
│  ├── Success Patterns: 189                                  │
│  └── Anti-patterns: 45                                      │
│                                                             │
│  🎯 Predictive Accuracy                                     │
│  ├── Duration Predictions: 88% accurate (±10%)              │
│  ├── Timeline Predictions: 91% accurate                     │
│  └── Risk Predictions: 85% accurate                         │
│                                                             │
│  🚨 Alerts                                                  │
│  ├── 3 workflows with quality < 70                          │
│  ├── 1 recurring deviation pattern detected                 │
│  └── 0 critical issues                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ SUMMARY

PDCA Rules Engine полностью интегрирован в платформу:

### ОТКУДА БЕРЁТ ДАННЫЕ:
1. **EventBus** - workflow события (started, stage, completed)
2. **Case Library** - похожие прошлые workflows (k≥5, success≥0.8)
3. **Knowledge Base** - standards, lessons, patterns (ISO/BCI/WHO)
4. **Predictive Engine** - timeline forecasts, risk predictions
5. **Pattern Detector** - success/failure patterns, trends
6. **Workflow Engine** - context, gaps, issues, progress

### КУДА ПУБЛИКУЕТ/СОХРАНЯЕТ:
1. **EventBus** - pdca.plan/do/check/act events
2. **Knowledge Base** - lessons, patterns, improvements (Qdrant + PostgreSQL)
3. **PostgreSQL** - cycle history, benchmarks, metadata
4. **Prometheus** - metrics для monitoring
5. **Predictive Learning** - feedback для ML models

### КОГО СЛУШАЕТ:
1. **workflow.started** → plan_workflow()
2. **workflow.stage.changed** → track_execution()
3. **workflow.completed** → check_workflow() + complete_cycle()

### КОМУ ПОДОТЧЁТНА:
1. **Workflow Engine** - не может изменять state, только анализировать
2. **Monitoring** - все действия логируются (Prometheus + Grafana)
3. **Governance** - полный audit trail для compliance

### КТО МОЖЕТ ВЛИЯТЬ:
1. **Workflow Engine** - запускает/завершает cycles
2. **Case Library** - качество данных → качество recommendations
3. **Predictive Engine** - точность прогнозов → точность планирования
4. **Pattern Detector** - ML insights → извлечение lessons

### КАК РЕАГИРУЕТ НА СОСТОЯНИЯ:
- **workflow=started** → PLAN phase (recommendations)
- **workflow=in_progress** → DO phase (tracking)
- **workflow=completed** → CHECK+ACT phases (validation+learning)
- **score<70** → Alert event
- **deviations>5** → Root cause analysis
- **score≥90** → Save success pattern

### СВЯЗЬ С PREDICTIVE:
- **PLAN** → использует predictions
- **ACT** → обучает predictive models
- **Loop** → каждый cycle улучшает accuracy

### СВЯЗЬ С LEARNING:
- **Читает** → standards, lessons, patterns
- **Пишет** → новые lessons и patterns
- **Обучает** → competency tracking, badges
- **Создаёт** → training materials из patterns

---

**РЕЗУЛЬТАТ**: Живая самообучающаяся система где каждый workflow делает платформу умнее! 🌱
