# Module Scan Report: workflow_intelligence

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `intelligent-core/workflow_intelligence`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 17303 |
| **Python файлов** | 78 |
| **Классов** | 115 |
| **Функций** | 60 |
| **API Endpoints** | 1 |
| **Зависимостей** | 76 |

---

## 🔗 Зависимости (76)


### abc
- `abc`

### activities
- `activities`

### ai.context_advisor
- `ai.context_advisor`

### ai_context_builder
- `ai_context_builder`

### ai_foundation
- `ai_foundation/core`
- `ai_foundation/workflow_intelligence`

### ai_foundation.context
- `ai_foundation.context`

### ai_foundation.llm
- `ai_foundation.llm`

### ai_foundation.rag
- `ai_foundation.rag`

### aiohttp
- `aiohttp`

### asyncio
- `asyncio`

### asyncpg
- `asyncpg`

### auth
- `auth`

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

### events
- `events`

### exceptions
- `exceptions`

### external
- `external/anthropic`
- `external/temporal-cloud`

### functools
- `functools`

### health
- `health`

### httpx
- `httpx`

### inspect
- `inspect`

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

### orchestration.bcm_services_orchestrator
- `orchestration.bcm_services_orchestrator`

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

### traceback
- `traceback`

### typing
- `typing`

### uuid
- `uuid`

### warnings
- `warnings`

### workflows
- `workflows`

### yaml
- `yaml`

### yaml_workflows
- `yaml_workflows`

---

## 🌐 API Endpoints (1)

- **GET** `/api/compliance/check` (файл: `service_integration_template.py`)

---

## 💻 Классы (115)

- **StateMachine** (12 методов) - `state_machine.py`
- **BIAWorkflowEngine** (12 методов) - `bia_workflow.py`
- **BIARules** (11 методов) - `bia_rules.py`
- **BIARules** (11 методов) - `rules_engine.py`
- **WorkflowEngine** (10 методов) - `workflow_engine.py`
- **WorkflowMetrics** (10 методов) - `metrics.py`
- **ContextAdvisor** (7 методов) - `context_advisor.py`
- **CaseCollector** (7 методов) - `collector.py`
- **AuthContext** (6 методов) - `middleware.py`
- **WorkflowAIContextBuilder** (6 методов) - `ai_context_builder.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 4618 символов (179 строк)

**Превью:**
```
# Workflow Intelligence Engine

**Status:** ✅ Temporal Cloud Connected
**Version:** 1.0.0
**Python:** 3.11.13
**Temporal SDK:** 1.18.1

---

## 🎯 Overview

**Workflow Intelligence Engine** - это МОЗГ всей BCM платформы.

**Из `арх2.md`:**
> "Это единственный компонент, который НЕЛЬЗЯ заменить позже. Определяет как работают ВСЕ остальные компоненты."

**Powered by:** [Temporal Cloud](https://cloud.temporal.io)

---

## ✅ Setup Status

- [x] Python 3.11.13 installed
- [x] Temporal CLI 1.4.1 installed (`~/bin/temporal`)
- [x] Temporal Python SDK 1.18.1 installed
- [x] Temporal Cloud account created
- [x] Temporal Cloud connected ✅
- [ ] Core Workflow Engine (Phase 2, Day 1-4)
- [ ] Case Library (Phase 2, Day 5-8)
- [ ] Governance System (Phase 2, Day 9-11)
- [ ] BIA Workflow (Phase 2, Day 12-14)

---

## 🚀 Quick Start

### View Temporal Cloud UI
**Dashboard:** https://cloud.temporal.io
**Namespace:** `ai-platform-iso-22301.r3gxp`

**Current Status:** ✅ Connected and ready

### Activate En
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `intelligent-core/workflow_intelligence/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 118
**Директорий:** 23
