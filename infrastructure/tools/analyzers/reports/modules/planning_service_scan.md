# Module Scan Report: planning_service

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `platform-services/planning_service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 6197 |
| **Python файлов** | 34 |
| **Классов** | 50 |
| **Функций** | 10 |
| **API Endpoints** | 22 |
| **Зависимостей** | 52 |

---

## 🔗 Зависимости (52)


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

## 🌐 API Endpoints (22)

- **GET** `/health` (файл: `main.py`)
- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/strategies/{strategy_id}/ai-advice` (файл: `workflow_ai.py`)
- **POST** `/strategies/{strategy_id}/complete-case` (файл: `workflow_ai.py`)
- **GET** `/benchmarks` (файл: `workflow_ai.py`)
- **GET** `/metrics` (файл: `metrics.py`)
- **GET** `/health` (файл: `health.py`)
- **GET** `/health/detailed` (файл: `health.py`)
- **GET** `/health/ready` (файл: `health.py`)

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
**Размер:** 8552 символов (329 строк)

**Превью:**
```
# Planning Service - Business Continuity Strategy

**Service:** `planning_service`
**Port:** `8011`
**ISO 22301:** Clause 8.3
**BCI Practice:** PP4 (Solutions Design)

## Overview

Planning Service manages business continuity strategy development, cost-benefit analysis, and strategy approval workflows. This service implements ISO 22301 Clause 8.3 requirements for determining and selecting business continuity strategies.

## Architecture

```
planning_service/
├── config.py                   # Configuration
├── main.py                     # FastAPI app
├── database.py                 # Database connection
├── dependencies.py             # Dependency injection
├── models/
│   ├── domain.py              # Pydantic models
│   └── database.py            # SQLAlchemy models
├── api/
│   └── routes.py              # API endpoints
├── services/
│   └── business_logic.py      # Business logic
├── repositories/
│   └── repository.py          # Data access layer
├── events/
│   └── publishers.py 
```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/planning_service/.env.example`
- `requirements.txt` → `platform-services/planning_service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 98
**Директорий:** 11
