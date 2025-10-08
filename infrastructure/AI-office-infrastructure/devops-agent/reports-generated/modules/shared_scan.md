# Module Scan Report: shared

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/shared`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 513 |
| **Python файлов** | 4 |
| **Классов** | 0 |
| **Функций** | 2 |
| **API Endpoints** | 4 |
| **Зависимостей** | 12 |

---

## 🔗 Зависимости (12)


### asyncio
- `asyncio`

### datetime
- `datetime`

### fastapi
- `fastapi`

### healthcheck
- `healthcheck`

### logging
- `logging`

### logging_config
- `logging_config`

### shared
- `shared`
- `shared/healthcheck`
- `shared/logging_config`

### sys
- `sys`

### typing
- `typing`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (4)

- **GET** `/health` (файл: `USAGE_EXAMPLE.py`)
- **GET** `/health/simple` (файл: `USAGE_EXAMPLE.py`)
- **GET** `/health/database` (файл: `USAGE_EXAMPLE.py`)
- **GET** `/api/example` (файл: `USAGE_EXAMPLE.py`)

---

## 📄 README

**Файл:** `README.md`
**Размер:** 4145 символов (190 строк)

**Превью:**
```
# Shared Utilities for Platform Services

Common utilities and helpers used across all platform services.

## Installation

The shared module is automatically available when you're in the `platform-services` directory:

```python
from shared import setup_logging, comprehensive_healthcheck
```

## Modules

### 1. Logging Configuration (`logging_config.py`)

Standardized logging setup for all services.

#### Basic Usage:

```python
from shared import setup_logging

logger = setup_logging("my-service", "INFO")
logger.info("Service started")
```

#### With File Output:

```python
from shared.logging_config import setup_file_logging

logger = setup_file_logging(
    service_name="my-service",
    log_level="DEBUG",
    log_file="/var/log/my-service.log"
)
```

#### Log Format:

```
2025-10-08 09:36:45,123 - my-service - module_name - INFO - Log message
```

### 2. Health Check System (`healthcheck.py`)

Comprehensive health monitoring with dependency tracking.

#### Full Health Check:

```p
```

---

## 📂 Структура

**Всего файлов:** 6
**Директорий:** 1
