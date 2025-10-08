# Module Scan Report: learning-service

**Дата сканирования:** 2025-10-06 21:11
**Путь:** `platform-services/learning-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 6268 |
| **Python файлов** | 33 |
| **Классов** | 83 |
| **Функций** | 45 |
| **API Endpoints** | 34 |
| **Зависимостей** | 48 |

---

## 🔗 Зависимости (48)


### ai_foundation
- `ai_foundation/workflow_intelligence`

### api.analytics
- `api.analytics`

### api.routes
- `api.routes`

### api.workflow_ai
- `api.workflow_ai`

### config
- `config`

### connection
- `connection`

### contextlib
- `contextlib`

### database
- `database/postgresql`

### datetime
- `datetime`

### dateutil.relativedelta
- `dateutil.relativedelta`

### dotenv
- `dotenv`

### enum
- `enum`

### events.subscribers
- `events.subscribers`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.security
- `fastapi.security`

### gamification_workflow
- `gamification_workflow`

### importlib.util
- `importlib.util`

### jwt
- `jwt`

### logging
- `logging`

### main
- `main`

### models
- `models`

### models.database
- `models.database`

### models.domain
- `models.domain`

### os
- `os`

### pathlib
- `pathlib`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### repositories.gamification_repository
- `repositories.gamification_repository`

### repositories.training_repository
- `repositories.training_repository`

### runtime
- `runtime/eventbus`

### services.gamification_service
- `services.gamification_service`

### services.training_service
- `services.training_service`

### shared
- `shared/auth`
- `shared/config`
- `shared/database`
- `shared/models`
- `shared/utils`

### ssl
- `ssl`

### sys
- `sys`

### time
- `time`

### training_workflow
- `training_workflow`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### workflow_integration
- `workflow_integration`

### workflows.gamification_workflow
- `workflows.gamification_workflow`

### workflows.training_workflow
- `workflows.training_workflow`

---

## 🌐 API Endpoints (34)

- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **POST** `/auth/token` (файл: `main.py`)
- **GET** `/api/learning/programs` (файл: `connection.py`)
- **GET** `/api/governance/policies` (файл: `connection.py`)
- **GET** `/{item_id}/ai-advice` (файл: `workflow_ai.py`)
- **GET** `/benchmarks` (файл: `workflow_ai.py`)
- **GET** `/metrics` (файл: `analytics.py`)
- **GET** `/programs/performance` (файл: `analytics.py`)

---

## 💻 Классы (83)

- **WorkflowSecurityMiddleware** (1 методов) - `workflow_integration.py`
- **TrainingProgram** (1 методов) - `models.py`
- **TrainingEnrollment** (1 методов) - `models.py`
- **CompetencyAssessment** (1 методов) - `models.py`
- **AwarenessCampaign** (1 методов) - `models.py`
- **TrainingTemplate** (1 методов) - `models.py`
- **UserAchievement** (1 методов) - `models.py`
- **TrainingProgramRepository** (1 методов) - `training_repository.py`
- **TrainingEnrollmentRepository** (1 методов) - `training_repository.py`
- **GamificationRepository** (1 методов) - `gamification_repository.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 13695 символов (502 строк)

**Превью:**
```
# BCM Learning Service

**ISO 22301:2019 Clauses 7.2 & 7.3 - Competence & Awareness**
**BCI GPG Practice 2 (PP2: Embracing BC)**

## Overview

The Learning Service provides comprehensive training, competency, and awareness management for Business Continuity Management (BCM) aligned with ISO 22301 standards and BCI Good Practice Guidelines.

### Core Features

- 🎓 **Training Programs** - Create and manage BCM training programs (basic → expert levels)
- 📊 **Competency Assessment** - Identify and track competency gaps (ISO 7.2)
- 📢 **Awareness Campaigns** - Run organization-wide awareness initiatives (ISO 7.3)
- 🏆 **Gamification** - Points, achievements, leaderboards, and learning streaks
- 📄 **Template Library** - Reusable training content and scenarios
- 📈 **Analytics** - Track completion rates, effectiveness, and compliance

## Architecture

```
learning/
├── main.py                          # FastAPI application (26 endpoints)
├── database/
│   ├── models.py                    # SQLAl
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `platform-services/learning-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 51
**Директорий:** 12
