# Module Scan Report: workflow_intelligence

**Дата сканирования:** 2025-10-08 14:33
**Путь:** `intelligent-core/workflow_intelligence`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 24392 |
| **Python файлов** | 94 |
| **Классов** | 171 |
| **Функций** | 89 |
| **API Endpoints** | 11 |
| **Зависимостей** | 100 |

---

## 🔗 Зависимости (100)


### abc
- `abc`

### activities
- `activities`

### agent
- `agent`

### ai.context_advisor
- `ai.context_advisor`

### ai_context_builder
- `ai_context_builder`

### ai_foundation
- `ai_foundation/core`
- `ai_foundation/integrations`
- `ai_foundation/intelligent_core`
- `ai_foundation/workflow_intelligence`

### ai_foundation.context
- `ai_foundation.context`

### ai_foundation.llm
- `ai_foundation.llm`

### ai_foundation.rag
- `ai_foundation.rag`

### aiohttp
- `aiohttp`

### argparse
- `argparse`

### asyncio
- `asyncio`

### asyncpg
- `asyncpg`

### auth
- `auth`

### auto_remediation.dockerfile_generator
- `auto_remediation.dockerfile_generator`

### banking_service
- `banking_service`

### base
- `base`

### bia_adapter
- `bia_adapter`

### bia_workflow
- `bia_workflow`

### case_library.collector
- `case_library.collector`

### case_library.models
- `case_library.models`

### case_library.repository
- `case_library.repository`

### client_provider
- `client_provider`

### collections
- `collections`

### contextlib
- `contextlib`

### contextvars
- `contextvars`

### coordination_workflow
- `coordination_workflow`

### cross_module_learning
- `cross_module_learning`

### database
- `database`
- `database/postgresql`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### decorators
- `decorators`

### dotenv
- `dotenv`

### enum
- `enum`

### event_intelligence_workflow
- `event_intelligence_workflow`

### events
- `events`

### exceptions
- `exceptions`

### expertise_workflow
- `expertise_workflow`

### external
- `external/anthropic`
- `external/temporal-cloud`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### functools
- `functools`

### health
- `health`

### httpx
- `httpx`

### inspect
- `inspect`

### intelligent_core.event_intelligence.analyzer
- `intelligent_core.event_intelligence.analyzer`

### intelligent_core.event_intelligence.knowledge_base
- `intelligent_core.event_intelligence.knowledge_base`

### intelligent_core.event_intelligence.learner
- `intelligent_core.event_intelligence.learner`

### intelligent_core.event_intelligence.predictor
- `intelligent_core.event_intelligence.predictor`

### iso_checker
- `iso_checker`

### json
- `json`

### logger
- `logger`

### logging
- `logging`

### metrics
- `metrics`

### middleware
- `middleware`

### models
- `models`

### monitoring
- `monitoring`

### monitoring.metrics
- `monitoring.metrics`

### orchestration.bcm_services_orchestrator
- `orchestration.bcm_services_orchestrator`

### orchestration.coordination_center.core.tool_registry
- `orchestration.coordination_center.core.tool_registry`

### os
- `os`

### pathlib
- `pathlib`

### permissions
- `permissions`

### postgres_adapter
- `postgres_adapter`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### pytest
- `pytest`

### random
- `random`

### risk_workflow
- `risk_workflow`

### rls_context
- `rls_context`

### rules_engine
- `rules_engine`

### runtime
- `runtime/eventbus`

### services.demand_forecaster
- `services.demand_forecaster`

### services.journey_predictor
- `services.journey_predictor`

### services.proactive_recommendations
- `services.proactive_recommendations`

### setuptools
- `setuptools`

### shared
- `shared`
- `shared/database`

### statistics
- `statistics`

### storage
- `storage`

### storage.postgres_adapter
- `storage.postgres_adapter`

### structlog
- `structlog`

### sys
- `sys`

### time
- `time`

### tools.event_intelligence
- `tools.event_intelligence`

### traceback
- `traceback`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### warnings
- `warnings`

### werkzeug.middleware.dispatcher
- `werkzeug.middleware.dispatcher`

### werkzeug.serving
- `werkzeug.serving`

### workflows
- `workflows`

### yaml
- `yaml`

### yaml_workflows
- `yaml_workflows`

---

## 🌐 API Endpoints (11)

- **GET** `/health` (файл: `main.py`)
- **GET** `/metrics` (файл: `main.py`)
- **GET** `/info` (файл: `main.py`)
- **POST** `/cases/add` (файл: `main.py`)
- **GET** `/cases/{case_id}` (файл: `main.py`)
- **POST** `/cases/search` (файл: `main.py`)
- **POST** `/cases/bulk` (файл: `main.py`)
- **POST** `/analyze` (файл: `main.py`)
- **POST** `/recommend` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)

---

## 💻 Классы (171)

- **StateMachine** (12 методов) - `state_machine.py`
- **BIAWorkflowEngine** (12 методов) - `bia_workflow.py`
- **BIARules** (11 методов) - `bia_rules.py`
- **BIARules** (11 методов) - `rules_engine.py`
- **WorkflowMetrics** (11 методов) - `metrics.py`
- **WorkflowEngine** (10 методов) - `workflow_engine.py`
- **ContextAdvisor** (7 методов) - `context_advisor.py`
- **CaseCollector** (7 методов) - `collector.py`
- **AuthContext** (6 методов) - `middleware.py`
- **WorkflowAIContextBuilder** (6 методов) - `ai_context_builder.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 1797 символов (109 строк)

**Превью:**
```
# workflow_intelligence

> Интеллектуальное управление workflow и бизнес-процессами

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 17,303 |
| **Python файлов** | 78 |
| **Классов** | 115 |
| **Функций** | 60 |
| **API Endpoints** | 1 |
| **Зависимостей** | 76 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (1)

- `/api/compliance/check`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **StateMachine** (12 методов) - `state_machine.py`
- **BIAWorkflowEngine** (12 методов) - `bia_workflow.py`
- **BIARules** (11 методов) - `bia_rules.py`
- **BIARules** (11 методов) - `rules_engine.py`
- **WorkflowEngine** (10 методов) - `workflow_engine.py`

### Функции

Всего публичных функций: 60

---

## 🔗 Зависимости

### Внутренние
- `ai_foundation.context`
- `ai_foundation.llm`
- `ai_foundation.rag`
- `ai_foundation/core`
- `ai_foundation/workflow_intelligence`
- `shared`
- `s
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `intelligent-core/workflow_intelligence/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 137
**Директорий:** 27
