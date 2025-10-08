# Module Scan Report: plans_service

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `platform-services/plans_service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 8609 |
| **Python файлов** | 37 |
| **Классов** | 79 |
| **Функций** | 28 |
| **API Endpoints** | 34 |
| **Зависимостей** | 51 |

---

## 🔗 Зависимости (51)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### asyncio
- `asyncio`

### auth
- `auth`

### auth.dependencies
- `auth.dependencies`

### config
- `config`

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
- `shared/utils`

### time
- `time`

### typing
- `typing`

### unittest.mock
- `unittest.mock`

### uuid
- `uuid`

### workflows.plan_lifecycle
- `workflows.plan_lifecycle`

### workflows.review_workflow
- `workflows.review_workflow`

---

## 🌐 API Endpoints (34)

- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/{item_id}/ai-advice` (файл: `workflow_ai.py`)
- **GET** `/benchmarks` (файл: `workflow_ai.py`)
- **GET** `/metrics` (файл: `metrics.py`)
- **GET** `/health` (файл: `health.py`)
- **GET** `/health/detailed` (файл: `health.py`)
- **GET** `/health/ready` (файл: `health.py`)
- **GET** `/health/live` (файл: `health.py`)

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
**Размер:** 5768 символов (222 строк)

**Превью:**
```
# Plans Service - Business Continuity Plans & Procedures

**Service:** `plans_service`
**Port:** `8023`
**ISO 22301:** Clause 8.4
**BCI Practice:** PP5 (Enabling Solutions)

## Overview

Plans Service manages business continuity plans, procedures, resources, and plan lifecycle. This service implements ISO 22301 Clause 8.4 requirements for BC plans and procedures.

## Architecture

```
plans_service/
├── config.py                   # Configuration
├── main.py                     # FastAPI app
├── database.py                 # Database connection
├── dependencies.py             # Dependency injection
├── models/
│   ├── domain.py              # Pydantic models
│   └── database.py            # SQLAlchemy models (8 models)
├── api/
│   └── routes.py              # API endpoints (25+)
├── services/
│   └── plan_service.py        # Business logic
├── repositories/
│   └── plan_repository.py     # Data access layer
├── workflows/
│   ├── plan_lifecycle.py      # Plan workflow
│   └── review_w
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `platform-services/plans_service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 56
**Директорий:** 10
