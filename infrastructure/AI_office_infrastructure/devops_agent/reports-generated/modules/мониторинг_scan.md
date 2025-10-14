# Module Scan Report: мониторинг

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/мониторинг`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 3346 |
| **Python файлов** | 5 |
| **Классов** | 20 |
| **Функций** | 1 |
| **API Endpoints** | 33 |
| **Зависимостей** | 30 |

---

## 🔗 Зависимости (30)


### aiofiles
- `aiofiles`

### analyzers.ast_analyzer
- `analyzers.ast_analyzer`

### analyzers.dependency_mapper
- `analyzers.dependency_mapper`

### apscheduler.schedulers.asyncio
- `apscheduler.schedulers.asyncio`

### asyncio
- `asyncio`

### automation_toolkit
- `automation_toolkit`

### collections
- `collections`

### database
- `database/postgresql`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.responses
- `fastapi.responses`

### httpx
- `httpx`

### json
- `json`

### logging
- `logging`

### numpy
- `numpy`

### os
- `os`

### pandas
- `pandas`

### pathlib
- `pathlib`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### statistics
- `statistics`

### subprocess
- `subprocess`

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

### yaml
- `yaml`

---

## 🌐 API Endpoints (33)

- **GET** `/health` (файл: `main.py`)
- **GET** `/compliance/status` (файл: `main.py`)
- **GET** `/compliance/iso-clauses` (файл: `main.py`)
- **GET** `/compliance/services` (файл: `main.py`)
- **GET** `/compliance/alerts` (файл: `main.py`)
- **POST** `/compliance/alerts` (файл: `main.py`)
- **PUT** `/compliance/alerts/{alert_id}/acknowledge` (файл: `main.py`)
- **PUT** `/compliance/alerts/{alert_id}/resolve` (файл: `main.py`)
- **GET** `/compliance/nonconformities` (файл: `main.py`)
- **POST** `/compliance/nonconformities` (файл: `main.py`)

---

## 💻 Классы (20)

- **ProcessMiningEngine** (21 методов) - `main.py`
- **AutomationToolkitIntegration** (7 методов) - `automation_toolkit.py`
- **ComplianceStorage** (6 методов) - `main.py`
- **NotificationIntegration** (1 методов) - `notifications.py`
- **Config** (0 методов) - `main.py`
- **ComplianceAlert** (0 методов) - `main.py`
- **NonconformityRecord** (0 методов) - `main.py`
- **AuditRequirement** (0 методов) - `main.py`
- **ServiceRegistration** (0 методов) - `main.py`
- **ComplianceMetrics** (0 методов) - `main.py`

---

## 📂 Структура

**Всего файлов:** 29
**Директорий:** 7
