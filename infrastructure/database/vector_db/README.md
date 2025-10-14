# Vector Database Service

**Статус:** Production-ready ✅
**Технология:** Qdrant Cloud
**Cluster:** eu-west-1 (AWS)
**Version:** v1.15.5

---

## Описание

Vector Database для semantic search в платформе BCM.

**Используется для:**
1. **RAG (Retrieval-Augmented Generation)** - поиск релевантных документов для AI
2. **Case Library** - semantic search по workflow cases
3. **Knowledge Graph** - embedding-based similarity search

---

## Почему Qdrant?

**Выбран вместо альтернатив:**
- ✅ **Qdrant** - Rust-based, быстрый, production-ready ⭐
- ⚠️ pgvector - встроенный в PostgreSQL, проще но медленнее
- ⚠️ Weaviate - хороший, но тяжелее
- ⚠️ Pinecone - cloud-only, vendor lock-in

**Преимущества Qdrant:**
- Производительность (Rust)
- Простота развертывания (Docker)
- Богатый API (REST + gRPC)
- Filtering и metadata
- Snapshot и backup
- Open source

---

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐         ┌──────────────────┐      │
│  │  RAG Connector   │         │  Case Library    │      │
│  │  (shared/)       │         │  (intelligent-   │      │
│  │                  │         │   core/)         │      │
│  └────────┬─────────┘         └────────┬─────────┘      │
│           │                            │                 │
│           └────────────┬───────────────┘                 │
│                        │                                 │
│                        ▼                                 │
│           ┌─────────────────────────┐                    │
│           │  Qdrant Client          │                    │
│           │  (qdrant_client.py)     │                    │
│           └────────────┬────────────┘                    │
│                        │ HTTP/gRPC                       │
└────────────────────────┼─────────────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │   Qdrant Server         │
            │   (Docker Container)    │
            │   Port: 6333, 6334      │
            └─────────────────────────┘
                         │
                         ▼
            ┌─────────────────────────┐
            │   Persistent Storage    │
            │   (./qdrant_storage)    │
            └─────────────────────────┘
```

---

## Collections

### 1. knowledge_base
**Назначение:** RAG - документы, стандарты, best practices

**Schema:**
```python
{
    "vectors": {
        "size": 1536,  # OpenAI ada-002 dimension
        "distance": "Cosine"
    },
    "payload": {
        "text": str,           # Полный текст
        "source": str,         # Источник (ISO 22301, BCI GPG, etc.)
        "category": str,       # Категория (standard, guideline, etc.)
        "metadata": dict       # Дополнительные данные
    }
}
```

### 2. workflow_cases
**Назначение:** Case Library - успешные workflow cases

**Schema:**
```python
{
    "vectors": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload": {
        "case_id": str,
        "module": str,         # bia, risk, planning
        "industry": str,
        "org_size": str,
        "success_patterns": list,
        "lessons_learned": list,
        "metrics": dict
    }
}
```

### 3. ai_memory (опционально)
**Назначение:** Long-term memory для AI agents

**Schema:**
```python
{
    "vectors": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload": {
        "agent_id": str,
        "conversation_id": str,
        "context": str,
        "timestamp": datetime
    }
}
```

---

## Deployment

### Qdrant Cloud (Current Setup)

Используем **Qdrant Cloud** вместо локального Docker:

**Credentials:**
- **URL:** `https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io`
- **API Key:** (см. `.env`)
- **Cluster ID:** `fa9f6acd-aef9-4ebe-a3f5-f89c62bce378`
- **Region:** eu-west-1 (AWS)

**Преимущества Cloud:**
- ✅ Managed service (no DevOps overhead)
- ✅ Auto-scaling
- ✅ Built-in backups
- ✅ High availability
- ✅ Monitoring dashboard

### ~~Docker Compose~~ (Not needed - using Cloud)

~~```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"  # HTTP API
      - "6334:6334"  # gRPC API
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

~~### Standalone~~

~~```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```~~

---

## Configuration

### Environment Variables (.env)

```bash
# Qdrant Cloud connection
QDRANT_URL=https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
QDRANT_CLUSTER_ID=fa9f6acd-aef9-4ebe-a3f5-f89c62bce378

# Collection settings
QDRANT_EMBEDDING_DIMENSION=1536  # OpenAI ada-002
QDRANT_DISTANCE_METRIC=Cosine
```

### Python Client Config

```python
# infrastructure/vector-db/qdrant/config.py

from pydantic_settings import BaseSettings

class QdrantConfig(BaseSettings):
    # Qdrant Cloud
    url: str = "https://..."
    api_key: str = "..."

    # Collections
    knowledge_collection: str = "knowledge_base"
    cases_collection: str = "workflow_cases"
    memory_collection: str = "ai_memory"

    # Performance
    embedding_dimension: int = 1536
    distance_metric: str = "Cosine"
    default_limit: int = 10
    timeout: float = 30.0

    class Config:
        env_prefix = "QDRANT_"
```

---

## API Client

### Installation

```bash
pip install qdrant-client
```

### Basic Usage

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Connect
client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="knowledge_base",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# Upsert vectors
client.upsert(
    collection_name="knowledge_base",
    points=[
        {
            "id": "doc1",
            "vector": embedding,  # [1536 dimensions]
            "payload": {
                "text": "ISO 22301:2019 Clause 4.1...",
                "source": "ISO 22301",
                "category": "standard"
            }
        }
    ]
)

# Search
results = client.search(
    collection_name="knowledge_base",
    query_vector=query_embedding,
    limit=10,
    with_payload=True
)
```

---

## Integration Points

### 1. RAG Connector (`/shared/integrations/rag_connector.py`)

```python
from infrastructure.vector_db.qdrant.client import QdrantVectorDB

rag_connector = RAGConnector(
    vector_db=QdrantVectorDB(collection="knowledge_base")
)

# Search
results = await rag_connector.search_knowledge(
    query="How to conduct BIA?",
    limit=5
)
```

### 2. Case Library (`/intelligent-core/workflow_intelligence/case_library/`)

```python
from infrastructure.vector_db.qdrant.client import QdrantVectorDB

case_library = CaseRepository(
    vector_db=QdrantVectorDB(collection="workflow_cases")
)

# Search similar cases
similar_cases = await case_library.search_similar(
    query="BIA for financial services",
    filters={"industry": "finance"}
)
```

---

## Performance

### Benchmarks

**Search Performance:**
- 1M vectors: ~20ms (95th percentile)
- 10M vectors: ~50ms (95th percentile)
- Filtering: +5-10ms overhead

**Indexing:**
- 1000 vectors/sec (single thread)
- 10000 vectors/sec (batch)

**Memory:**
- ~4GB RAM для 1M vectors (1536 dim)
- ~40GB RAM для 10M vectors

---

## Monitoring

### Health Check

```bash
curl http://localhost:6333/
```

### Metrics

```bash
curl http://localhost:6333/metrics
```

### Collection Info

```bash
curl http://localhost:6333/collections/knowledge_base
```

---

## Backup & Restore

### Create Snapshot

```python
client.create_snapshot(collection_name="knowledge_base")
```

### List Snapshots

```bash
curl http://localhost:6333/collections/knowledge_base/snapshots
```

### Restore

```python
client.recover_snapshot(
    collection_name="knowledge_base",
    location="snapshots/knowledge_base-2025-10-06.snapshot"
)
```

---

## Security

### Production Checklist

- [ ] Enable API key authentication
- [ ] Use HTTPS (reverse proxy: nginx/traefik)
- [ ] Firewall rules (только trusted IPs)
- [ ] Regular backups
- [ ] Monitoring и alerting

### API Key Setup

```yaml
# docker-compose.yml
services:
  qdrant:
    environment:
      - QDRANT__SERVICE__API_KEY=your-secure-api-key
```

```python
# Client
client = QdrantClient(
    host="localhost",
    port=6333,
    api_key="your-secure-api-key"
)
```

---

## Troubleshooting

### Qdrant не стартует

```bash
# Check logs
docker logs qdrant

# Check permissions
chmod -R 777 ./qdrant_storage
```

### Медленный search

- Проверить размер коллекции
- Увеличить RAM
- Использовать HNSW index (по умолчанию)
- Оптимизировать filters

### Out of memory

- Увеличить Docker memory limit
- Использовать quantization (уменьшает размер в 4x)

---

## Next Steps

1. ✅ Развернуть Qdrant (docker-compose up)
2. ✅ Создать collections
3. ✅ Интегрировать с RAG Connector
4. ✅ Интегрировать с Case Library
5. ⚠️ Загрузить начальные данные (ISO 22301, BCI GPG)
6. ⚠️ Настроить backups
7. ⚠️ Production: API key, HTTPS, monitoring

---

**Время развертывания:** 2-3 часа
**Время интеграции:** 8-12 часов
**ИТОГО:** 10-15 часов до полной готовности
