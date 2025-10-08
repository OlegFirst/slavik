# Module Scan Report: gateway

**Дата сканирования:** 2025-10-07 01:16
**Путь:** `infrastructure/gateway`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 5335 |
| **Python файлов** | 22 |
| **Классов** | 32 |
| **Функций** | 8 |
| **API Endpoints** | 10 |
| **Зависимостей** | 44 |

---

## 🔗 Зависимости (44)


### aio_pika
- `aio_pika`

### asyncio
- `asyncio`

### asyncpg
- `asyncpg`

### collections
- `collections`

### config
- `config`

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

### fastapi.security
- `fastapi.security`

### hashlib
- `hashlib`

### httpx
- `httpx`

### json
- `json`

### jwt
- `jwt`

### jwt.exceptions
- `jwt.exceptions`

### logging
- `logging`

### middleware.audit
- `middleware.audit`

### middleware.auth
- `middleware.auth`

### middleware.rate_limit
- `middleware.rate_limit`

### motor.motor_asyncio
- `motor.motor_asyncio`

### os
- `os`

### prometheus_fastapi_instrumentator
- `prometheus_fastapi_instrumentator`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### random
- `random`

### re
- `re`

### router
- `router`

### routing.health_checker
- `routing.health_checker`

### routing.load_balancer
- `routing.load_balancer`

### routing.router
- `routing.router`

### runtime
- `runtime/eventbus`

### secrets
- `secrets`

### starlette.middleware.base
- `starlette.middleware.base`

### structlog
- `structlog`

### sys
- `sys`

### time
- `time`

### typing
- `typing`

### utils.jwt_handler
- `utils.jwt_handler`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (10)

- **GET** `/health` (файл: `main.py`)
- **POST** `/api/v1/gateway/ai/analyze` (файл: `main.py`)
- **POST** `/api/v1/gateway/ai/optimize` (файл: `main.py`)
- **GET** `/api/v1/gateway/services` (файл: `main.py`)
- **GET** `/health/databases` (файл: `main.py`)
- **POST** `/query` (файл: `main.py`)
- **POST** `/auth/odoo` (файл: `main.py`)
- **GET** `/auth/odoo/session/{session_id}` (файл: `main.py`)
- **DELETE** `/auth/odoo/session/{session_id}` (файл: `main.py`)
- **GET** `/metrics` (файл: `main.py`)

---

## 💻 Классы (32)

- **HealthChecker** (9 методов) - `health_checker.py`
- **JWTHandler** (7 методов) - `jwt_handler.py`
- **RateLimitMiddleware** (6 методов) - `rate_limit.py`
- **LoadBalancer** (6 методов) - `load_balancer.py`
- **ServiceRouter** (5 методов) - `router.py`
- **AIAgentRouter** (5 методов) - `router.py`
- **AuthenticationMiddleware** (4 методов) - `auth.py`
- **RedisClient** (3 методов) - `redis_client.py`
- **AuditLogMiddleware** (2 методов) - `audit.py`
- **AdaptiveRateLimiter** (1 методов) - `rate_limit.py`

---

## 📂 Структура

**Всего файлов:** 38
**Директорий:** 10
