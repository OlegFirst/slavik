# Module Scan Report: collective

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `intelligent-core/collective`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 4779 |
| **Python файлов** | 14 |
| **Классов** | 34 |
| **Функций** | 0 |
| **API Endpoints** | 9 |
| **Зависимостей** | 34 |

---

## 🔗 Зависимости (34)


### ai_services
- `ai_services/intelligent_core`
- `ai_services/services`

### api
- `api`

### asyncio
- `asyncio`

### config
- `config`

### contextlib
- `contextlib`

### database
- `database/postgresql`

### datetime
- `datetime`

### dependencies
- `dependencies`

### enum
- `enum`

### external
- `external/anthropic`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.security
- `fastapi.security`

### hashlib
- `hashlib`

### httpx
- `httpx`

### json
- `json`

### logging
- `logging`

### math
- `math`

### models.database
- `models.database`

### os
- `os`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### re
- `re`

### services.analytics_client
- `services.analytics_client`

### services.anonymizer_service
- `services.anonymizer_service`

### services.case_library
- `services.case_library`

### services.llm_client
- `services.llm_client`

### services.mcp_partisia_integration
- `services.mcp_partisia_integration`

### services.stuck_detector_service
- `services.stuck_detector_service`

### shared
- `shared/database`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (9)

- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/check` (файл: `stuck_detection.py`)
- **POST** `/accept-help` (файл: `stuck_detection.py`)
- **POST** `/create` (файл: `collective_agents.py`)
- **POST** `/{agent_id}/chat` (файл: `collective_agents.py`)
- **GET** `/{agent_id}` (файл: `collective_agents.py`)
- **GET** `/active` (файл: `collective_agents.py`)
- **GET** `/{agent_id}/history` (файл: `collective_agents.py`)

---

## 💻 Классы (34)

- **AnonymizerService** (21 методов) - `anonymizer_service.py`
- **CollectiveAgentService** (9 методов) - `collective_agent_service.py`
- **CollectiveLLMClient** (4 методов) - `llm_client.py`
- **StuckDetectorService** (3 методов) - `stuck_detector_service.py`
- **AnonymizationResult** (2 методов) - `anonymizer_service.py`
- **CaseLibrary** (2 методов) - `case_library.py`
- **MCPPartisiaIntegration** (2 методов) - `mcp_partisia_integration.py`
- **CollectiveAgentWithBlockchain** (2 методов) - `mcp_partisia_integration.py`
- **AnalyticsClient** (1 методов) - `analytics_client.py`
- **CollectiveConfig** (0 методов) - `config.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 13483 символов (499 строк)

**Превью:**
```
# Collective Agent Networks

**Innovation Level:** Revolutionary
**Port:** 8032
**Purpose:** Organizations help each other through AI without revealing their identities

## Documentation

All technical documentation is located in the [`docs/`](docs/) folder:
- **[Technical Specification](docs/TECHNICAL_SPECIFICATION.md)** - Complete technical documentation
- **[Architecture](docs/ARCHITECTURE.md)** - Detailed architecture design
- **[Integration Guide](docs/INTEGRATION_COMPLETE.md)** - Integration with platform services
- **[MCP/Partisia Integration](docs/INTEGRATION_MCP_PARTISIA.md)** - Blockchain integration
- **[Analysis and Improvements](docs/ANALYSIS_AND_IMPROVEMENTS.md)** - Critical issues and recommendations

---

## 🎯 THE BREAKTHROUGH IDEA

**Problem:**
- Organization A stuck on BIA problem
- Organization B, C, D already solved it
- But they can't share (confidentiality!)

**Solution:**
- Create temporary **Collective Agent** from B, C, D's experience
- Agent helps A **without 
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `intelligent-core/collective/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 23
**Директорий:** 5
