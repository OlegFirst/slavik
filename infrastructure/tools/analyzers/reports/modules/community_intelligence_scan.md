# Module Scan Report: community_intelligence

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `intelligent-core/community_intelligence`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 7408 |
| **Python файлов** | 31 |
| **Классов** | 51 |
| **Функций** | 7 |
| **API Endpoints** | 36 |
| **Зависимостей** | 53 |

---

## 🔗 Зависимости (53)


### ai_services
- `ai_services/community_intelligence`
- `ai_services/intelligent_core`
- `ai_services/living_docs`
- `ai_services/predictive_timeline`
- `ai_services/services`

### anonymizer
- `anonymizer`

### api
- `api`

### asyncio
- `asyncio`

### collections
- `collections`

### config
- `config`

### contextlib
- `contextlib`

### contribution_service
- `contribution_service`

### database
- `database`
- `database/postgresql`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### enum
- `enum`

### events.subscribers
- `events.subscribers`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### hashlib
- `hashlib`

### httpx
- `httpx`

### joblib
- `joblib`

### json
- `json`

### logging
- `logging`

### models.database
- `models.database`

### numpy
- `numpy`

### os
- `os`

### pathlib
- `pathlib`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### pytest
- `pytest`

### re
- `re`

### routes
- `routes`

### runtime
- `runtime/eventbus`

### services.anonymizer
- `services.anonymizer`

### services.case_library_bridge
- `services.case_library_bridge`

### services.contribution_service
- `services.contribution_service`

### services.peer_review_service
- `services.peer_review_service`

### services.reputation_engine
- `services.reputation_engine`

### services.workflow_completion_handler
- `services.workflow_completion_handler`

### services.workflow_integration_service
- `services.workflow_integration_service`

### shared
- `shared/auth`
- `shared/database`

### sklearn.ensemble
- `sklearn.ensemble`

### sklearn.model_selection
- `sklearn.model_selection`

### sklearn.preprocessing
- `sklearn.preprocessing`

### sys
- `sys`

### typing
- `typing`

### unittest.mock
- `unittest.mock`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### yaml
- `yaml`

---

## 🌐 API Endpoints (36)

- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/pending` (файл: `reviews.py`)
- **GET** `/my` (файл: `reviews.py`)
- **GET** `/{review_id}` (файл: `reviews.py`)
- **GET** `/{user_id}` (файл: `reputation.py`)
- **GET** `/{user_id}/expertise/{module}` (файл: `reputation.py`)
- **GET** `/leaderboard/global` (файл: `reputation.py`)
- **GET** `/leaderboard/{module}` (файл: `reputation.py`)
- **GET** `/transactions/{user_id}` (файл: `reputation.py`)

---

## 💻 Классы (51)

- **LivingDocumentationService** (9 методов) - `living_docs.py`
- **SmartAnonymizer** (9 методов) - `anonymizer.py`
- **MLPredictor** (7 методов) - `ml_predictor.py`
- **UnifiedAIContextBuilder** (6 методов) - `unified_ai_context.py`
- **PredictiveTimelineService** (5 методов) - `predictive_timeline.py`
- **ContributionService** (4 методов) - `contribution_service.py`
- **ReputationEngine** (3 методов) - `reputation_engine.py`
- **CaseLibraryBridge** (3 методов) - `case_library_bridge.py`
- **PeerReviewService** (2 методов) - `peer_review_service.py`
- **WorkflowIntegrationService** (1 методов) - `workflow_integration_service.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 3074 символов (140 строк)

**Превью:**
```
# Community Intelligence Service

**Port:** 8030
**Status:** Production Ready
**Version:** 1.0.0

## Documentation

All technical documentation is located in the [`docs/`](docs/) folder:
- **[Technical Specification](docs/TECHNICAL_SPECIFICATION.md)** - Comprehensive technical documentation
- **[Analysis and Improvements](docs/ANALYSIS_AND_IMPROVEMENTS.md)** - Production readiness assessment and recommendations

Archived documentation can be found in [`archive/docs/`](archive/docs/).

---

## 🎯 Purpose

Transforms passive case collection into **active community-driven knowledge creation** through:

- **Workflow Integration:** Auto-capture success stories from completed workflows
- **Peer Review:** Quality assurance through expert validation
- **Reputation Economy:** Gamification to incentivize contributions
- **Case Library:** Searchable knowledge base of best practices

---

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

```
Workfl
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `intelligent-core/community_intelligence/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 45
**Директорий:** 10
