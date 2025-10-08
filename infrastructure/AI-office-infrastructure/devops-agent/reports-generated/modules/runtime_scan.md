# Module Scan Report: runtime

**Дата сканирования:** 2025-10-08 16:44
**Путь:** `infrastructure/runtime`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 2107 |
| **Python файлов** | 6 |
| **Классов** | 18 |
| **Функций** | 5 |
| **API Endpoints** | 6 |
| **Зависимостей** | 23 |

---

## 🔗 Зависимости (23)


### aio_pika
- `aio_pika`

### aio_pika.abc
- `aio_pika.abc`

### asyncio
- `asyncio`

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

## 🌐 API Endpoints (6)

- **GET** `/health` (файл: `main.py`)
- **POST** `/api/v1/notifications/broadcast` (файл: `main.py`)
- **GET** `/api/v1/channels/{channel_id}/users` (файл: `main.py`)
- **GET** `/api/v1/channels/{channel_id}/messages` (файл: `main.py`)
- **GET** `/api/v1/stats` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)

---

## 💻 Классы (18)

- **ConnectionManager** (3 методов) - `main.py`
- **WebSocketMessage** (1 методов) - `main.py`
- **RabbitMQManager** (1 методов) - `rabbitmq_manager.py`
- **HealthCheckResult** (1 методов) - `health_monitor.py`
- **HealthMonitor** (1 методов) - `health_monitor.py`
- **Service** (1 методов) - `service_registry.py`
- **ServiceRegistry** (1 методов) - `service_registry.py`
- **MessageType** (0 методов) - `main.py`
- **ChannelType** (0 методов) - `main.py`
- **UserStatus** (0 методов) - `main.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 10548 символов (474 строк)

**Превью:**
```
# Runtime Infrastructure

**Status:** ✅ Production Ready
**Last Updated:** 2025-10-07
**Coverage:** 100%

---

## Overview

Runtime layer provides messaging (RabbitMQ), real-time communication (WebSocket), event-driven architecture (EventBus), and service discovery.

### Components Status

| Component | Status | Port | Details |
|-----------|--------|------|---------|
| **RabbitMQ** | ✅ Running | 5673 | Message queue, Management UI on 15673 |
| **WebSocket** | ✅ Running | 8050 | Real-time bidirectional communication |
| **EventBus** | ✅ Ready | - | Event-driven architecture library |
| **Service Discovery** | ✅ Ready | - | Service registry with health checks |

---

## Quick Start

### 1. Start RabbitMQ (Already Running)

```bash
docker ps | grep rabbitmq
# intelligent-core-rabbitmq is running
```

Management UI: http://localhost:15673 (guest/guest)

### 2. Start WebSocket Service

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/runtime/realtime-websocket
python3 main.py
```

WebSo
```

---

## 📂 Структура

**Всего файлов:** 18
**Директорий:** 4
