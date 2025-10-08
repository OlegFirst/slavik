# Module Scan Report: predictive

**Дата сканирования:** 2025-10-08 14:33
**Путь:** `intelligent-core/predictive`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 4761 |
| **Python файлов** | 15 |
| **Классов** | 22 |
| **Функций** | 4 |
| **API Endpoints** | 9 |
| **Зависимостей** | 40 |

---

## 🔗 Зависимости (40)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### ai_services
- `ai_services/predictive`

### aiohttp
- `aiohttp`

### api
- `api`

### apscheduler.schedulers.asyncio
- `apscheduler.schedulers.asyncio`

### apscheduler.triggers.cron
- `apscheduler.triggers.cron`

### asyncio
- `asyncio`

### asyncpg
- `asyncpg`

### collections
- `collections`

### contextlib
- `contextlib`

### daily_digests
- `daily_digests`

### database
- `database/postgresql`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### dependencies
- `dependencies`

### event_handlers
- `event_handlers`

### event_intelligence.continuous_monitor
- `event_intelligence.continuous_monitor`

### event_intelligence.event_intelligence_system
- `event_intelligence.event_intelligence_system`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### httpx
- `httpx`

### integration.dependencies
- `integration.dependencies`

### journey_predictor
- `journey_predictor`

### llm.llm_router
- `llm.llm_router`

### logging
- `logging`

### numpy
- `numpy`

### os
- `os`

### pathlib
- `pathlib`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### rag.pipeline
- `rag.pipeline`

### repository
- `repository`

### runtime
- `runtime/eventbus`

### scheduler.daily_digests
- `scheduler.daily_digests`

### services.journey_predictor
- `services.journey_predictor`

### services.proactive_recommendations
- `services.proactive_recommendations`

### sys
- `sys`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (9)

- **GET** `/health` (файл: `main.py`)
- **GET** `/metrics` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/journey/{org_id}` (файл: `predictions.py`)
- **GET** `/certification/{org_id}` (файл: `predictions.py`)
- **GET** `/recommendations/{org_id}` (файл: `predictions.py`)
- **GET** `/expert-demand` (файл: `predictions.py`)
- **GET** `/similar-organizations/{org_id}` (файл: `predictions.py`)
- **GET** `/stats/eventbus` (файл: `predictions.py`)

---

## 💻 Классы (22)

- **JourneyPredictor** (11 методов) - `journey_predictor.py`
- **ProactiveRecommendationsEngine** (6 методов) - `proactive_recommendations.py`
- **EventIntelligenceLearning** (5 методов) - `event_intelligence_learning.py`
- **ExpertDemandForecaster** (5 методов) - `demand_forecaster.py`
- **PredictiveAIFoundation** (4 методов) - `ai_foundation_integration.py`
- **PredictiveEventHandlers** (3 методов) - `event_handlers.py`
- **NotificationClient** (2 методов) - `dependencies.py`
- **PredictiveRepository** (1 методов) - `repository.py`
- **EventBusService** (1 методов) - `dependencies.py`
- **Dependencies** (1 методов) - `dependencies.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 1579 символов (93 строк)

**Превью:**
```
# predictive

> Предиктивная аналитика и ML модели

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 2,995 |
| **Python файлов** | 12 |
| **Классов** | 18 |
| **Функций** | 3 |
| **API Endpoints** | 7 |
| **Зависимостей** | 32 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (7)

- `/`
- `/certification/{org_id}`
- `/expert-demand`
- `/health`
- `/journey/{org_id}`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **JourneyPredictor** (11 методов) - `journey_predictor.py`
- **ProactiveRecommendationsEngine** (6 методов) - `proactive_recommendations.py`
- **ExpertDemandForecaster** (5 методов) - `demand_forecaster.py`
- **NotificationClient** (2 методов) - `dependencies.py`
- **PredictiveRepository** (1 методов) - `repository.py`

### Функции

Всего публичных функций: 3

---

## 🔗 Зависимости

### Внутренние
- `ai_foundation/workflow_intelligence`
- `ai_services/predic
```

---

## 📂 Структура

**Всего файлов:** 25
**Директорий:** 8
