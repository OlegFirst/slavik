# Module Scan Report: ai_workflow_optimizer

**Дата сканирования:** 2025-10-08 14:33
**Путь:** `intelligent-core/ai_workflow_optimizer`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 1701 |
| **Python файлов** | 2 |
| **Классов** | 10 |
| **Функций** | 2 |
| **API Endpoints** | 12 |
| **Зависимостей** | 28 |

---

## 🔗 Зависимости (28)


### asyncio
- `asyncio`

### base64
- `base64`

### contextlib
- `contextlib`

### database
- `database/postgresql`

### datetime
- `datetime`

### event_intelligence.event_intelligence_system
- `event_intelligence.event_intelligence_system`

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

### pathlib
- `pathlib`

### pickle
- `pickle`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### shared
- `shared/platform_client`

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

### subprocess
- `subprocess`

### sys
- `sys`

### typing
- `typing`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (12)

- **GET** `/health` (файл: `main.py`)
- **GET** `/metrics` (файл: `main.py`)
- **POST** `/api/v1/optimize/performance` (файл: `main.py`)
- **GET** `/api/v1/analyze/bottlenecks/{process_id}` (файл: `main.py`)
- **GET** `/api/v1/optimize/resources/{process_id}` (файл: `main.py`)
- **GET** `/api/v1/detect/anomalies/{process_id}` (файл: `main.py`)
- **POST** `/api/v1/models/retrain` (файл: `main.py`)
- **GET** `/api/v1/models/status` (файл: `main.py`)
- **GET** `/api/v1/ai/analyze/{process_id}` (файл: `main.py`)
- **POST** `/api/v1/ai/recommendations` (файл: `main.py`)

---

## 💻 Классы (10)

- **WorkflowOptimizerService** (17 методов) - `main.py`
- **EventIntelligenceIntegration** (7 методов) - `event_intelligence_integration.py`
- **ProcessExecution** (0 методов) - `main.py`
- **OptimizationPrediction** (0 методов) - `main.py`
- **MLModel** (0 методов) - `main.py`
- **ProcessOptimizationRequest** (0 методов) - `main.py`
- **OptimizationPredictionResponse** (0 методов) - `main.py`
- **BottleneckAnalysisResponse** (0 методов) - `main.py`
- **ResourceOptimizationResponse** (0 методов) - `main.py`
- **AnomalyDetectionResponse** (0 методов) - `main.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 14722 символов (602 строк)

**Превью:**
```
# AI Workflow Optimizer

## Overview
AI Workflow Optimizer is an ML-powered service that provides intelligent optimization and prediction capabilities for business process workflows. It uses machine learning models to predict execution times, detect bottlenecks, identify anomalies, and optimize resource allocation for business continuity and incident response processes.

## Features

- **Performance Prediction**: ML-based prediction of process execution times
- **Bottleneck Detection**: Identifies potential workflow bottlenecks before they occur
- **Anomaly Detection**: Detects unusual patterns in process execution using Isolation Forest
- **Resource Optimization**: Recommends optimal resource allocation for processes
- **Self-Learning Models**: Continuously improves predictions based on historical data
- **Platform Integration**: Integrates with AI Foundation, Expertise Center, and Workflow Intelligence
- **Real-time Analysis**: Provides instant AI-powered analysis and recommendations
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `intelligent-core/ai_workflow_optimizer/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 6
**Директорий:** 2
