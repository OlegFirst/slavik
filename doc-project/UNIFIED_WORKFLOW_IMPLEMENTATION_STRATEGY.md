# 🎯 Unified Workflow Engine - Стратегия Реализации

**Дата**: 2025-10-05
**Решение**: Реализовать как МОДУЛЬ внутри платформы (не отдельный сервис)

---

## ✅ ПРАВИЛЬНАЯ АРХИТЕКТУРА

### Почему внутри платформы:

```
✅ Плюсы модульного подхода:
- Меньше network overhead (нет HTTP между компонентами)
- Проще debugging (всё в одном кодебейзе)
- Единая база данных (PostgreSQL)
- Единый EventBus
- Легче поддерживать

❌ Минусы отдельного сервиса:
- Лишний network hop
- Сложнее синхронизация
- Дублирование конфигурации
- Больше DevOps overhead
```

### Текущее состояние платформы:

```python
# УЖЕ ЕСТЬ в platform-services:
platform-services/bia-service/
└── workflow/
    └── state_machine.py          # ← Базовая state machine

# УЖЕ ЕСТЬ в intelligent-core:
intelligent-core/workflow_intelligence/
├── core/workflow_engine.py       # ← AI-powered workflow
├── ai/context_advisor.py         # ← AI advisor
└── case_library/collector.py    # ← Learning

# УЖЕ ЕСТЬ BPMN прототип:
intelligent-core/bpmn-workflow/
└── main.py                       # ← BPMN engine (in-memory)
```

**Проблема:** Они НЕ связаны между собой!

**Решение:** Создать Integration Module внутри платформы

---

## 🏗️ Новая Архитектура (Модульная)

```
AI-Platform-ISO/
│
├── intelligent-core/
│   │
│   ├── unified-workflow/                    # 🆕 НОВЫЙ модуль
│   │   ├── __init__.py
│   │   │
│   │   ├── core/                            # Core integration
│   │   │   ├── __init__.py
│   │   │   ├── unified_engine.py            # Объединяет BPMN + Intelligence
│   │   │   └── adapter.py                   # Связующий слой
│   │   │
│   │   ├── bpmn/                            # BPMN слой (из bpmn-workflow)
│   │   │   ├── __init__.py
│   │   │   ├── engine.py                    # BPMNEngine
│   │   │   ├── parser.py                    # XML parsing
│   │   │   ├── executor.py                  # Process execution
│   │   │   └── models.py                    # Data models
│   │   │
│   │   ├── persistence/                     # 🆕 Database layer
│   │   │   ├── __init__.py
│   │   │   ├── repositories/
│   │   │   │   ├── process_repository.py
│   │   │   │   ├── instance_repository.py
│   │   │   │   └── task_repository.py
│   │   │   └── models.py                    # SQLAlchemy models
│   │   │
│   │   ├── visualization/                   # 🆕 Visual data preparation
│   │   │   ├── __init__.py
│   │   │   ├── renderer.py                  # BPMN → UI format
│   │   │   ├── monitor.py                   # Real-time state
│   │   │   └── analytics.py                 # Process mining
│   │   │
│   │   └── api/                             # 🆕 FastAPI routes (optional)
│   │       ├── __init__.py
│   │       ├── processes.py
│   │       └── visualization.py
│   │
│   ├── workflow_intelligence/               # ✅ СУЩЕСТВУЮЩИЙ
│   │   ├── core/
│   │   │   └── workflow_engine.py           # State machine + AI
│   │   ├── ai/
│   │   │   └── context_advisor.py
│   │   └── case_library/
│   │       └── collector.py
│   │
│   └── bpmn-workflow/                       # ⚠️ АРХИВИРОВАТЬ после миграции
│       └── main.py                          # (используем код, но не сервис)
│
├── platform-services/
│   ├── bia-service/
│   │   └── workflow/
│   │       └── state_machine.py             # ← Будет использовать unified-workflow
│   └── ...
│
└── infrastructure/
    └── database/
        └── migrations_source/
            └── 036_unified_workflow.sql     # 🆕 Migration
```

---

## 🔧 Как Это Работает

### 1. UnifiedEngine - Центральный класс

```python
# intelligent-core/unified-workflow/core/unified_engine.py

from typing import Dict, Any, Optional
from ..bpmn.engine import BPMNEngine
from workflow_intelligence.core import WorkflowEngine
from workflow_intelligence.ai import ContextAdvisor

class UnifiedWorkflowEngine:
    """
    Объединяет BPMN Orchestration + Workflow Intelligence

    Использование:
    - BCM сервисы импортируют этот класс
    - Получают и BPMN и AI capabilities
    """

    def __init__(
        self,
        tenant_id: str,
        module: str  # "bia", "risk", "compliance", etc
    ):
        self.tenant_id = tenant_id
        self.module = module

        # Initialize both engines
        self.bpmn_engine = BPMNEngine(
            persistence=True  # PostgreSQL, не in-memory!
        )

        self.workflow_engine = WorkflowEngine(
            module=module,
            tenant_id=tenant_id
        )

        self.ai_advisor = ContextAdvisor(
            workflow_engine=self.workflow_engine
        )

        # Setup event sync
        self._setup_event_sync()

    def _setup_event_sync(self):
        """Synchronize events between BPMN and Workflow Intelligence"""

        # BPMN events → Workflow Intelligence
        @self.bpmn_engine.on_event("bpmn.instance.started")
        async def on_bpmn_started(event):
            await self.workflow_engine.track_workflow_start(
                workflow_id=event.data["instance_id"],
                module=self.module,
                initial_data=event.data["variables"]
            )

        @self.bpmn_engine.on_event("bpmn.task.completed")
        async def on_bpmn_task_completed(event):
            await self.workflow_engine.track_action(
                workflow_id=event.data["instance_id"],
                action="task_completed",
                data=event.data["variables"]
            )

            # Get AI recommendations for next step
            advice = await self.ai_advisor.get_next_step_advice(
                workflow_id=event.data["instance_id"]
            )

            # Inject AI recommendations into BPMN
            if advice.get("recommendations"):
                await self.bpmn_engine.update_variables(
                    instance_id=event.data["instance_id"],
                    variables={"ai_advice": advice}
                )

    # ===== UNIFIED API =====

    async def start_process_from_bpmn(
        self,
        bpmn_xml: str,
        initial_variables: Dict[str, Any]
    ) -> str:
        """Start process from BPMN visual model"""

        # 1. Deploy BPMN
        process_id = await self.bpmn_engine.deploy_process(
            bpmn_xml=bpmn_xml,
            tenant_id=self.tenant_id
        )

        # 2. Get AI startup advice
        startup_advice = await self.ai_advisor.get_startup_advice(
            process_id=process_id,
            module=self.module,
            org_context=initial_variables.get("org_context", {})
        )

        # 3. Enrich with AI
        enriched_vars = {
            **initial_variables,
            "ai_startup_advice": startup_advice
        }

        # 4. Start instance
        instance_id = await self.bpmn_engine.start_process(
            process_id=process_id,
            variables=enriched_vars
        )

        return instance_id

    async def start_process_from_template(
        self,
        template_name: str,  # "bia_standard", "risk_assessment"
        initial_variables: Dict[str, Any]
    ) -> str:
        """Start from predefined template (YAML)"""

        # Use Workflow Intelligence (не BPMN)
        workflow_id = await self.workflow_engine.start(
            workflow_definition=template_name,
            initial_data=initial_variables
        )

        return workflow_id

    async def get_visual_state(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Get state for visual representation"""

        # Check if BPMN or template-based
        if await self.bpmn_engine.has_instance(workflow_id):
            return await self._get_bpmn_visual_state(workflow_id)
        else:
            return await self._get_template_visual_state(workflow_id)

    async def _get_bpmn_visual_state(self, instance_id: str):
        """Visual state for BPMN process"""

        # BPMN state
        instance = await self.bpmn_engine.get_instance(instance_id)
        process = await self.bpmn_engine.get_process(instance.process_id)
        tasks = await self.bpmn_engine.get_active_tasks(instance_id)

        # Workflow Intelligence context
        context = await self.workflow_engine.get_context(instance_id)

        # AI predictions
        predictions = await self.ai_advisor.predict_outcome(instance_id)

        return {
            "type": "bpmn",
            "bpmn_xml": process.bpmn_xml,
            "current_activities": instance.current_activities,
            "active_tasks": [
                {
                    **task.dict(),
                    "ai_recommendations": await self.ai_advisor.get_task_advice(
                        workflow_id=instance_id,
                        task_id=task.id
                    )
                }
                for task in tasks
            ],
            "workflow_context": context,
            "predictions": predictions,
            "visualization_hints": {
                "highlight": instance.current_activities,
                "show_ai_overlay": True
            }
        }

    async def _get_template_visual_state(self, workflow_id: str):
        """Visual state for template-based workflow (без BPMN XML)"""

        context = await self.workflow_engine.get_context(workflow_id)
        predictions = await self.ai_advisor.predict_outcome(workflow_id)

        return {
            "type": "template",
            "current_stage": context.current_stage,
            "progress": context.progress_percentage,
            "available_actions": context.available_actions,
            "gaps": context.gaps,
            "ai_recommendations": await self.ai_advisor.get_contextual_advice(
                workflow_id=workflow_id
            ),
            "predictions": predictions
        }

    async def complete_task(
        self,
        task_id: str,
        completed_by: str,
        variables: Dict[str, Any]
    ):
        """Complete task (works for both BPMN and template)"""

        # Determine type
        task = await self.bpmn_engine.get_task(task_id)

        # Complete in BPMN
        await self.bpmn_engine.complete_task(
            task_id=task_id,
            variables=variables
        )

        # Events auto-sync to Workflow Intelligence via _setup_event_sync()
```

---

### 2. Использование в BCM сервисах

```python
# platform-services/bia-service/main.py

from intelligent_core.unified_workflow import UnifiedWorkflowEngine

class BIAService:
    def __init__(self, tenant_id: str):
        # Initialize unified workflow
        self.workflow = UnifiedWorkflowEngine(
            tenant_id=tenant_id,
            module="bia"
        )

    async def start_bia_visual(
        self,
        org_id: str,
        bpmn_xml: Optional[str] = None
    ) -> str:
        """Start BIA with visual BPMN or standard template"""

        org = await db.get_organization(org_id)

        if bpmn_xml:
            # User created custom BPMN process
            instance_id = await self.workflow.start_process_from_bpmn(
                bpmn_xml=bpmn_xml,
                initial_variables={
                    "org_id": org_id,
                    "org_context": {
                        "industry": org.industry,
                        "size": org.size
                    }
                }
            )
        else:
            # Use standard template
            instance_id = await self.workflow.start_process_from_template(
                template_name="bia_standard",
                initial_variables={
                    "org_id": org_id,
                    "org_context": {
                        "industry": org.industry,
                        "size": org.size
                    }
                }
            )

        return instance_id

    async def get_bia_visual_state(self, bia_id: str):
        """Get state for UI visualization"""

        return await self.workflow.get_visual_state(bia_id)

# API endpoint
@router.get("/bia/{bia_id}/visual")
async def get_bia_visualization(
    bia_id: str,
    tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Returns visual state for frontend

    Frontend can:
    - Render BPMN diagram with bpmn-js (if type="bpmn")
    - Show custom UI with progress (if type="template")
    - Display AI recommendations
    - Show predictions
    """
    bia_service = BIAService(tenant_id)
    return await bia_service.get_bia_visual_state(bia_id)
```

---

### 3. Database Migration

```sql
-- infrastructure/database/migrations_source/036_unified_workflow.sql

-- BPMN Processes
CREATE TABLE IF NOT EXISTS workflow.bpmn_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    module TEXT NOT NULL,  -- "bia", "risk", etc
    name TEXT NOT NULL,
    bpmn_xml TEXT NOT NULL,
    version TEXT DEFAULT '1.0',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- BPMN Instances
CREATE TABLE IF NOT EXISTS workflow.bpmn_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID REFERENCES workflow.bpmn_processes(id),
    tenant_id TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE',
    variables JSONB DEFAULT '{}',
    current_activities TEXT[] DEFAULT '{}',

    -- Link to Workflow Intelligence
    workflow_intelligence_context JSONB,  -- Cache от WorkflowEngine

    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- BPMN Tasks
CREATE TABLE IF NOT EXISTS workflow.bpmn_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES workflow.bpmn_instances(id) ON DELETE CASCADE,
    activity_id TEXT NOT NULL,
    name TEXT NOT NULL,
    assignee TEXT,
    status TEXT DEFAULT 'ACTIVE',
    variables JSONB DEFAULT '{}',

    -- AI enhancements
    ai_recommendations JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_bpmn_instances_tenant ON workflow.bpmn_instances(tenant_id);
CREATE INDEX idx_bpmn_tasks_assignee ON workflow.bpmn_tasks(assignee, status);
```

---

## 🎯 План Реализации (Пошаговый)

### Фаза 1: Базовая Интеграция (Я могу сам - 3-5 дней)

**Шаг 1: Создать структуру модуля**
```bash
mkdir -p intelligent-core/unified-workflow/{core,bpmn,persistence,visualization,api}
touch intelligent-core/unified-workflow/__init__.py
```

**Шаг 2: Мигрировать BPMN код**
```bash
# Скопировать из bpmn-workflow
cp intelligent-core/bpmn-workflow/main.py \
   intelligent-core/unified-workflow/bpmn/engine.py

# Разбить на модули
# - parser.py (XML parsing)
# - executor.py (process execution)
# - models.py (data models)
```

**Шаг 3: Создать UnifiedEngine**
```python
# intelligent-core/unified-workflow/core/unified_engine.py
# Минимальная версия с базовой интеграцией
```

**Шаг 4: Database migration**
```bash
# Создать 036_unified_workflow.sql
# Применить миграцию
```

**Deliverable:**
- ✅ Модуль создан
- ✅ BPMN код мигрирован
- ✅ UnifiedEngine работает (базовая версия)
- ✅ БД готова

---

### Фаза 2: Persistence Layer (Я могу сам - 2-3 дня)

**Заменить in-memory на PostgreSQL**

```python
# intelligent-core/unified-workflow/persistence/repositories/process_repository.py

class ProcessRepository:
    def __init__(self, db_session):
        self.db = db_session

    async def save_process(self, process: BPMNProcess) -> str:
        result = await self.db.execute("""
            INSERT INTO workflow.bpmn_processes
            (tenant_id, module, name, bpmn_xml, version)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """, process.tenant_id, process.module, process.name,
            process.bpmn_xml, process.version)

        return result.fetchone()['id']

    async def get_process(self, process_id: str) -> BPMNProcess:
        result = await self.db.execute("""
            SELECT * FROM workflow.bpmn_processes WHERE id = $1
        """, process_id)

        row = result.fetchone()
        return BPMNProcess(**row)

# Similar for InstanceRepository, TaskRepository
```

**Deliverable:**
- ✅ Нет in-memory storage
- ✅ PostgreSQL persistence
- ✅ Redis caching (optional)

---

### Фаза 3: Event Synchronization (Я могу сам - 2-3 дня)

**Связать события BPMN ↔ Workflow Intelligence**

```python
# intelligent-core/unified-workflow/core/unified_engine.py

def _setup_event_sync(self):
    """Полная синхронизация"""

    # BPMN → Workflow Intelligence
    self.bpmn_engine.on_event("bpmn.instance.started",
                              self._on_bpmn_started)
    self.bpmn_engine.on_event("bpmn.task.created",
                              self._on_bpmn_task_created)
    self.bpmn_engine.on_event("bpmn.task.completed",
                              self._on_bpmn_task_completed)

    # Workflow Intelligence → BPMN (if needed)
    # ...

async def _on_bpmn_task_completed(self, event):
    # Update Workflow Intelligence
    await self.workflow_engine.track_action(...)

    # Get AI advice
    advice = await self.ai_advisor.get_next_step_advice(...)

    # Update BPMN variables
    await self.bpmn_engine.update_variables(...)
```

**Deliverable:**
- ✅ События синхронизированы
- ✅ AI advice инжектится в BPMN
- ✅ Case Library собирает данные

---

### Фаза 4: Frontend Integration (НУЖЕН Frontend Dev - 5-7 дней)

**React components + bpmn-js**

```typescript
// frontend/src/components/BPMNMonitor.tsx

import BpmnViewer from 'bpmn-js/lib/Viewer';

export const BPMNMonitor = ({ workflowId }) => {
  const { data } = useQuery(`/api/workflows/${workflowId}/visual`);

  useEffect(() => {
    if (!data) return;

    const viewer = new BpmnViewer({ container });
    viewer.importXML(data.bpmn_xml);

    // Highlight current activities
    const canvas = viewer.get('canvas');
    data.current_activities.forEach(activityId => {
      canvas.addMarker(activityId, 'highlight-active');
    });

    // Add AI overlays
    const overlays = viewer.get('overlays');
    data.active_tasks.forEach(task => {
      overlays.add(task.activity_id, {
        html: `<div class="ai-tip">${task.ai_recommendations[0]}</div>`
      });
    });

  }, [data]);

  return <div ref={containerRef} />;
};
```

**Deliverable:**
- ✅ Visual BPMN viewer
- ✅ Real-time updates
- ✅ AI recommendations overlay

---

### Фаза 5: Visualization API (Я могу сам - 2 дня)

```python
# intelligent-core/unified-workflow/visualization/renderer.py

class BPMNRenderer:
    async def prepare_visual_data(self, instance_id: str):
        """Prepare data for frontend"""

        instance = await db.get_instance(instance_id)
        process = await db.get_process(instance.process_id)
        tasks = await db.get_active_tasks(instance_id)

        # Get AI context
        context = await workflow_engine.get_context(instance_id)
        predictions = await ai_advisor.predict_outcome(instance_id)

        return {
            "bpmn_xml": process.bpmn_xml,
            "current_activities": instance.current_activities,
            "tasks": [
                {
                    "id": t.id,
                    "activity_id": t.activity_id,
                    "name": t.name,
                    "ai_tip": self._generate_task_tip(t, context)
                }
                for t in tasks
            ],
            "ai_panel": {
                "recommendations": context.get("ai_recommendations", []),
                "predictions": predictions,
                "similar_cases": await case_library.find_similar(...)
            }
        }
```

---

## 👥 Разделение на Команды

### Вариант 1: Я делаю всё (медленно, но возможно)

**Timeline:** 3-4 недели
**Риски:**
- Frontend может быть слабоват (я не React expert)
- Нет code review
- Одна точка отказа (я)

**Подходит если:** Нет бюджета на команду, нет спешки

---

### Вариант 2: Мини-команда (2 человека)

**Backend Dev (я):**
- ✅ Phases 1-3: Integration + Persistence + Events (1-2 недели)
- ✅ Phase 5: Visualization API (2 дня)
- ✅ Testing + Documentation

**Frontend Dev:**
- ✅ Phase 4: React + bpmn-js integration (1 неделя)
- ✅ Real-time updates (WebSocket)
- ✅ UI/UX polish

**Timeline:** 2 недели parallel work
**Риски:** Минимальны
**Подходит если:** Есть бюджет на 1 frontend dev

---

### Вариант 3: Полная команда (3-4 человека)

**Backend Lead (я):**
- Architecture oversight
- Integration Layer
- Code review

**Backend Dev 2:**
- Persistence Layer
- Testing
- DevOps

**Frontend Dev:**
- React components
- bpmn-js integration

**UI/UX Designer:**
- Process visualization design
- User flow

**Timeline:** 1-1.5 недели
**Подходит если:** Production deadline tight

---

## 🎯 Моя Рекомендация

### **Hybrid Approach: Я + 1 Frontend Dev**

**Я делаю (backend - моя зона комфорта):**
```
Week 1:
✅ Phase 1: Setup + Migration (3 дня)
✅ Phase 2: Integration Layer (2 дня)

Week 2:
✅ Phase 3: Persistence (2 дня)
✅ Phase 5: Visualization API (1 день)
✅ Testing + Docs (2 дня)
```

**Frontend Dev делает (параллельно):**
```
Week 1-2:
✅ Phase 4: React components
✅ bpmn-js integration
✅ Real-time updates
✅ UI polish
```

**Total:** 2 недели, production-ready

---

## 📊 Comparison Matrix

| Approach | Timeline | Quality | Risk | Cost |
|----------|----------|---------|------|------|
| **Solo (я)** | 3-4 weeks | Good (backend), OK (frontend) | Medium | $0 |
| **Me + 1 Frontend** | 2 weeks | Excellent | Low | $ |
| **Full Team** | 1-1.5 weeks | Excellent | Very Low | $$$ |

---

## 🚀 Что делать дальше?

**Option A: Я начинаю Phase 1 сейчас**
```bash
# Создаю структуру
mkdir -p intelligent-core/unified-workflow/...

# Мигрирую BPMN код
# ...

# Через 3-5 дней - рабочий прототип
```

**Option B: Найти frontend dev, затем parallel work**
```
Me: Backend (Phases 1-3, 5)
Frontend Dev: UI (Phase 4)
Timeline: 2 weeks
```

**Option C: Подождать команду, затем full speed**
```
Team of 3-4
Timeline: 1-1.5 weeks
```

---

## ❓ Твое Решение?

1. **Делаю сам?** (медленно, но бесплатно)
2. **Ищем frontend dev?** (оптимально)
3. **Собираем команду?** (быстро, но дорого)
4. **Начинаю Phase 1 прототип, решаем по ходу?** (гибко)

Что выбираешь?
