# Module Scan Report: predictive

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `intelligent-core/predictive`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 2995 |
| **Python файлов** | 12 |
| **Классов** | 18 |
| **Функций** | 3 |
| **API Endpoints** | 7 |
| **Зависимостей** | 32 |

---

## 🔗 Зависимости (32)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### ai_services
- `ai_services/predictive`

### api
- `api`

### apscheduler.schedulers.asyncio
- `apscheduler.schedulers.asyncio`

### apscheduler.triggers.cron
- `apscheduler.triggers.cron`

### asyncio
- `asyncio`

### asyncpg
- `asyncpg`

### collections
- `collections`

### contextlib
- `contextlib`

### daily_digests
- `daily_digests`

### database
- `database/postgresql`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### dependencies
- `dependencies`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### httpx
- `httpx`

### integration.dependencies
- `integration.dependencies`

### journey_predictor
- `journey_predictor`

### logging
- `logging`

### numpy
- `numpy`

### os
- `os`

### pathlib
- `pathlib`

### pydantic
- `pydantic`

### repository
- `repository`

### scheduler.daily_digests
- `scheduler.daily_digests`

### services.journey_predictor
- `services.journey_predictor`

### services.proactive_recommendations
- `services.proactive_recommendations`

### sys
- `sys`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (7)

- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/journey/{org_id}` (файл: `predictions.py`)
- **GET** `/certification/{org_id}` (файл: `predictions.py`)
- **GET** `/recommendations/{org_id}` (файл: `predictions.py`)
- **GET** `/expert-demand` (файл: `predictions.py`)
- **GET** `/similar-organizations/{org_id}` (файл: `predictions.py`)

---

## 💻 Классы (18)

- **JourneyPredictor** (11 методов) - `journey_predictor.py`
- **ProactiveRecommendationsEngine** (6 методов) - `proactive_recommendations.py`
- **ExpertDemandForecaster** (5 методов) - `demand_forecaster.py`
- **NotificationClient** (2 методов) - `dependencies.py`
- **PredictiveRepository** (1 методов) - `repository.py`
- **Dependencies** (1 методов) - `dependencies.py`
- **DailyDigestScheduler** (1 методов) - `daily_digests.py`
- **MilestoneResponse** (0 методов) - `predictions.py`
- **JourneyPredictionResponse** (0 методов) - `predictions.py`
- **CertificationPredictionResponse** (0 методов) - `predictions.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 9620 символов (444 строк)

**Превью:**
```
# 🔮 Predictive Journey Service

**Magic Level:** ⭐⭐⭐⭐⭐
**Port:** 8031
**Status:** MAGIC COMPLETE! ✨

## 📚 Documentation

Вся документация находится в папке [`docs/`](docs/):
- **[Архитектура](docs/ARCHITECTURE.md)** - детальная архитектура системы
- **[Интеграция](docs/INTEGRATION_COMPLETE.md)** - интеграция с платформой
- **[Magic Complete](docs/MAGIC_COMPLETE.md)** - описание "магических" функций
- **[Анализ и улучшения](docs/ANALYSIS_AND_IMPROVEMENTS.md)** - ⚠️ найденные проблемы и рекомендации

---

## 🎯 The Magic

Platform **predicts the future** of your BCM journey:

```
User completes BIA
   ↓
Platform instantly shows:
"Based on 83 similar organizations:

📅 Your Next 90 Days:
   Week 2 (Oct 18): Risk Assessment
     - Duration: 4-5 weeks
     - Confidence: 87%
     - Expert: Jane Doe (recommended)
     - Cost: $6K-10K

   Week 6 (Nov 15): BC Plans
     - Duration: 6 weeks
     - Confidence: 76%

   Week 12 (Dec 27): Internal Audit
     - Duration: 2 weeks
     - Confidence: 68%

```

---

## 📂 Структура

**Всего файлов:** 19
**Директорий:** 7
