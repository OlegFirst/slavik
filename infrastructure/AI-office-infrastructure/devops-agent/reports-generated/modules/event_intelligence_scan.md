# Module Scan Report: event_intelligence

**Дата сканирования:** 2025-10-08 14:33
**Путь:** `intelligent-core/event_intelligence`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 3545 |
| **Python файлов** | 11 |
| **Классов** | 31 |
| **Функций** | 0 |
| **API Endpoints** | 17 |
| **Зависимостей** | 30 |

---

## 🔗 Зависимости (30)


### analyzer
- `analyzer`

### api
- `api`

### argparse
- `argparse`

### ast
- `ast`

### asyncio
- `asyncio`

### collections
- `collections`

### contextlib
- `contextlib`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### event_intelligence.api
- `event_intelligence.api`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### json
- `json`

### knowledge_base
- `knowledge_base`

### learner
- `learner`

### learning.engines.knowledge_base_connector
- `learning.engines.knowledge_base_connector`

### llm.llm_router
- `llm.llm_router`

### logging
- `logging`

### os
- `os`

### pathlib
- `pathlib`

### predictor
- `predictor`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### rag.pipeline
- `rag.pipeline`

### routes
- `routes`

### services.ai_foundation_integration
- `services.ai_foundation_integration`

### subprocess
- `subprocess`

### sys
- `sys`

### typing
- `typing`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (17)

- **GET** `/health` (файл: `api.py`)
- **POST** `/analyze` (файл: `api.py`)
- **POST** `/analyze/domain` (файл: `api.py`)
- **POST** `/learning/suggest` (файл: `api.py`)
- **POST** `/learning/feedback` (файл: `api.py`)
- **GET** `/learning/stats` (файл: `api.py`)
- **GET** `/learning/report` (файл: `api.py`)
- **POST** `/predict/gaps` (файл: `api.py`)
- **GET** `/knowledge/similar/{event_name}` (файл: `api.py`)
- **GET** `/knowledge/patterns/{event_name}` (файл: `api.py`)

---

## 💻 Классы (31)

- **CodeHealer** (11 методов) - `code_healer.py`
- **EventAnalyzer** (6 методов) - `analyzer.py`
- **EventLearner** (6 методов) - `learner.py`
- **EventIntelligenceAIFoundation** (5 методов) - `ai_foundation_integration.py`
- **EventKnowledgeBase** (3 методов) - `knowledge_base.py`
- **EventPredictor** (1 методов) - `predictor.py`
- **StubKnowledgeBase** (1 методов) - `knowledge_base.py`
- **LearningExample** (1 методов) - `learner.py`
- **EventPrediction** (0 методов) - `predictor.py`
- **EventAnalysis** (0 методов) - `analyzer.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 8131 символов (322 строк)

**Превью:**
```
# Event Intelligence

## Overview
Event Intelligence is an AI-powered layer that provides intelligent analysis, learning, and prediction capabilities for event-driven architecture. It analyzes event patterns, learns from historical data, predicts future gaps, and accumulates knowledge to continuously improve the event-based system.

## Features
- **Event Analysis**: Deep analysis of events and patterns with importance scoring
- **ML-Powered Learning**: Learns from historical event data and developer feedback
- **Gap Prediction**: Predicts missing event handlers and publishers using machine learning
- **Knowledge Base**: Accumulates and retrieves event-related knowledge
- **Pattern Detection**: Identifies common event patterns and anti-patterns
- **AI-Powered Recommendations**: Generates actionable insights based on event analysis
- **Real-time Feedback Loop**: Records developer decisions and outcomes for continuous improvement

## Architecture

### Key Components

#### EventAnalyzer (`
```

---

## 📂 Структура

**Всего файлов:** 13
**Директорий:** 3
