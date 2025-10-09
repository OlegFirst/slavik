# 🔄 BPMN + Workflow Intelligence - План Интеграции

**Дата**: 2025-10-05
**Цель**: Объединить лучшее из двух систем в одно полноценное решение

---

## 🎯 Что получим в результате

**Unified Workflow Intelligence Platform с BPMN визуализацией:**

✅ **От BPMN Service:**
- BPMN 2.0 XML parsing и execution
- Визуальное моделирование процессов
- Task assignment и inbox
- Industry standard совместимость

✅ **От Workflow Intelligence:**
- AI-powered recommendations
- Case Library и self-learning
- ML predictions
- Context-aware advice
- Production-ready persistence (PostgreSQL + Redis)

✅ **Новое:**
- Визуальный BPMN редактор в UI
- AI помогает моделировать процессы
- Visual process mining
- Real-time process analytics

---

## 🏗️ Архитектура Интеграции

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (UI)                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ BPMN Modeler     │  │ Process Monitor  │  │ AI Assistant  │ │
│  │ (bpmn-js)        │  │ (live tracking)  │  │ (contextual)  │ │
│  │                  │  │                  │  │               │ │
│  │ - Drag & drop    │  │ - Active tasks   │  │ - Suggestions │ │
│  │ - Visual editor  │  │ - Bottlenecks    │  │ - Best cases  │ │
│  │ - Export XML     │  │ - Metrics        │  │ - Predictions │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              UNIFIED WORKFLOW ENGINE (Backend)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  BPMN Orchestration Layer                              │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  ✅ BPMNEngine (from bpmn-workflow)                     │   │
│  │     - Parse BPMN 2.0 XML                                │   │
│  │     - Execute process instances                         │   │
│  │     - Manage tasks (create, assign, complete)           │   │
│  │     - Handle gateways, timers, events                   │   │
│  │                                                          │   │
│  │  🆕 Enhanced with:                                       │   │
│  │     - PostgreSQL persistence (не in-memory)             │   │
│  │     - Redis для distributed locking                     │   │
│  │     - EventBus integration (publish всех событий)       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Workflow Intelligence Layer                            │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  ✅ WorkflowEngine (from workflow_intelligence)         │   │
│  │     - State tracking и context                          │   │
│  │     - Event publishing                                  │   │
│  │     - Validation rules                                  │   │
│  │                                                          │   │
│  │  ✅ ContextAdvisor (AI)                                 │   │
│  │     - Contextual recommendations                        │   │
│  │     - Process improvement suggestions                   │   │
│  │     - Bottleneck detection                              │   │
│  │                                                          │   │
│  │  ✅ CaseLibrary (Learning)                              │   │
│  │     - Auto-collect completed processes                  │   │
│  │     - Find similar cases                                │   │
│  │     - Benchmarking                                      │   │
│  │                                                          │   │
│  │  ✅ MLPredictor (Predictions)                           │   │
│  │     - Success probability                               │   │
│  │     - Duration estimation                               │   │
│  │     - Risk factors                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Integration Layer (NEW)                                │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  BPMNWorkflowAdapter - связывает оба слоя:              │   │
│  │                                                          │   │
│  │  1. BPMN events → Workflow Intelligence events          │   │
│  │     bpmn.task.created → workflow.stage.changed          │   │
│  │                                                          │   │
│  │  2. Workflow context → BPMN process variables           │   │
│  │     AI recommendations → task assignments               │   │
│  │                                                          │   │
│  │  3. Unified API:                                        │   │
│  │     POST /workflows/{id}/model  (BPMN XML)              │   │
│  │     POST /workflows/{id}/start                          │   │
│  │     GET  /workflows/{id}/advice (AI)                    │   │
│  │     GET  /workflows/{id}/visual (для UI)                │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ PostgreSQL   │  │ Redis        │  │ Vector DB            │  │
│  │              │  │              │  │ (pgvector)           │  │
│  │ - Processes  │  │ - Tasks lock │  │                      │  │
│  │ - Instances  │  │ - Cache      │  │ - Cases semantic     │  │
│  │ - Tasks      │  │ - Sessions   │  │ - Similarity search  │  │
│  │ - Cases      │  │              │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Модульная Структура

```
intelligent-core/
└── unified-workflow-engine/          # НОВЫЙ объединённый модуль
    ├── README.md
    ├── requirements.txt
    │
    ├── bpmn/                          # BPMN Orchestration
    │   ├── __init__.py
    │   ├── engine.py                  # BPMNEngine (из bpmn-workflow)
    │   ├── parser.py                  # BPMN XML parsing
    │   ├── executor.py                # Process execution
    │   ├── tasks.py                   # Task management
    │   └── models.py                  # BPMNProcess, ProcessInstance, Task
    │
    ├── intelligence/                  # Workflow Intelligence
    │   ├── __init__.py
    │   ├── workflow_engine.py         # WorkflowEngine (из workflow_intelligence)
    │   ├── context_advisor.py         # AI Advisor
    │   ├── case_library.py            # Learning
    │   ├── ml_predictor.py            # Predictions
    │   └── governance.py              # Rules & safety
    │
    ├── integration/                   # Связующий слой (NEW)
    │   ├── __init__.py
    │   ├── adapter.py                 # BPMNWorkflowAdapter
    │   ├── event_mapper.py            # Map BPMN events ↔ Workflow events
    │   ├── context_bridge.py          # Sync context between layers
    │   └── unified_api.py             # Single API для обоих слоев
    │
    ├── persistence/                   # Database layer
    │   ├── __init__.py
    │   ├── repositories/
    │   │   ├── process_repository.py  # BPMN processes
    │   │   ├── instance_repository.py # Process instances
    │   │   ├── task_repository.py     # Tasks
    │   │   └── case_repository.py     # Cases
    │   └── migrations/
    │       └── 035_unified_workflow.sql
    │
    ├── visualization/                 # Visual layer (NEW)
    │   ├── __init__.py
    │   ├── bpmn_renderer.py           # Convert BPMN XML → UI format
    │   ├── process_monitor.py         # Real-time tracking
    │   ├── analytics.py               # Process mining analytics
    │   └── export.py                  # Export to PNG, SVG, PDF
    │
    ├── api/                           # FastAPI routes
    │   ├── __init__.py
    │   ├── processes.py               # CRUD для BPMN processes
    │   ├── instances.py               # Process instances
    │   ├── tasks.py                   # Task management
    │   ├── intelligence.py            # AI advice endpoints
    │   └── visualization.py           # Visual data endpoints
    │
    └── tests/
        ├── test_bpmn_engine.py
        ├── test_workflow_intelligence.py
        └── test_integration.py
```

---

## 🔌 Integration Layer - Как работает

### BPMNWorkflowAdapter

```python
# integration/adapter.py

from typing import Dict, Any
from ..bpmn.engine import BPMNEngine
from ..intelligence.workflow_engine import WorkflowEngine
from ..intelligence.context_advisor import ContextAdvisor

class BPMNWorkflowAdapter:
    """
    Связывает BPMN Orchestration и Workflow Intelligence

    Роль:
    1. Синхронизирует состояние между двумя engines
    2. Маппит события
    3. Обогащает BPMN context данными от AI
    """

    def __init__(
        self,
        bpmn_engine: BPMNEngine,
        workflow_engine: WorkflowEngine,
        ai_advisor: ContextAdvisor
    ):
        self.bpmn = bpmn_engine
        self.workflow = workflow_engine
        self.ai = ai_advisor

        # Subscribe to BPMN events
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Map BPMN events → Workflow Intelligence"""

        @self.bpmn.on_event("bpmn.instance.started")
        async def on_process_started(event):
            # Notify Workflow Intelligence
            await self.workflow.track_workflow_start(
                workflow_id=event.data["instance_id"],
                module=self._detect_module(event.data["process_id"]),
                initial_data=event.data["variables"]
            )

            # Get AI advice for starting
            advice = await self.ai.get_startup_advice(
                workflow_id=event.data["instance_id"]
            )

            # Add AI suggestions as process variables
            await self.bpmn.update_variables(
                instance_id=event.data["instance_id"],
                variables={"ai_startup_advice": advice}
            )

        @self.bpmn.on_event("bpmn.task.created")
        async def on_task_created(event):
            # Track stage change
            await self.workflow.track_stage_change(
                workflow_id=event.data["instance_id"],
                new_stage=event.data["activity_id"]
            )

            # Get AI recommendations for this task
            recommendations = await self.ai.get_task_recommendations(
                workflow_id=event.data["instance_id"],
                task_id=event.data["task_id"],
                activity=event.data["activity_id"]
            )

            # Enhance task with AI data
            await self.bpmn.update_task(
                task_id=event.data["task_id"],
                data={"ai_recommendations": recommendations}
            )

        @self.bpmn.on_event("bpmn.task.completed")
        async def on_task_completed(event):
            # Update workflow context
            await self.workflow.track_action(
                workflow_id=event.data["instance_id"],
                action="task_completed",
                data=event.data["variables"]
            )

            # Check if can proceed to next stage
            context = await self.workflow.get_context(
                workflow_id=event.data["instance_id"]
            )

            # If gaps exist, add AI help
            if context.get("gaps"):
                help_advice = await self.ai.get_gap_resolution_advice(
                    workflow_id=event.data["instance_id"],
                    gaps=context["gaps"]
                )

                # Create advisory task in BPMN
                await self.bpmn.create_advisory_task(
                    instance_id=event.data["instance_id"],
                    advice=help_advice
                )

        @self.bpmn.on_event("bpmn.instance.completed")
        async def on_process_completed(event):
            # Collect case for learning
            from ..intelligence.case_library import CaseCollector

            collector = CaseCollector()
            case = await collector.create_case(
                workflow_id=event.data["instance_id"],
                bpmn_process_id=event.data["process_id"],
                variables=event.data["variables"]
            )

            await self.workflow.case_library.save(case)

            # Trigger ML retraining
            await self.ai.ml_predictor.schedule_retraining()

    async def start_visual_process(
        self,
        bpmn_xml: str,
        tenant_id: str,
        initial_variables: Dict[str, Any]
    ) -> str:
        """
        Unified API: Start process from BPMN visual model

        Workflow:
        1. Deploy BPMN process
        2. Register with Workflow Intelligence
        3. Get AI startup advice
        4. Start instance with enriched context
        """

        # 1. Deploy BPMN
        process_id = await self.bpmn.deploy_process(
            bpmn_xml=bpmn_xml,
            tenant_id=tenant_id
        )

        # 2. Register workflow definition with Intelligence
        module = self._detect_module(process_id)
        await self.workflow.register_workflow_definition(
            workflow_id=process_id,
            module=module,
            source="bpmn_visual"
        )

        # 3. Get AI startup advice
        startup_advice = await self.ai.get_startup_advice(
            process_id=process_id,
            initial_variables=initial_variables
        )

        # 4. Enrich variables with AI
        enriched_variables = {
            **initial_variables,
            "ai_startup_advice": startup_advice,
            "similar_cases": await self.ai.find_similar_cases(
                module=module,
                org_context=initial_variables.get("org_context", {})
            )
        }

        # 5. Start instance
        instance_id = await self.bpmn.start_process(
            process_id=process_id,
            tenant_id=tenant_id,
            variables=enriched_variables
        )

        return instance_id

    async def get_visual_state(self, instance_id: str) -> Dict[str, Any]:
        """
        Get data for visual representation

        Returns:
        - BPMN XML with highlighted current activities
        - Active tasks with AI recommendations
        - Process metrics and predictions
        - Bottleneck analysis
        """

        # BPMN state
        instance = await self.bpmn.get_instance(instance_id)
        process = await self.bpmn.get_process(instance.process_id)
        active_tasks = await self.bpmn.get_tasks(
            instance_id=instance_id,
            status="ACTIVE"
        )

        # Workflow Intelligence context
        context = await self.workflow.get_context(instance_id)

        # AI predictions
        predictions = await self.ai.predict_outcome(instance_id)

        # Process mining analytics
        analytics = await self._calculate_process_analytics(instance_id)

        return {
            "bpmn_xml": process.bpmn_xml,
            "current_activities": instance.current_activities,
            "active_tasks": [
                {
                    **task.dict(),
                    "ai_recommendations": task.variables.get("ai_recommendations", [])
                }
                for task in active_tasks
            ],
            "workflow_context": context,
            "predictions": predictions,
            "analytics": analytics,
            "visualization_hints": {
                "highlight_activities": instance.current_activities,
                "show_bottlenecks": analytics["bottlenecks"],
                "show_duration_overlay": True
            }
        }

    def _detect_module(self, process_id: str) -> str:
        """Detect BCM module from process ID"""
        if "bia" in process_id.lower():
            return "bia"
        elif "risk" in process_id.lower():
            return "risk"
        elif "incident" in process_id.lower():
            return "response"
        elif "exercise" in process_id.lower():
            return "exercise"
        elif "compliance" in process_id.lower():
            return "compliance"
        return "generic"

    async def _calculate_process_analytics(self, instance_id: str):
        """Process mining analytics"""
        # TODO: Implement process mining
        # - Average duration per activity
        # - Bottleneck detection
        # - Path analysis
        return {}
```

---

## 🗄️ Database Schema

```sql
-- migration: 035_unified_workflow.sql

-- BPMN Processes (definitions)
CREATE TABLE IF NOT EXISTS workflow.bpmn_processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    bpmn_xml TEXT NOT NULL,
    version TEXT DEFAULT '1.0',
    is_active BOOLEAN DEFAULT true,
    module TEXT,  -- bia, risk, compliance, etc
    created_by TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bpmn_processes_tenant ON workflow.bpmn_processes(tenant_id);
CREATE INDEX idx_bpmn_processes_module ON workflow.bpmn_processes(module);

-- BPMN Process Instances (running processes)
CREATE TABLE IF NOT EXISTS workflow.bpmn_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id UUID REFERENCES workflow.bpmn_processes(id),
    tenant_id TEXT NOT NULL,
    status TEXT DEFAULT 'ACTIVE',  -- ACTIVE, COMPLETED, SUSPENDED, TERMINATED
    variables JSONB DEFAULT '{}',
    current_activities TEXT[] DEFAULT '{}',
    started_by TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Link to Workflow Intelligence
    workflow_intelligence_id TEXT,  -- Link to WorkflowEngine tracking

    CONSTRAINT valid_status CHECK (status IN ('ACTIVE', 'COMPLETED', 'SUSPENDED', 'TERMINATED'))
);

CREATE INDEX idx_bpmn_instances_tenant ON workflow.bpmn_instances(tenant_id);
CREATE INDEX idx_bpmn_instances_status ON workflow.bpmn_instances(status);
CREATE INDEX idx_bpmn_instances_process ON workflow.bpmn_instances(process_id);
CREATE INDEX idx_bpmn_instances_workflow ON workflow.bpmn_instances(workflow_intelligence_id);

-- BPMN Tasks
CREATE TABLE IF NOT EXISTS workflow.bpmn_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES workflow.bpmn_instances(id) ON DELETE CASCADE,
    activity_id TEXT NOT NULL,
    name TEXT NOT NULL,
    task_type TEXT NOT NULL,  -- USER_TASK, SERVICE_TASK, SCRIPT_TASK
    assignee TEXT,
    status TEXT DEFAULT 'ACTIVE',  -- ACTIVE, COMPLETED, CANCELLED
    variables JSONB DEFAULT '{}',

    -- AI enhancements
    ai_recommendations JSONB,
    ai_predicted_duration_hours FLOAT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    CONSTRAINT valid_task_status CHECK (status IN ('ACTIVE', 'COMPLETED', 'CANCELLED'))
);

CREATE INDEX idx_bpmn_tasks_instance ON workflow.bpmn_tasks(instance_id);
CREATE INDEX idx_bpmn_tasks_assignee ON workflow.bpmn_tasks(assignee);
CREATE INDEX idx_bpmn_tasks_status ON workflow.bpmn_tasks(status);

-- Process Analytics (for process mining)
CREATE TABLE IF NOT EXISTS workflow.process_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id UUID REFERENCES workflow.bpmn_instances(id),
    activity_id TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    variables_snapshot JSONB,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_process_analytics_instance ON workflow.process_analytics(instance_id);
CREATE INDEX idx_process_analytics_activity ON workflow.process_analytics(activity_id);

-- Enable RLS
ALTER TABLE workflow.bpmn_processes ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow.bpmn_instances ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow.bpmn_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow.process_analytics ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY tenant_isolation_bpmn_processes ON workflow.bpmn_processes
    FOR ALL USING (tenant_id = current_setting('app.current_tenant')::text);

CREATE POLICY tenant_isolation_bpmn_instances ON workflow.bpmn_instances
    FOR ALL USING (tenant_id = current_setting('app.current_tenant')::text);

CREATE POLICY tenant_isolation_bpmn_tasks ON workflow.bpmn_tasks
    FOR ALL USING (
        instance_id IN (
            SELECT id FROM workflow.bpmn_instances
            WHERE tenant_id = current_setting('app.current_tenant')::text
        )
    );

CREATE POLICY tenant_isolation_process_analytics ON workflow.process_analytics
    FOR ALL USING (
        instance_id IN (
            SELECT id FROM workflow.bpmn_instances
            WHERE tenant_id = current_setting('app.current_tenant')::text
        )
    );
```

---

## 🎨 Frontend - Visual BPMN Modeler

### Technology Stack

```json
{
  "visualization": {
    "bpmn-js": "^17.0.0",  // Visual BPMN modeler/viewer
    "bpmn-js-properties-panel": "^5.0.0",  // Properties editor
    "diagram-js": "^14.0.0"  // Underlying diagram framework
  },
  "ui": {
    "react": "^18.0.0",
    "react-flow": "^11.0.0",  // For custom process views
    "d3": "^7.0.0"  // Process mining visualizations
  }
}
```

### UI Components

```typescript
// frontend/src/components/workflow/BPMNModeler.tsx

import BpmnModeler from 'bpmn-js/lib/Modeler';
import { useEffect, useRef, useState } from 'react';

interface BPMNModelerProps {
  initialXML?: string;
  onSave?: (xml: string) => void;
  readonly?: boolean;
}

export const BPMNModeler: React.FC<BPMNModelerProps> = ({
  initialXML,
  onSave,
  readonly = false
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [modeler, setModeler] = useState<BpmnModeler | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const bpmnModeler = new BpmnModeler({
      container: containerRef.current,
      keyboard: { bindTo: document }
    });

    setModeler(bpmnModeler);

    // Load initial diagram
    if (initialXML) {
      bpmnModeler.importXML(initialXML);
    } else {
      // Load empty diagram
      bpmnModeler.createDiagram();
    }

    return () => {
      bpmnModeler.destroy();
    };
  }, []);

  const handleSave = async () => {
    if (!modeler) return;

    const { xml } = await modeler.saveXML({ format: true });
    onSave?.(xml);
  };

  return (
    <div className="bpmn-modeler-container">
      <div className="toolbar">
        <button onClick={handleSave}>Save BPMN</button>
        <button onClick={() => modeler?.get('zoomScroll').zoom('fit-viewport')}>
          Fit to Screen
        </button>
      </div>
      <div ref={containerRef} className="bpmn-canvas" />
    </div>
  );
};
```

```typescript
// frontend/src/components/workflow/ProcessMonitor.tsx

import BpmnViewer from 'bpmn-js/lib/Viewer';
import { useEffect, useRef } from 'react';
import { useWorkflowState } from '@/hooks/useWorkflowState';

interface ProcessMonitorProps {
  instanceId: string;
}

export const ProcessMonitor: React.FC<ProcessMonitorProps> = ({ instanceId }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [viewer, setViewer] = useState<BpmnViewer | null>(null);
  const { state, tasks, predictions } = useWorkflowState(instanceId);

  useEffect(() => {
    if (!containerRef.current || !state) return;

    const bpmnViewer = new BpmnViewer({
      container: containerRef.current
    });

    setViewer(bpmnViewer);

    // Load BPMN XML
    bpmnViewer.importXML(state.bpmn_xml);

    return () => {
      bpmnViewer.destroy();
    };
  }, [state]);

  useEffect(() => {
    if (!viewer) return;

    const canvas = viewer.get('canvas');
    const overlays = viewer.get('overlays');

    // Highlight current activities
    state?.current_activities?.forEach(activityId => {
      canvas.addMarker(activityId, 'highlight-active');

      // Add overlay with task info
      const task = tasks.find(t => t.activity_id === activityId);
      if (task) {
        overlays.add(activityId, {
          position: { top: -20, right: 10 },
          html: `<div class="task-overlay">
            <span class="assignee">${task.assignee || 'Unassigned'}</span>
            <span class="ai-score">${task.ai_predicted_duration_hours}h</span>
          </div>`
        });
      }
    });

    // Show bottlenecks
    state?.analytics?.bottlenecks?.forEach(bottleneck => {
      canvas.addMarker(bottleneck.activity_id, 'highlight-bottleneck');
    });

  }, [viewer, state, tasks]);

  return (
    <div className="process-monitor">
      <div className="stats-panel">
        <div className="stat">
          <label>Progress</label>
          <div className="progress-bar">
            <div style={{ width: `${state?.progress_percentage}%` }} />
          </div>
        </div>

        <div className="stat">
          <label>Success Probability</label>
          <span className="value">{predictions?.success_probability}%</span>
        </div>

        <div className="stat">
          <label>Est. Completion</label>
          <span className="value">{predictions?.estimated_duration_days} days</span>
        </div>
      </div>

      <div ref={containerRef} className="bpmn-canvas" />

      <div className="ai-panel">
        <h3>AI Recommendations</h3>
        {state?.ai_recommendations?.map(rec => (
          <div key={rec.id} className="recommendation">
            {rec.message}
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## 🚀 Migration Plan

### Phase 1: Setup Foundation (Week 1)

```bash
# 1. Create unified module structure
mkdir -p intelligent-core/unified-workflow-engine/{bpmn,intelligence,integration,persistence,visualization,api}

# 2. Migrate BPMN code
cp -r intelligent-core/bpmn-workflow/*.py intelligent-core/unified-workflow-engine/bpmn/

# 3. Link Workflow Intelligence (не копировать, использовать как библиотеку)
# В unified-workflow-engine/intelligence/__init__.py:
from workflow_intelligence.core import WorkflowEngine
from workflow_intelligence.ai import ContextAdvisor
from workflow_intelligence.case_library import CaseLibrary

# 4. Create database migration
# Создать 035_unified_workflow.sql
```

**Deliverables:**
- ✅ Module structure created
- ✅ BPMN code migrated
- ✅ Database schema ready
- ✅ Basic tests passing

---

### Phase 2: Integration Layer (Week 2)

```python
# Create BPMNWorkflowAdapter
# intelligent-core/unified-workflow-engine/integration/adapter.py

# Implement:
1. Event mapping (BPMN ↔ Workflow Intelligence)
2. Context synchronization
3. Unified API endpoints

# Test:
- BPMN process start triggers Workflow Intelligence tracking
- Task completion updates both engines
- AI recommendations injected into BPMN tasks
```

**Deliverables:**
- ✅ BPMNWorkflowAdapter working
- ✅ Events synchronized
- ✅ Unified API endpoints
- ✅ Integration tests passing

---

### Phase 3: Database Persistence (Week 2-3)

```python
# Replace in-memory storage with PostgreSQL

# bpmn/persistence/repositories/process_repository.py
class ProcessRepository:
    async def save_process(self, process: BPMNProcess):
        # Save to workflow.bpmn_processes

    async def get_process(self, process_id: str):
        # Load from DB

# Similar for:
- InstanceRepository
- TaskRepository
```

**Deliverables:**
- ✅ All BPMN data persisted in PostgreSQL
- ✅ Redis caching for performance
- ✅ No in-memory storage
- ✅ Production-ready

---

### Phase 4: Frontend Visualization (Week 3-4)

```bash
# Install dependencies
npm install bpmn-js bpmn-js-properties-panel

# Create components:
1. BPMNModeler (edit mode)
2. ProcessMonitor (view mode with real-time updates)
3. TaskInbox (user tasks with AI recommendations)
4. ProcessAnalytics (process mining dashboard)
```

**Deliverables:**
- ✅ Visual BPMN editor working
- ✅ Real-time process monitoring
- ✅ AI recommendations in UI
- ✅ Task inbox with assignment

---

### Phase 5: AI Enhancements (Week 4-5)

```python
# Enhanced AI capabilities for visual workflows

# 1. AI-Powered Process Design
class ProcessDesignAdvisor:
    async def suggest_process_structure(self, requirements: str):
        # Generate BPMN XML from natural language

    async def validate_process_design(self, bpmn_xml: str):
        # Check for anti-patterns, suggest improvements

# 2. Predictive Task Assignment
class SmartTaskAssignment:
    async def recommend_assignee(self, task: Task):
        # Based on:
        # - Historical performance
        # - Current workload
        # - Skill match

# 3. Bottleneck Prediction
class BottleneckPredictor:
    async def predict_bottlenecks(self, instance_id: str):
        # Predict where process will slow down
```

**Deliverables:**
- ✅ AI process design suggestions
- ✅ Smart task assignment
- ✅ Bottleneck prediction
- ✅ Process optimization recommendations

---

## 📊 Success Metrics

### Technical Metrics
- ✅ BPMN 2.0 compliance (pass official test suite)
- ✅ Sub-second response time for visual updates
- ✅ 99.9% uptime (distributed architecture)
- ✅ Support 1000+ concurrent process instances

### Business Metrics
- ✅ 50% reduction in process modeling time (AI assistance)
- ✅ 30% improvement in process efficiency (bottleneck detection)
- ✅ 80% task assignment accuracy (ML predictions)
- ✅ User satisfaction > 4.5/5 (visual interface)

---

## 🎯 Final Result

**Unified Workflow Intelligence Platform:**

```python
# Example: User creates visual process

# 1. User draws BPMN in visual editor
bpmn_xml = """
<definitions>
  <process id="bia_process">
    <startEvent id="start"/>
    <userTask id="identify_processes" name="Identify Critical Processes"/>
    <userTask id="analyze_impact" name="Analyze Impact"/>
    <endEvent id="end"/>
  </process>
</definitions>
"""

# 2. Deploy with AI enhancement
POST /api/workflows/deploy
{
  "bpmn_xml": bpmn_xml,
  "tenant_id": "acme-corp",
  "enable_ai": true
}

# 3. Start instance
instance_id = POST /api/workflows/{process_id}/start
{
  "variables": {
    "org_context": {"industry": "healthcare", "size": "medium"}
  }
}

# 4. User sees in UI:
GET /api/workflows/{instance_id}/visual
{
  "bpmn_xml": "...",
  "current_activities": ["identify_processes"],
  "active_tasks": [{
    "name": "Identify Critical Processes",
    "assignee": "user123",
    "ai_recommendations": [
      "Based on similar healthcare organizations, start with Emergency Dept",
      "Typical completion time: 2-3 days",
      "3 other users working on similar tasks now"
    ],
    "ai_predicted_duration_hours": 48
  }],
  "predictions": {
    "success_probability": 0.85,
    "estimated_duration_days": 14
  }
}

# 5. Visual shows:
- Highlighted current activity (identify_processes)
- AI recommendations overlay
- Progress bar (25% complete)
- Predicted completion date
- Similar cases from library
```

---

## 💪 Why This is Better Than Camunda/Temporal

| Feature | Our Solution | Camunda | Temporal |
|---------|-------------|---------|----------|
| **BPMN 2.0** | ✅ Yes | ✅ Yes | ❌ No (own DSL) |
| **Visual Editor** | ✅ Yes | ✅ Yes (paid) | ❌ No |
| **AI Integration** | ✅ Built-in | ❌ No | ❌ No |
| **Case Learning** | ✅ Built-in | ❌ No | ❌ No |
| **BCM Context** | ✅ Native | ❌ Generic | ❌ Generic |
| **Open Source** | ✅ Yes | ⚠️ Limited | ✅ Yes |
| **Cost** | ✅ Free | 💰 $$$$ | ✅ Free |

**Competitive Advantage:**
- Camunda: Great BPMN engine, но нет AI и BCM knowledge
- Temporal: Powerful workflows, но не BPMN и сложнее
- **Мы**: BPMN + AI + BCM expertise + Self-learning = Уникально!

---

## 📝 Next Steps

1. ✅ **Approve architecture** (this document)
2. ⏭️ **Phase 1: Setup** - Create module structure
3. ⏭️ **Phase 2: Integration** - Build adapter layer
4. ⏭️ **Phase 3: Persistence** - Migrate to PostgreSQL
5. ⏭️ **Phase 4: Frontend** - Visual BPMN editor
6. ⏭️ **Phase 5: AI** - Enhanced intelligence

**Estimated Timeline:** 5 weeks to production-ready
**Team Required:** 2 developers (backend + frontend)

---

**Это будет ШЕДЕВР! 🚀**

Unified Workflow Intelligence Platform = BPMN визуализация + AI recommendations + Self-learning + BCM expertise
