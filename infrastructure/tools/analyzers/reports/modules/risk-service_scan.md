# Module Scan Report: risk-service

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `platform-services/risk-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 6127 |
| **Python файлов** | 23 |
| **Классов** | 48 |
| **Функций** | 23 |
| **API Endpoints** | 30 |
| **Зависимостей** | 47 |

---

## 🔗 Зависимости (47)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### api.routes
- `api.routes`

### api.workflow_ai
- `api.workflow_ai`

### auth.dependencies
- `auth.dependencies`

### auth.jwt_handler
- `auth.jwt_handler`

### business_logic
- `business_logic`

### config
- `config`

### contextlib
- `contextlib`

### database
- `database`
- `database/postgresql`

### database.connection
- `database.connection`

### datetime
- `datetime`

### dependencies
- `dependencies`

### domain
- `domain`

### enum
- `enum`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.security
- `fastapi.security`

### fastapi.testclient
- `fastapi.testclient`

### httpx
- `httpx`

### importlib.util
- `importlib.util`

### jose
- `jose`

### jwt
- `jwt`

### jwt_handler
- `jwt_handler`

### logging
- `logging`

### main
- `main`

### models.database
- `models.database`

### models.domain
- `models.domain`

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

### pydantic_settings
- `pydantic_settings`

### pytest
- `pytest`

### pytest_asyncio
- `pytest_asyncio`

### random
- `random`

### repositories.repository
- `repositories.repository`

### repository
- `repository`

### routes
- `routes`

### services.business_logic
- `services.business_logic`

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

## 🌐 API Endpoints (30)

- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/risks` (файл: `dependencies.py`)
- **GET** `/public-risks` (файл: `dependencies.py`)
- **POST** `/critical-risks` (файл: `dependencies.py`)
- **GET** `/insights` (файл: `workflow_ai.py`)
- **GET** `/recommendations` (файл: `workflow_ai.py`)
- **GET** `/cases/search` (файл: `workflow_ai.py`)
- **GET** `/cases/{case_id}/similar` (файл: `workflow_ai.py`)

---

## 💻 Классы (48)

- **RiskService** (7 методов) - `business_logic.py`
- **TestUserCreation** (6 методов) - `test_auth.py`
- **TestJWTVerification** (5 методов) - `test_auth.py`
- **TestJWTDecoding** (4 методов) - `test_auth.py`
- **TestUtilities** (4 методов) - `test_business_logic.py`
- **TestTokenEdgeCases** (3 методов) - `test_auth.py`
- **WorkflowSecurityMiddleware** (1 методов) - `workflow_integration.py`
- **RiskRepository** (1 методов) - `repository.py`
- **RiskDB** (1 методов) - `database.py`
- **FAIRAnalysisDB** (1 методов) - `database.py`

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/risk-service/.env.example`
- `requirements.txt` → `platform-services/risk-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 27
**Директорий:** 7
