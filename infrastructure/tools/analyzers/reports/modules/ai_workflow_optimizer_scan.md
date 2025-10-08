# Module Scan Report: ai_workflow_optimizer

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `intelligent-core/ai_workflow_optimizer`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 946 |
| **Python файлов** | 1 |
| **Классов** | 9 |
| **Функций** | 1 |
| **API Endpoints** | 7 |
| **Зависимостей** | 20 |

---

## 🔗 Зависимости (20)


### asyncio
- `asyncio`

### database
- `database/postgresql`

### datetime
- `datetime`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### joblib
- `joblib`

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

### pickle
- `pickle`

### pydantic
- `pydantic`

### sklearn.cluster
- `sklearn.cluster`

### sklearn.ensemble
- `sklearn.ensemble`

### sklearn.metrics
- `sklearn.metrics`

### sklearn.model_selection
- `sklearn.model_selection`

### sklearn.preprocessing
- `sklearn.preprocessing`

### typing
- `typing`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (7)

- **GET** `/health` (файл: `main.py`)
- **POST** `/api/v1/optimize/performance` (файл: `main.py`)
- **GET** `/api/v1/analyze/bottlenecks/{process_id}` (файл: `main.py`)
- **GET** `/api/v1/optimize/resources/{process_id}` (файл: `main.py`)
- **GET** `/api/v1/detect/anomalies/{process_id}` (файл: `main.py`)
- **POST** `/api/v1/models/retrain` (файл: `main.py`)
- **GET** `/api/v1/models/status` (файл: `main.py`)

---

## 💻 Классы (9)

- **WorkflowOptimizerService** (17 методов) - `main.py`
- **ProcessExecution** (0 методов) - `main.py`
- **OptimizationPrediction** (0 методов) - `main.py`
- **MLModel** (0 методов) - `main.py`
- **ProcessOptimizationRequest** (0 методов) - `main.py`
- **OptimizationPredictionResponse** (0 методов) - `main.py`
- **BottleneckAnalysisResponse** (0 методов) - `main.py`
- **ResourceOptimizationResponse** (0 методов) - `main.py`
- **AnomalyDetectionResponse** (0 методов) - `main.py`

---

## ⚙️ Конфигурация

- `requirements.txt` → `intelligent-core/ai_workflow_optimizer/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 3
**Директорий:** 1
