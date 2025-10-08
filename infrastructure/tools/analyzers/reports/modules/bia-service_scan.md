# Module Scan Report: bia-service

**Дата сканирования:** 2025-10-06 22:40
**Путь:** `platform-services/bia-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 6919 |
| **Python файлов** | 30 |
| **Классов** | 77 |
| **Функций** | 26 |
| **API Endpoints** | 31 |
| **Зависимостей** | 60 |

---

## 🔗 Зависимости (60)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### ai_service
- `ai_service`

### api
- `api`

### api.workflow_ai
- `api.workflow_ai`

### asyncio
- `asyncio`

### auth.dependencies
- `auth.dependencies`

### bia_repository
- `bia_repository`

### bia_service
- `bia_service`

### calculations
- `calculations`

### config
- `config`

### connection
- `connection`

### contextlib
- `contextlib`

### database
- `database`
- `database/postgresql`

### database.connection
- `database.connection`

### datetime
- `datetime`

### domain
- `domain`

### enum
- `enum`

### enums
- `enums`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.security
- `fastapi.security`

### httpx
- `httpx`

### jwt
- `jwt`

### logging
- `logging`

### main
- `main`

### models.database
- `models.database`

### models.domain
- `models.domain`

### models.enums
- `models.enums`

### numpy
- `numpy`

### pathlib
- `pathlib`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### pytest
- `pytest`

### report_service
- `report_service`

### repositories.bia_repository
- `repositories.bia_repository`

### routes
- `routes`

### runtime
- `runtime/eventbus`

### services.ai_service
- `services.ai_service`

### services.bia_service
- `services.bia_service`

### services.report_service
- `services.report_service`

### shared
- `shared/audit`
- `shared/auth`
- `shared/cache`
- `shared/config`
- `shared/database`
- `shared/exceptions`
- `shared/history`
- `shared/middleware`
- `shared/utils`

### supply_chain_api
- `supply_chain_api`

### supply_chain_schemas
- `supply_chain_schemas`

### sys
- `sys`

### typing
- `typing`

### unittest.mock
- `unittest.mock`

### utils.calculations
- `utils.calculations`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### validators.business_rules
- `validators.business_rules`

### workflow_integration
- `workflow_integration`

---

## 🌐 API Endpoints (31)

- **POST** `/suppliers` (файл: `supply_chain_api.py`)
- **GET** `/suppliers` (файл: `supply_chain_api.py`)
- **GET** `/suppliers/{supplier_id}` (файл: `supply_chain_api.py`)
- **PATCH** `/suppliers/{supplier_id}` (файл: `supply_chain_api.py`)
- **GET** `/suppliers/{supplier_id}/risk-profile` (файл: `supply_chain_api.py`)
- **GET** `/single-points-of-failure` (файл: `supply_chain_api.py`)
- **POST** `/disruptions` (файл: `supply_chain_api.py`)
- **POST** `/what-if-analysis` (файл: `supply_chain_api.py`)
- **GET** `/summary` (файл: `supply_chain_api.py`)
- **GET** `/health` (файл: `main.py`)

---

## 💻 Классы (77)

- **TestBIAProcessModel** (14 методов) - `test_models.py`
- **TestRecoveryObjectivesValidation** (5 методов) - `test_business_validators.py`
- **TestWorkaroundCapacityValidation** (3 методов) - `test_business_validators.py`
- **TestDependencyModel** (3 методов) - `test_models.py`
- **TestBIAProcessCreateModel** (3 методов) - `test_models.py`
- **BIARepository** (3 методов) - `bia_repository.py`
- **BIAProcess** (3 методов) - `domain.py`
- **TestFinancialImpactTimelineValidation** (2 методов) - `test_business_validators.py`
- **TestNonSelfDependencyValidation** (2 методов) - `test_business_validators.py`
- **TestCriticalProcessRequirementsValidation** (2 методов) - `test_business_validators.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 7111 символов (294 строк)

**Превью:**
```
# BIA Service - Business Impact Analysis

**ISO 22301 Clause 8.2.2**

Unified architecture microservice for comprehensive Business Impact Analysis.

---

## ✅ MIGRATION STATUS

**Source:** `/Users/MD/ISO-22301—копия/services/SERVICES/BCM/bia/main.py` (695 lines)
**Target:** `/Users/MD/AI-Platform-ISO/services/bcm/bia/` (unified architecture)
**Status:** ✅ **COMPLETE - NO FUNCTIONALITY LOST**

### What Was Preserved:
- ✅ All 8 Enums (CriticalityLevel, ProcessStatus, etc.)
- ✅ All 6 Models (BIAProcess, AIRTOSuggestion, etc.)
- ✅ All 12 BIA endpoints
- ✅ All 8 Supply Chain endpoints (supply_chain_api.py)
- ✅ All helper functions (calculate_criticality_score, etc.)
- ✅ Event publishing (bcm.bia.started, bcm.bia.completed, etc.)
- ✅ AI integration (RTO suggestions, dependency discovery)
- ✅ WHO Essential Services tiers (healthcare)
- ✅ In-memory storage (original behavior)

---

## 📁 Structure

```
bia/
├── __init__.py
├── main.py                      # FastAPI app with lifespan
├── config.
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `platform-services/bia-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 37
**Директорий:** 8
