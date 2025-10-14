# Module Scan Report: governance-service

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/governance-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 7224 |
| **Python файлов** | 27 |
| **Классов** | 90 |
| **Функций** | 4 |
| **API Endpoints** | 46 |
| **Зависимостей** | 48 |

---

## 🔗 Зависимости (48)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### api.routes
- `api.routes`

### api.workflow_ai
- `api.workflow_ai`

### audit_logger
- `audit_logger`

### config
- `config`

### contextlib
- `contextlib`

### database
- `database`
- `database/postgresql`

### database.domain_models
- `database.domain_models`

### datetime
- `datetime`

### domain_schemas
- `domain_schemas`

### enum
- `enum`

### events.subscribers
- `events.subscribers`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.security
- `fastapi.security`

### jwt
- `jwt`

### logging
- `logging`

### main
- `main`

### models.database
- `models.database`

### pathlib
- `pathlib`

### policy_workflow
- `policy_workflow`

### prometheus_client
- `prometheus_client`

### publishers
- `publishers`

### pydantic
- `pydantic`

### re
- `re`

### repositories.competence_repository
- `repositories.competence_repository`

### repositories.policy_repository
- `repositories.policy_repository`

### repositories.resource_repository
- `repositories.resource_repository`

### repositories.role_repository
- `repositories.role_repository`

### resource_workflow
- `resource_workflow`

### role_workflow
- `role_workflow`

### runtime
- `runtime/eventbus`

### services.governance_service
- `services.governance_service`

### shared
- `shared/auth`
- `shared/config`
- `shared/database`
- `shared/models`
- `shared/utils`

### subscribers
- `subscribers`

### sys
- `sys`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### workflow_integration
- `workflow_integration`

### workflows.policy_workflow
- `workflows.policy_workflow`

### workflows.resource_workflow
- `workflows.resource_workflow`

### workflows.role_workflow
- `workflows.role_workflow`

---

## 🌐 API Endpoints (46)

- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **POST** `/auth/token` (файл: `main.py`)
- **GET** `/{item_id}/ai-advice` (файл: `workflow_ai.py`)
- **GET** `/benchmarks` (файл: `workflow_ai.py`)
- **POST** `/policies` (файл: `routes.py`)
- **GET** `/policies` (файл: `routes.py`)
- **GET** `/policies/{policy_id}` (файл: `routes.py`)
- **PATCH** `/policies/{policy_id}` (файл: `routes.py`)

---

## 💻 Классы (90)

- **PolicyWorkflowEngine** (8 методов) - `policy_workflow.py`
- **PolicyValidator** (5 методов) - `policy_workflow.py`
- **ResourceValidator** (5 методов) - `resource_workflow.py`
- **RoleWorkflowEngine** (4 методов) - `role_workflow.py`
- **RoleValidator** (4 методов) - `role_workflow.py`
- **ResourceWorkflowEngine** (4 методов) - `resource_workflow.py`
- **PolicyService** (3 методов) - `governance_service.py`
- **RoleService** (2 методов) - `governance_service.py`
- **ResourceService** (2 методов) - `governance_service.py`
- **WorkflowSecurityMiddleware** (1 методов) - `workflow_integration.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 2155 символов (130 строк)

**Превью:**
```
# governance-service

> 🌐 API Service модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 7,225 |
| **Python файлов** | 27 |
| **Классов** | 90 |
| **Функций** | 4 |
| **API Endpoints** | 46 |
| **Зависимостей** | 48 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (26)

- `/`
- `/api/compliance/check`
- `/benchmarks`
- `/benchmarks/{metric_name}`
- `/communication-plans`

### POST (13)

- `/api/bia/processes/{process_id}/suggest-rto`
- `/auth/token`
- `/communication-plans`
- `/competence`
- `/context-analysis`

### DELETE (1)

- `/policies/{policy_id}`

### PATCH (6)

- `/objectives/{objective_id}`
- `/policies/{policy_id}`
- `/resources/{resource_id}`
- `/roles/{role_id}`
- `/stakeholders/{stakeholder_id}`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **PolicyWorkflowEngine** (8 методов) - `policy_workflow.py`
- **PolicyValidator** (5 методов) - 
```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/governance-service/.env.example`
- `requirements.txt` → `platform-services/governance-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 34
**Директорий:** 7
