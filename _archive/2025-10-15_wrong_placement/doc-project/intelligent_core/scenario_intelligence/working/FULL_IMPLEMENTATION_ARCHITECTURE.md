# ПОЛНАЯ АРХИТЕКТУРА РЕАЛИЗАЦИИ SCENARIO INTELLIGENCE

## 🎯 ЦЕЛЬ: Полная картина как это работает в системе

---

## 1. 🏗️ АРХИТЕКТУРНАЯ РАССТАНОВКА В СИСТЕМЕ

### **Где живет Scenario Intelligence в intelligent-core:**

```
intelligent-core/
│
├─ scenario-intelligence/              # 🆕 НОВЫЙ СЛОЙ (верхний уровень!)
│  │
│  │  ┌─────────────────────────────────────────────────┐
│  │  │   SCENARIO INTELLIGENCE LAYER                   │
│  │  │  (Самый верхний уровень координации)            │
│  │  └─────────────────────────────────────────────────┘
│  │                         ↓
│  ├─ engines/              # Движки исполнения
│  │  ├─ scenario_engine.py           # Главный оркестратор
│  │  ├─ call_engine.py               # BPMN Call Activity
│  │  ├─ event_engine.py              # Event Storming Events
│  │  ├─ chaos_engine.py              # Netflix Chaos
│  │  └─ compliance_engine.py         # ISO compliance checks
│  │
│  ├─ storage/             # Хранилище сценариев
│  │  ├─ file_storage.py              # Файловое (git)
│  │  ├─ rag_storage.py               # RAG (Qdrant) - поиск
│  │  ├─ versioning.py                # Semantic versioning
│  │  └─ registry.py                  # Scenario Registry (индекс)
│  │
│  ├─ learning/            # Обучение и предсказания
│  │  ├─ scenario_learner.py          # Учится на выполнении
│  │  ├─ pattern_detector.py          # Находит паттерны
│  │  ├─ predictor.py                 # Предсказывает нужные сценарии
│  │  └─ auto_generator.py            # Генерирует новые сценарии
│  │
│  ├─ integration/         # Интеграция с intelligent-core
│  │  ├─ ai_orchestrator_adapter.py   # ↔ AI Orchestrator
│  │  ├─ rag_adapter.py               # ↔ RAG (Qdrant)
│  │  ├─ knowledge_adapter.py         # ↔ Knowledge Base
│  │  └─ expertise_adapter.py         # ↔ Domain Expertise
│  │
│  └─ api/                 # API endpoints
│     └─ api.py
│
├─ orchestration/
│  └─ ai-orchestration/    # ⬆️ ИСПОЛЬЗУЕТ Scenario Intelligence
│     └─ orchestrator.py   # Теперь использует сценарии!
│
├─ ai-foundation/
│  ├─ rag/                 # ⬆️ Хранит сценарии в векторах
│  ├─ learning-knowledge/  # ⬆️ Учится на сценариях
│  └─ llm/                 # ⬆️ Генерирует сценарии
│
└─ domain-expertise/       # ⬆️ Добавляет экспертизу в сценарии
```

### **Позиционирование в системе:**

```
┌─────────────────────────────────────────────────────┐
│          SCENARIO INTELLIGENCE                       │
│     (Самый ВЕРХНИЙ слой координации)                │
│                                                       │
│  "Знает КАК должна работать вся система"            │
│  "Оркестрирует все компоненты через сценарии"       │
└─────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴─────────────────┐
        ↓                                   ↓
┌──────────────────┐            ┌─────────────────────┐
│  AI Orchestrator │            │  Platform Services  │
│                  │            │                     │
│ Использует       │            │ Используют          │
│ сценарии для     │            │ сценарии для        │
│ AI решений       │            │ бизнес-процессов    │
└──────────────────┘            └─────────────────────┘
        ↓                                   ↓
┌──────────────────────────────────────────────────────┐
│           AI FOUNDATION                               │
│  ├─ RAG (хранит сценарии)                            │
│  ├─ LLM (генерирует сценарии)                        │
│  └─ Knowledge (дает контекст для сценариев)          │
└──────────────────────────────────────────────────────┘
```

**КЛЮЧЕВАЯ ИДЕЯ:**
- Scenario Intelligence = **МОЗГ СИСТЕМЫ**
- Знает КАК должны работать ВСЕ компоненты
- Оркестрирует их через сценарии

---

## 2. ⚙️ ДВИЖКИ ИСПОЛНЕНИЯ (Engines)

### **A) Главный Scenario Engine (оркестратор)**

```python
# scenario-intelligence/engines/scenario_engine.py

from typing import Dict, Any, Optional
import asyncio
from .call_engine import CallEngine
from .event_engine import EventEngine
from .chaos_engine import ChaosEngine
from .compliance_engine import ComplianceEngine

class ScenarioEngine:
    """
    Главный движок - оркестрирует все остальные движки
    """

    def __init__(self):
        # Подчиненные движки
        self.call_engine = CallEngine()           # BPMN Call Activity
        self.event_engine = EventEngine()         # Event-driven
        self.chaos_engine = ChaosEngine()         # Chaos experiments
        self.compliance_engine = ComplianceEngine() # Compliance checks

        # Интеграции
        from integration.ai_orchestrator_adapter import AIAdapter
        from integration.rag_adapter import RAGAdapter

        self.ai = AIAdapter()
        self.rag = RAGAdapter()

    async def execute_scenario(
        self,
        scenario: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Главный метод - исполняет сценарий любого типа/уровня
        """

        context = context or {}
        scenario_meta = scenario.get('meta', {})
        scenario_type = scenario_meta.get('type')
        scenario_level = scenario_meta.get('level')

        print(f"🎬 Executing: {scenario_meta.get('id')} (L{scenario_level}, {scenario_type})")

        # 1. Выполнить шаги сценария
        execution_result = await self._execute_steps(scenario, context)

        # 2. Обработать Call Activity (синхронные вызовы)
        if 'integration' in scenario and 'calls' in scenario['integration']:
            call_results = await self.call_engine.execute_calls(
                scenario['integration']['calls'],
                context
            )
            execution_result['call_results'] = call_results

        # 3. Обработать Events (асинхронные)
        if 'integration' in scenario and 'events' in scenario['integration']:
            await self.event_engine.emit_events(
                scenario['integration']['events']['emits'],
                context
            )

        # 4. Если это chaos сценарий - запустить chaos engine
        if 'chaos' in scenario:
            chaos_result = await self.chaos_engine.execute_chaos(
                scenario['chaos'],
                context
            )
            execution_result['chaos_result'] = chaos_result

        # 5. Проверить compliance
        if 'compliance' in scenario:
            compliance_result = await self.compliance_engine.check_compliance(
                scenario['compliance'],
                execution_result
            )
            execution_result['compliance'] = compliance_result

        # 6. Отправить результаты в learning system
        await self._send_to_learning(scenario, execution_result, context)

        return execution_result

    async def _execute_steps(
        self,
        scenario: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнить шаги из execution.steps"""

        steps = scenario.get('execution', {}).get('steps', [])
        results = []

        for step in steps:
            step_id = step.get('id')
            action = step.get('action')

            print(f"  ▶️  Step: {step_id} ({action})")

            # Выполнить action
            step_result = await self._execute_action(step, context)

            # Обработать on_error (BPMN Boundary Events)
            if step_result.get('error') and 'on_error' in step:
                step_result = await self._handle_error(
                    step['on_error'],
                    step_result,
                    context
                )

            # Обработать calls (вложенные сценарии)
            if 'calls' in step:
                call_results = await self.call_engine.execute_calls(
                    step['calls'],
                    {**context, f"steps.{step_id}": step_result}
                )
                step_result['call_results'] = call_results

            results.append({
                'step_id': step_id,
                'result': step_result
            })

            # Обновить контекст
            context[f"steps.{step_id}"] = step_result

        return {
            'steps': results,
            'context': context
        }

    async def _execute_action(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнить конкретный action"""

        action = step.get('action')
        params = step.get('params', {})

        # Resolve variables like {{user_id}}
        resolved_params = self._resolve_params(params, context)

        # Вызвать соответствующий сервис
        # Формат action: "service.method" или просто "method"
        if '.' in action:
            service, method = action.split('.', 1)
            result = await self._call_service(service, method, resolved_params)
        else:
            # Внутренний метод
            result = await self._call_internal_action(action, resolved_params)

        return result

    async def _send_to_learning(
        self,
        scenario: Dict[str, Any],
        result: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """Отправить результаты выполнения в learning system"""

        from learning.scenario_learner import ScenarioLearner
        learner = ScenarioLearner()

        await learner.record_execution(
            scenario_id=scenario['meta']['id'],
            scenario=scenario,
            result=result,
            context=context
        )
```

### **B) Call Engine (BPMN Call Activity)**

```python
# scenario-intelligence/engines/call_engine.py

class CallEngine:
    """
    Движок для синхронных вызовов сценариев (BPMN Call Activity)
    """

    def __init__(self):
        from storage.registry import ScenarioRegistry
        self.registry = ScenarioRegistry()

    async def execute_calls(
        self,
        calls: list,
        context: Dict[str, Any]
    ) -> list:
        """
        Выполнить список вызовов (calls)

        Поддерживает:
        - Последовательные вызовы (wait_for: "completion")
        - Параллельные вызовы (parallel: true)
        """

        # Разделить на параллельные и последовательные
        parallel_calls = [c for c in calls if c.get('parallel', False)]
        sequential_calls = [c for c in calls if not c.get('parallel', False)]

        results = []

        # Параллельные вызовы
        if parallel_calls:
            parallel_results = await asyncio.gather(*[
                self._execute_single_call(call, context)
                for call in parallel_calls
            ])
            results.extend(parallel_results)

        # Последовательные вызовы
        for call in sequential_calls:
            call_result = await self._execute_single_call(call, context)
            results.append(call_result)

            # Обновить контекст для следующего вызова
            context.update(call_result.get('output', {}))

        return results

    async def _execute_single_call(
        self,
        call: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Выполнить один вызов"""

        scenario_id = call.get('scenario_id')
        level = call.get('level')
        params = call.get('params', {})
        timeout = call.get('timeout', 30)

        # Загрузить сценарий из registry
        called_scenario = await self.registry.get_scenario(scenario_id, level)

        if not called_scenario:
            return {
                'error': f"Scenario {scenario_id} (level {level}) not found",
                'scenario_id': scenario_id
            }

        # Input mapping
        if 'input_mapping' in call:
            mapped_params = self._map_params(
                call['input_mapping'],
                context
            )
            params.update(mapped_params)

        # Выполнить вызванный сценарий (рекурсия!)
        from .scenario_engine import ScenarioEngine
        engine = ScenarioEngine()

        try:
            result = await asyncio.wait_for(
                engine.execute_scenario(called_scenario, params),
                timeout=timeout
            )

            # Output mapping
            output = result
            if 'output_mapping' in call:
                output = self._map_params(
                    call['output_mapping'],
                    result
                )

            return {
                'scenario_id': scenario_id,
                'status': 'success',
                'output': output
            }

        except asyncio.TimeoutError:
            return {
                'scenario_id': scenario_id,
                'status': 'timeout',
                'error': f"Timeout after {timeout}s"
            }
```

### **C) Event Engine (Event Storming)**

```python
# scenario-intelligence/engines/event_engine.py

from typing import List, Dict, Any
import asyncio

class EventEngine:
    """
    Движок для асинхронных событий (Event Storming)
    """

    def __init__(self):
        # Event Bus (можно Redis Pub/Sub, Kafka, или простой in-memory)
        from infrastructure.eventbus import EventBus
        self.event_bus = EventBus()

        # Registry для подписок
        self.subscriptions = {}  # event_type -> [scenario_ids]

    async def emit_events(
        self,
        events: List[Dict[str, Any]],
        context: Dict[str, Any]
    ):
        """
        Испустить события (emits)
        """

        for event_config in events:
            event_type = event_config.get('event_type')
            payload = self._resolve_payload(event_config.get('payload', {}), context)

            event = {
                'type': event_type,
                'aggregate': event_config.get('aggregate'),
                'aggregate_id': event_config.get('aggregate_id'),
                'payload': payload,
                'timestamp': datetime.utcnow().isoformat(),
                'correlation_id': context.get('correlation_id')
            }

            print(f"  📡 Emitting event: {event_type}")

            # Опубликовать в Event Bus
            await self.event_bus.publish(event_type, event)

    async def subscribe_scenario(
        self,
        scenario_id: str,
        event_type: str
    ):
        """
        Подписать сценарий на событие
        """

        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []

        if scenario_id not in self.subscriptions[event_type]:
            self.subscriptions[event_type].append(scenario_id)

            # Подписаться в Event Bus
            await self.event_bus.subscribe(
                event_type,
                lambda event: self._handle_event(event, scenario_id)
            )

    async def _handle_event(
        self,
        event: Dict[str, Any],
        scenario_id: str
    ):
        """
        Обработать событие - запустить сценарий
        """

        print(f"  🎯 Event {event['type']} triggered scenario: {scenario_id}")

        # Загрузить сценарий
        from storage.registry import ScenarioRegistry
        registry = ScenarioRegistry()
        scenario = await registry.get_scenario_by_id(scenario_id)

        if scenario:
            # Запустить сценарий с событием в контексте
            from .scenario_engine import ScenarioEngine
            engine = ScenarioEngine()

            await engine.execute_scenario(
                scenario,
                context={'event': event}
            )
```

### **D) Chaos Engine (Netflix)**

```python
# scenario-intelligence/engines/chaos_engine.py

class ChaosEngine:
    """
    Движок для chaos experiments (Netflix Chaos Engineering)
    """

    async def execute_chaos(
        self,
        chaos_config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Выполнить chaos experiment
        """

        experiment = chaos_config.get('experiment', {})
        hypothesis = experiment.get('hypothesis', {})

        print(f"  💥 Starting Chaos Experiment")
        print(f"     Hypothesis: {hypothesis.get('expected')}")

        # 1. Измерить steady state (до chaos)
        steady_state_before = await self._measure_steady_state(
            experiment.get('steady_state_verification', {}).get('before_chaos', [])
        )

        # 2. Progressive rollout
        rollout = experiment.get('rollout', {})
        for phase in rollout.get('phases', []):
            print(f"     Phase {phase['phase']}: {phase['scope']}")

            # Inject chaos
            chaos_actions = experiment.get('chaos_actions', [])
            for action in chaos_actions:
                await self._inject_chaos(action, phase)

            # Measure during chaos
            steady_state_during = await self._measure_steady_state(
                experiment.get('steady_state_verification', {}).get('during_chaos', [])
            )

            # Check abort conditions
            should_abort = await self._check_abort_conditions(
                experiment.get('abort_conditions', []),
                steady_state_during
            )

            if should_abort:
                print(f"     ⚠️  ABORTING: Abort condition triggered!")
                await self._rollback_chaos(chaos_actions)
                break

            # Wait for phase duration
            await asyncio.sleep(self._parse_duration(phase.get('duration', '5m')))

            # Restore chaos
            await self._rollback_chaos(chaos_actions)

        # 3. Measure steady state (после chaos)
        steady_state_after = await self._measure_steady_state(
            experiment.get('steady_state_verification', {}).get('after_chaos', [])
        )

        return {
            'hypothesis_confirmed': self._validate_hypothesis(
                hypothesis,
                steady_state_before,
                steady_state_during,
                steady_state_after
            ),
            'measurements': {
                'before': steady_state_before,
                'during': steady_state_during,
                'after': steady_state_after
            }
        }

    async def _inject_chaos(
        self,
        action: Dict[str, Any],
        phase: Dict[str, Any]
    ):
        """Inject chaos (kill pod, network latency, etc.)"""

        chaos_type = action.get('type')

        if chaos_type == 'pod_failure':
            # kubectl delete pod ...
            target = action.get('target', {})
            await self._kill_pod(target)

        elif chaos_type == 'network_latency':
            # tc qdisc add dev eth0 root netem delay 5000ms
            await self._add_network_latency(action)

        # ... другие типы chaos
```

### **E) Compliance Engine (ISO 22301)**

```python
# scenario-intelligence/engines/compliance_engine.py

class ComplianceEngine:
    """
    Движок для проверки compliance (ISO 22301, ISO 27001, etc.)
    """

    async def check_compliance(
        self,
        compliance_config: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Проверить соответствие стандартам
        """

        results = {}

        # ISO 22301
        if 'iso_22301' in compliance_config:
            iso22301 = compliance_config['iso_22301']

            results['iso_22301'] = {
                'clauses': await self._check_clauses(
                    iso22301.get('clauses', []),
                    execution_result
                ),
                'evidence': await self._generate_evidence(
                    iso22301.get('evidence_generated', []),
                    execution_result
                ),
                'retention': await self._apply_retention(
                    iso22301.get('evidence_generated', [])
                )
            }

        # ISO 27001
        if 'iso_27001' in compliance_config:
            iso27001 = compliance_config['iso_27001']

            results['iso_27001'] = {
                'controls': await self._check_controls(
                    iso27001.get('controls', []),
                    execution_result
                )
            }

        return results

    async def _generate_evidence(
        self,
        evidence_configs: List[Dict[str, Any]],
        execution_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Генерировать evidence для аудита
        """

        evidence_generated = []

        for config in evidence_configs:
            evidence = {
                'type': config.get('type'),
                'format': config.get('format'),
                'generated_at': datetime.utcnow().isoformat(),
                'data': self._extract_evidence_data(config, execution_result),
                'storage': config.get('storage'),
                'retention_until': self._calculate_retention_date(
                    config.get('retention')
                )
            }

            # Сохранить в compliance archive
            await self._store_evidence(evidence)

            evidence_generated.append(evidence)

        return evidence_generated
```

---

## 3. 💾 СИСТЕМА ХРАНЕНИЯ (Storage Strategy)

### **A) Гибридное хранилище:**

```python
# scenario-intelligence/storage/hybrid_storage.py

class HybridStorage:
    """
    Гибридное хранилище сценариев:
    1. File Storage (Git) - source of truth
    2. RAG Storage (Qdrant) - AI поиск
    3. Registry (Redis/PostgreSQL) - быстрый индекс
    """

    def __init__(self):
        self.file_storage = FileStorage()
        self.rag_storage = RAGStorage()
        self.registry = ScenarioRegistry()

    async def store_scenario(
        self,
        scenario: Dict[str, Any]
    ) -> bool:
        """
        Сохранить сценарий во ВСЕ хранилища
        """

        scenario_id = scenario['meta']['id']
        version = scenario['meta']['version']

        # 1. File Storage (Git) - source of truth
        await self.file_storage.save(scenario)

        # 2. RAG Storage (Qdrant) - для AI поиска
        await self.rag_storage.embed_and_store(scenario)

        # 3. Registry - быстрый индекс
        await self.registry.register(scenario)

        print(f"✅ Stored scenario: {scenario_id} v{version}")

        return True
```

### **B) File Storage (Git):**

```python
# scenario-intelligence/storage/file_storage.py

class FileStorage:
    """
    Файловое хранилище (Git versioned)
    """

    def __init__(self):
        self.base_path = "/Users/MD/AI-Platform-ISO/intelligent-core/scenario-intelligence/scenarios"

    async def save(self, scenario: Dict[str, Any]):
        """
        Сохранить сценарий в файл
        """

        meta = scenario['meta']
        level = meta['level']
        scenario_type = meta['type']
        scenario_id = meta['id']
        version = meta['version']

        # Путь: scenarios/level{X}-{name}/{module}/{type}/{id}.v{version}.yaml
        if level == 1:
            module = scenario.get('ownership', {}).get('module', 'unknown')
            path = f"{self.base_path}/level1-modules/{module}/{scenario_type}/{scenario_id}.v{version}.yaml"
        elif level == 2:
            subsystem = scenario.get('ownership', {}).get('subsystem', 'unknown')
            path = f"{self.base_path}/level2-subsystems/{subsystem}/{scenario_type}/{scenario_id}.v{version}.yaml"
        elif level == 3:
            path = f"{self.base_path}/level3-intersystem/{scenario_id}.v{version}.yaml"
        else:  # level 4
            category = scenario.get('meta', {}).get('category', 'workflows')
            path = f"{self.base_path}/level4-user/{category}/{scenario_id}.v{version}.yaml"

        # Создать директории
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Сохранить YAML
        with open(path, 'w') as f:
            yaml.dump({'scenario': scenario}, f, default_flow_style=False, sort_keys=False)

        # Git commit (опционально)
        await self._git_commit(path, f"Add {scenario_id} v{version}")
```

### **C) RAG Storage (Qdrant):**

```python
# scenario-intelligence/storage/rag_storage.py

class RAGStorage:
    """
    RAG хранилище для AI поиска сценариев
    """

    def __init__(self):
        from integration.rag_adapter import RAGAdapter
        self.rag = RAGAdapter()
        self.collection = "scenarios"

    async def embed_and_store(self, scenario: Dict[str, Any]):
        """
        Создать embeddings и сохранить в Qdrant
        """

        # 1. Создать текстовое представление сценария
        scenario_text = self._create_searchable_text(scenario)

        # 2. Генерировать embeddings через LLM
        from integration.ai_orchestrator_adapter import AIAdapter
        ai = AIAdapter()
        embeddings = await ai.generate_embeddings(scenario_text)

        # 3. Сохранить в Qdrant с метаданными
        await self.rag.upsert(
            collection=self.collection,
            id=scenario['meta']['id'],
            vector=embeddings,
            payload={
                'scenario': scenario,
                'level': scenario['meta']['level'],
                'type': scenario['meta']['type'],
                'pillar': scenario.get('well_architected', {}).get('pillar'),
                'domain': scenario.get('meta', {}).get('domain'),
                'tags': self._extract_tags(scenario)
            }
        )

    def _create_searchable_text(self, scenario: Dict[str, Any]) -> str:
        """
        Создать текст для поиска и embeddings
        """

        parts = []

        # Metadata
        meta = scenario.get('meta', {})
        parts.append(f"ID: {meta.get('id')}")
        parts.append(f"Type: {meta.get('type')}")
        parts.append(f"Level: {meta.get('level')}")

        # Description
        desc = scenario.get('description', {})
        parts.append(f"Title: {desc.get('title')}")
        parts.append(f"Summary: {desc.get('summary')}")
        parts.append(f"Business Value: {desc.get('business_value')}")

        # Behavior (Gherkin)
        behavior = scenario.get('behavior', {})
        parts.append(f"Feature: {behavior.get('feature')}")
        parts.append(f"Scenario: {behavior.get('scenario')}")
        parts.append(f"Given: {', '.join(behavior.get('given', []))}")
        parts.append(f"When: {', '.join(behavior.get('when', []))}")
        parts.append(f"Then: {', '.join(behavior.get('then', []))}")

        # Compliance
        compliance = scenario.get('compliance', {})
        if 'iso_22301' in compliance:
            clauses = [c.get('id') for c in compliance['iso_22301'].get('clauses', [])]
            parts.append(f"ISO 22301 Clauses: {', '.join(clauses)}")

        # Domain
        if 'meta' in scenario and 'domain' in scenario['meta']:
            parts.append(f"Domain: {scenario['meta']['domain']}")

        return "\n".join(parts)
```

### **D) Registry (быстрый индекс):**

```python
# scenario-intelligence/storage/registry.py

class ScenarioRegistry:
    """
    Быстрый индекс всех сценариев (PostgreSQL или Redis)
    """

    def __init__(self):
        # Можно использовать PostgreSQL или Redis
        from infrastructure.database import get_db
        self.db = get_db()

    async def register(self, scenario: Dict[str, Any]):
        """
        Зарегистрировать сценарий в индексе
        """

        meta = scenario['meta']

        await self.db.execute("""
            INSERT INTO scenario_registry (
                scenario_id,
                version,
                level,
                type,
                pillar,
                module,
                subsystem,
                domain,
                file_path,
                created_at,
                updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (scenario_id, version)
            DO UPDATE SET updated_at = $11
        """,
            meta['id'],
            meta['version'],
            meta['level'],
            meta['type'],
            scenario.get('well_architected', {}).get('pillar'),
            scenario.get('ownership', {}).get('module'),
            scenario.get('ownership', {}).get('subsystem'),
            meta.get('domain'),
            self._get_file_path(scenario),
            meta.get('created_at'),
            meta.get('updated_at')
        )

    async def find_scenarios(
        self,
        level: Optional[int] = None,
        type: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Найти сценарии по фильтрам (быстро!)
        """

        query = "SELECT * FROM scenario_registry WHERE 1=1"
        params = []

        if level:
            query += " AND level = $" + str(len(params) + 1)
            params.append(level)

        if type:
            query += " AND type = $" + str(len(params) + 1)
            params.append(type)

        if domain:
            query += " AND domain = $" + str(len(params) + 1)
            params.append(domain)

        return await self.db.fetch(query, *params)
```

---

## 4. 🧠 ОБУЧЕНИЕ И ПРЕДСКАЗАНИЯ (Learning & Predictions)

### **A) Scenario Learner (учится на выполнении):**

```python
# scenario-intelligence/learning/scenario_learner.py

class ScenarioLearner:
    """
    Учится на результатах выполнения сценариев
    """

    def __init__(self):
        from integration.rag_adapter import RAGAdapter
        self.rag = RAGAdapter()
        self.collection_executions = "scenario_executions"

    async def record_execution(
        self,
        scenario_id: str,
        scenario: Dict[str, Any],
        result: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """
        Записать результат выполнения сценария
        """

        execution_record = {
            'scenario_id': scenario_id,
            'executed_at': datetime.utcnow().isoformat(),
            'context': context,
            'result': result,
            'success': result.get('status') == 'success',
            'duration': result.get('duration'),
            'errors': result.get('errors', [])
        }

        # 1. Сохранить в БД
        await self._save_to_db(execution_record)

        # 2. Создать embeddings для pattern detection
        execution_text = self._create_execution_text(
            scenario,
            result,
            context
        )
        embeddings = await self._generate_embeddings(execution_text)

        # 3. Сохранить в RAG для анализа паттернов
        await self.rag.upsert(
            collection=self.collection_executions,
            id=f"{scenario_id}_{datetime.utcnow().timestamp()}",
            vector=embeddings,
            payload=execution_record
        )

        # 4. Обновить статистику
        await self._update_statistics(scenario_id, result)

    async def _update_statistics(
        self,
        scenario_id: str,
        result: Dict[str, Any]
    ):
        """
        Обновить статистику использования сценария
        """

        await self.db.execute("""
            INSERT INTO scenario_statistics (
                scenario_id,
                total_executions,
                successful_executions,
                failed_executions,
                avg_duration,
                last_executed_at
            ) VALUES ($1, 1, $2, $3, $4, $5)
            ON CONFLICT (scenario_id) DO UPDATE SET
                total_executions = scenario_statistics.total_executions + 1,
                successful_executions = scenario_statistics.successful_executions + $2,
                failed_executions = scenario_statistics.failed_executions + $3,
                avg_duration = (scenario_statistics.avg_duration * scenario_statistics.total_executions + $4) / (scenario_statistics.total_executions + 1),
                last_executed_at = $5
        """,
            scenario_id,
            1 if result.get('status') == 'success' else 0,
            0 if result.get('status') == 'success' else 1,
            result.get('duration', 0),
            datetime.utcnow()
        )
```

### **B) Pattern Detector (находит паттерны):**

```python
# scenario-intelligence/learning/pattern_detector.py

class PatternDetector:
    """
    Находит паттерны в выполнении сценариев
    """

    async def detect_patterns(self) -> List[Dict[str, Any]]:
        """
        Анализировать executions и находить паттерны
        """

        patterns = []

        # Pattern 1: Частые последовательности сценариев
        common_sequences = await self._find_common_sequences()
        patterns.append({
            'type': 'common_sequence',
            'data': common_sequences
        })

        # Pattern 2: Сценарии которые часто падают вместе
        correlated_failures = await self._find_correlated_failures()
        patterns.append({
            'type': 'correlated_failures',
            'data': correlated_failures
        })

        # Pattern 3: Контексты которые приводят к успеху/неуспеху
        success_contexts = await self._find_success_contexts()
        patterns.append({
            'type': 'success_contexts',
            'data': success_contexts
        })

        return patterns

    async def _find_common_sequences(self) -> List[Dict[str, Any]]:
        """
        Найти частые последовательности сценариев

        Например:
        "user-create-bia" → "bia-ai-integration" → "ai-foundation-query"
        Встречается 500 раз
        """

        # Используем RAG для поиска похожих execution chains
        from integration.rag_adapter import RAGAdapter
        rag = RAGAdapter()

        # Простой подход: GROUP BY в SQL
        sequences = await self.db.fetch("""
            WITH scenario_pairs AS (
                SELECT
                    e1.scenario_id as scenario_1,
                    e2.scenario_id as scenario_2,
                    COUNT(*) as frequency
                FROM scenario_executions e1
                JOIN scenario_executions e2
                    ON e1.session_id = e2.session_id
                    AND e2.executed_at > e1.executed_at
                    AND e2.executed_at - e1.executed_at < interval '5 minutes'
                GROUP BY e1.scenario_id, e2.scenario_id
                HAVING COUNT(*) > 10
                ORDER BY frequency DESC
                LIMIT 20
            )
            SELECT * FROM scenario_pairs
        """)

        return sequences
```

### **C) Predictor (предсказывает нужные сценарии):**

```python
# scenario-intelligence/learning/predictor.py

class ScenarioPredictor:
    """
    Предсказывает какие сценарии понадобятся дальше
    """

    async def predict_next_scenarios(
        self,
        current_context: Dict[str, Any],
        executed_scenarios: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Предсказать следующие сценарии на основе:
        - Текущего контекста (user action, domain, etc.)
        - Уже выполненных сценариев
        - Исторических паттернов
        """

        predictions = []

        # 1. Sequence-based prediction (Markov chains)
        sequence_predictions = await self._predict_by_sequence(
            executed_scenarios
        )
        predictions.extend(sequence_predictions)

        # 2. Context-based prediction (ML model)
        context_predictions = await self._predict_by_context(
            current_context
        )
        predictions.extend(context_predictions)

        # 3. RAG-based prediction (semantic similarity)
        rag_predictions = await self._predict_by_rag(
            current_context,
            executed_scenarios
        )
        predictions.extend(rag_predictions)

        # Объединить и ранжировать
        ranked_predictions = self._rank_predictions(predictions)

        return ranked_predictions[:5]  # Top 5

    async def _predict_by_rag(
        self,
        current_context: Dict[str, Any],
        executed_scenarios: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Предсказание через RAG (семантическое сходство)
        """

        # Создать query из контекста
        query_text = f"""
        User action: {current_context.get('user_action')}
        Domain: {current_context.get('domain')}
        Already executed: {', '.join(executed_scenarios)}
        What should happen next?
        """

        # Поискать похожие execution chains в RAG
        from integration.rag_adapter import RAGAdapter
        rag = RAGAdapter()

        similar_executions = await rag.search(
            collection="scenario_executions",
            query_text=query_text,
            limit=10
        )

        # Извлечь сценарии которые выполнялись после
        predictions = []
        for execution in similar_executions:
            next_scenarios = execution.get('payload', {}).get('next_scenarios', [])
            for scenario in next_scenarios:
                predictions.append({
                    'scenario_id': scenario,
                    'confidence': execution.get('score', 0.5),
                    'reason': 'rag_similarity'
                })

        return predictions
```

### **D) Auto-Generator (генерирует новые сценарии):**

```python
# scenario-intelligence/learning/auto_generator.py

class ScenarioAutoGenerator:
    """
    Автоматически генерирует новые сценарии на основе:
    - Паттернов выполнения
    - Недостающих сценариев
    - AI анализа
    """

    async def generate_missing_scenarios(
        self,
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Генерировать сценарии которых не хватает
        """

        generated_scenarios = []

        for pattern in patterns:
            if pattern['type'] == 'common_sequence':
                # Если последовательность часто повторяется -
                # создать composite scenario
                composite = await self._generate_composite_scenario(
                    pattern['data']
                )
                generated_scenarios.append(composite)

            elif pattern['type'] == 'correlated_failures':
                # Если сценарии часто падают вместе -
                # создать recovery scenario
                recovery = await self._generate_recovery_scenario(
                    pattern['data']
                )
                generated_scenarios.append(recovery)

        return generated_scenarios

    async def _generate_composite_scenario(
        self,
        sequence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Сгенерировать composite сценарий из последовательности
        """

        from integration.ai_orchestrator_adapter import AIAdapter
        ai = AIAdapter()

        prompt = f"""
        Пользователи часто выполняют эту последовательность сценариев:
        {sequence['scenario_1']} → {sequence['scenario_2']}
        (Выполнено {sequence['frequency']} раз)

        Создай composite сценарий который объединит их в один.
        Формат: YAML (наша схема scenario).
        """

        generated_yaml = await ai.generate_content(
            prompt=prompt,
            temperature=0.7
        )

        # Parse YAML
        scenario = yaml.safe_load(generated_yaml)

        # Добавить метаданные
        scenario['meta']['created_by'] = 'ai_auto_generator'
        scenario['meta']['created_at'] = datetime.utcnow().isoformat()
        scenario['meta']['version'] = '0.1.0'  # Draft version

        return scenario
```

---

## 5. 🔄 ПОЛНАЯ РЕАЛИЗАЦИЯ - КАК ВСЁ РАБОТАЕТ ВМЕСТЕ

### **Пример: Пользователь создает BIA**

```python
# Поток выполнения:

# 1. USER ACTION
user_clicks_button("Create BIA")
    ↓
# 2. SCENARIO ENGINE запускается
scenario = load_scenario("user-create-bia", level=4)
engine = ScenarioEngine()
result = await engine.execute_scenario(scenario, {
    'user_id': 'user123',
    'org_id': 'hospital_1',
    'scope': ['emergency', 'surgery']
})
    ↓
# 3. EXECUTION STEPS
for step in scenario['execution']['steps']:

    # Step 1: Create BIA record
    step_result = await execute_step({
        'action': 'bia-service.create',
        'params': {'name': 'Q1 BIA', 'scope': [...]}
    })

    # Step 2: AI recommendations (CALL ENGINE)
    if 'calls' in step:
        call_results = await call_engine.execute_calls([
            {
                'scenario_id': 'bia-ai-integration',  # Level 3
                'level': 3,
                'params': {'bia_id': step_result['id']}
            }
        ])
        # Это вызывает сценарий уровня 3!
            ↓
        # Level 3 scenario выполняется
        scenario_l3 = load_scenario('bia-ai-integration', level=3)
        await engine.execute_scenario(scenario_l3, {...})
            ↓
        # Level 3 вызывает Level 2
        calls_l2 = await call_engine.execute_calls([
            {
                'scenario_id': 'ai-foundation-query-workflow',
                'level': 2
            }
        ])
            ↓
        # Level 2 вызывает Level 1 (параллельно!)
        calls_l1 = await call_engine.execute_calls([
            {'scenario_id': 'rag-search', 'level': 1, 'parallel': True},
            {'scenario_id': 'knowledge-query', 'level': 1, 'parallel': True},
            {'scenario_id': 'llm-generate', 'level': 1, 'parallel': True}
        ])
            ↓
        # Результаты поднимаются обратно
        # L1 → L2 → L3 → L4

    # Step 3: Events (EVENT ENGINE)
    if 'events' in scenario['integration']:
        await event_engine.emit_events([
            {
                'event_type': 'bia.created',
                'payload': {'bia_id': step_result['id']}
            }
        ])
        # Event опубликован в Event Bus
        # Подписчики (другие сценарии) автоматически запустятся!

    # Step 4: Compliance (COMPLIANCE ENGINE)
    if 'compliance' in scenario:
        compliance_result = await compliance_engine.check_compliance(
            scenario['compliance'],
            result
        )
        # Генерируется evidence для ISO 22301
        # Сохраняется с retention 7 years

    # Step 5: Learning (LEARNER)
    await scenario_learner.record_execution(
        scenario_id='user-create-bia',
        scenario=scenario,
        result=result,
        context={...}
    )
    # Система учится:
    # - Какой контекст → какой результат
    # - Какие сценарии идут вместе
    # - Где узкие места

# 6. PREDICTION (в фоне)
await predictor.predict_next_scenarios(
    current_context={'bia_id': result['bia_id']},
    executed_scenarios=['user-create-bia', 'bia-ai-integration']
)
# Предсказывает: "Вероятно пользователь далее запустит risk-assessment"
# Можем pre-load сценарий, прогреть кеш и т.д.

# 7. AUTO-GENERATION (периодически)
patterns = await pattern_detector.detect_patterns()
new_scenarios = await auto_generator.generate_missing_scenarios(patterns)
# AI создал новый сценарий: "bia-with-ai-recommendations-composite"
# Потому что заметил что эта последовательность часто повторяется
```

---

## 6. 📊 ВИЗУАЛИЗАЦИЯ АРХИТЕКТУРЫ

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              SCENARIO INTELLIGENCE LAYER                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  SCENARIO ENGINE                          │  │
│  │              (Main Orchestrator)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│          ↓              ↓             ↓             ↓          │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────┐ ┌─────────────┐ │
│  │ Call Engine │ │Event Engine │ │  Chaos   │ │ Compliance  │ │
│  │   (BPMN)    │ │   (Events)  │ │  Engine  │ │   Engine    │ │
│  └─────────────┘ └─────────────┘ └──────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                                 │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐   │
│  │ File Storage │  │  RAG Storage  │  │  Registry (Index)  │   │
│  │    (Git)     │  │   (Qdrant)    │  │   (PostgreSQL)     │   │
│  └──────────────┘  └───────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   LEARNING LAYER                                 │
│  ┌─────────────┐  ┌───────────────┐  ┌──────────┐  ┌─────────┐ │
│  │   Learner   │  │    Pattern    │  │Predictor │  │   Auto  │ │
│  │  (Records)  │  │   Detector    │  │(Next SC) │  │Generator│ │
│  └─────────────┘  └───────────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              INTEGRATION WITH INTELLIGENT-CORE                   │
│  ┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │AI Orchestr. │  │   RAG    │  │Knowledge │  │   Domain     │ │
│  │  (Adapter)  │  │(Adapter) │  │(Adapter) │  │   Expertise  │ │
│  └─────────────┘  └──────────┘  └──────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. 🎯 ИТОГОВЫЕ ОТВЕТЫ НА ВАШИ ВОПРОСЫ

### ❓ "Движки - как правильно?"

**ОТВЕТ:**
- **Главный Scenario Engine** - оркестратор всех остальных
- **Call Engine** - для BPMN Call Activity (синхронные вызовы)
- **Event Engine** - для Event Storming (асинхронные события)
- **Chaos Engine** - для Netflix chaos experiments
- **Compliance Engine** - для ISO 22301/27001 checks

### ❓ "Расстановка в системе?"

**ОТВЕТ:**
- **Scenario Intelligence** = ВЕРХНИЙ слой в intelligent-core
- Находится НАД AI Orchestrator, AI Foundation
- Использует их как "подчиненные" компоненты
- Координирует всю систему через сценарии

### ❓ "Система хранения?"

**ОТВЕТ:** Гибридная (3 слоя):
1. **File Storage (Git)** - source of truth, версионирование
2. **RAG Storage (Qdrant)** - AI поиск, embeddings
3. **Registry (PostgreSQL)** - быстрый индекс, метаданные

### ❓ "Как система учится?"

**ОТВЕТ:**
- **Learner** записывает каждое выполнение
- **Pattern Detector** находит паттерны (частые последовательности)
- **Predictor** предсказывает следующие сценарии
- **Auto-Generator** создает новые сценарии на основе паттернов

### ❓ "Предсказания - как использовать?"

**ОТВЕТ:**
- Предсказание следующих сценариев → pre-loading
- Предсказание ошибок → preventive actions
- Предсказание bottlenecks → optimization
- AI recommendations для пользователей

---

## 8. 🚀 ЧТО ДАЛЬШЕ?

**Готов создать:**

**A)** Полную имплементацию всех движков (код)?

**B)** Схему БД для хранения (PostgreSQL schema)?

**C)** Docker Compose для запуска всей системы?

**D)** Первые 10 примеров сценариев всех уровней?

**Что выбираете?**
