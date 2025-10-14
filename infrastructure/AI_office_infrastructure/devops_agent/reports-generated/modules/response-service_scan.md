# Module Scan Report: response-service

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/response-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 10711 |
| **Python файлов** | 30 |
| **Классов** | 80 |
| **Функций** | 33 |
| **API Endpoints** | 38 |
| **Зависимостей** | 50 |

---

## 🔗 Зависимости (50)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### aio_pika
- `aio_pika`

### aio_pika.exceptions
- `aio_pika.exceptions`

### api.routes
- `api.routes`

### api.workflow_ai
- `api.workflow_ai`

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

### prometheus_client
- `prometheus_client`

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

### starlette.exceptions
- `starlette.exceptions`

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

### uvicorn
- `uvicorn`

### workflow_integration
- `workflow_integration`

---

## 🌐 API Endpoints (38)

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
**Размер:** 1680 символов (107 строк)

**Превью:**
```
# response-service

> 🌐 API Service модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 10,708 |
| **Python файлов** | 30 |
| **Классов** | 80 |
| **Функций** | 33 |
| **API Endpoints** | 18 |
| **Зависимостей** | 42 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (17)

- `/`
- `/analytics/patterns`
- `/analytics/performance`
- `/api/compliance/check`
- `/cases/search`

### POST (1)

- `/critical-incidents`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **TestIncidentEndpoints** (9 методов) - `test_api.py`
- **ResponseRepository** (8 методов) - `repository.py`
- **Settings** (4 методов) - `config.py`
- **TestSubscriberInitialization** (4 методов) - `test_subscribers.py`
- **ResponseEventSubscriber** (4 методов) - `subscribers.py`

### Функции

Всего публичных функций: 33

---

## 🔗 Зависимости

### Внутренние
- `ai_foundation/workflow_intelligence`

```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/response-service/.env.example`
- `requirements.txt` → `platform-services/response-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 47
**Директорий:** 12
