# Module Scan Report: integration

**Дата сканирования:** 2025-10-08 16:44
**Путь:** `infrastructure/integration`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 1839 |
| **Python файлов** | 8 |
| **Классов** | 19 |
| **Функций** | 0 |
| **API Endpoints** | 8 |
| **Зависимостей** | 25 |

---

## 🔗 Зависимости (25)


### asyncio
- `asyncio`

### auth
- `auth`

### config
- `config`

### datetime
- `datetime`

### enum
- `enum`

### fastapi
- `fastapi`

### hashlib
- `hashlib`

### hmac
- `hmac`

### httpx
- `httpx`

### json
- `json`

### jwt
- `jwt`

### logging
- `logging`

### mcp.server
- `mcp.server`

### mcp.server.stdio
- `mcp.server.stdio`

### mcp.types
- `mcp.types`

### models
- `models`

### os
- `os`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### runtime
- `runtime/eventbus`

### tenacity
- `tenacity`

### time
- `time`

### typing
- `typing`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

---

## 🌐 API Endpoints (8)

- **GET** `/` (файл: `main.py`)
- **POST** `/github/webhook` (файл: `main.py`)
- **POST** `/auth/token-exchange` (файл: `main.py`)
- **POST** `/claude/analyze-changes` (файл: `main.py`)
- **POST** `/claude/generate-config` (файл: `main.py`)
- **GET** `/deployment/history` (файл: `main.py`)
- **POST** `/claude/analyze-deployment` (файл: `main.py`)
- **POST** `/deployment/orchestrate` (файл: `main.py`)

---

## 💻 Классы (19)

- **GitHubAuth** (3 методов) - `auth.py`
- **GitHubConfig** (3 методов) - `config.py`
- **WebhookHandler** (2 методов) - `webhook_handler.py`
- **GitHubClient** (2 методов) - `github_client.py`
- **PartisiaClient** (1 методов) - `bcm_collective_mcp.py`
- **Config** (0 методов) - `config.py`
- **GitHubEventType** (0 методов) - `models.py`
- **WebhookEvent** (0 методов) - `models.py`
- **PRWebhookPayload** (0 методов) - `models.py`
- **IssueWebhookPayload** (0 методов) - `models.py`

---

## 📂 Структура

**Всего файлов:** 18
**Директорий:** 4
