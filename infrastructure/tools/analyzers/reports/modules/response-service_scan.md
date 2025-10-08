# Module Scan Report: response-service

**Дата сканирования:** 2025-10-06 21:11
**Путь:** `platform-services/response-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 10708 |
| **Python файлов** | 30 |
| **Классов** | 80 |
| **Функций** | 33 |
| **API Endpoints** | 18 |
| **Зависимостей** | 42 |

---

## 🔗 Зависимости (42)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### aio_pika
- `aio_pika`

### aio_pika.exceptions
- `aio_pika.exceptions`

### api.routes
- `api.routes`

### asyncio
- `asyncio`

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

### enum
- `enum`

### events.publishers
- `events.publishers`

### events.subscribers
- `events.subscribers`

### fastapi
- `fastapi`

### fastapi.security
- `fastapi.security`

### fastapi.testclient
- `fastapi.testclient`

### importlib.util
- `importlib.util`

### jose
- `jose`

### json
- `json`

### jwt
- `jwt`

### jwt_handler
- `jwt_handler`

### logging
- `logging`

### logging.config
- `logging.config`

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

### publishers
- `publishers`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### pytest
- `pytest`

### repositories.repository
- `repositories.repository`

### services.business_logic
- `services.business_logic`

### services.transactions
- `services.transactions`

### subscribers
- `subscribers`

### sys
- `sys`

### typing
- `typing`

### unittest.mock
- `unittest.mock`

### uuid
- `uuid`

---

## 🌐 API Endpoints (18)

- **GET** `/` (файл: `main.py`)
- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/ready` (файл: `main.py`)
- **GET** `/live` (файл: `main.py`)
- **GET** `/metrics` (файл: `main.py`)
- **GET** `/incidents` (файл: `dependencies.py`)
- **GET** `/public-incidents` (файл: `dependencies.py`)
- **POST** `/critical-incidents` (файл: `dependencies.py`)
- **GET** `/insights` (файл: `workflow_ai.py`)

---

## 💻 Классы (80)

- **TestIncidentEndpoints** (9 методов) - `test_api.py`
- **ResponseRepository** (8 методов) - `repository.py`
- **Settings** (4 методов) - `config.py`
- **TestSubscriberInitialization** (4 методов) - `test_subscribers.py`
- **ResponseEventSubscriber** (4 методов) - `subscribers.py`
- **TestPublisherInitialization** (3 методов) - `test_publishers.py`
- **TestCustomHandlers** (3 методов) - `test_subscribers.py`
- **TestResponseTeamEndpoints** (3 методов) - `test_api.py`
- **TestDashboardEndpoints** (3 методов) - `test_api.py`
- **TestResponseActionEndpoints** (2 методов) - `test_api.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 9377 символов (401 строк)

**Превью:**
```
# Response Module

**ISO 22301:2019 Clause 8.4 - Incident Response**

Complete incident response management module for BCM Platform.

## Overview

The Response module provides comprehensive incident response capabilities including:

- **Incident Management**: Create, track, and manage incidents
- **Response Actions**: Define and track response actions
- **Response Teams**: Manage incident response teams
- **Communications**: Track all incident communications
- **Timeline**: Chronological incident timeline
- **Recovery Metrics**: RTO/RPO tracking and validation
- **Escalation**: Automatic and manual incident escalation
- **Reporting**: Comprehensive incident reports
- **Dashboard**: Real-time incident analytics

## Architecture

```
response/
├── api/
│   ├── __init__.py
│   └── routes.py          # All 15+ API endpoints
├── models/
│   ├── __init__.py
│   ├── domain.py          # Pydantic models
│   └── database.py        # SQLAlchemy models
├── services/
│   ├── __init__.py
│   └── bu
```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/response-service/.env.example`
- `requirements.txt` → `platform-services/response-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 44
**Директорий:** 12
