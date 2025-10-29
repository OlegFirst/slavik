# 📚 ТЕХНИЧЕСКАЯ ДОКУМЕНТАЦИЯ: СЕРВИСЫ BCM PLATFORM

**Тип документа:** Техническая справка
**Дата:** 2025-09-28
**Версия:** 1.0.0
**Статус:** ✅ АКТУАЛЬНО

---

# СОДЕРЖАНИЕ

1. [Архитектура платформы](#1-архитектура-платформы)
2. [Полный список сервисов](#2-полный-список-сервисов)
3. [Детальная спецификация каждого сервиса](#3-детальная-спецификация)
4. [Entry Points и паттерны запуска](#4-entry-points)
5. [API Endpoints](#5-api-endpoints)
6. [Технологический стек](#6-технологический-стек)
7. [Развёртывание](#7-развёртывание)

---

# 1. АРХИТЕКТУРА ПЛАТФОРМЫ

## 1.1 Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Browser (localhost:3000)                        │       │
│  │  • React/Next.js Frontend                        │       │
│  │  • Admin Panel (localhost:5173)                  │       │
│  │  • Web Portal (localhost:3001)                   │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                         │
│  ┌──────────────────────────────────────────────────┐       │
│  │  unified_api_gateway (localhost:8777)            │       │
│  │  • Service Discovery                             │       │
│  │  • Request Routing                               │       │
│  │  • Load Balancing                                │       │
│  │  • Authentication (JWT)                          │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                  MICROSERVICES LAYER                         │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   AI Layer   │  │ Analysis     │  │ Integration  │      │
│  │              │  │ Layer        │  │ Layer        │      │
│  │ • orchestr.  │  │ • bia_engine │  │ • crm_bridge │      │
│  │ • workflow   │  │ • compliance │  │ • github_app │      │
│  │ • scenario   │  │ • monitoring │  │ • db_gateway │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Communication │  │ Platform     │  │ Support      │      │
│  │ Layer        │  │ Layer        │  │ Layer        │      │
│  │ • notific.   │  │ • digital    │  │ • document   │      │
│  │ • websocket  │  │   twin       │  │ • deployer   │      │
│  │ • community  │  │ • control    │  │ • process    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PostgreSQL   │  │ Redis        │  │ MongoDB      │      │
│  │ :5432        │  │ :6379        │  │ :27017       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ RabbitMQ     │  │ Odoo         │                         │
│  │ :5672        │  │ :8069        │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## 1.2 Service Groups

### 🤖 AI Services (3)
Искусственный интеллект и автоматизация
- ai_orchestrator
- ai_workflow_optimizer
- scenario_orchestrator

### 📊 Analysis Services (4)
Анализ и расчёты
- bia_engine
- compliance_checker
- monitoring_service
- process_mining_service

### 🔗 Integration Services (5)
Интеграции с внешними системами
- crm_bridge
- github_app
- unified_database_gateway
- bcm_content_training_bridge
- deployer

### 💬 Communication Services (3)
Коммуникация и уведомления
- notification_service
- realtime_websocket
- community_forum_service

### 🏗️ Platform Services (4)
Платформенные сервисы
- digital-twin-platform
- ai_control_center
- unified_api_gateway
- digital-twin-engine

### 📄 Support Services (3)
Вспомогательные сервисы
- document_processor
- document_management
- docker-ai

### 🔧 Tools & Extensions (3)
Инструменты разработчика
- vscode-extension

---

# 2. ПОЛНЫЙ СПИСОК СЕРВИСОВ

## 2.1 Backend Services (Python + FastAPI)

| # | Название | Порт | Entry Point | Строк | Статус |
|---|----------|------|-------------|-------|--------|
| 1 | ai_orchestrator | 8000 | main.py | 1195 | 🟢 85% |
| 2 | ai_workflow_optimizer | 8001 | main.py | 450 | 🟡 75% |
| 3 | bia_engine | 8082 | app.py + main.py | 483 | 🟢 80% |
| 4 | compliance_checker | 8005 | app.py | 320 | 🟡 70% |
| 5 | crm_bridge | 8086 | main.py | 280 | 🟡 65% |
| 6 | deployer | 8087 | main.py | 350 | 🟡 60% |
| 7 | document_management | 8088 | main.py | 400 | 🟡 70% |
| 8 | document_processor | 8083 | app.py | 380 | 🟡 75% |
| 9 | github_app | 8089 | main.py | 290 | 🟡 60% |
| 10 | monitoring_service | 8090 | main.py | 500 | 🟢 80% |
| 11 | notification_service | 8007 | main.py | 600 | 🟢 85% |
| 12 | process_mining_service | 8091 | main.py | 420 | 🟡 70% |
| 13 | realtime_websocket | 8084 | main.py | 810 | 🟢 95% |
| 14 | scenario_orchestrator | 8085 | main.py | 576 | 🟡 75% |
| 15 | unified_api_gateway | 8777 | main.py | 300 | 🟡 70% |
| 16 | unified_database_gateway | 8888 | main.py | 680 | 🟢 85% |

## 2.2 Production Services (Python + uvicorn direct)

| # | Название | Порт | Entry Point | Строк | Статус |
|---|----------|------|-------------|-------|--------|
| 17 | community_forum_service | 8006 | forum_service.py | 869 | 🟢 95% |
| 18 | bcm_content_training_bridge | 8085 | bridge_api_gateway.py | 457 | 🟢 90% |
| 19 | docker-ai | 8900 | unified_ai_service.py | 264 | 🟡 60% |
| 20 | docker-ai-poc | 8901 | unified_ai_service.py | 263 | 🔴 50% |

## 2.3 Node.js Services

| # | Название | Порт | Entry Point | Строк | Статус |
|---|----------|------|-------------|-------|--------|
| 21 | digital-twin-platform | 8100 | index.js | 146+ | 🟡 65% |
| 22 | ai_control_center | 8200 | src/index.js | 223 | 🟡 70% |
| 23 | digital-twin-engine | MCP | src/index.js | 712 | 🔴 40% |

## 2.4 Extensions & Tools

| # | Название | Type | Entry Point | Строк | Статус |
|---|----------|------|-------------|-------|--------|
| 24 | vscode-extension | VSCode Ext | extension.js | 130+ | 🟡 60% |

## 2.5 Libraries & Utilities

| # | Название | Type | Размер | Статус |
|---|----------|------|--------|--------|
| 25 | ai | Python Lib | 23KB | 🟢 80% |
| 26 | knowledge-base | TypeScript Lib | 50KB | 🟢 95% |
| 27 | digital-twin-engine | JS Lib | 5KB | 🔴 40% |

**ИТОГО: 25 сервисов + 3 библиотеки**

---

# 3. ДЕТАЛЬНАЯ СПЕЦИФИКАЦИЯ

## 3.1 ai_orchestrator

### Общая информация
- **Название:** AI Orchestrator Service
- **Порт:** 8000
- **Технология:** Python 3.10+, FastAPI
- **Entry Point:** `main.py`
- **Готовность:** 85%

### Описание
Центральный AI оркестратор для управления всеми AI компонентами платформы.

### Функциональность
- DevOps AI Engine с самообучением
- Интеграция с Claude API (Anthropic)
- GitHub token exchange authentication
- Risk analysis и incident classification
- NLP query processing
- Deployment strategy recommendations
- Memory system (Supabase integration)

### API Endpoints

#### POST /claude/analyze-changes
Анализ изменений с AI рекомендациями

**Request:**
```json
{
  "changes": "string",
  "context": {
    "type": "docker-compose | code | config",
    "file": "string"
  }
}
```

**Response:**
```json
{
  "analysis": {
    "deployment_risk": "low | medium | high",
    "recommended_strategy": "blue-green | canary | rolling",
    "estimated_deployment_time": "string",
    "optimizations": ["string"],
    "memory_sources": 0
  }
}
```

#### POST /claude/chat
AI чат интерфейс

**Request:**
```json
{
  "message": "string",
  "context": "object"
}
```

#### POST /devops/analyze
DevOps анализ

**Request:**
```json
{
  "action": "deploy | rollback | scale",
  "target": "string",
  "params": {}
}
```

#### GET /health
Health check

**Response:**
```json
{
  "status": "healthy",
  "service": "ai_orchestrator",
  "timestamp": "ISO8601"
}
```

### Зависимости
```python
anthropic==0.28.0
fastapi==0.109.0
uvicorn==0.27.0
supabase==2.3.0
pydantic==2.6.0
redis==5.0.1  # optional
```

### Environment Variables
```bash
ANTHROPIC_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
PORT=8000
REDIS_URL=redis://localhost:6379  # optional
```

### Запуск

**Local:**
```bash
cd services/ai_orchestrator
python main.py
```

**Docker:**
```bash
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-... \
  bcm/ai_orchestrator
```

**Docker Compose:**
```yaml
ai_orchestrator:
  build: ./services/ai_orchestrator
  ports:
    - "8000:8000"
  environment:
    - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    - SUPABASE_URL=${SUPABASE_URL}
    - SUPABASE_KEY=${SUPABASE_KEY}
```

### Известные проблемы
🔴 **CRITICAL:** Hardcoded Supabase credentials в main.py:615-616

---

## 3.2 bia_engine

### Общая информация
- **Название:** Business Impact Analysis Engine
- **Порт:** 8082
- **Технология:** Python 3.10+, FastAPI
- **Entry Point:** `app.py` + `main.py`
- **Готовность:** 80%

### Описание
BIA движок для расчёта финансовых потерь, RTO/RPO оптимизации.

### Функциональность
- Financial impact calculation
- Industry-specific multipliers
- ML-based RTO/RPO optimization
- Cascading risk analysis
- Dependency mapping

### Industry Multipliers
```python
INDUSTRY_MULTIPLIERS = {
    "FINANCIAL": {
        "revenue_loss_multiplier": 2.5,
        "reputation_impact": 3.0,
        "base_rto_hours": 2
    },
    "HEALTHCARE": {
        "revenue_loss_multiplier": 3.0,
        "reputation_impact": 4.0,
        "base_rto_hours": 1
    },
    "MANUFACTURING": {
        "revenue_loss_multiplier": 1.5,
        "reputation_impact": 2.0,
        "base_rto_hours": 8
    }
}
```

### API Endpoints

#### POST /api/v1/bia/calculate
Расчёт BIA

**Request:**
```json
{
  "process_name": "string",
  "industry": "FINANCIAL | HEALTHCARE | MANUFACTURING | RETAIL | IT",
  "annual_revenue": 1000000,
  "dependencies": [
    {
      "name": "string",
      "criticality": "high | medium | low",
      "recovery_time": "1h"
    }
  ]
}
```

**Response:**
```json
{
  "total_impact": 150000,
  "rto_recommended": "2h",
  "rpo_recommended": "15m",
  "cascading_risks": [],
  "mitigation_strategies": []
}
```

#### POST /api/v1/bia/optimize-rto
Оптимизация RTO

**Request:**
```json
{
  "process_id": "string",
  "constraints": {
    "max_downtime": "4h",
    "budget": 50000
  }
}
```

#### GET /health
Health check

### Зависимости
```python
fastapi==0.109.0
pydantic==2.6.0
numpy==1.26.0
scikit-learn==1.4.0
```

### Запуск

**Local:**
```bash
cd services/bia_engine
python main.py
```

**Docker:**
```bash
docker run -p 8082:8082 bcm/bia_engine
```

---

## 3.3 unified_api_gateway

### Общая информация
- **Название:** Unified API Gateway
- **Порт:** 8777
- **Технология:** Python 3.10+, FastAPI
- **Entry Point:** `main.py`
- **Готовность:** 70%

### Описание
Центральный API Gateway для маршрутизации запросов ко всем 37 сервисам.

### Service Registry
```python
SERVICE_REGISTRY = {
    "odoo": {
        "url": "http://odoo:8069",
        "health": "/web/health"
    },
    "ai_orchestrator": {
        "url": "http://ai_orchestrator:8000",
        "health": "/health"
    },
    "bia_engine": {
        "url": "http://bia_engine:8082",
        "health": "/health"
    },
    # ... 34 more services
}
```

### API Endpoints

#### POST /proxy/{service_name}/{path:path}
Прокси запроса к сервису

**Example:**
```bash
POST /proxy/ai_orchestrator/claude/chat
→ http://ai_orchestrator:8000/claude/chat
```

#### GET /services
Список всех сервисов

**Response:**
```json
{
  "services": {
    "ai_orchestrator": {
      "url": "http://ai_orchestrator:8000",
      "status": "healthy",
      "response_time": 45
    }
  }
}
```

#### GET /health
Gateway health check

### Функциональность
- Service discovery
- Request routing
- Health checks
- Load balancing
- Metrics collection

### Запланированные функции
- [ ] JWT Authentication
- [ ] Rate limiting
- [ ] Circuit breaker
- [ ] Request caching
- [ ] API versioning

### Известные проблемы
🔴 **CRITICAL:** Отсутствует authentication

---

## 3.4 community_forum_service

### Общая информация
- **Название:** Community Forum Service
- **Порт:** 8006
- **Технология:** Python 3.11, FastAPI, WebSocket
- **Entry Point:** `forum_service.py` (uvicorn direct)
- **Готовность:** 95%

### Описание
Полноценный форум с WebSocket real-time обновлениями.

### Функциональность
- Multi-category forums
- Topic and post management
- Rich text editor (Markdown)
- File attachments (images, documents)
- Full-text search
- User profiles with reputation
- Reaction system (like, helpful, solved)
- @username mentions
- Topic subscriptions
- Real-time notifications (WebSocket)

### Architecture
```
forum_service.py (869 lines) - Main FastAPI app
worker.py (18KB)             - Celery background worker
├── Notification processing
├── Analytics aggregation
├── Content indexing
└── Reputation calculation
```

### API Endpoints

#### GET /api/forums
Список форумов

**Response:**
```json
{
  "forums": [
    {
      "id": "uuid",
      "name": "General Discussion",
      "description": "string",
      "topic_count": 150,
      "post_count": 3420
    }
  ]
}
```

#### POST /api/topics
Создать топик

**Request:**
```json
{
  "forum_id": "uuid",
  "title": "string",
  "content": "markdown string",
  "tags": ["string"]
}
```

#### WebSocket /ws/forum/{forum_id}
Real-time updates

**Messages:**
```json
{
  "type": "new_topic | new_post | reaction",
  "data": {}
}
```

### Технологический стек
- FastAPI
- WebSocket
- PostgreSQL (forums, topics, posts)
- Redis (cache, sessions)
- Celery (background tasks)

### Запуск

**Production:**
```bash
uvicorn forum_service:app \
  --host 0.0.0.0 \
  --port 8006 \
  --workers 4
```

**Worker:**
```bash
celery -A worker worker \
  --loglevel=info
```

---

## 3.5 realtime_websocket

### Общая информация
- **Название:** Real-time WebSocket Service
- **Порт:** 8084
- **Технология:** Python 3.11, FastAPI, WebSocket
- **Entry Point:** `main.py`
- **Готовность:** 95%

### Описание
Универсальный WebSocket сервис для real-time коммуникации.

### Функциональность
- Multi-channel support
- User presence tracking
- Message history (PostgreSQL)
- Message caching (Redis)
- Typing indicators
- Read receipts
- File upload support
- Connection management

### API Endpoints

#### WebSocket /ws/{channel_id}
Подключение к каналу

**Query Parameters:**
- user_id: string (required)
- username: string (required)

**Message Types:**
```json
{
  "type": "user_message | system_notification | typing | heartbeat",
  "content": "string | object",
  "metadata": {}
}
```

#### POST /api/v1/notifications/broadcast
Broadcast уведомление

**Request:**
```json
{
  "notification_type": "string",
  "channel_id": "string",
  "recipients": ["user_id"],
  "content": {},
  "priority": "normal | high"
}
```

#### GET /api/v1/channels/{channel_id}/users
Список пользователей в канале

#### GET /api/v1/channels/{channel_id}/messages
История сообщений

### Architecture
```python
class ConnectionManager:
    channels: Dict[str, Set[WebSocket]]
    connections: Dict[WebSocket, Dict[str, str]]
    user_connections: Dict[str, Set[WebSocket]]

    async def connect(websocket, user_id, username, channel_id)
    async def disconnect(websocket)
    async def broadcast_to_channel(channel_id, message)
    async def send_to_user(user_id, message)
```

### Запуск

**Local:**
```bash
cd services/realtime_websocket
python main.py
```

**Test Page:**
```
http://localhost:8084/
```

---

## 3.6 digital-twin-platform

### Общая информация
- **Название:** Digital Twin Platform
- **Порт:** 8100
- **Технология:** Node.js 18+, Express
- **Entry Point:** `index.js`
- **Готовность:** 65%

### Описание
Standalone Digital Twin модуль с 3D visualization.

### Функциональность
- Organization modeling
- Scenario simulation
- 3D visualization
- Metrics tracking
- Report generation

### Configuration
```javascript
const digitalTwin = new DigitalTwinModule({
    environment: 'standalone',
    port: 8100,
    features: {
        organizationModeling: true,
        scenarioSimulation: true,
        visualization3D: true
    }
});
```

### API Endpoints

#### POST /api/twins
Создать digital twin

**Request:**
```json
{
  "organization_name": "string",
  "type": "nonprofit | company",
  "budget": 1000000,
  "staff_count": 50
}
```

#### GET /api/twins/{twin_id}
Получить twin

#### POST /api/twins/{twin_id}/simulate
Запустить симуляцию

**Request:**
```json
{
  "scenario": "crisis | growth | optimization",
  "duration_days": 365
}
```

### Запуск

**Local:**
```bash
cd services/digital-twin-platform
npm install
npm start
```

**Docker:**
```bash
docker run -p 8100:8100 bcm/digital-twin-platform
```

---

## 3.7 ai_control_center

### Общая информация
- **Название:** AI Control Center
- **Порт:** 8200
- **Технология:** Vue.js 3, Vite, Express
- **Entry Point:** `src/index.js`
- **Готовность:** 70%

### Описание
Управление Digital BCM Organism (10 AI organs).

### AI Organs
```javascript
const AI_ORGANS = {
  governance_brain: {
    name: 'Governance Brain',
    provider: 'anthropic',
    model: 'claude-3-sonnet',
    endpoint: 'http://localhost:8069/governance-brain'
  },
  emergency_response: { ... },
  impact_oracle: { ... },
  scenario_creator: { ... },
  risk_advisor: { ... },
  compliance_guardian: { ... },
  performance_analyst: { ... },
  learning_coach: { ... },
  plan_generator: { ... },
  lifecycle_monitor: { ... }
};
```

### API Endpoints

#### GET /api/organism/health
Health dashboard всех AI organs

**Response:**
```json
{
  "organism": {
    "name": "Digital BCM Organism",
    "overall_health": 0.85,
    "status": "healthy",
    "organs_count": 10
  },
  "organs": {
    "governance_brain": {
      "status": "healthy",
      "health_score": 0.92,
      "load": 45
    }
  }
}
```

#### GET /api/tokens/usage
Token usage analytics

#### GET /api/memory/status
Memory system status

### Technologies
- Vue.js 3 + Composition API
- Vite (dev server)
- Express (backend)
- WebSocket (real-time)
- Anthropic SDK
- Chart.js (visualizations)
- Monaco Editor (code editing)

### Запуск

**Dev:**
```bash
npm run dev  # → http://localhost:8200
```

**Production:**
```bash
npm run build
npm start
```

---

# 4. ENTRY POINTS

## 4.1 Паттерн 1: main.py (18 сервисов)

### Структура
```
service/
├── main.py          # Entry point
├── app.py           # FastAPI app
├── models/
├── services/
└── requirements.txt
```

### Код
```python
# main.py
from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000"))
    )
```

### Запуск
```bash
python main.py
```

### Используется в
- ai_orchestrator
- ai_workflow_optimizer
- bia_engine (+ app.py)
- compliance_checker
- crm_bridge
- deployer
- document_management
- document_processor
- github_app
- monitoring_service
- notification_service
- process_mining_service
- realtime_websocket
- scenario_orchestrator
- unified_api_gateway
- unified_database_gateway

---

## 4.2 Паттерн 2: uvicorn direct (4 сервиса)

### Структура
```
service/
├── service_name.py  # FastAPI app directly
└── requirements.txt
```

### Код
```python
# service_name.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello"}

# NO if __name__ == "__main__" block
```

### Запуск
```bash
uvicorn service_name:app --host 0.0.0.0 --port 8000
```

### Используется в
- community (forum_service.py)
- bcm_content_training_bridge (bridge_api_gateway.py)
- docker-ai (unified_ai_service.py)
- docker-ai-poc (unified_ai_service.py)

---

## 4.3 Паттерн 3: npm start (3 сервиса)

### Структура
```
service/
├── package.json
├── src/
│   ├── index.js
│   └── server.js
└── Dockerfile
```

### package.json
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "start": "node src/server.js"
  }
}
```

### Запуск
```bash
npm start
```

### Используется в
- ai_control_center
- digital-twin-platform
- digital-twin-engine

---

# 5. API ENDPOINTS

## 5.1 Общие endpoints

Каждый сервис обязательно имеет:

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy | degraded | unhealthy",
  "service": "service_name",
  "timestamp": "ISO8601",
  "version": "1.0.0"
}
```

### GET /metrics (опционально)
Prometheus metrics

**Response:** Prometheus format

---

## 5.2 API Gateway (:8777)

### Маршрутизация
```
/proxy/{service_name}/{path}
→ http://{service_name}:port/{path}
```

### Примеры
```bash
# AI Orchestrator
POST /proxy/ai_orchestrator/claude/chat

# BIA Engine
POST /proxy/bia_engine/api/v1/bia/calculate

# Community Forum
GET /proxy/community/api/forums
```

---

# 6. ТЕХНОЛОГИЧЕСКИЙ СТЕК

## 6.1 Backend

### Python Services
```
Python: 3.10+
Framework: FastAPI 0.109+
ASGI Server: uvicorn 0.27+
Validation: pydantic 2.6+
Testing: pytest 8.0+
```

### Node.js Services
```
Node.js: 18+
Framework: Express 4.18+
Build: Vite 5.0+ / Next.js 14+
Testing: Jest / Vitest
```

## 6.2 Databases

```
PostgreSQL: 14+  (primary)
Redis: 7+        (cache, sessions)
MongoDB: 6+      (documents)
Supabase         (AI memory)
```

## 6.3 Message Brokers

```
RabbitMQ: 3.12+  (async messaging)
```

## 6.4 Monitoring

```
Prometheus       (metrics)
Grafana          (visualization)
Loki             (logs)
Jaeger           (tracing)
```

---

# 7. РАЗВЁРТЫВАНИЕ

## 7.1 Local Development

### Prerequisites
```bash
# Python services
python >= 3.10
pip >= 23.0

# Node.js services
node >= 18.0
npm >= 9.0

# Databases
docker >= 24.0
docker-compose >= 2.20
```

### Запуск отдельного сервиса

**Python:**
```bash
cd services/ai_orchestrator
pip install -r requirements.txt
python main.py
```

**Node.js:**
```bash
cd services/ai_control_center
npm install
npm start
```

---

## 7.2 Docker Compose

### Запуск всей платформы
```bash
cd /Users/MD/ISO-22301
docker-compose up -d
```

### Проверка статуса
```bash
docker-compose ps
```

### Логи
```bash
docker-compose logs -f ai_orchestrator
```

---

## 7.3 Environment Variables

### Обязательные
```bash
# AI Services
ANTHROPIC_API_KEY=sk-ant-...

# Databases
DATABASE_URL=postgresql://user:pass@localhost:5432/bcm
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017

# Supabase
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
```

### Опциональные
```bash
# Ports (с дефолтами)
AI_ORCHESTRATOR_PORT=8000
BIA_ENGINE_PORT=8082
API_GATEWAY_PORT=8777

# Logging
LOG_LEVEL=info
```

---

## 7.4 Production Deployment

### Docker Images
```bash
# Build
docker build -t bcm/ai_orchestrator services/ai_orchestrator

# Push to registry
docker push registry.example.com/bcm/ai_orchestrator
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-orchestrator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-orchestrator
  template:
    metadata:
      labels:
        app: ai-orchestrator
    spec:
      containers:
      - name: ai-orchestrator
        image: bcm/ai_orchestrator:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: bcm-secrets
              key: anthropic-api-key
```

---

# 8. ПРИЛОЖЕНИЯ

## A. Port Allocation

| Range | Purpose | Services |
|-------|---------|----------|
| 8000-8010 | Core AI | 5 |
| 8080-8099 | Analysis | 8 |
| 8100-8200 | Platform | 3 |
| 8777 | API Gateway | 1 |
| 8888 | DB Gateway | 1 |
| 3000-3002 | Frontend Prod | 3 |
| 5173 | Frontend Dev | 1 |

## B. Dependencies Matrix

См. каждый сервис индивидуально

## C. Testing Guide

### Unit Tests
```bash
cd services/ai_orchestrator
pytest tests/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Load Tests
```bash
locust -f tests/load/locustfile.py
```

---

**Конец технической документации**

**Версия:** 1.0.0
**Последнее обновление:** 2025-09-28