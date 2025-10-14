# Module Scan Report: compliance-service

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/compliance-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 17480 |
| **Python файлов** | 55 |
| **Классов** | 136 |
| **Функций** | 41 |
| **API Endpoints** | 95 |
| **Зависимостей** | 94 |

---

## 🔗 Зависимости (94)


### abc
- `abc`

### ai_foundation
- `ai_foundation/workflow_intelligence`

### aiohttp
- `aiohttp`

### api
- `api`

### api.workflow_ai
- `api.workflow_ai`

### assessment_engine
- `assessment_engine`

### assessment_repository
- `assessment_repository`

### assessment_workflow
- `assessment_workflow`

### asyncio
- `asyncio`

### audit_repository
- `audit_repository`

### audit_workflow
- `audit_workflow`

### auth.dependencies
- `auth.dependencies`

### base_repository
- `base_repository`

### base_workflow
- `base_workflow`

### compliance.config.settings
- `compliance.config.settings`

### compliance.core.assessment_engine
- `compliance.core.assessment_engine`

### compliance.core.gap_analyzer
- `compliance.core.gap_analyzer`

### compliance.database.connection
- `compliance.database.connection`

### compliance.integrations.ai_orchestrator
- `compliance.integrations.ai_orchestrator`

### compliance.models.database
- `compliance.models.database`

### compliance.models.enums
- `compliance.models.enums`

### compliance.models.schemas
- `compliance.models.schemas`

### compliance.repositories.assessment_repository
- `compliance.repositories.assessment_repository`

### compliance.repositories.audit_repository
- `compliance.repositories.audit_repository`

### compliance.repositories.evidence_repository
- `compliance.repositories.evidence_repository`

### compliance.repositories.gap_repository
- `compliance.repositories.gap_repository`

### compliance.repositories.nonconformity_repository
- `compliance.repositories.nonconformity_repository`

### compliance.services.rca_templates
- `compliance.services.rca_templates`

### compliance.standards.iso_22301
- `compliance.standards.iso_22301`

### compliance.workflows.audit_workflow
- `compliance.workflows.audit_workflow`

### compliance.workflows.evidence_workflow
- `compliance.workflows.evidence_workflow`

### compliance.workflows.gap_workflow
- `compliance.workflows.gap_workflow`

### compliance.workflows.nonconformity_workflow
- `compliance.workflows.nonconformity_workflow`

### config
- `config`

### connection
- `connection`

### contextlib
- `contextlib`

### database
- `database`
- `database/postgresql`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### enum
- `enum`

### enums
- `enums`

### evidence_repository
- `evidence_repository`

### evidence_workflow
- `evidence_workflow`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.security
- `fastapi.security`

### gap_analyzer
- `gap_analyzer`

### gap_repository
- `gap_repository`

### gap_workflow
- `gap_workflow`

### improvements
- `improvements`

### iso_22301
- `iso_22301`

### json
- `json`

### jwt
- `jwt`

### logging
- `logging`

### main
- `main`

### models
- `models`

### models.database
- `models.database`

### models.enums
- `models.enums`

### nonconformities
- `nonconformities`

### nonconformity_repository
- `nonconformity_repository`

### nonconformity_workflow
- `nonconformity_workflow`

### os
- `os`

### pathlib
- `pathlib`

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

### schemas
- `schemas`

### services.rca_templates
- `services.rca_templates`

### shared
- `shared/audit`
- `shared/auth`
- `shared/cache`
- `shared/config`
- `shared/database`
- `shared/exceptions`
- `shared/middleware`
- `shared/utils`

### standards.iso_22301
- `standards.iso_22301`

### storage
- `storage`

### sys
- `sys`

### templates.models
- `templates.models`

### typing
- `typing`

### unittest.mock
- `unittest.mock`

### utils
- `utils`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### validators
- `validators`

### validators.business_rules
- `validators.business_rules`

### workflow_integration
- `workflow_integration`

### workflows.audit_workflow
- `workflows.audit_workflow`

### workflows.nonconformity_workflow
- `workflows.nonconformity_workflow`

### workflows.validators
- `workflows.validators`

---

## 🌐 API Endpoints (95)

- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/items` (файл: `connection.py`)
- **GET** `/{item_id}/ai-advice` (файл: `workflow_ai.py`)
- **GET** `/benchmarks` (файл: `workflow_ai.py`)
- **GET** `/guides` (файл: `library.py`)
- **GET** `/guides/{guide_id}` (файл: `library.py`)
- **GET** `/research` (файл: `library.py`)
- **GET** `/research/{source}` (файл: `library.py`)
- **GET** `/best-practices` (файл: `library.py`)

---

## 💻 Классы (136)

- **TestWorkflowValidators** (24 методов) - `test_workflows.py`
- **WorkflowValidator** (11 методов) - `validators.py`
- **BaseWorkflow** (11 методов) - `base_workflow.py`
- **ComplianceAIClient** (9 методов) - `ai_orchestrator.py`
- **TestNonconformityWorkflowTransitions** (6 методов) - `test_workflows.py`
- **TestFaultTreeTemplate** (6 методов) - `test_rca_templates.py`
- **TestRCAAnalyzer** (6 методов) - `test_rca_templates.py`
- **NonconformityWorkflow** (6 методов) - `nonconformity_workflow.py`
- **TestAuditWorkflowTransitions** (5 методов) - `test_workflows.py`
- **TestFiveWhysTemplate** (5 методов) - `test_rca_templates.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 2265 символов (139 строк)

**Превью:**
```
# compliance-service

> 🌐 API Service модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 17,481 |
| **Python файлов** | 55 |
| **Классов** | 136 |
| **Функций** | 41 |
| **API Endpoints** | 97 |
| **Зависимостей** | 94 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (60)

- `/`
- `/`
- `/`
- `/`
- `/analytics`

### POST (29)

- `/batch-ai-scan`
- `/corrective-actions/bulk`
- `/evidence/bulk`
- `/improvements`
- `/improvements/{initiative_id}/verify`

### PUT (1)

- `/templates/{template_id}`

### DELETE (3)

- `/templates/{template_id}`
- `/{assessment_id}`
- `/{evidence_id}`

### PATCH (4)

- `/improvements/{initiative_id}`
- `/improvements/{initiative_id}/progress`
- `/{evidence_id}`
- `/{gap_id}`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **TestWorkflowValidators** (24 методов) - `test_workflows.py`
- **WorkflowValidator** (11 методов) - `va
```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/compliance-service/.env.example`
- `requirements.txt` → `platform-services/compliance-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 65
**Директорий:** 13
