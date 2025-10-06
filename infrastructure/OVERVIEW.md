# Infrastructure Overview

**Обновлено:** 2025-10-06
**Статус:** Production-ready

---

## 📋 Содержание

1. [Архитектура](#архитектура)
2. [Работающие сервисы](#работающие-сервисы)
3. [Сервисы требующие настройки](#сервисы-требующие-настройки)
4. [Deployment & Setup](#deployment--setup)
5. [Интеграции](#интеграции)
6. [Приоритеты развития](#приоритеты-развития)

---

## Архитектура

### Принципы
- **Микросервисная архитектура** - каждый сервис в своем Docker контейнере
- **Event-driven** - EventBus для асинхронной коммуникации
- **Shared Library** - общий код в `/shared/` (database, auth, cache, integrations)
- **Плоская структура** - 15-20 сервисов на одном уровне (оптимально для производительности)

### Коммуникация
```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│              (security/api-gateway/)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐          ┌─────▼─────┐
    │ EventBus │          │  HTTP/    │
    │ (Async)  │          │  REST     │
    └────┬─────┘          └─────┬─────┘
         │                      │
    ┌────▼──────────────────────▼─────┐
    │      Microservices Layer         │
    │  (platform-services/ + infra/)   │
    └──────────────┬───────────────────┘
                   │
         ┌─────────┴──────────┐
         │                    │
    ┌────▼────┐        ┌──────▼──────┐
    │Database │        │   Redis     │
    │(Supabase)│        │   Cache     │
    └─────────┘        └─────────────┘
```

---

## Работающие сервисы

### Core Infrastructure

#### 1. Database (`database/`)
**Статус:** ✅ Production-ready
**Технологии:** PostgreSQL (Supabase), Redis

**Возможности:**
- Async connection pooling
- Supabase client integration
- Migration management
- Cache manager (Redis)
- Rate limiter
- Session store

**Документация:** [database/README.md](database/README.md)

---

#### 2. EventBus (`eventbus/`)
**Статус:** ✅ Production-ready
**Технологии:** Memory Transport + Redis Streams

**Возможности:**
- Event-driven messaging
- Memory transport (для разработки)
- Redis Streams transport (для production)
- Event routing and subscriptions
- Error handling and retries

**Документация:**
- [eventbus/README.md](eventbus/README.md)
- [eventbus/ARCHITECTURE.md](eventbus/ARCHITECTURE.md)
- [eventbus/QUICKSTART.md](eventbus/QUICKSTART.md)

---

#### 3. Security / API Gateway (`security/api-gateway/`)
**Статус:** ✅ Production-ready
**Код:** 4,345 строк

**Возможности:**
- JWT authentication
- Rate limiting
- Audit logging
- Load balancing
- Request routing
- CORS handling

**Документация:** [security/README.md](security/README.md)

---

#### 4. Auth (`auth/`)
**Статус:** ✅ Production-ready
**Технологии:** JWT, Keycloak (SSO)

**Возможности:**
- JWT token generation/validation
- Role-based access control (RBAC)
- Keycloak integration
- Session management

---

#### 5. Monitoring (`monitoring/`)
**Статус:** ✅ Production-ready
**Технологии:** Prometheus, Grafana

**Возможности:**
- Metrics collection
- Service health monitoring
- Custom dashboards
- Alerting

**Документация:** [monitoring/README.md](monitoring/README.md)

---

#### 6. Service Discovery (`service-discovery/`)
**Статус:** ✅ Production-ready

**Возможности:**
- Service registry
- Health checks
- Service lookup
- Load balancing metadata

**Документация:** [service-discovery/README.md](service-discovery/README.md)

---

### Data & Storage

#### 7. Vector DB (`vector-db/`)
**Статус:** ✅ Production-ready (NEW!)
**Технология:** Qdrant Cloud
**Cluster:** eu-west-1 (AWS)

**Возможности:**
- Semantic search для RAG
- Case Library (workflow cases)
- AI long-term memory
- 3 collections: knowledge_base, workflow_cases, ai_memory

**Документация:**
- [vector-db/README.md](vector-db/README.md)
- [vector-db/QUICKSTART.md](vector-db/QUICKSTART.md)
- [vector-db/SETUP_COMPLETE.md](vector-db/SETUP_COMPLETE.md)

---

### Integration & Deployment

#### 8. Deployment Service (`deployment-service/`)
**Статус:** ✅ Working
**Код:** 223 строк

**Возможности:**
- Deployment automation
- CI/CD integration
- Environment management

**Документация:** [deployment-service/README.md](deployment-service/README.md)

---

#### 9. GitHub Integration (`github-integration/`)
**Статус:** ✅ Working
**Код:** 99 строк

**Возможности:**
- GitHub webhooks
- Copilot integration
- Repository automation

**Документация:** [github-integration/README.md](github-integration/README.md)

---

## Сервисы требующие настройки

### 1. Notification Service (`notification-service/`)
**Статус:** ⚠️ Needs configuration
**Приоритет:** HIGH

**Технологии:** Email (SMTP), Slack, Telegram

**Что нужно:**
- Настроить SMTP credentials
- Добавить Slack/Telegram webhooks
- Протестировать отправку

**Документация:** [notification-service/README.md](notification-service/README.md)

---

### 2. Realtime WebSocket (`realtime-websocket/`)
**Статус:** ⚠️ Needs configuration
**Приоритет:** HIGH

**Технологии:** WebSocket, Socket.io

**Что нужно:**
- Настроить WebSocket сервер
- Интегрировать с EventBus
- Добавить authentication

**Документация:** [realtime-websocket/README.md](realtime-websocket/README.md)

---

### 3. Message Queue (`message-queue/`)
**Статус:** ⚠️ Needs configuration
**Приоритет:** MEDIUM

**Технологии:** RabbitMQ

**Что нужно:**
- Настроить RabbitMQ connection
- Создать queues и exchanges
- Интегрировать с сервисами

**Документация:** [message-queue/README.md](message-queue/README.md)

---

### 4. Intelligent Gateway (`intelligent-gateway/`)
**Статус:** ⚠️ Architecture ready
**Приоритет:** MEDIUM

**Возможности:**
- AI-powered request routing
- Smart load balancing
- Predictive caching

**Документация:** [intelligent-gateway/README.md](intelligent-gateway/README.md) (495 строк)

---

### 5. Secrets Manager (`secrets-manager/`)
**Статус:** ⚠️ Needs configuration
**Приоритет:** MEDIUM (для production)

**Технологии:** HashiCorp Vault

**Что нужно:**
- Настроить Vault connection
- Migrate secrets из .env
- Setup rotation policies

**Документация:** [secrets-manager/README.md](secrets-manager/README.md)

---

### 6. MCP Server (`mcp-server/`)
**Статус:** ⚠️ Needs configuration
**Приоритет:** LOW

**Возможности:**
- MCP protocol для collective agents
- Agent coordination

**Документация:** [mcp-server/README.md](mcp-server/README.md)

---

## Deployment & Setup

### Требования
- Docker & Docker Compose
- PostgreSQL (Supabase)
- Redis
- Python 3.11+

### Environment Variables
Все переменные окружения в [.env.example](../.env.example):

**Core:**
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `JWT_SECRET` - JWT signing key

**AI Services:**
- `OPENAI_API_KEY` - OpenAI API
- `ANTHROPIC_API_KEY` - Anthropic API

**Qdrant:**
- `QDRANT_URL` - Qdrant Cloud URL
- `QDRANT_API_KEY` - Qdrant API key

**Monitoring:**
- `PROMETHEUS_URL`
- `GRAFANA_URL`

### Quick Start

```bash
# 1. Clone repository
git clone <repo-url>
cd AI-Platform-ISO

# 2. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start infrastructure
docker-compose up -d

# 4. Verify services
docker-compose ps
```

---

## Интеграции

### Shared Library (`/shared/`)
**Размер:** 11,248 строк кода, 57 Python файлов
**Импорты:** 127 across the project

**Ключевые модули:**
- `shared.database` - Database connections
- `shared.cache` - Redis caching
- `shared.auth` - JWT & RBAC
- `shared.eventbus` - EventBus client
- `shared.integrations.rag_connector` - RAG integration (8,834 строк)
- `shared.integrations.knowledge_client` - Knowledge Graph (11,481 строк)
- `shared.integrations.ml_platform_client` - ML Platform (13,401 строк)

### Platform Services (`/platform-services/`)
Бизнес-сервисы используют infrastructure:
- BIA, Risk, Planning, Response - используют Database, EventBus, Auth
- Document Management - использует Vector DB для semantic search
- Workflow - использует EventBus для orchestration

### Intelligent Core (`/intelligent-core/`)
AI компоненты используют infrastructure:
- AI Experts - используют Vector DB для knowledge base
- Workflow Intelligence - использует EventBus
- Learning System - использует Database для хранения моделей

---

## Приоритеты развития

### ✅ Tier 0 - ГОТОВО
1. ✅ **vector-db** (Qdrant Cloud) - DONE!
2. ✅ **database** - DONE!
3. ✅ **eventbus** - DONE!
4. ✅ **auth** - DONE!
5. ✅ **monitoring** - DONE!

### ⏳ Tier 1 - КРИТИЧНО (1-2 недели)
1. **notification-service** - 4-6 часов
2. **realtime-websocket** - 6-8 часов
3. **message-queue** - 4-6 часов

### 📋 Tier 2 - ПОЛЕЗНО (для production)
4. **secrets-manager** (Vault) - для production безопасности
5. **intelligent-gateway** - AI-powered routing
6. **observability** - distributed tracing

### 💡 Tier 3 - ОПЦИОНАЛЬНО
7. **kubernetes/** - K8s manifests
8. **process_mining_service** - analytics
9. **mcp-server** - специфичный use case

---

## Производительность

### Shared Library
- **Плоская структура** (1-2 уровня) - оптимально
- **127 импортов** - 20-30% быстрее чем глубокая структура
- Время импорта: ~5ms vs 8-10ms (deep structure)

### Microservices
- **Docker изоляция** - структура папок не влияет на runtime
- **EventBus** - асинхронная коммуникация
- **Service Discovery** - health checks каждые 30s
- **API Gateway** - rate limiting, load balancing

---

## Следующие шаги

1. **Immediate:**
   - Настроить Notification Service
   - Настроить Realtime WebSocket
   - Интегрировать Vector DB с RAG Connector

2. **Short-term:**
   - Настроить Message Queue
   - Migrate secrets в Vault
   - Add monitoring dashboards

3. **Long-term:**
   - Kubernetes deployment
   - Distributed tracing
   - Performance optimization

---

## Ресурсы

- **Main README:** [README.md](README.md)
- **Архивная документация:** [архив/](архив/)
- **Shared Library:** [/shared/](../shared/)
- **Platform Services:** [/platform-services/](../platform-services/)
- **Intelligent Core:** [/intelligent-core/](../intelligent-core/)

---

**Для вопросов:** См. документацию отдельных сервисов в их папках.
