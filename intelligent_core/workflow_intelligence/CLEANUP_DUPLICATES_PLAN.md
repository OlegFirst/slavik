# Cleanup Duplicates Plan

## Problem

ДУБЛИРОВАНИЕ СТРУКТУРЫ! Есть две версии одних и тех же модулей:

### ROOT-level files (УДАЛИТЬ - это дубли!):
```
workflow_intelligence/
├── process_framework.py          ← ДУБЛЬ infrastructure/process_framework/
├── bcm_processes.py              ← ДУБЛЬ workflows/
├── document_templates.py         ← ДУБЛЬ infrastructure/templates/
├── process_orchestration_api.py  ← ДУБЛЬ infrastructure/orchestration/
├── metrics_exporter.py           ← ДУБЛЬ infrastructure/monitoring/
├── monitoring/                   ← ДУБЛЬ infrastructure/monitoring/
└── temporal_workflows/           ← ОТДЕЛЬНАЯ СИСТЕМА (оставить)
```

### ПРАВИЛЬНАЯ структура (ОСТАВИТЬ):
```
workflow_intelligence/
├── infrastructure/               ← ПРАВИЛЬНАЯ СТРУКТУРА
│   ├── process_framework/       ✅ Модели процессов
│   ├── templates/               ✅ Шаблоны документов
│   ├── orchestration/           ✅ Координация процессов
│   ├── monitoring/              ✅ Метрики и health checks
│   └── policies/                ✅ Compliance, Security, Performance
│
├── temporal_workflows/          ✅ Temporal workflow definitions (оставить)
│   ├── bia_workflow.py
│   ├── risk_workflow.py
│   ├── coordination_workflow.py
│   └── ... (11 workflows)
│
├── core/                        ✅ Workflow engine
├── governance/                  ✅ Goals + Rules
├── ai/                          ✅ Context Advisor
├── case_library/                ✅ Learning
├── storage/                     ✅ PostgreSQL
├── integration/                 ✅ Service listeners (BIA)
└── workflows/                   ✅ BCM process definitions
```

---

## Actions

### 1. УДАЛИТЬ root-level дубли:

```bash
cd /Users/MD/AI-Platform-ISO/intelligent_core/workflow_intelligence

# Backup first (just in case)
mkdir -p .cleanup-backup
mv process_framework.py .cleanup-backup/
mv bcm_processes.py .cleanup-backup/
mv document_templates.py .cleanup-backup/
mv process_orchestration_api.py .cleanup-backup/
mv metrics_exporter.py .cleanup-backup/

# Duplicate monitoring directory
mv monitoring .cleanup-backup/monitoring-root-duplicate
```

### 2. VERIFY infrastructure/ has all functionality:

Check that infrastructure/ modules are complete:
- `infrastructure/process_framework/` ✅
- `infrastructure/templates/` ✅
- `infrastructure/orchestration/` ✅
- `infrastructure/monitoring/` ✅
- `infrastructure/policies/` ✅

### 3. UPDATE imports in main.py and other files:

Change:
```python
# OLD (wrong)
from process_framework import ProcessFramework
from document_templates import DocumentTemplateLibrary
from metrics_exporter import MetricsExporter

# NEW (correct)
from infrastructure.process_framework import ProcessFramework
from infrastructure.templates import DocumentTemplateLibrary
from infrastructure.monitoring import MetricsExporter
```

### 4. KEEP temporal_workflows/ separate:

`temporal_workflows/` is CORRECT - это Temporal workflow definitions, не дубликат!

Содержит:
- bia_workflow.py
- risk_workflow.py
- coordination_workflow.py
- collective_workflow.py
- predictive_workflow.py
- и другие Temporal workflows

---

## IDEA за infrastructure/

**infrastructure/** - это "МОЗГ" workflow_intelligence:

### 1. **process_framework/** - Процессные модели
- Определения BCM процессов (BIA, Risk, BC Planning)
- Валидация шагов
- Связи между процессами

### 2. **templates/** - Генерация документов
- Шаблоны ISO 22301 документов
- AI-powered генерация
- Export в Word/PDF

### 3. **orchestration/** - Координация
- Multi-service workflows (BIA → Risk → BC Plan)
- Saga pattern для компенсации
- Temporal integration

### 4. **monitoring/** - Наблюдение
- Prometheus metrics
- Health checks
- Performance tracking

### 5. **policies/** - Правила
- Compliance policies (ISO 22301, NIST, WHO)
- Security policies (RLS, RBAC)
- Performance policies (SLA, timeouts)

---

## После cleanup:

Структура станет ЧИСТОЙ:

```
workflow_intelligence/
├── core/              # Workflow Engine, State Machines
├── governance/        # Goals + Rules Orchestrator
├── ai/               # Context Advisor, ML Predictor
├── case_library/     # Learning from executions
├── storage/          # PostgreSQL, RLS
├── integration/      # Service listeners (BIA, Planning, ...)
├── workflows/        # BCM process definitions (create_bia_process, etc)
├── infrastructure/   # 🧠 BRAIN: Process Framework, Templates, Orchestration, Monitoring, Policies
└── temporal_workflows/ # Temporal workflow definitions (coordination)
```

**Логика:**
- `core/` - ENGINE (выполнение workflows)
- `governance/` - GUARDIAN (валидация, правила)
- `ai/` - ADVISOR (контекстные советы)
- `case_library/` - MEMORY (обучение)
- `storage/` - PERSISTENCE (PostgreSQL)
- `integration/` - NERVOUS SYSTEM (EventBus listeners)
- `workflows/` - DEFINITIONS (BCM processes)
- `infrastructure/` - 🧠 BRAIN (координация, мониторинг, политики)
- `temporal_workflows/` - DURABILITY (Temporal orchestration)

---

## Execute?

Ready to cleanup duplicates and consolidate structure!

**MD:** Готов начать cleanup? Я удалю дубли и обновлю импорты.
