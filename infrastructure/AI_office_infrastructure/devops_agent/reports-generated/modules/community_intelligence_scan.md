# Module Scan Report: community_intelligence

**Дата сканирования:** 2025-10-08 14:33
**Путь:** `intelligent-core/community_intelligence`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 8116 |
| **Python файлов** | 32 |
| **Классов** | 52 |
| **Функций** | 7 |
| **API Endpoints** | 37 |
| **Зависимостей** | 57 |

---

## 🔗 Зависимости (57)


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

### llm.llm_router
- `llm.llm_router`

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

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### pytest
- `pytest`

### rag.pipeline
- `rag.pipeline`

### re
- `re`

### routes
- `routes`

### runtime
- `runtime/eventbus`

### services.ai_foundation_integration
- `services.ai_foundation_integration`

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

## 🌐 API Endpoints (37)

- **GET** `/health` (файл: `main.py`)
- **GET** `/metrics` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **POST** `, response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def submit_review(
    request: ReviewSubmit,
    current_user: dict = Depends(get_current_user),
    service: PeerReviewService = Depends(get_peer_review_service),
    db: AsyncSession = Depends(get_db)
):
    ` (файл: `reviews.py`)
- **GET** `/pending` (файл: `reviews.py`)
- **GET** `/my` (файл: `reviews.py`)
- **GET** `/{review_id}` (файл: `reviews.py`)
- **GET** `/{user_id}` (файл: `reputation.py`)
- **GET** `/{user_id}/expertise/{module}` (файл: `reputation.py`)
- **GET** `/leaderboard/global` (файл: `reputation.py`)

---

## 💻 Классы (52)

- **LivingDocumentationService** (9 методов) - `living_docs.py`
- **SmartAnonymizer** (9 методов) - `anonymizer.py`
- **MLPredictor** (7 методов) - `ml_predictor.py`
- **CommunityAIFoundation** (7 методов) - `ai_foundation_integration.py`
- **UnifiedAIContextBuilder** (6 методов) - `unified_ai_context.py`
- **PredictiveTimelineService** (5 методов) - `predictive_timeline.py`
- **ContributionService** (4 методов) - `contribution_service.py`
- **ReputationEngine** (3 методов) - `reputation_engine.py`
- **CaseLibraryBridge** (3 методов) - `case_library_bridge.py`
- **PeerReviewService** (2 методов) - `peer_review_service.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 2084 символов (122 строк)

**Превью:**
```
# community_intelligence

> Сообщество и обмен знаниями

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 7,408 |
| **Python файлов** | 31 |
| **Классов** | 51 |
| **Функций** | 7 |
| **API Endpoints** | 36 |
| **Зависимостей** | 53 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (28)

- `/`
- `/clauses/search`
- `/contributions/pending-reviews`
- `/contributions/{contribution_id}`
- `/guidance/{clause_id}`

### POST (7)

- `/annotations`
- `/annotations/{annotation_id}/vote`
- `/contributions`
- `/contributions/{contribution_id}/review`
- `/from-workflow/{workflow_id}`

### DELETE (1)

- `/{contribution_id}`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые классы

- **LivingDocumentationService** (9 методов) - `living_docs.py`
- **SmartAnonymizer** (9 методов) - `anonymizer.py`
- **MLPredictor** (7 методов) - `ml_predictor.py`
- **UnifiedAIContextBuilder** (6 методов) - `uni
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `intelligent-core/community_intelligence/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 48
**Директорий:** 10
