# ПРАВИЛЬНАЯ АРХИТЕКТУРА INFRASTRUCTURE

**На основе:** арх2.md + текущее состояние проекта
**Дата:** 5 октября 2025

---

## 1. АРХИТЕКТУРА ИЗ арх2.md

### Ключевые компоненты платформы (из документа):

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA & KNOWLEDGE LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │ Knowledge Graph  │  │  Case Library   │  │  Vector DB       │ │
│  │   (Neo4j)        │  │  (PostgreSQL +  │  │  (Pinecone/      │ │
│  │                  │  │   Vector Search)│  │   pgvector)      │ │
│  │ • ISO Standards  │  │                 │  │                  │ │
│  │ • BCI GPG        │  │ • Workflow      │  │ • RAG Knowledge  │ │
│  │ • WHO Framework  │  │   Cases         │  │ • Embeddings     │ │
│  │ • Requirements   │  │ • Success       │  │ • Semantic       │ │
│  │ • Relationships  │  │   Patterns      │  │   Search         │ │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. ГДЕ ЭТО ДОЛЖНО БЫТЬ В ПРОЕКТЕ

### 2.1 Knowledge Graph (Neo4j) - ГДЕ?

**Из арх2.md нужно:**
- ISO Standards
- BCI GPG
- WHO Framework
- Requirements
- Relationships

**Текущее состояние:**
- ❌ Нет папки `/infrastructure/knowledge-graph/`
- ❌ Нет Neo4j integration

**РЕШЕНИЕ - создать:**
```
infrastructure/
└── knowledge-graph/
    ├── main.py                    # FastAPI service
    ├── neo4j_client.py            # Neo4j connector
    ├── models/
    │   ├── iso_standards.py       # ISO 22301 model
    │   ├── bci_gpg.py             # BCI Good Practice model
    │   └── who_framework.py       # WHO model
    ├── loaders/
    │   ├── load_iso_standards.py  # Загрузка ISO
    │   ├── load_bci_gpg.py        # Загрузка BCI
    │   └── load_who.py            # Загрузка WHO
    ├── api/
    │   ├── query_router.py        # GraphQL queries
    │   └── relationships.py       # Relationship API
    ├── requirements.txt           # neo4j, neomodel, etc.
    └── README.md
```

**Порт:** 8051 (Neo4j browser: 7474)

---

### 2.2 Case Library (PostgreSQL + Vector Search) - ГДЕ?

**Из арх2.md нужно:**
- Workflow Cases
- Success Patterns
- PostgreSQL storage
- Vector Search

**Текущее состояние:**
- ✅ Код есть: `/intelligent-core/workflow_intelligence/case_library/`
- ⚠️ НО это в intelligent-core, не в infrastructure
- ⚠️ НЕТ сервиса

**РЕШЕНИЕ - переместить/дополнить:**

**Option A: Оставить в intelligent-core (логичнее)**
```
intelligent-core/workflow_intelligence/
├── case_library/                  ✅ УЖЕ ЕСТЬ
│   ├── collector.py               ✅ УЖЕ ЕСТЬ
│   ├── repository.py              ✅ УЖЕ ЕСТЬ
│   ├── analyzer.py                ✅ УЖЕ ЕСТЬ
│   ├── search.py                  ✅ УЖЕ ЕСТЬ
│   └── models.py                  ✅ УЖЕ ЕСТЬ
└── main.py                        ❌ СОЗДАТЬ (FastAPI service)
```

**Option B: Создать infrastructure service**
```
infrastructure/
└── case-library-service/
    ├── main.py                    # FastAPI proxy to intelligent-core
    ├── api/
    │   ├── search.py              # Search API
    │   ├── cases.py               # Cases CRUD
    │   └── patterns.py            # Patterns API
    └── integration/
        └── workflow_intelligence.py  # Integration
```

**Рекомендация:** Option A (оставить в intelligent-core, добавить FastAPI service)

**Порт:** 8052

---

### 2.3 Vector DB (Pinecone/pgvector) - ГДЕ?

**Из арх2.md нужно:**
- RAG Knowledge
- Embeddings
- Semantic Search

**Текущее состояние:**
- ✅ RAG Connector: `/shared/integrations/rag_connector.py`
- ❌ НЕТ Vector DB service
- ❌ НЕТ выбранного Vector DB

**РЕШЕНИЕ - создать:**

**Option A: pgvector (встроенный в PostgreSQL)**
```
infrastructure/
└── vector-db/
    ├── README.md                  # Documentation
    ├── migrations/
    │   └── enable_pgvector.sql    # CREATE EXTENSION vector
    └── setup_pgvector.sh          # Setup script
```

**Option B: Pinecone (cloud)**
```
infrastructure/
└── vector-db/
    ├── pinecone_client.py         # Pinecone connector
    ├── embeddings.py              # Embedding generation
    └── config.py                  # API keys
```

**Option C: Weaviate (self-hosted)**
```
infrastructure/
└── vector-db/
    ├── docker-compose.yml         # Weaviate service
    ├── weaviate_client.py         # Weaviate connector
    ├── schema/
    │   ├── knowledge.json         # Knowledge schema
    │   └── cases.json             # Cases schema
    └── main.py                    # FastAPI wrapper
```

**Option D: Qdrant (Rust-based, fast)**
```
infrastructure/
└── vector-db/
    ├── docker-compose.yml         # Qdrant service
    ├── qdrant_client.py           # Qdrant connector
    ├── collections/
    │   ├── knowledge.py           # Knowledge collection
    │   └── cases.py               # Cases collection
    └── main.py                    # FastAPI wrapper
```

**Рекомендация:**
- **Для MVP:** pgvector (Option A) - проще, уже есть PostgreSQL
- **Для Production:** Qdrant (Option D) - быстрее, лучше масштабируется

**Порт:**
- pgvector: использует PostgreSQL (5432)
- Weaviate: 8053
- Qdrant: 6333

---

## 3. ПРАВИЛЬНАЯ СТРУКТУРА INFRASTRUCTURE

### Финальная структура с учетом арх2.md:

```
infrastructure/
│
├── database/                      ✅ ЕСТЬ
│   ├── managers/
│   │   ├── supabase_client.py     ✅
│   │   ├── db_manager.py          ✅
│   │   ├── redis_client.py        ✅
│   │   ├── cache_manager.py       ✅
│   │   ├── rate_limiter.py        ✅
│   │   └── session_store.py       ✅
│   └── migrations_source/         ✅ 41+ migrations
│
├── eventbus/                      ✅ ЕСТЬ
│   ├── core/                      ✅
│   ├── backends/                  ✅
│   ├── subscribers/               ✅
│   └── examples/                  ✅
│
├── auth/                          ✅ ЕСТЬ
│   └── auth_service.py            ✅
│
├── security/                      ✅ ЕСТЬ
│   ├── api-gateway/               ✅
│   ├── persistent-security/       ✅
│   └── security-headers/          ✅
│
├── monitoring/                    ✅ ЕСТЬ
│   ├── main.py                    ✅
│   ├── dashboards/                ✅
│   └── integrations/              ✅
│
├── service-discovery/             ✅ ЕСТЬ
│   ├── service_registry.py        ✅
│   └── health_monitor.py          ✅
│
├── reliability/                   ✅ ЕСТЬ
│   ├── circuit-breaker/           ✅
│   ├── retry-patterns/            ✅
│   └── health-checks/             ✅
│
├── performance/                   ✅ ЕСТЬ
│   ├── connection-pooling/        ✅
│   ├── caching/                   ✅
│   └── database/                  ✅
│
├── deployment-service/            ✅ ЕСТЬ (переименовали)
│   ├── main.py                    ✅
│   ├── ai_client.py               ✅
│   ├── config.py                  ✅
│   ├── db.py                      ✅
│   └── ...                        ✅
│
├── github-integration/            ✅ ЕСТЬ (переименовали)
│   ├── main.py                    ✅
│   ├── github_client.py           ✅
│   ├── webhook_handler.py         ✅
│   └── ...                        ✅
│
├── intelligent-gateway/           ⚠️ ЕСТЬ (архитектура)
│   ├── README.md                  ✅
│   ├── caching/                   ✅ (пусто)
│   ├── circuit_breaker/           ✅ (пусто)
│   ├── load_balancing/            ✅ (пусто)
│   └── routing/                   ✅ (пусто)
│
├── notification-service/          ⚠️ ЕСТЬ (частично)
│   ├── main.py                    ✅
│   └── external_integrations.py   ✅
│
├── realtime-websocket/            ⚠️ ЕСТЬ (частично)
│   └── main.py                    ✅
│
├── message-queue/                 ⚠️ ЕСТЬ (частично)
│   └── rabbitmq_manager.py        ✅
│
├── process_mining_service/        ⚠️ ЕСТЬ (частично)
│   └── main.py                    ✅
│
├── secrets-manager/               ⚠️ ЕСТЬ (частично)
│   └── vault_manager.py           ✅
│
├── docker-management/             ⚠️ ЕСТЬ (частично)
│   └── docker_manager.py          ✅
│
├── mcp-server/                    ⚠️ ЕСТЬ (частично)
│   └── bcm_collective_mcp.py      ✅
│
├── kubernetes/                    ⚠️ ЕСТЬ (пустые папки)
│   ├── deployments/
│   ├── ingress/
│   ├── namespaces/
│   └── services/
│
├── partisia-contracts/            ❌ ПУСТО
│   └── README.md
│
├── scalability/                   ⚠️ ЧАСТИЧНО
│   └── websocket-scaling/
│       └── connection_manager.py  ✅
│
├── observability/                 ❌ ПУСТО
│   └── README.md
│
│
│  ┌────────── ИЗ арх2.md (НУЖНО ДОБАВИТЬ) ──────────┐
│
├── knowledge-graph/               ❌ СОЗДАТЬ
│   ├── main.py                    # Neo4j service
│   ├── neo4j_client.py
│   ├── models/
│   │   ├── iso_standards.py
│   │   ├── bci_gpg.py
│   │   └── who_framework.py
│   ├── loaders/
│   │   ├── load_iso_standards.py
│   │   ├── load_bci_gpg.py
│   │   └── load_who.py
│   └── api/
│       ├── query_router.py
│       └── relationships.py
│
└── vector-db/                     ❌ СОЗДАТЬ
    ├── README.md
    ├── pgvector/                  # Option A: pgvector
    │   ├── migrations/
    │   │   └── enable_pgvector.sql
    │   └── setup.sh
    ├── weaviate/                  # Option B: Weaviate
    │   ├── docker-compose.yml
    │   ├── weaviate_client.py
    │   └── schema/
    ├── qdrant/                    # Option C: Qdrant
    │   ├── docker-compose.yml
    │   ├── qdrant_client.py
    │   └── collections/
    └── pinecone/                  # Option D: Pinecone
        ├── pinecone_client.py
        └── config.py
```

---

## 4. ПЛАН ДЕЙСТВИЙ

### Шаг 1: Создать Knowledge Graph (из арх2.md)

```bash
mkdir -p infrastructure/knowledge-graph/{models,loaders,api}
```

**Файлы:**
1. `main.py` - FastAPI service
2. `neo4j_client.py` - Neo4j connector
3. `models/iso_standards.py` - ISO 22301 model
4. `loaders/load_iso_standards.py` - Load ISO data
5. `api/query_router.py` - GraphQL/REST API

**Время:** 12-16 часов

---

### Шаг 2: Настроить Vector DB (из арх2.md)

**Выбрать один из вариантов:**

**Вариант A: pgvector (быстрее всего)**
```bash
mkdir -p infrastructure/vector-db/pgvector/migrations
```

**Вариант B: Qdrant (рекомендуется)**
```bash
mkdir -p infrastructure/vector-db/qdrant/collections
```

**Время:** 6-8 часов (pgvector) или 12-16 часов (Qdrant)

---

### Шаг 3: Переименовать папки-заглушки

**Текущие заглушки переименовать/настроить:**

```bash
# Уже есть код, просто настроить:
infrastructure/notification-service/     ⚠️ → ✅
infrastructure/realtime-websocket/       ⚠️ → ✅
infrastructure/message-queue/            ⚠️ → ✅
infrastructure/intelligent-gateway/      ⚠️ → ✅ (реализовать)

# Создать с нуля:
infrastructure/observability/            ❌ → ✅
infrastructure/partisia-contracts/       ❌ → ✅ (позже)
```

**Время:** 20-30 часов

---

## 5. ПРИОРИТЕТЫ (обновлено с учетом арх2.md)

### Tier 0 - КРИТИЧНО (из арх2.md, нужно СЕЙЧАС):

1. **Knowledge Graph (Neo4j)** (12-16 часов)
   - ISO Standards
   - BCI GPG
   - WHO Framework
   - Relationships API

2. **Vector DB** (6-16 часов)
   - Выбрать: pgvector (быстро) или Qdrant (правильно)
   - Настроить embeddings
   - Semantic search API

3. **Case Library Service** (4-6 часов)
   - Обернуть существующий код в FastAPI
   - API endpoints
   - Интеграция с Vector DB

**Итого Tier 0:** 22-38 часов (1 неделя)

---

### Tier 1 - ВАЖНО (настроить существующие):

4. **Notification Service** (4-6 часов)
5. **Realtime WebSocket** (6-8 часов)
6. **Message Queue** (4-6 часов)
7. **Intelligent Gateway** (14-19 часов)

**Итого Tier 1:** 28-39 часов (1 неделя)

---

### Tier 2 - ДОПОЛНИТЕЛЬНО:

8. **Observability** (12-16 часов)
9. **Kubernetes Manifests** (8-12 часов)
10. **Partisia Contracts** (30-40 часов)

**Итого Tier 2:** 50-68 часов (2 недели)

---

## 6. ФИНАЛЬНАЯ КАРТА ПОРТОВ

```
INFRASTRUCTURE SERVICES:
├── PostgreSQL (Supabase)       5432  ✅
├── Redis                       6379  ✅
├── EventBus                    8001  ✅
├── API Gateway                 8000  ✅
├── Monitoring                  9090  ✅ (Prometheus)
│                               3000  ✅ (Grafana)
├── Neo4j                       7474  ❌ (browser)
│                               7687  ❌ (bolt)
├── Knowledge Graph Service     8051  ❌ СОЗДАТЬ
├── Case Library Service        8052  ❌ СОЗДАТЬ
├── Vector DB (Qdrant)          6333  ❌ СОЗДАТЬ
│   или Vector DB (Weaviate)    8053  ❌
├── RAG Service                 8050  ✅ (указан в коде)
├── Notification Service        8054  ⚠️ НАСТРОИТЬ
├── WebSocket Service           8055  ⚠️ НАСТРОИТЬ
├── RabbitMQ                    5672  ⚠️ НАСТРОИТЬ
└── Intelligent Gateway         8080  ⚠️ СОЗДАТЬ
```

---

## 7. ВЫВОДЫ И РЕКОМЕНДАЦИИ

### ЧТО ТОЧНО НУЖНО (из арх2.md):

1. ✅ **Workflow Intelligence** - УЖЕ ЕСТЬ в `/intelligent-core/workflow_intelligence/`
2. ❌ **Knowledge Graph (Neo4j)** - НУЖНО СОЗДАТЬ
3. ❌ **Vector DB** - НУЖНО СОЗДАТЬ (pgvector/Qdrant)
4. ⚠️ **Case Library Service** - код есть, нужен сервис

### ПОРЯДОК РЕАЛИЗАЦИИ:

**Неделя 1 (Tier 0 - из арх2.md):**
1. День 1-2: Knowledge Graph (Neo4j)
2. День 3-4: Vector DB (pgvector или Qdrant)
3. День 5: Case Library Service

**Неделя 2 (Tier 1 - настроить существующие):**
4. День 1: Notification + Message Queue
5. День 2-3: Realtime WebSocket
6. День 4-5: Intelligent Gateway

**Неделя 3+ (Tier 2 - опционально):**
7. Observability
8. Kubernetes
9. Partisia Contracts

---

**Что делаем сначала?**

**Вариант A:** Следовать арх2.md (Knowledge Graph + Vector DB)
**Вариант B:** Настроить существующие сервисы сначала
**Вариант C:** Комбо (Vector DB + Notification + WebSocket)

Какой вариант?
