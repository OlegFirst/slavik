# Module Scan Report: можетпригодится

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `intelligent-core/можетпригодится`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 8234 |
| **Python файлов** | 28 |
| **Классов** | 91 |
| **Функций** | 24 |
| **API Endpoints** | 99 |
| **Зависимостей** | 43 |

---

## 🔗 Зависимости (43)


### __future__
- `__future__`

### abc
- `abc`

### app.api.v1.endpoints.scenarios
- `app.api.v1.endpoints.scenarios`

### app.core.ai_engine
- `app.core.ai_engine`

### app.core.database
- `app.core.database`

### app.core.security
- `app.core.security`

### app.models
- `app.models`

### app.schemas.scenario
- `app.schemas.scenario`

### asyncio
- `asyncio`

### bcrypt
- `bcrypt`

### contextlib
- `contextlib`

### crud
- `crud`

### database
- `database/postgresql`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### db
- `db`

### email.mime.multipart
- `email.mime.multipart`

### email.mime.text
- `email.mime.text`

### enum
- `enum`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.security
- `fastapi.security`

### httpx
- `httpx`

### json
- `json`

### jwt
- `jwt`

### logging
- `logging`

### main
- `main`

### mock_data
- `mock_data`

### models
- `models`

### odoo
- `odoo`

### odoo.exceptions
- `odoo.exceptions`

### os
- `os`

### pydantic
- `pydantic`

### requests
- `requests`

### runtime
- `runtime/eventbus`

### scenario
- `scenario`

### smtplib
- `smtplib`

### sys
- `sys`

### typing
- `typing`

### utils
- `utils`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### xml.etree.ElementTree
- `xml.etree.ElementTree`

---

## 🌐 API Endpoints (99)

- **GET** `/health` (файл: `main.py`)
- **POST** `/api/bpmn/processes` (файл: `main.py`)
- **GET** `/api/bpmn/processes` (файл: `main.py`)
- **GET** `/api/bpmn/processes/{process_id}` (файл: `main.py`)
- **POST** `/api/bpmn/processes/{process_id}/start` (файл: `main.py`)
- **GET** `/api/bpmn/instances` (файл: `main.py`)
- **GET** `/api/bpmn/instances/{instance_id}` (файл: `main.py`)
- **GET** `/api/bpmn/tasks` (файл: `main.py`)
- **POST** `/api/bpmn/tasks/{task_id}/complete` (файл: `main.py`)
- **POST** `/api/bpmn/instances/{instance_id}/terminate` (файл: `main.py`)

---

## 💻 Классы (91)

- **ConsultationSessionManager** (9 методов) - `consultation_session_pattern.py`
- **BCMAIControlDashboard** (8 методов) - `ai_control_dashboard.py`
- **BCMAnthropicIntegration** (7 методов) - `anthropic_integration.py`
- **AIOrganRegistry** (6 методов) - `collective_intelligence_pattern.py`
- **IntelligentComplianceChecker** (6 методов) - `app.py`
- **CollectiveWisdomTracker** (5 методов) - `collective_intelligence_pattern.py`
- **BCMEventBusIntegration** (3 методов) - `eventbus_integration.py`
- **CollectiveDecisionSynthesizer** (3 методов) - `collective_intelligence_pattern.py`
- **SessionContextBuilder** (3 методов) - `consultation_session_pattern.py`
- **WeightedConfidenceScorer** (2 методов) - `collective_intelligence_pattern.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 852 символов (31 строк)

**Превью:**
```
# Может Пригодиться - Полезный Код

Здесь хранится код который был убран из основной кодовой базы, но может пригодиться в будущем.

## llm_clients/

**Источник**: `orchestration/ai-orchestration/muscles/llm_clients/`

**Что**: Старый Anthropic client специально для governance анализа

**Файлы**:
- `anthropic_client.py` - AnthropicGovernanceBrain класс

**Почему сохранили**:
- Использует claude-3-sonnet-20240229 (старая модель)
- Специализированные governance prompts
- Может пригодиться для легаси интеграций
- НЕ ДУБЛИКАТ ai-foundation/llm/llm_router.py (это другое!)

**Когда использовать**:
- Если нужен специфичный governance-анализ
- Если нужна конкретная версия Claude модели
- Для миграции старого кода

**Также доступен в**: `workflow_intelligence/integration/legacy_anthropic_client.py`

---

**Дата**: 2025-10-06
**Команда**: Claude + MD

```

---

## 📂 Структура

**Всего файлов:** 51
**Директорий:** 15
