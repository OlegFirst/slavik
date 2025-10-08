# Module Scan Report: collective

**Дата сканирования:** 2025-10-08 14:33
**Путь:** `intelligent-core/collective`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 5230 |
| **Python файлов** | 15 |
| **Классов** | 35 |
| **Функций** | 0 |
| **API Endpoints** | 10 |
| **Зависимостей** | 40 |

---

## 🔗 Зависимости (40)


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

### llm.llm_router
- `llm.llm_router`

### logging
- `logging`

### math
- `math`

### models.database
- `models.database`

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

### rag.pipeline
- `rag.pipeline`

### re
- `re`

### services.ai_foundation_integration
- `services.ai_foundation_integration`

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

### sys
- `sys`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (10)

- **GET** `/health` (файл: `main.py`)
- **GET** `/metrics` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/check` (файл: `stuck_detection.py`)
- **POST** `/accept-help` (файл: `stuck_detection.py`)
- **POST** `/create` (файл: `collective_agents.py`)
- **POST** `/{agent_id}/chat` (файл: `collective_agents.py`)
- **GET** `/{agent_id}` (файл: `collective_agents.py`)
- **GET** `/active` (файл: `collective_agents.py`)
- **GET** `/{agent_id}/history` (файл: `collective_agents.py`)

---

## 💻 Классы (35)

- **AnonymizerService** (21 методов) - `anonymizer_service.py`
- **CollectiveAgentService** (9 методов) - `collective_agent_service.py`
- **CollectiveAIFoundation** (5 методов) - `ai_foundation_integration.py`
- **CollectiveLLMClient** (4 методов) - `llm_client.py`
- **StuckDetectorService** (3 методов) - `stuck_detector_service.py`
- **AnonymizationResult** (2 методов) - `anonymizer_service.py`
- **CaseLibrary** (2 методов) - `case_library.py`
- **MCPPartisiaIntegration** (2 методов) - `mcp_partisia_integration.py`
- **CollectiveAgentWithBlockchain** (2 методов) - `mcp_partisia_integration.py`
- **AnalyticsClient** (1 методов) - `analytics_client.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 13205 символов (462 строк)

**Превью:**
```
# Collective Agent Networks

## Overview
Collective Agent Networks is a revolutionary privacy-preserving collaboration system that enables organizations to help each other through AI without revealing their identities. Organizations share collective wisdom while maintaining complete anonymity through multi-layer privacy protection and k-anonymity guarantees.

## Features

- **Anonymous Collective Agents**: Temporary AI agents created from multiple organizations' experiences
- **Stuck Detection**: Automatically detects when organizations need help based on progress indicators
- **Privacy-Preserving Architecture**: Multi-layer anonymization with k-anonymity (minimum 5 organizations)
- **Intelligent Matching**: Finds organizations that solved similar problems
- **Temporary Agents**: Auto-expiring agents (7 days default) for security
- **Real-time Collaboration**: Chat-based interface with collective wisdom
- **Partisia Integration**: Blockchain-based privacy using Partisia MPC
- **Case Li
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `intelligent-core/collective/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 26
**Директорий:** 5
