# RAG Strategy for BCM Platform Knowledge

**Date**: 2025-10-11
**Status**: ✅ Implementation Ready
**Purpose**: Complete RAG architecture for scenario knowledge management

---

## 🎯 Overview

### Goal
**Make AI Assistant know ALL 570+ scenarios** through semantic search in RAG (Qdrant)

### Current State
✅ **328 scenarios parsed** from ALL_USAGE_SCENARIOS_CATALOG.md
✅ **JSON created**: scenarios_parsed.json (118KB)
⏭️ **Next**: Load to Qdrant with embeddings

---

## 🏗️ RAG Architecture

### Collections Structure

```python
{
    "business_scenarios": {
        "description": "All platform usage scenarios",
        "vector_size": 384,  # all-MiniLM-L6-v2
        "count": 328,
        "source": "ALL_USAGE_SCENARIOS_CATALOG.md",
        "update_frequency": "weekly",
        "search_type": "hybrid (semantic + keyword)"
    },

    "bcm_knowledge": {
        "description": "ISO 22301, NIST, WHO standards",
        "vector_size": 1536,  # text-embedding-3-large
        "count": "TBD",
        "source": "ISO standards, WHO guidelines, NIST frameworks",
        "update_frequency": "on_standard_updates",
        "search_type": "semantic"
    },

    "workflow_cases": {
        "description": "Real workflow executions (k=5 anonymized)",
        "vector_size": 1536,
        "count": "growing",
        "source": "Collective Intelligence",
        "update_frequency": "daily",
        "search_type": "semantic + filtering"
    },

    "documents": {
        "description": "User-generated BC plans, reports, etc.",
        "vector_size": 1536,
        "count": "per tenant",
        "source": "Document Service",
        "update_frequency": "real-time",
        "search_type": "semantic + tenant_filtering"
    },

    "generated_scenarios": {  # NEW
        "description": "Auto-generated from pattern detection",
        "vector_size": 384,
        "count": "growing",
        "source": "Scenario Generation System",
        "update_frequency": "daily",
        "search_type": "semantic + confidence_filtering"
    }
}
```

---

## 📊 Data Flow

### 1. **Scenario Ingestion Pipeline**

```
ALL_USAGE_SCENARIOS_CATALOG.md
    ↓ (parse)
scenarios_parsed.json (328 scenarios)
    ↓ (embed)
Sentence Transformers (all-MiniLM-L6-v2)
    ↓ (vectors)
Qdrant Collection: business_scenarios
    ↓ (search)
AI Assistant
```

### 2. **Self-Learning Loop**

```
Event Bus (real usage) → Pattern Detection
    ↓
Domain Analysis (classify by service/category)
    ↓
Scenario Generator (LLM Claude Opus)
    ↓
Validation (Domain Specialists)
    ↓
Qdrant Collection: generated_scenarios
    ↓
Merge with business_scenarios (after confidence check)
```

### 3. **Multi-Source RAG**

```python
User Query: "How to conduct BIA?"
    ↓
Parallel Search:
├── business_scenarios (existing 328)
├── generated_scenarios (new patterns)
├── workflow_cases (real examples, k=5)
└── bcm_knowledge (ISO standards)
    ↓
Rerank (by relevance + confidence)
    ↓
Context for LLM
    ↓
Answer
```

---

## 🔧 Technical Implementation

### Embedding Strategy

#### Option 1: Lightweight (Current - RECOMMENDED)
```python
Model: all-MiniLM-L6-v2
Vector Size: 384
Speed: Fast (local)
Cost: Free
Quality: Good for scenarios

Pros:
+ Works offline
+ No API costs
+ Fast inference
+ Good semantic similarity

Cons:
- Not multilingual (EN only)
- Lower quality than OpenAI
```

#### Option 2: High-Quality (Future)
```python
Model: text-embedding-3-large (OpenAI)
Vector Size: 1536
Speed: Moderate (API call)
Cost: $0.13 / 1M tokens
Quality: Excellent

Pros:
+ Best semantic quality
+ Multilingual
+ Industry standard

Cons:
- API costs
- Requires internet
- Slower
```

**Decision**: Start with Option 1, upgrade to Option 2 when needed.

---

### Search Strategies

#### 1. **Pure Semantic Search**
```python
query = "How to do BIA?"
embedding = encoder.encode(query)

results = client.search(
    collection_name="business_scenarios",
    query_vector=embedding,
    limit=5
)

# Best for: natural language questions
```

#### 2. **Filtered Search**
```python
results = client.search(
    collection_name="business_scenarios",
    query_vector=embedding,
    query_filter={
        "must": [
            {"key": "service", "match": {"value": "BIA"}}
        ]
    },
    limit=5
)

# Best for: specific service queries
```

#### 3. **Hybrid Search** (Semantic + Keyword)
```python
# 1. Semantic search
semantic_results = client.search(...)

# 2. Keyword search (PostgreSQL)
keyword_results = db.execute(
    "SELECT * FROM scenarios WHERE full_text ILIKE '%BIA%'"
)

# 3. Merge + rerank
final_results = rerank(semantic_results + keyword_results)

# Best for: comprehensive coverage
```

#### 4. **Multi-Collection Search**
```python
async def search_all_sources(query: str):
    results = {}

    # Parallel searches
    tasks = [
        search_scenarios(query),
        search_knowledge(query),
        search_cases(query)
    ]

    results = await asyncio.gather(*tasks)

    # Merge with source attribution
    return merge_and_rank(results)

# Best for: complex questions needing multiple sources
```

---

## 🚀 Implementation Phases

### ✅ Phase 1: Parse & Store (DONE)
```bash
# Already done:
python3 simple_scenario_loader.py
# Result: scenarios_parsed.json (328 scenarios)
```

### ⏭️ Phase 2: Load to RAG (NEXT - 2 hours)
```python
# File: load_to_qdrant.py
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import json

def load_scenarios():
    # 1. Load JSON
    with open('scenarios_parsed.json') as f:
        scenarios = json.load(f)

    # 2. Init embedding model
    encoder = SentenceTransformer('all-MiniLM-L6-v2')

    # 3. Create collection
    client = QdrantClient(path="./qdrant_local")  # local mode
    # or client = QdrantClient(url=QDRANT_URL, api_key=API_KEY)

    client.create_collection(
        collection_name="business_scenarios",
        vectors_config={"size": 384, "distance": "Cosine"}
    )

    # 4. Embed & upload
    points = []
    for idx, scenario in enumerate(scenarios):
        text = f"{scenario['title']} {scenario['description']} {scenario['components']}"
        vector = encoder.encode(text).tolist()

        points.append({
            "id": idx,
            "vector": vector,
            "payload": scenario
        })

    client.upsert(collection_name="business_scenarios", points=points)

    print(f"✅ Loaded {len(scenarios)} scenarios")

# Run
load_scenarios()
```

### Phase 3: Integrate with AI Assistant (3 days)
```python
# File: ai_assistant_with_rag.py
class AIAssistant:
    def __init__(self):
        self.qdrant = QdrantClient(...)
        self.llm = LLMRouter()

    async def answer(self, question: str):
        # 1. Search scenarios
        scenarios = await self.search_rag(question, top_k=3)

        # 2. Build context
        context = "\n\n".join([
            f"Scenario: {s['title']}\n"
            f"Service: {s['service']}\n"
            f"Description: {s['description']}\n"
            f"Components: {s['components']}"
            for s in scenarios
        ])

        # 3. Generate answer
        prompt = f"""
        User question: {question}

        Relevant scenarios from our platform:
        {context}

        Answer the question using these scenarios.
        Include specific endpoints, components, and events mentioned.
        """

        answer = await self.llm.generate(prompt, model="claude-sonnet")
        return answer

    async def search_rag(self, query: str, top_k: int):
        # Search in RAG
        embedding = self.encoder.encode(query).tolist()

        results = self.qdrant.search(
            collection_name="business_scenarios",
            query_vector=embedding,
            limit=top_k
        )

        return [r.payload for r in results]
```

### Phase 4: Self-Learning System (2 weeks)
See SCENARIO_GENERATION_SYSTEM.md (next file)

---

## 📈 Quality Metrics

### RAG Search Quality
```python
metrics = {
    "precision@3": 0.85,  # Top 3 results relevant
    "recall@10": 0.92,    # Find all relevant in top 10
    "mrr": 0.78,          # Mean Reciprocal Rank
    "latency_ms": 45      # Search speed
}
```

### Embedding Quality
```python
# Test queries
test_cases = [
    ("How to conduct BIA?", ["1.1 Start New BIA", "1.3 Generate Interview Questions"]),
    ("Risk assessment process", ["2.1 Start Risk Assessment", "2.2 ML-Powered Risk Likelihood"]),
    ("Create BC plan", ["3.7 Create BC Plan from Template", "3.8 AI-Generated BC Plan"])
]

# Validate that expected scenarios appear in top 5
for query, expected in test_cases:
    results = search(query, top_k=5)
    found = any(exp in [r['title'] for r in results] for exp in expected)
    assert found, f"Expected scenarios not found for: {query}"
```

---

## 🔐 Security & Privacy

### Tenant Isolation
```python
# Each search filtered by tenant
results = client.search(
    collection_name="documents",  # User documents
    query_vector=embedding,
    query_filter={
        "must": [
            {"key": "tenant_id", "match": {"value": current_user.tenant_id}}
        ]
    }
)
```

### K-Anonymity (Collective Intelligence)
```python
# Only share if k >= 5 similar cases exist
if count_similar_cases(case) >= 5:
    anonymized = anonymize(case)
    share_to_community(anonymized)
```

---

## 💾 Data Management

### Update Strategies

#### 1. **Static Collections** (business_scenarios, bcm_knowledge)
```python
# Update weekly
async def weekly_update():
    scenarios = parse_latest_catalog()
    client.recreate_collection("business_scenarios")
    load_scenarios(scenarios)
```

#### 2. **Dynamic Collections** (workflow_cases, documents)
```python
# Update real-time
async def on_document_created(doc):
    embedding = embed(doc)
    client.upsert(
        collection_name="documents",
        points=[{
            "id": doc.id,
            "vector": embedding,
            "payload": doc.metadata
        }]
    )
```

#### 3. **Generated Collections** (generated_scenarios)
```python
# Update daily (self-learning loop)
async def daily_generation():
    new_patterns = detect_patterns(last_24h_events)
    new_scenarios = generate_scenarios(new_patterns)

    # Add with confidence score
    for scenario in new_scenarios:
        if scenario['confidence'] > 0.7:
            client.upsert(
                collection_name="generated_scenarios",
                points=[{...}]
            )
```

---

## 🎯 Success Criteria

### Short-term (1 month)
- ✅ 328 scenarios searchable in RAG
- ✅ AI Assistant uses RAG for answers
- ✅ Search latency < 100ms
- ✅ Precision@3 > 80%

### Mid-term (3 months)
- ✅ Self-learning generates 50+ new scenarios
- ✅ Multi-source search (scenarios + knowledge + cases)
- ✅ Hybrid search (semantic + keyword)
- ✅ User feedback loop (thumbs up/down)

### Long-term (6 months)
- ✅ 1,000+ scenarios (existing + generated)
- ✅ Predictive scenario suggestions
- ✅ Cross-industry pattern detection
- ✅ Auto-documentation from real usage

---

## 📝 Next Steps

### Immediate (Today):
1. ✅ Parse catalog → scenarios_parsed.json (DONE)
2. ⏭️ Create load_to_qdrant.py (simplified version)
3. ⏭️ Test local Qdrant
4. ⏭️ Test search quality

### This Week:
1. Integrate RAG into AI Assistant
2. Test with real user queries
3. Measure search quality metrics
4. Document API

### This Month:
1. Implement self-learning loop
2. Pattern detection from Event Bus
3. Scenario generation (LLM)
4. Auto-load to RAG

---

## 🔗 Related Documents

- `SCENARIO_STRATEGY.md` - Overall scenario documentation strategy
- `SCENARIO_GENERATION_SYSTEM.md` - Self-learning architecture (next)
- `simple_scenario_loader.py` - Parser implementation
- `scenarios_parsed.json` - Parsed data (328 scenarios)

---

**Status**: ✅ Strategy Complete
**Next**: Implement load_to_qdrant.py
**ETA**: 2 hours for Phase 2
