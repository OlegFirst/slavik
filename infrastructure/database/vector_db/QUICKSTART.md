# Qdrant Vector DB - Quick Start

## 1. Test Connection

```bash
cd infrastructure/vector-db
pip install -r requirements.txt
python test_connection.py
```

**Expected output:**
```
🔌 Testing Qdrant Cloud connection...
✅ Connected successfully!

📊 Cluster Info:
   • URL: https://fa9f6acd-aef9-4ebe-a3f5-f89c62bce378.eu-west-1-0.aws.cloud.qdrant.io
   • Version: v1.15.5
   • Region: eu-west-1 (AWS)

📦 Collections (0):
   (no collections yet)
```

---

## 2. Initialize Collections

```bash
python qdrant/init_collections.py
```

**Expected output:**
```
🚀 Starting Qdrant collections initialization...
✅ Qdrant is healthy

📦 Creating collection: knowledge_base
   Description: RAG knowledge base - documents, standards, best practices
   ✅ Created: knowledge_base
   📊 Vector size: 1536
   📊 Distance: Cosine
   📊 Status: green

📦 Creating collection: workflow_cases
   Description: Case Library - successful workflow cases
   ✅ Created: workflow_cases
   ...

📦 Creating collection: ai_memory
   Description: Long-term memory for AI agents
   ✅ Created: ai_memory
   ...

✅ All collections initialized successfully!

📊 Collections Summary:
   • knowledge_base: 0 points
   • workflow_cases: 0 points
   • ai_memory: 0 points
```

---

## 3. Use in Code

### Basic Usage

```python
from infrastructure.vector_db.qdrant import QdrantVectorDB

# Initialize client
db = QdrantVectorDB(collection="knowledge_base")

# Upsert vectors
db.upsert(
    vectors=[[0.1, 0.2, ..., 0.5]],  # 1536-dim vector
    payloads=[{
        "text": "ISO 22301 requires business impact analysis...",
        "source": "ISO 22301:2019",
        "category": "standard"
    }]
)

# Search similar vectors
results = db.search(
    query_vector=[0.1, 0.2, ..., 0.5],
    limit=5,
    filters={"category": "standard"},
    min_score=0.7
)

for hit in results:
    print(f"Score: {hit['score']}")
    print(f"Text: {hit['payload']['text']}")
```

### RAG Integration

```python
from shared.integrations.rag_connector import RAGConnector

rag = RAGConnector()

# Semantic search in knowledge base
docs = await rag.search(
    query="What is business impact analysis?",
    collection="knowledge_base",
    limit=5
)
```

### Case Library Integration

```python
from infrastructure.vector_db.qdrant import QdrantVectorDB

# Find similar cases
db = QdrantVectorDB(collection="workflow_cases")

similar_cases = db.search(
    query_vector=case_embedding,
    filters={
        "industry": "healthcare",
        "org_size": "large",
        "module": "bia"
    },
    limit=3
)
```

---

## 4. Management Commands

### Check Collection Info

```python
from infrastructure.vector_db.qdrant import QdrantVectorDB

db = QdrantVectorDB()
info = db.get_collection_info("knowledge_base")
print(info)
```

**Output:**
```python
{
    "name": "knowledge_base",
    "vectors_count": 1234,
    "points_count": 1234,
    "status": "green",
    "config": {
        "vector_size": 1536,
        "distance": "Cosine"
    }
}
```

### Scroll Through Collection

```python
# Paginate through all points
offset = None
while True:
    points, next_offset = db.scroll(
        collection_name="knowledge_base",
        limit=100,
        offset=offset
    )

    for point in points:
        print(point["payload"]["text"])

    if not next_offset:
        break
    offset = next_offset
```

### Delete Points

```python
# Delete by IDs
db.delete(
    ids=["id1", "id2", "id3"],
    collection_name="knowledge_base"
)
```

---

## 5. Reset Collections (Caution!)

```bash
# Delete all collections
python qdrant/init_collections.py delete

# Reset (delete + recreate)
python qdrant/init_collections.py reset
```

---

## Troubleshooting

### Connection Error

```
❌ Connection failed: Could not connect to Qdrant
```

**Fix:** Check `.env` file has correct `QDRANT_URL` and `QDRANT_API_KEY`

### Collection Already Exists

```
ℹ️  Already exists: knowledge_base
```

**Not an error** - collection was already created. Use `reset` to recreate.

### Authentication Error

```
❌ 401 Unauthorized
```

**Fix:** Verify `QDRANT_API_KEY` in `.env` matches Qdrant Cloud dashboard

---

## Next Steps

1. ✅ Test connection
2. ✅ Initialize collections
3. ⏳ Integrate with RAG Connector (see `/shared/integrations/rag_connector.py`)
4. ⏳ Integrate with Case Library
5. ⏳ Populate knowledge_base with ISO standards
6. ⏳ Add embedding generation pipeline
