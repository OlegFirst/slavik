# Module Scan Report: bcm-coordination-service

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/bcm-coordination-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 1023 |
| **Python файлов** | 2 |
| **Классов** | 3 |
| **Функций** | 0 |
| **API Endpoints** | 9 |
| **Зависимостей** | 12 |

---

## 🔗 Зависимости (12)


### analyzer_coordinator
- `analyzer_coordinator`

### contextlib
- `contextlib`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### httpx
- `httpx`

### logging
- `logging`

### orchestration.bcm_services_orchestrator.analyzer_coordinator
- `orchestration.bcm_services_orchestrator.analyzer_coordinator`

### pathlib
- `pathlib`

### pydantic
- `pydantic`

### sys
- `sys`

### typing
- `typing`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (9)

- **GET** `/health` (файл: `main.py`)
- **GET** `/api/v1/analyzers` (файл: `main.py`)
- **GET** `/api/v1/stats` (файл: `main.py`)
- **POST** `/api/v1/analyze` (файл: `main.py`)
- **POST** `/api/v1/analyze/batch` (файл: `main.py`)
- **POST** `/api/v1/analyze/compliance` (файл: `main.py`)
- **POST** `/api/v1/analyze/risk` (файл: `main.py`)
- **POST** `/api/v1/analyze/impact` (файл: `main.py`)
- **POST** `/api/v1/analyze/iso_clause` (файл: `main.py`)

---

## 💻 Классы (3)

- **BCMExecutor** (1 методов) - `bcm_executor.py`
- **AnalysisRequest** (0 методов) - `main.py`
- **BatchAnalysisRequest** (0 методов) - `main.py`

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/bcm-coordination-service/.env.example`
- `requirements.txt` → `platform-services/bcm-coordination-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 5
**Директорий:** 1
