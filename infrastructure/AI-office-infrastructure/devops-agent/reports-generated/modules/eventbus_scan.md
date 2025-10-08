# Module Scan Report: eventbus

**Дата сканирования:** 2025-10-08 16:44
**Путь:** `infrastructure/eventbus`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 3445 |
| **Python файлов** | 27 |
| **Классов** | 22 |
| **Функций** | 25 |
| **API Endpoints** | 4 |
| **Зависимостей** | 22 |

---

## 🔗 Зависимости (22)


### abc
- `abc`

### asyncio
- `asyncio`

### base
- `base`

### collections
- `collections`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### enum
- `enum`

### fastapi
- `fastapi`

### fontTools.misc.timeTools
- `fontTools.misc.timeTools`

### fontTools.ttLib
- `fontTools.ttLib`

### json
- `json`

### os
- `os`

### parse_tfm
- `parse_tfm`

### pathlib
- `pathlib`

### pytest
- `pytest`

### re
- `re`

### runtime
- `runtime/eventbus`

### subprocess
- `subprocess`

### sys
- `sys`

### traceback
- `traceback`

### typing
- `typing`

### uuid
- `uuid`

---

## 🌐 API Endpoints (4)

- **POST** `/workflows` (файл: `fastapi_integration.py`)
- **GET** `/` (файл: `fastapi_integration.py`)
- **POST** `/workflows/{workflow_id}/complete` (файл: `fastapi_integration.py`)
- **GET** `/stats` (файл: `fastapi_integration.py`)

---

## 💻 Классы (22)

- **TfmReader** (6 методов) - `parse_tfm.py`
- **CharInfoWord** (3 методов) - `parse_tfm.py`
- **Event** (3 методов) - `events.py`
- **InMemoryEventBus** (3 методов) - `memory.py`
- **EventBusConfig** (2 методов) - `config.py`
- **LigKernProgram** (2 методов) - `parse_tfm.py`
- **TfmFile** (2 методов) - `parse_tfm.py`
- **RedisStreamEventBus** (2 методов) - `redis_streams.py`
- **BaseSubscriber** (2 методов) - `base.py`
- **_Known** (1 методов) - `flatted.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 10636 символов (552 строк)

**Превью:**
```
# EventBus - Pluggable Event System

Clean architecture event bus for the BCM Platform with multiple backend support.

## Features

- ✅ Clean interface (`IEventBus`) - backend-agnostic
- ✅ Multiple backends: memory, Redis Streams, (RabbitMQ coming)
- ✅ Type-safe events with `Event` class
- ✅ Wildcard subscriptions (`workflow.*`, `*`)
- ✅ Consumer groups (load balancing)
- ✅ Automatic retry logic
- ✅ Zero vendor lock-in

## Quick Start

### 1. Install

```bash
# No dependencies for in-memory backend
pip install -e .

# For Redis backend
pip install redis
```

### 2. Basic Usage

```python
from infrastructure.eventbus import create_eventbus, Event, EventPriority

# Create bus
bus = create_eventbus('memory')  # or 'redis'

# Publish event
event = Event.create(
    event_type='workflow.stage_changed',
    data={'workflow_id': 'bia_001', 'stage': 'analysis'},
    source='workflow-engine',
    tenant_id='tenant_123'
)
await bus.publish(event)

# Subscribe to events
async def handle_workflow_
```

---

## ⚙️ Конфигурация

- `pyproject.toml` → `infrastructure/eventbus/pyproject.toml`
- `requirements.txt` → `infrastructure/eventbus/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 46
**Директорий:** 11
