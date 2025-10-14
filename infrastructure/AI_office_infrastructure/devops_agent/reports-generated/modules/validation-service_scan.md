# Module Scan Report: validation-service

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/validation-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 7567 |
| **Python файлов** | 32 |
| **Классов** | 109 |
| **Функций** | 53 |
| **API Endpoints** | 49 |
| **Зависимостей** | 60 |

---

## 🔗 Зависимости (60)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### api
- `api`

### api.schemas
- `api.schemas`

### api.workflow_ai
- `api.workflow_ai`

### asyncio
- `asyncio`

### audit_service
- `audit_service`

### audit_workflow
- `audit_workflow`

### capa_service
- `capa_service`

### capa_workflow
- `capa_workflow`

### celery
- `celery`

### celery.schedules
- `celery.schedules`

### config
- `config`

### contextlib
- `contextlib`

### database
- `database`
- `database/postgresql`

### datetime
- `datetime`

### domain
- `domain`

### email.mime.multipart
- `email.mime.multipart`

### email.mime.text
- `email.mime.text`

### enum
- `enum`

### events.subscribers
- `events.subscribers`

### exercise_service
- `exercise_service`

### exercise_workflow
- `exercise_workflow`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.security
- `fastapi.security`

### httpx
- `httpx`

### integrations.bcm_client
- `integrations.bcm_client`

### jwt
- `jwt`

### kpi_calculations
- `kpi_calculations`

### kpi_service
- `kpi_service`

### logging
- `logging`

### main
- `main`

### models.database
- `models.database`

### models.domain
- `models.domain`

### os
- `os`

### pathlib
- `pathlib`

### prometheus_client
- `prometheus_client`

### publishers
- `publishers`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### repositories.repository
- `repositories.repository`

### repository
- `repository`

### scenario_service
- `scenario_service`

### services.audit_service
- `services.audit_service`

### services.capa_service
- `services.capa_service`

### services.exercise_service
- `services.exercise_service`

### services.kpi_service
- `services.kpi_service`

### services.scenario_service
- `services.scenario_service`

### shared
- `shared/database`

### smtplib
- `smtplib`

### subscribers
- `subscribers`

### sys
- `sys`

### typing
- `typing`

### uvicorn
- `uvicorn`

### workflow_integration
- `workflow_integration`

### workflows
- `workflows`

### workflows.audit_workflow
- `workflows.audit_workflow`

### workflows.capa_workflow
- `workflows.capa_workflow`

### workflows.kpi_calculations
- `workflows.kpi_calculations`

---

## 🌐 API Endpoints (49)

- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **POST** `/api/events/webhook` (файл: `main.py`)
- **GET** `/insights` (файл: `workflow_ai.py`)
- **GET** `/recommendations` (файл: `workflow_ai.py`)
- **GET** `/cases/search` (файл: `workflow_ai.py`)
- **GET** `/cases/{case_id}/similar` (файл: `workflow_ai.py`)
- **GET** `/cases/{case_id}/timeline` (файл: `workflow_ai.py`)
- **GET** `/analytics/patterns` (файл: `workflow_ai.py`)
- **GET** `/analytics/performance` (файл: `workflow_ai.py`)

---

## 💻 Классы (109)

- **KPIService** (3 методов) - `kpi_service.py`
- **WorkflowSecurityMiddleware** (1 методов) - `workflow_integration.py`
- **ValidationRepository** (1 методов) - `repository.py`
- **EventPublisher** (1 методов) - `publishers.py`
- **ExerciseService** (1 методов) - `exercise_service.py`
- **ScenarioService** (1 методов) - `scenario_service.py`
- **CAPAService** (1 методов) - `capa_service.py`
- **AuditService** (1 методов) - `audit_service.py`
- **Settings** (0 методов) - `config.py`
- **Config** (0 методов) - `config.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 1950 символов (119 строк)

**Превью:**
```
# validation-service

> 🌐 API Service модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 7,568 |
| **Python файлов** | 32 |
| **Классов** | 109 |
| **Функций** | 53 |
| **API Endpoints** | 50 |
| **Зависимостей** | 60 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (32)

- `/analytics/patterns`
- `/analytics/performance`
- `/api/compliance/check`
- `/audits`
- `/audits/findings-analysis`

### POST (15)

- `/api/events/webhook`
- `/audits`
- `/audits/{audit_id}/findings`
- `/capa`
- `/capa/{capa_id}/verify`

### PATCH (3)

- `/audits/{audit_id}/close`
- `/capa/{capa_id}`
- `/kpis/{kpi_id}`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **KPIService** (3 методов) - `kpi_service.py`
- **WorkflowSecurityMiddleware** (1 методов) - `workflow_integration.py`
- **ValidationRepository** (1 методов) - `repository.py`
- **EventPublisher** (1 методов) - `publi
```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/validation-service/.env.example`
- `requirements.txt` → `platform-services/validation-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 42
**Директорий:** 8
