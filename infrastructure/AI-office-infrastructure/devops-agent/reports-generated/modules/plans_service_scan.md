# Module Scan Report: plans_service

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/plans_service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 8612 |
| **Python файлов** | 38 |
| **Классов** | 79 |
| **Функций** | 28 |
| **API Endpoints** | 32 |
| **Зависимостей** | 64 |

---

## 🔗 Зависимости (64)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### api.error_handlers
- `api.error_handlers`

### api.health
- `api.health`

### api.metrics
- `api.metrics`

### api.rate_limit
- `api.rate_limit`

### api.routes
- `api.routes`

### api.workflow_ai
- `api.workflow_ai`

### asyncio
- `asyncio`

### auth
- `auth`

### auth.dependencies
- `auth.dependencies`

### config
- `config`

### contextlib
- `contextlib`

### database
- `database`
- `database/postgresql`

### datetime
- `datetime`

### dependencies
- `dependencies`

### domain
- `domain`

### enum
- `enum`

### fastapi
- `fastapi`

### fastapi.exceptions
- `fastapi.exceptions`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.responses
- `fastapi.responses`

### fastapi.security
- `fastapi.security`

### fastapi.testclient
- `fastapi.testclient`

### functools
- `functools`

### httpx
- `httpx`

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

### models.domain
- `models.domain`

### pathlib
- `pathlib`

### plan_lifecycle
- `plan_lifecycle`

### plan_repository
- `plan_repository`

### plan_service
- `plan_service`

### plans_service.auth.dependencies
- `plans_service.auth.dependencies`

### plans_service.auth.models
- `plans_service.auth.models`

### plans_service.config
- `plans_service.config`

### plans_service.models.database
- `plans_service.models.database`

### plans_service.models.domain
- `plans_service.models.domain`

### plans_service.repositories.plan_repository
- `plans_service.repositories.plan_repository`

### plans_service.services.procedure_validator
- `plans_service.services.procedure_validator`

### plans_service.workflows.plan_lifecycle
- `plans_service.workflows.plan_lifecycle`

### procedure_validator
- `procedure_validator`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### pytest
- `pytest`

### repositories.plan_repository
- `repositories.plan_repository`

### review_workflow
- `review_workflow`

### services.plan_service
- `services.plan_service`

### shared
- `shared/cache`
- `shared/utils`

### sys
- `sys`

### time
- `time`

### typing
- `typing`

### unittest.mock
- `unittest.mock`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### workflow_integration
- `workflow_integration`

### workflows.plan_lifecycle
- `workflows.plan_lifecycle`

### workflows.review_workflow
- `workflows.review_workflow`

---

## 🌐 API Endpoints (32)

- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/{item_id}/ai-advice` (файл: `workflow_ai.py`)
- **GET** `/benchmarks` (файл: `workflow_ai.py`)
- **GET** `/metrics` (файл: `metrics.py`)
- **GET** `/health/detailed` (файл: `health.py`)
- **GET** `/health/ready` (файл: `health.py`)
- **GET** `/health/live` (файл: `health.py`)
- **POST** `/plans` (файл: `bulk_operations.py`)

---

## 💻 Классы (79)

- **TestPlanWorkflow** (23 методов) - `test_workflows.py`
- **TestProcedureDependencyValidator** (19 методов) - `test_procedure_validator.py`
- **TestPlanValidation** (12 методов) - `test_validation.py`
- **TestProcedureValidation** (8 методов) - `test_validation.py`
- **TestContactValidation** (8 методов) - `test_validation.py`
- **PlanService** (7 методов) - `plan_service.py`
- **TestRecoveryPriorityValidation** (6 методов) - `test_validation.py`
- **TestResourceValidation** (4 методов) - `test_validation.py`
- **TestUserContextModel** (4 методов) - `test_auth.py`
- **Contact** (4 методов) - `domain.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 1996 символов (122 строк)

**Превью:**
```
# plans_service

> 🌐 API Service модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 8,609 |
| **Python файлов** | 37 |
| **Классов** | 79 |
| **Функций** | 28 |
| **API Endpoints** | 34 |
| **Зависимостей** | 51 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (18)

- `/`
- `/activations`
- `/api/compliance/check`
- `/benchmarks`
- `/contact-lists`

### POST (12)

- `/contact-lists`
- `/exercises/schedule`
- `/plans`
- `/plans`
- `/plans/{plan_id}/activate`

### PUT (2)

- `/plans/{plan_id}`
- `/plans/{plan_id}/procedures/{procedure_id}`

### DELETE (2)

- `/plans/{plan_id}`
- `/plans/{plan_id}/procedures/{procedure_id}`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **TestPlanWorkflow** (23 методов) - `test_workflows.py`
- **TestProcedureDependencyValidator** (19 методов) - `test_procedure_validator.py`
- **TestPlanValidation** (12 методов) - `test
```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/plans_service/.env.example`
- `requirements.txt` → `platform-services/plans_service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 60
**Директорий:** 10
