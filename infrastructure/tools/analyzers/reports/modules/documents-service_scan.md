# Module Scan Report: documents-service

**Дата сканирования:** 2025-10-06 21:11
**Путь:** `platform-services/documents-service`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 10132 |
| **Python файлов** | 32 |
| **Классов** | 71 |
| **Функций** | 51 |
| **API Endpoints** | 30 |
| **Зависимостей** | 78 |

---

## 🔗 Зависимости (78)


### PIL
- `PIL`

### ai_foundation
- `ai_foundation/workflow_intelligence`

### aio_pika
- `aio_pika`

### analyzer
- `analyzer`

### api.routes
- `api.routes`

### api.workflow_ai
- `api.workflow_ai`

### approval_workflow
- `approval_workflow`

### asyncio
- `asyncio`

### classifier
- `classifier`

### collections
- `collections`

### comparator
- `comparator`

### config
- `config`

### contextlib
- `contextlib`

### core.analyzer
- `core.analyzer`

### core.classifier
- `core.classifier`

### core.comparator
- `core.comparator`

### core.extractor
- `core.extractor`

### database
- `database`
- `database/postgresql`

### database.models
- `database.models`

### datetime
- `datetime`

### difflib
- `difflib`

### document_service
- `document_service`

### docx
- `docx`

### domain
- `domain`

### enum
- `enum`

### events.handlers
- `events.handlers`

### extractor
- `extractor`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.responses
- `fastapi.responses`

### fastapi.security
- `fastapi.security`

### fitz
- `fitz`

### governance
- `governance`

### handlers
- `handlers`

### hashlib
- `hashlib`

### httpx
- `httpx`

### integrations
- `integrations`

### json
- `json`

### jwt
- `jwt`

### lifecycle_workflow
- `lifecycle_workflow`

### logging
- `logging`

### main
- `main`

### mimetypes
- `mimetypes`

### models.database
- `models.database`

### models.domain
- `models.domain`

### openai
- `openai`

### openpyxl
- `openpyxl`

### os
- `os`

### pandas
- `pandas`

### pathlib
- `pathlib`

### pdfplumber
- `pdfplumber`

### plans
- `plans`

### prometheus_client
- `prometheus_client`

### publishers
- `publishers`

### pydantic
- `pydantic`

### pydantic_settings
- `pydantic_settings`

### pytesseract
- `pytesseract`

### re
- `re`

### repositories.repository
- `repositories.repository`

### repository
- `repository`

### retention_workflow
- `retention_workflow`

### routes
- `routes`

### runtime
- `runtime/eventbus`

### services.document_service
- `services.document_service`

### shared
- `shared/auth`
- `shared/database`

### sklearn.feature_extraction.text
- `sklearn.feature_extraction.text`

### spacy
- `spacy`

### sys
- `sys`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### validation
- `validation`

### workflow_integration
- `workflow_integration`

### workflows.approval_workflow
- `workflows.approval_workflow`

### workflows.lifecycle_workflow
- `workflows.lifecycle_workflow`

### workflows.retention_workflow
- `workflows.retention_workflow`

---

## 🌐 API Endpoints (30)

- **GET** `/api/compliance/check` (файл: `main.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/{item_id}/ai-advice` (файл: `workflow_ai.py`)
- **GET** `/benchmarks` (файл: `workflow_ai.py`)
- **POST** `/documents` (файл: `routes.py`)
- **POST** `/documents/{document_id}/upload` (файл: `routes.py`)
- **GET** `/documents/{document_id}` (файл: `routes.py`)
- **GET** `/documents/{document_id}/download` (файл: `routes.py`)
- **GET** `/documents` (файл: `routes.py`)

---

## 💻 Классы (71)

- **DocumentAnalyzer** (10 методов) - `analyzer.py`
- **DocumentClassifier** (8 методов) - `classifier.py`
- **DocumentComparator** (8 методов) - `comparator.py`
- **DocumentExtractor** (8 методов) - `extractor.py`
- **WorkflowSecurityMiddleware** (1 методов) - `workflow_integration.py`
- **DocumentRepository** (1 методов) - `repository.py`
- **DocumentAccessRepository** (1 методов) - `repository.py`
- **DocumentShareRepository** (1 методов) - `repository.py`
- **DocumentApprovalRepository** (1 методов) - `repository.py`
- **DocumentTagRepository** (1 методов) - `repository.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 11115 символов (375 строк)

**Превью:**
```
# Documents Service - Production

**ISO 22301 Clause 7.5 - Documented Information Management**

Production-ready microservice for comprehensive document lifecycle management with AI/NLP capabilities, approval workflows, and retention policies.

## Overview

This service provides enterprise-grade document management with:

- **Document Lifecycle Management**: DRAFT → REVIEW → APPROVED → PUBLISHED → ARCHIVED
- **AI/NLP Processing**: Text extraction, auto-classification, entity recognition, summarization
- **Version Control**: Full version history with comparison capabilities
- **Approval Workflows**: Multi-stage approval chains with role-based approvers
- **Retention Policies**: Automated archival and destruction per ISO 22301 and HIPAA
- **Security**: Classification levels, access control, audit logging
- **Event-Driven**: Integration with other BCM platform services

## Architecture

### 4-Tier Architecture

```
documents/
├── models/              # Data layer
│   ├── database.py      
```

---

## ⚙️ Конфигурация

- `.env.example` → `platform-services/documents-service/.env.example`
- `requirements.txt` → `platform-services/documents-service/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 35
**Директорий:** 9
