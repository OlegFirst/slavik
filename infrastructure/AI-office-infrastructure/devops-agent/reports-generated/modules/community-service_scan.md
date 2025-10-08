# Module Scan Report: community-service

**Дата сканирования:** 2025-10-08 15:17
**Путь:** `platform-services/community-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 18334 |
| **Python файлов** | 70 |
| **Классов** | 170 |
| **Функций** | 8 |
| **API Endpoints** | 107 |
| **Зависимостей** | 84 |

---

## 🔗 Зависимости (84)


### abc
- `abc`

### ai_client
- `ai_client`

### api
- `api`

### api.dependencies
- `api.dependencies`

### api.execution_router
- `api.execution_router`

### api.forum
- `api.forum`

### api.knowledge
- `api.knowledge`

### api.organizations
- `api.organizations`

### api.scenarios
- `api.scenarios`

### api.simulation_router
- `api.simulation_router`

### asyncio
- `asyncio`

### asyncpg
- `asyncpg`

### base_engine
- `base_engine`

### clients_client
- `clients_client`

### connection
- `connection`

### contextlib
- `contextlib`

### database
- `database/postgresql`

### database.connection
- `database.connection`

### database.models
- `database.models`

### database.organization_model
- `database.organization_model`

### database.simulation_model
- `database.simulation_model`

### datetime
- `datetime`

### decimal
- `decimal`

### dotenv
- `dotenv`

### engines.monte_carlo_engine
- `engines.monte_carlo_engine`

### engines.scenario_engine
- `engines.scenario_engine`

### engines.what_if_engine
- `engines.what_if_engine`

### enum
- `enum`

### events.subscribers
- `events.subscribers`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### forum
- `forum`

### forum_service
- `forum_service`

### httpx
- `httpx`

### integrations.ai_client
- `integrations.ai_client`

### integrations.governance_client
- `integrations.governance_client`

### integrations.learning_client
- `integrations.learning_client`

### integrations.portal_client
- `integrations.portal_client`

### integrations.validation_client
- `integrations.validation_client`

### knowledge
- `knowledge`

### knowledge_service
- `knowledge_service`

### logging
- `logging`

### markdown
- `markdown`

### models
- `models`

### moderation_service
- `moderation_service`

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

### re
- `re`

### reputation_service
- `reputation_service`

### runtime
- `runtime/eventbus`

### scenario_service
- `scenario_service`

### scenarios
- `scenarios`

### schemas.forum
- `schemas.forum`

### schemas.knowledge
- `schemas.knowledge`

### schemas.project
- `schemas.project`

### schemas.proposal
- `schemas.proposal`

### schemas.review
- `schemas.review`

### schemas.scenarios
- `schemas.scenarios`

### schemas.specialist
- `schemas.specialist`

### search_service
- `search_service`

### services.forum_service
- `services.forum_service`

### services.knowledge_service
- `services.knowledge_service`

### services.moderation_service
- `services.moderation_service`

### services.project_service
- `services.project_service`

### services.proposal_service
- `services.proposal_service`

### services.reputation_service
- `services.reputation_service`

### services.review_service
- `services.review_service`

### services.scenario_service
- `services.scenario_service`

### services.search_service
- `services.search_service`

### services.specialist_service
- `services.specialist_service`

### shared
- `shared/auth`
- `shared/database`

### slugify
- `slugify`

### ssl
- `ssl`

### sys
- `sys`

### time
- `time`

### traceback
- `traceback`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### validation_client
- `validation_client`

---

## 🌐 API Endpoints (107)

- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `, response_model=ScenarioListResponse)
async def get_scenarios(
    scenario_type: Optional[str] = Query(None, description=` (файл: `scenarios.py`)
- **GET** `/{scenario_id}` (файл: `scenarios.py`)
- **POST** `/{scenario_id}/deploy` (файл: `scenarios.py`)
- **POST** `/{scenario_id}/reviews` (файл: `scenarios.py`)
- **GET** `/{scenario_id}/reviews` (файл: `scenarios.py`)
- **GET** `/featured/popular` (файл: `scenarios.py`)
- **GET** `/library` (файл: `scenario_library_router.py`)
- **GET** `/library/{scenario_id}` (файл: `scenario_library_router.py`)

---

## 💻 Классы (170)

- **MonteCarloEngine** (4 методов) - `monte_carlo_engine.py`
- **BaseSimulationEngine** (3 методов) - `base_engine.py`
- **KnowledgeService** (3 методов) - `knowledge_service.py`
- **SpecialistService** (2 методов) - `specialist_service.py`
- **Organization** (1 методов) - `organization_model.py`
- **OrganizationUser** (1 методов) - `organization_model.py`
- **OrganizationAuditLog** (1 методов) - `organization_model.py`
- **KnowledgeArticle** (1 методов) - `models.py`
- **ArticleBookmark** (1 методов) - `models.py`
- **ArticleVote** (1 методов) - `models.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 2148 символов (127 строк)

**Превью:**
```
# community-service

> 🌐 API Service модуль платформы

## 📊 Обзор

| Метрика | Значение |
|---------|----------|
| **Строк кода** | 18,334 |
| **Python файлов** | 70 |
| **Классов** | 170 |
| **Функций** | 8 |
| **API Endpoints** | 100 |
| **Зависимостей** | 84 |

**Тип модуля:** 🌐 API Service
**Последнее обновление:** 2025-10-07

---

## 🌐 API Endpoints

### GET (52)

- `/`
- `/`
- `/articles`
- `/articles/{article_id}`
- `/articles/{article_id}/discussion`

### POST (34)

- `/ai-generate`
- `/articles`
- `/articles/{article_id}/bookmark`
- `/articles/{article_id}/discuss`
- `/articles/{article_id}/verify`

### PUT (3)

- `/{project_id}`
- `/{proposal_id}`
- `/{specialist_id}`

### DELETE (8)

- `/articles/{article_id}/bookmark`
- `/articles/{article_id}/vote`
- `/simulations/{sim_id}`
- `/{project_id}`
- `/{proposal_id}`

### PATCH (3)

- `/articles/{article_id}`
- `/posts/{post_id}`
- `/topics/{topic_id}`

[→ Полная документация API](./API.md)

---

## 🏗️ Архитектура

### Ключевые к
```

---

## 📂 Структура

**Всего файлов:** 114
**Директорий:** 22
