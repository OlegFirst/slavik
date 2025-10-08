# Module Scan Report: workflow-engine

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `intelligent-core/workflow-engine`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 6309 |
| **Python файлов** | 22 |
| **Классов** | 29 |
| **Функций** | 6 |
| **API Endpoints** | 10 |
| **Зависимостей** | 48 |

---

## 🔗 Зависимости (48)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### asyncio
- `asyncio`

### bpmn.engine_persistent
- `bpmn.engine_persistent`

### bpmn.models
- `bpmn.models`

### bpmn.parser
- `bpmn.parser`

### collections
- `collections`

### core.unified_engine
- `core.unified_engine`

### database
- `database/postgresql`

### datetime
- `datetime`

### engine_persistent
- `engine_persistent`

### enum
- `enum`

### expression_evaluator
- `expression_evaluator`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.responses
- `fastapi.responses`

### gateway_evaluator
- `gateway_evaluator`

### instance_repository
- `instance_repository`

### intelligent_core.platform_core.workflow.bpmn.models
- `intelligent_core.platform_core.workflow.bpmn.models`

### intelligent_core.platform_core.workflow.core.unified_engine
- `intelligent_core.platform_core.workflow.core.unified_engine`

### intelligent_core.platform_core.workflow.persistence.database
- `intelligent_core.platform_core.workflow.persistence.database`

### intelligent_core.unified_workflow
- `intelligent_core.unified_workflow`

### json
- `json`

### loader.case_loader
- `loader.case_loader`

### logging
- `logging`

### models
- `models`

### os
- `os`

### parser
- `parser`

### pathlib
- `pathlib`

### persistence.database
- `persistence.database`

### persistence.repositories
- `persistence.repositories`

### process_repository
- `process_repository`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### pytest
- `pytest`

### re
- `re`

### runtime
- `runtime/eventbus`

### shared
- `shared/cache`
- `shared/database`

### sys
- `sys`

### task_repository
- `task_repository`

### typing
- `typing`

### unified_engine
- `unified_engine`

### unified_workflow.bpmn.models
- `unified_workflow.bpmn.models`

### unified_workflow.core.unified_engine
- `unified_workflow.core.unified_engine`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### workflow
- `workflow`

### xml.etree.ElementTree
- `xml.etree.ElementTree`

---

## 🌐 API Endpoints (10)

- **GET** `/health` (файл: `main.py`)
- **GET** `/metrics` (файл: `main.py`)
- **POST** `/processes` (файл: `main.py`)
- **GET** `/instances/{instance_id}/visual-state` (файл: `main.py`)
- **POST** `/tasks/{task_id}/complete` (файл: `main.py`)
- **POST** `/tasks/{task_id}/assign` (файл: `main.py`)
- **GET** `/users/{user_email}/tasks` (файл: `main.py`)
- **GET** `/processes` (файл: `main.py`)
- **GET** `/instances` (файл: `main.py`)
- **DELETE** `/instances/{instance_id}` (файл: `main.py`)

---

## 💻 Классы (29)

- **BPMNParser** (15 методов) - `parser.py`
- **GatewayEvaluator** (5 методов) - `gateway_evaluator.py`
- **ExpressionEvaluator** (4 методов) - `expression_evaluator.py`
- **BPMNWorkflowEngineWrapper** (3 методов) - `unified_engine.py`
- **UnifiedWorkflowEngine** (2 методов) - `unified_engine.py`
- **BPMNEnginePersistent** (2 методов) - `engine_persistent.py`
- **BPMNEngine** (2 методов) - `engine.py`
- **DatabaseManager** (2 методов) - `database.py`
- **InstanceRepository** (1 методов) - `instance_repository.py`
- **ProcessRepository** (1 методов) - `process_repository.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 1914 символов (95 строк)

**Превью:**
```
# Platform Core - Layer 1

**Purpose:** Domain-agnostic system functions
**Version:** 1.0.0
**Created:** 2025-10-05

---

## 🎯 What is Platform Core?

**Platform Core** contains foundational system services that work independently of business domain.

These modules can be used for **ANY domain** - not just BCM (Business Continuity Management).

---

## 📦 Modules

### 1. workflow/
**Unified Workflow Engine** - BPMN orchestration + AI recommendations

- BPMN 2.0 visual modeling
- PostgreSQL persistence
- AI-powered recommendations
- Event-driven architecture
- Multi-tenancy support

**Status:** ✅ Production-ready (v2.0)

**Location:** `platform-core/workflow/` (formerly `unified-workflow/`)

**Documentation:** See `workflow/PHASE_2_COMPLETE.md`

---

### 2. coordination/ (Future)
**Coordination Center** - Multi-agent coordination

---

### 3. learning/ (Future)
**Learning Systems** - Platform-wide learning

---

### 4. community/ (Future)
**Community Intelligence** - Collective intellige
```

---

## 📂 Структура

**Всего файлов:** 37
**Директорий:** 11
