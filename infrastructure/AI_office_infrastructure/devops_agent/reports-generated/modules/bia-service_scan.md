# Module Scan Report: bia-service

**Дата сканирования:** 2025-10-08 15:17
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
**Размер:** 2207 символов (136 строк)

**Превью:**
```
# bia-service

> 🌐 API Service модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 6,919 |
| **Python файлов** | 30 |
| **Классов** | 77 |
| **Функций** | 26 |
| **API Endpoints** | 31 |
| **Зависимостей** | 60 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (17)

- `/api/compliance/check`
- `/benchmarks`
- `/health`
- `/metrics/cache`
- `/processes`

### POST (9)

- `/disruptions`
- `/processes`
- `/processes/bulk`
- `/processes/bulk/validate`
- `/processes/{process_id}/complete`

### PUT (1)

- `/processes/{process_id}`

### DELETE (2)

- `/processes/bulk`
- `/processes/{process_id}`

### PATCH (2)

- `/processes/bulk`
- `/suppliers/{supplier_id}`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **TestBIAProcessModel** (14 методов) - `test_models.py`
- **TestRecoveryObjectivesValidation** (5 методов) - `test_business_validators.py`
- **TestWorkaroun
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `platform-services/bia-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 40
**Директорий:** 8
