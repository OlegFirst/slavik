# Module Scan Report: security

**Дата сканирования:** 2025-10-08 16:44
**Путь:** `infrastructure/security`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 1847 |
| **Python файлов** | 5 |
| **Классов** | 9 |
| **Функций** | 8 |
| **API Endpoints** | 9 |
| **Зависимостей** | 25 |

---

## 🔗 Зависимости (25)


### asyncio
- `asyncio`

### base64
- `base64`

### bcrypt
- `bcrypt`

### contextlib
- `contextlib`

### database
- `database/postgresql`

### database.managers.db_manager
- `database.managers.db_manager`

### database.managers.session_store
- `database.managers.session_store`

### datetime
- `datetime`

### dotenv
- `dotenv`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.security
- `fastapi.security`

### httpx
- `httpx`

### hvac
- `hvac`

### hvac.exceptions
- `hvac.exceptions`

### jwt
- `jwt`

### logging
- `logging`

### os
- `os`

### pydantic
- `pydantic`

### runtime
- `runtime/eventbus`

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

## 🌐 API Endpoints (9)

- **POST** `/signup` (файл: `auth_service.py`)
- **POST** `/login` (файл: `auth_service.py`)
- **POST** `/logout` (файл: `auth_service.py`)
- **GET** `/me` (файл: `auth_service.py`)
- **GET** `/health` (файл: `auth_service.py`)
- **POST** `/auth/login` (файл: `main.py`)
- **POST** `/auth/signup` (файл: `main.py`)
- **GET** `/auth/me` (файл: `main.py`)
- **POST** `/auth/logout` (файл: `main.py`)

---

## 💻 Классы (9)

- **VaultManager** (16 методов) - `vault_manager.py`
- **VaultHelper** (7 методов) - `vault_helper.py`
- **LoginRequest** (0 методов) - `auth_service.py`
- **SignupRequest** (0 методов) - `auth_service.py`
- **TokenResponse** (0 методов) - `auth_service.py`
- **UserInfo** (0 методов) - `auth_service.py`
- **LoginRequest** (0 методов) - `main.py`
- **SignupRequest** (0 методов) - `main.py`
- **TokenResponse** (0 методов) - `main.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 6015 символов (302 строк)

**Превью:**
```
# Security Infrastructure

**Status:** ✅ Production Ready
**Last Updated:** 2025-10-07
**Coverage:** 100%

---

## Overview

Security layer provides authentication, authorization, secrets management, and API gateway functionality for the AI-Platform-ISO.

### Components Status

| Component | Status | Port | Details |
|-----------|--------|------|---------|
| **HashiCorp Vault** | ✅ Running | 8200 | Centralized secrets management |
| **Auth Service** | ✅ Running | 8001 | JWT + Supabase authentication |
| **API Gateway** | ⚠️ Planned | 8000 | Kong or custom FastAPI gateway |
| **Rate Limiting** | ✅ Ready | - | Redis-based rate limiter |
| **Audit Logging** | ✅ Ready | - | PostgreSQL audit trail |

---

## Quick Start

### 1. Start Vault

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/security
./start_vault.sh
```

Vault will be available at `http://localhost:8200`

### 2. Start Auth Service

```bash
cd /Users/MD/AI-Platform-ISO/infrastructure/security/auth
python3 main.py
```

Auth 
```

---

## 📂 Структура

**Всего файлов:** 16
**Директорий:** 3
