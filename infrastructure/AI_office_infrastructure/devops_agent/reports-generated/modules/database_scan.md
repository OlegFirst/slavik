# Module Scan Report: database

**Дата сканирования:** 2025-10-08 16:44
**Путь:** `infrastructure/database`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 3830 |
| **Python файлов** | 21 |
| **Классов** | 17 |
| **Функций** | 13 |
| **API Endpoints** | 1 |
| **Зависимостей** | 34 |

---

## 🔗 Зависимости (34)


### argparse
- `argparse`

### asyncio
- `asyncio`

### asyncpg
- `asyncpg`

### client
- `client`

### config
- `config`

### contextlib
- `contextlib`

### database
- `database/postgresql`
- `database/vector-db`

### datetime
- `datetime`

### dotenv
- `dotenv`

### enum
- `enum`

### fastapi
- `fastapi`

### functools
- `functools`

### glob
- `glob`

### hashlib
- `hashlib`

### infrastructure.database.postgresql.managers.db_manager
- `infrastructure.database.postgresql.managers.db_manager`

### json
- `json`

### logging
- `logging`

### managers.cache_manager
- `managers.cache_manager`

### managers.db_manager
- `managers.db_manager`

### managers.rate_limiter
- `managers.rate_limiter`

### managers.session_store
- `managers.session_store`

### os
- `os`

### pathlib
- `pathlib`

### pydantic_settings
- `pydantic_settings`

### runtime
- `runtime/eventbus`

### secrets
- `secrets`

### subprocess
- `subprocess`

### sys
- `sys`

### time
- `time`

### traceback
- `traceback`

### typing
- `typing`

### urllib.parse
- `urllib.parse`

### uuid
- `uuid`

---

## 🌐 API Endpoints (1)

- **GET** `/data` (файл: `__init__.py`)

---

## 💻 Классы (17)

- **DatabaseManager** (8 методов) - `db_manager.py`
- **SupabaseManager** (8 методов) - `supabase_client.py`
- **QdrantVectorDB** (7 методов) - `client.py`
- **CacheManager** (5 методов) - `cache_manager.py`
- **MigrationRunner** (4 методов) - `db_manager.py`
- **SessionStore** (4 методов) - `session_store.py`
- **SystemDBManager** (3 методов) - `db_manager.py`
- **BusinessDBManager** (3 методов) - `db_manager.py`
- **PlatformDBManager** (2 методов) - `db_manager.py`
- **RLSManager** (2 методов) - `db_manager.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 11293 символов (496 строк)

**Превью:**
```
# Database Infrastructure 🧠

**Status:** ✅ Production Ready with AI Intelligence
**Last Updated:** 2025-10-08
**Coverage:** 100%

---

## Overview

Centralized infrastructure layer providing PostgreSQL, Vector DB (Qdrant), Redis, and RabbitMQ for the entire AI Platform.

**All services are centralized and shared across the platform.**

### 🆕 Database Intelligence Specialist ✅ PRODUCTION READY

**MOVED TO:** `/infrastructure/AI-office-infrastructure/db-intelligence/`

Database Intelligence Specialist теперь является **AI colleague** в Infrastructure Management Office.

AI-powered autonomous monitoring and optimization service with **dual integration**:

**Capabilities:**
- Real-time query performance monitoring (pg_stat_statements)
- Slow query detection and AI-powered optimization suggestions
- Security monitoring (RLS, SQL injection, DOS protection)
- Health monitoring and alerting
- CLI admin access via REST API
- Prometheus metrics export

**Integration Architecture:**
- **EventBus*
```

---

## 📂 Структура

**Всего файлов:** 103
**Директорий:** 9
