# Module Scan Report: database

**Дата сканирования:** 2025-10-07 01:16
**Путь:** `infrastructure/database`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 3543 |
| **Python файлов** | 20 |
| **Классов** | 17 |
| **Функций** | 10 |
| **API Endpoints** | 0 |
| **Зависимостей** | 33 |

---

## 🔗 Зависимости (33)


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
**Размер:** 2689 символов (116 строк)

**Превью:**
```
# Database Infrastructure

Централизованная инфраструктура для всех баз данных платформы.

---

## 📁 Структура

```
database/
├── postgresql/              # PostgreSQL (Supabase)
│   ├── managers/           # DB managers, cache, redis, rate limiter
│   ├── migrations_source/  # SQL миграции (001-043)
│   ├── DB_CONFIG.md       # Полная конфигурация
│   └── apply_*.sh         # Скрипты миграций
│
└── vector-db/              # Qdrant Vector Database
    ├── qdrant/            # Клиент и конфигурация
    └── SETUP_COMPLETE.md  # Статус настройки
```

---

## 🗄️ PostgreSQL (Supabase)

**Тип:** Relational Database (PostgreSQL 15)
**Регион:** eu-north-1 (AWS Stockholm)
**URL:** https://tpdkhddtbhpoqzzgxfni.supabase.co

**Архитектура:** Одна БД с множественными схемами
- 10+ схем (public, community, intelligence, bcm, bia, risk, governance...)
- RLS для изоляции tenant'ов
- Connection pooling (20 базовых + 40 burst = 60 одновременных)

**Документация:** [postgresql/DB_CONFIG.md](postgresql/DB
```

---

## 📂 Структура

**Всего файлов:** 92
**Директорий:** 6
