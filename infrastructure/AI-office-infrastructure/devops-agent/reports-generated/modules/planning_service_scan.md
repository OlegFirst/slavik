# Module Scan Report: planning_service

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/planning_service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 6201 |
| **Python файлов** | 35 |
| **Классов** | 50 |
| **Функций** | 10 |
| **API Endpoints** | 20 |
| **Зависимостей** | 54 |

---

## 🔗 Зависимости (54)


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

### auth.models
- `auth.models`

### business_logic
- `business_logic`

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

### events.publishers
- `events.publishers`

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

### functools
- `functools`

### httpx
- `httpx`

### jose
- `jose`

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

### repository
- `repository`

### routes
- `routes`

### services.business_logic
- `services.business_logic`

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

---

## 🌐 API Endpoints (20)

- **GET** `/health` (файл: `main.py`)
- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/strategies/{strategy_id}/ai-advice` (файл: `workflow_ai.py`)
- **POST** `/strategies/{strategy_id}/complete-case` (файл: `workflow_ai.py`)
- **GET** `/benchmarks` (файл: `workflow_ai.py`)
- **GET** `/metrics` (файл: `metrics.py`)
- **GET** `/health/detailed` (файл: `health.py`)
- **GET** `/health/ready` (файл: `health.py`)
- **GET** `/health/live` (файл: `health.py`)

---

## 💻 Классы (50)

- **TestCostBenefitRequestValidation** (11 методов) - `test_validation.py`
- **TestCostBreakdownValidation** (8 методов) - `test_validation.py`
- **TestBenefitAnalysisValidation** (8 методов) - `test_validation.py`
- **TestPaybackPeriodCalculation** (8 методов) - `test_cost_benefit.py`
- **TestRecommendationLogic** (8 методов) - `test_cost_benefit.py`
- **TestStrategyCreateValidation** (7 методов) - `test_validation.py`
- **TestNPVCalculation** (7 методов) - `test_cost_benefit.py`
- **TestROIAnalysisValidation** (6 методов) - `test_validation.py`
- **StrategyService** (6 методов) - `business_logic.py`
- **TestResourceRequirementValidation** (5 методов) - `test_validation.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 1896 символов (121 строк)

**Превью:**
```
# planning_service

> 🌐 API Service модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 6,197 |
| **Python файлов** | 34 |
| **Классов** | 50 |
| **Функций** | 10 |
| **API Endpoints** | 22 |
| **Зависимостей** | 52 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (12)

- `/`
- `/`
- `/api/compliance/check`
- `/benchmarks`
- `/health`

### POST (8)

- `/`
- `/approve`
- `/cost-benefit`
- `/strategies`
- `/strategies/{strategy_id}/complete-case`

### PUT (1)

- `/{strategy_id}`

### DELETE (1)

- `/{strategy_id}`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **TestCostBenefitRequestValidation** (11 методов) - `test_validation.py`
- **TestCostBreakdownValidation** (8 методов) - `test_validation.py`
- **TestBenefitAnalysisValidation** (8 методов) - `test_validation.py`
- **TestPaybackPeriodCalculation** (8 методов) - `test_cost_benefit.py`
- **TestReco
```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/planning_service/.env.example`
- `requirements.txt` → `platform-services/planning_service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 101
**Директорий:** 11
