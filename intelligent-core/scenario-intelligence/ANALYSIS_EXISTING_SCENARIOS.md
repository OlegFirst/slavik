# Анализ существующих Scenario компонентов в платформе

**Дата**: 2025-10-12
**Статус**: Обнаружены 3 существующих компонента сценариев

---

## 🔍 Что обнаружено

### 1. **Scenario Orchestrator** (Platform Services)
**Путь**: `/Users/MD/AI-Platform-ISO/platform-services/simulation/scenarios/scenario_orchestrator/`

**Что это**:
- FastAPI сервис для **AI-генерации BCM exercise scenarios**
- Интегрирован с AI Orchestrator для генерации сценариев
- **Учебные/тренировочные сценарии** для BCM exercises

**Ключевые возможности**:
```python
# AI-powered scenario generation
POST /scenarios/generate
{
  "category": "epidemic|blackout|cyber|supply|natural|terrorism",
  "complexity": 1-5,
  "duration_hours": 4,
  "participants": 10,
  "affected_systems": [],
  "custom_objectives": []
}

# Experience accumulation & learning
POST /learning/exercise-result
GET /learning/scenario/{id}/insights
GET /learning/dashboard
```

**Характеристики**:
- ✅ AI-генерация через существующий AI Orchestrator
- ✅ JaamSim integration для симуляций (complexity >= 4)
- ✅ Learning system - аккумуляция опыта после exercises
- ✅ Feedback collection и effectiveness tracking
- ✅ AI-powered improvement recommendations
- ⚠️ Сохранение локально (JSON files), не в Supabase
- ⚠️ In-memory storage для learning data (планируется Redis/Supabase)

**Формат сценария**:
```json
{
  "title": "Epidemic BCM Exercise Scenario",
  "category": "epidemic",
  "level": "tabletop|full",
  "meta_duration": 4,
  "meta_participants": 10,
  "content_md": "# Markdown format scenario...",
  "is_ai_generated": true,
  "ai_generation_params": {...},
  "jaamsim_config": "..."
}
```

**Модель данных** (app/models/scenario.py):
```python
class Scenario(BaseModel):
    id: str
    company_id: str
    title: str
    description: str
    scenario_type: str
    risk_level: str
    data: Dict[str, Any]
    created_by: str
    created_at: datetime
```

**Интеграции**:
- AI Orchestrator (`/nlp/query`)
- Odoo BCM Scenario Hub (планируется)
- JaamSim simulator

---

### 2. **BCM Incident Module** (Odoo Integration)
**Путь**: `/Users/MD/AI-Platform-ISO/platform-services/simulation/scenarios/bcm_incident/`

**Что это**:
- Odoo модуль для **incident management**
- **Incident scenarios** для реагирования на инциденты
- Unified incident tracking (bcm.incident model)

**Ключевые возможности**:
```python
# Incident classification
incident_type: [
    'operational', 'cyber', 'natural',
    'supply_chain', 'health_safety',
    'financial', 'reputational', 'other'
]

# Status workflow
status: [
    'draft', 'detected', 'assessing',
    'responding', 'recovering',
    'resolved', 'closed'
]

# Severity levels
severity: ['low', 'medium', 'high', 'critical']
```

**Характеристики**:
- ✅ Odoo ORM integration
- ✅ Mail tracking (mail.thread, mail.activity.mixin)
- ✅ Temporal metrics (detected_at, reported_at, resolved_at)
- ✅ Priority system (0-4 scale)
- ✅ AI Commander integration (data/ai_commander_data.xml)
- ⚠️ Специфичен для Odoo (не standalone)

**Модель данных**:
```python
class BCMIncidentUnified(models.Model):
    _name = 'bcm.incident'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    title: Char
    description: Text
    incident_number: Char (unique)
    severity: Selection
    status: Selection
    incident_type: Selection
    priority: Selection
    detected_at: Datetime
    reported_at: Datetime
    # ... + workflow methods
```

---

### 3. **Workflow Intelligence Production Modules**
**Путь**: `/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence/production_modules/`

**Что это**:
- **8 production-ready модулей** для Process Framework
- Созданы другим Claude агентом 2025-10-11
- **НЕ интегрированы** в основную систему!

**Содержимое**:
1. **api.py** (22KB) - FastAPI REST API с 17 endpoints
2. **database.py** (20KB) - PostgreSQL Connection Pool
3. **error_handling.py** (15KB) - Retry + Circuit Breaker
4. **eventbus_integration.py** (13KB) - EventBus events
5. **cache.py** (14KB) - Redis cache
6. **process_metrics.py** (22KB) - Prometheus metrics
7. **visualization.py** (31KB) - Mermaid, BPMN, Gantt charts
8. **test_process_framework_performance.py** - performance tests

**Характеристики**:
- ✅ Production-ready модули (166KB кода, ~4100 строк)
- ✅ Интеграция с СУЩЕСТВУЮЩИМИ компонентами (EventBus, DatabaseManager)
- ✅ Comprehensive error handling + retry policies
- ✅ Prometheus metrics + Redis caching
- ✅ Visualization (Mermaid/BPMN)
- ⚠️ **Standalone модули** - требуют интеграции
- ⚠️ Создано агентом без контекста scenario-intelligence

---

## 🎯 Что это значит для нашего Scenario Intelligence?

### Три разных подхода к сценариям:

| Аспект | Scenario Orchestrator | BCM Incident | Scenario Intelligence (наш) |
|--------|----------------------|--------------|----------------------------|
| **Цель** | BCM training exercises | Incident response | System behavior testing + orchestration |
| **Уровень** | User workflows | Operational events | Module → Subsystem → Inter-system → User |
| **Формат** | Markdown + JSON | Odoo records | YAML (declarative) |
| **Storage** | Local JSON files | Odoo PostgreSQL | Supabase + Qdrant RAG |
| **Execution** | Manual/JaamSim simulation | Workflow automation | Engine-based execution (5 engines) |
| **Learning** | Exercise feedback | Incident statistics | Pattern detection + ML prediction |
| **Integration** | AI Orchestrator + Odoo | Odoo ecosystem | EventBus + DB + RAG + All modules |

### Ключевые различия:

**Scenario Orchestrator**:
- 🎯 **Training/Exercise focus** - учебные сценарии для персонала
- 📝 **AI-generated content** - генерация через LLM
- 👥 **Human-oriented** - для тренировок и учений
- 📊 **Learning from feedback** - аккумуляция опыта

**BCM Incident**:
- 🚨 **Incident management** - реагирование на реальные инциденты
- 🔄 **Workflow automation** - статус-машина (draft → resolved)
- 📧 **Communication tracking** - mail.thread
- 🏢 **Odoo-centric** - часть Odoo ERP

**Scenario Intelligence (наш)**:
- 🏗️ **System architecture testing** - описание поведения системы
- 🔧 **Module-to-User levels** - 4 уровня иерархии
- 🤖 **Execution automation** - 5 engines (Scenario, Call, Event, Chaos, Compliance)
- 🧠 **Self-learning** - pattern detection, prediction, auto-generation
- 🌐 **Platform-wide integration** - единый язык описания поведения всей платформы

---

## 💡 Возможности интеграции

### 1. **Использовать Scenario Orchestrator как L4 User Scenario Generator**

**Идея**: Scenario Orchestrator может генерировать **L4 User Scenarios** для нашей системы!

```yaml
# Existing: AI-generated BCM exercise scenario (Scenario Orchestrator)
POST /scenarios/generate → JSON scenario

# New: Convert to L4 YAML format
→ L4 User Scenario: "bcm-exercise-epidemic-response.v1.0.0.yaml"

integration:
  calls:
    - scenario: "L3-ai-platform-integration/ai-assisted-bia"
    - scenario: "L3-platform-infrastructure/monitoring-integration"
  events:
    subscribes: ["incident.detected", "exercise.started"]
    publishes: ["exercise.completed", "lesson.learned"]
```

**Польза**:
- ✅ Автоматическая генерация L4 сценариев через AI
- ✅ Используем существующий AI Orchestrator integration
- ✅ Learning system → Pattern Detector
- ✅ Exercise feedback → Scenario Learner statistics

**Реализация**:
```python
# /intelligent-core/scenario-intelligence/integration/orchestrator_adapter.py
class ScenarioOrchestratorAdapter:
    """Adapter для Scenario Orchestrator → L4 YAML"""

    async def generate_l4_scenario(self, category: str, complexity: int):
        # Call Scenario Orchestrator
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://scenario-orchestrator:8085/scenarios/generate",
                json={
                    "category": category,
                    "complexity": complexity,
                    "duration_hours": 4,
                    "participants": 10
                }
            )

        scenario_json = response.json()

        # Convert to L4 YAML format
        l4_scenario = self._convert_to_l4_yaml(scenario_json)

        # Save to registry + PostgreSQL + RAG
        await scenario_registry.register(l4_scenario)

        return l4_scenario

    def _convert_to_l4_yaml(self, scenario_json: dict) -> dict:
        """Convert Scenario Orchestrator JSON → L4 YAML"""
        return {
            "meta": {
                "id": f"l4-user-exercise-{scenario_json['scenario_id']}",
                "version": "1.0.0",
                "level": 4,
                "type": "user_workflow",
                "pillar": "operational_excellence",
                "tags": ["bcm-exercise", scenario_json["category"], "ai-generated"]
            },
            "description": {
                "title": scenario_json["title"],
                "summary": scenario_json["content_md"][:200],
                "business_value": "Train BCM team through realistic scenario",
                "user_experience": {
                    "role": "BCM Coordinator",
                    "estimated_time": f"{scenario_json['meta_duration']}h",
                    "complexity": scenario_json.get("complexity", 3)
                }
            },
            # ... convert full scenario
        }
```

---

### 2. **Использовать BCM Incident как источник реальных L4 сценариев**

**Идея**: Incident patterns → L4 Scenarios (на основе реальных инцидентов)

```python
# /intelligent-core/scenario-intelligence/integration/incident_adapter.py
class IncidentScenarioAdapter:
    """Convert real incidents → L4 scenarios для тренировок"""

    async def create_scenario_from_incident(self, incident_id: str):
        """Создать L4 scenario на основе реального инцидента"""

        # Get incident from Odoo BCM
        incident = await self.get_odoo_incident(incident_id)

        # Anonymize + generalize
        scenario = {
            "meta": {
                "id": f"l4-user-incident-{incident['incident_type']}",
                "level": 4,
                "type": "incident_response",
                "source": "real_incident_anonymized"
            },
            "description": {
                "title": f"{incident['incident_type'].title()} Incident Response",
                "summary": self._anonymize_description(incident["description"]),
                "severity": incident["severity"],
                "incident_type": incident["incident_type"]
            },
            "execution": {
                "phases": self._extract_phases_from_incident(incident)
            }
        }

        return scenario
```

**Польза**:
- ✅ Real-world scenarios на основе фактических инцидентов
- ✅ Continuous improvement - каждый инцидент → learning
- ✅ Анонимизированные тренировочные сценарии
- ✅ Pattern detection - типичные инциденты → автоматические сценарии

---

### 3. **Использовать Workflow Intelligence Production Modules**

**Идея**: Интегрировать готовые модули в Scenario Intelligence

**Что взять**:

1. **eventbus_integration.py** → наш `/integration/eventbus_integration.py`
   - ✅ Готовая интеграция с EventBus
   - ✅ 8 типов событий
   - 🔧 Модифицировать под scenario events

2. **error_handling.py** → добавить в `/engines/`
   - ✅ Retry decorators (tenacity)
   - ✅ Circuit Breaker pattern
   - 🔧 Использовать в ScenarioExecutionEngine

3. **process_metrics.py** → добавить в `/learning/metrics_collector.py`
   - ✅ Prometheus metrics
   - ✅ 9 готовых метрик
   - 🔧 Адаптировать для scenario execution metrics

4. **visualization.py** → добавить в `/api/visualization.py`
   - ✅ Mermaid, BPMN, Gantt charts
   - ✅ 31KB кода готового
   - 🔧 Визуализация L1→L4 call chains

5. **cache.py** → добавить в `/storage/cache_manager.py`
   - ✅ Redis caching
   - ✅ TTL стратегии
   - 🔧 Кэширование scenario executions, RAG queries

**Реализация**:
```bash
# Copy useful modules
cp /intelligent-core/workflow_intelligence/production_modules/error_handling.py \
   /intelligent-core/scenario-intelligence/utils/

cp /intelligent-core/workflow_intelligence/production_modules/process_metrics.py \
   /intelligent-core/scenario-intelligence/learning/metrics_collector.py

cp /intelligent-core/workflow_intelligence/production_modules/cache.py \
   /intelligent-core/scenario-intelligence/storage/cache_manager.py

# Интегрировать в engines
# engines/scenario_engine.py
from utils.error_handling import retry_with_backoff, CircuitBreaker

@retry_with_backoff(max_attempts=3)
async def execute_scenario(self, scenario_id: str):
    # ...
```

---

## 📊 Рекомендуемая интеграция

### **Архитектура интеграции**:

```
┌─────────────────────────────────────────────────────────────┐
│                   Scenario Intelligence                      │
│                    (Core System)                             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ L1: Modules  │  │ L2: Subsystems│  │ L3: Inter-sys│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │           L4: User Workflows                      │      │
│  │  ┌─────────────────┐  ┌──────────────────────┐  │      │
│  │  │ Manual Scenarios│  │ AI-Generated (from   │  │      │
│  │  │ (YAML files)    │  │ Scenario Orchestrator)│  │      │
│  │  └─────────────────┘  └──────────────────────┘  │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
                         ▲    │    ▼
                         │    │    │
      ┌──────────────────┼────┼────┼──────────────────┐
      │                  │    │    │                   │
      ▼                  ▼    ▼    ▼                   ▼
┌─────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Scenario   │  │   BCM Incident   │  │  Workflow Intel  │
│ Orchestrator │  │   (Odoo Module)  │  │ Production Mods  │
│              │  │                  │  │                  │
│ • AI Gen L4  │  │ • Real incidents │  │ • Error handling │
│ • Learning   │  │ • Patterns       │  │ • Metrics        │
│ • Feedback   │  │ • Workflows      │  │ • Visualization  │
└─────────────┘  └──────────────────┘  └──────────────────┘
```

### **Приоритеты**:

**ФАЗА 1: Quick Wins** (1-2 дня)
1. ✅ Интегрировать Workflow Intelligence production modules:
   - `error_handling.py` → `/utils/error_handling.py`
   - `process_metrics.py` → `/learning/metrics_collector.py`
   - `cache.py` → `/storage/cache_manager.py`
   - `visualization.py` → `/api/visualization.py`

2. ✅ Добавить retry + circuit breaker в ScenarioExecutionEngine

**ФАЗА 2: AI-Generation** (3-5 дней)
3. ✅ Создать `orchestrator_adapter.py` для Scenario Orchestrator
4. ✅ Реализовать `generate_l4_scenario()` через AI
5. ✅ Конвертация JSON → YAML L4 format
6. ✅ Auto-registration в Registry + DB + RAG

**ФАЗА 3: Real-World Learning** (1 неделя)
7. ✅ Создать `incident_adapter.py` для BCM Incident
8. ✅ Паттерны из реальных инцидентов → L4 scenarios
9. ✅ Incident statistics → Pattern Detector
10. ✅ Auto-generation improvements на основе реальных данных

---

## 🚀 Следующие шаги

### Немедленные действия:

1. **Скопировать полезные модули из Workflow Intelligence**
   ```bash
   cp production_modules/{error_handling,cache,process_metrics,visualization}.py \
      scenario-intelligence/{utils,storage,learning,api}/
   ```

2. **Создать адаптеры**:
   - `/integration/orchestrator_adapter.py` (Scenario Orchestrator)
   - `/integration/incident_adapter.py` (BCM Incident)

3. **Интегрировать в Auto-Generator**:
   - Auto-Generator может использовать Scenario Orchestrator для AI-generation
   - Pattern Detector может учиться на incident patterns

4. **Обновить документацию**:
   - Добавить integration architecture в `SYSTEM_MODULE_INTEGRATION.md`
   - Документировать адаптеры

---

## 📝 Выводы

### Что мы получаем от интеграции:

✅ **AI-powered L4 generation** через Scenario Orchestrator
✅ **Real-world learning** через BCM Incident patterns
✅ **Production-ready utilities** из Workflow Intelligence
✅ **Единая платформа** для всех типов сценариев
✅ **Self-improving system** - учимся на реальных данных

### Уникальность нашего решения:

🎯 **Scenario Intelligence** = Testing + Orchestration + Learning
🏗️ **4-level hierarchy** - от модулей до пользовательских workflows
🔄 **Integration hub** - объединяет 3 существующих подхода
🤖 **Self-learning** - паттерны, предсказания, автогенерация
📊 **Single Source of Truth** - YAML DSL для всей платформы

---

**Статус**: ✅ Анализ завершен
**Действие**: Готовы начать интеграцию
**Приоритет**: HIGH - есть готовые компоненты для быстрой интеграции
