# Module Scan Report: runtime

**Дата сканирования:** 2025-10-07 01:16
**Путь:** `infrastructure/runtime`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 4689 |
| **Python файлов** | 24 |
| **Классов** | 33 |
| **Функций** | 12 |
| **API Endpoints** | 9 |
| **Зависимостей** | 27 |

---

## 🔗 Зависимости (27)


### abc
- `abc`

### aio_pika
- `aio_pika`

### aio_pika.abc
- `aio_pika.abc`

### asyncio
- `asyncio`

### base
- `base`

### contextlib
- `contextlib`

### database
- `database/postgresql`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### enum
- `enum`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.responses
- `fastapi.responses`

### health_monitor
- `health_monitor`

### httpx
- `httpx`

### iso_service_map
- `iso_service_map`

### json
- `json`

### logging
- `logging`

### os
- `os`

### pydantic
- `pydantic`

### pytest
- `pytest`

### re
- `re`

### runtime
- `runtime/eventbus`

### service_registry
- `service_registry`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (9)

- **POST** `/workflows` (файл: `fastapi_integration.py`)
- **GET** `/` (файл: `fastapi_integration.py`)
- **POST** `/workflows/{workflow_id}/complete` (файл: `fastapi_integration.py`)
- **GET** `/stats` (файл: `fastapi_integration.py`)
- **GET** `/health` (файл: `main.py`)
- **POST** `/api/v1/notifications/broadcast` (файл: `main.py`)
- **GET** `/api/v1/channels/{channel_id}/users` (файл: `main.py`)
- **GET** `/api/v1/channels/{channel_id}/messages` (файл: `main.py`)
- **GET** `/api/v1/stats` (файл: `main.py`)

---

## 💻 Классы (33)

- **Event** (3 методов) - `events.py`
- **InMemoryEventBus** (3 методов) - `memory.py`
- **ConnectionManager** (3 методов) - `main.py`
- **EventBusConfig** (2 методов) - `config.py`
- **RedisStreamEventBus** (2 методов) - `redis_streams.py`
- **BaseSubscriber** (2 методов) - `base.py`
- **CaseCollectorSubscriber** (1 методов) - `subscriber_example.py`
- **AnalyticsSubscriber** (1 методов) - `subscriber_example.py`
- **AuditSubscriber** (1 методов) - `subscriber_example.py`
- **WebSocketMessage** (1 методов) - `main.py`

---

## 📂 Структура

**Всего файлов:** 44
**Директорий:** 12
