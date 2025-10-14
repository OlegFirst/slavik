# Module Scan Report: gateway

**Дата сканирования:** 2025-10-08 16:44
**Путь:** `infrastructure/gateway`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 5036 |
| **Python файлов** | 20 |
| **Классов** | 28 |
| **Функций** | 8 |
| **API Endpoints** | 10 |
| **Зависимостей** | 42 |

---

## 🔗 Зависимости (42)


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

## 💻 Классы (28)

- **HealthChecker** (9 методов) - `health_checker.py`
- **JWTHandler** (7 методов) - `jwt_handler.py`
- **RateLimitMiddleware** (6 методов) - `rate_limit.py`
- **LoadBalancer** (6 методов) - `load_balancer.py`
- **ServiceRouter** (5 методов) - `router.py`
- **AuthenticationMiddleware** (4 методов) - `auth.py`
- **RedisClient** (3 методов) - `redis_client.py`
- **AuditLogMiddleware** (2 методов) - `audit.py`
- **AdaptiveRateLimiter** (1 методов) - `rate_limit.py`
- **ServiceInstance** (1 методов) - `load_balancer.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 10396 символов (523 строк)

**Превью:**
```
# Gateway Infrastructure

**Status:** ✅ Running (Degraded)
**Last Updated:** 2025-10-07
**Coverage:** 100%

---

## Overview

API Gateway provides centralized entry point for all platform services with authentication, rate limiting, load balancing, and intelligent routing.

### Components Status

| Component | Status | Port | Details |
|-----------|--------|------|---------|
| **API Gateway** | ✅ Running | 8000 | Main gateway operational |
| **Authentication** | ✅ Active | - | JWT-based auth middleware |
| **Rate Limiting** | ⚠️ Degraded | - | Redis connection issues |
| **Load Balancer** | ✅ Active | - | Intelligent routing enabled |
| **Health Checker** | ✅ Active | - | Service monitoring active |
| **Audit Logger** | ✅ Active | - | PostgreSQL audit trail |

---

## Quick Start

### 1. Gateway is Running

```bash
# Check status
curl http://localhost:8000/health

# Gateway already running on port 8000
ps aux | grep "gateway.*main.py"
```

### 2. Configuration

**Location:** `api-gatew
```

---

## 📂 Структура

**Всего файлов:** 38
**Директорий:** 8
