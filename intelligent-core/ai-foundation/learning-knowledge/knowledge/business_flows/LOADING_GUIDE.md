# Business Flows - Loading Guide
**How to Load 320+ BCM Flows into Qdrant for RAG**

---

## 🎯 Quick Start

### Step 1: Make Sure Qdrant is Running

```bash
# Check if Qdrant is running
curl http://localhost:6333/collections

# If not, start it:
cd /Users/MD/AI-Platform-ISO
docker-compose up -d qdrant

# Or if using infrastructure docker-compose:
cd infrastructure/vector-db
docker-compose up -d
```

---

### Step 2: Set Environment Variables (Optional)

```bash
# For cloud Qdrant (if using):
export QDRANT_URL="https://your-cluster.qdrant.io"
export QDRANT_API_KEY="your-api-key"

# For OpenAI embeddings (best quality, but costs $):
export OPENAI_API_KEY="sk-..."

# If not set:
# - Uses local Qdrant: http://localhost:6333
# - Uses local embeddings (sentence-transformers) - FREE
```

---

### Step 3: Run the Loader Script

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge

# Simple - just run it:
python scripts/load_business_flows.py

# Or with explicit Python:
python3 scripts/load_business_flows.py
```

**What it does:**
1. ✅ Loads 5 flow documents (WHO, ISO, NIST, Case Library, etc.)
2. ✅ Parses ~320 individual flows
3. ✅ Creates embeddings (OpenAI or local)
4. ✅ Indexes into Qdrant collection: `bcm_business_flows`
5. ✅ Takes 2-5 minutes total

**Expected output:**
```
╔══════════════════════════════════════════════════════════╗
║  BCM Business Flows Loader                               ║
║  Loading 320+ flows into Qdrant for RAG                  ║
╚══════════════════════════════════════════════════════════╝

📚 Initializing Business Flows Loader...
✅ Knowledge path found: .../business_flows/
  ✅ WHO_HEALTHCARE_BCM_FLOWS.md (78.0 KB)
  ✅ ISO_IMPLEMENTATION_FLOWS.md (82.0 KB)
  ✅ NIST_CONTINGENCY_PLANNING_FLOWS.md (19.0 KB)
  ✅ CASE_LIBRARY_PRACTICAL_FLOWS.md (31.0 KB)

📖 Loading flows from all sources...
✅ Loaded 89 flows from who_healthcare
✅ Loaded 118 flows from iso_implementation
✅ Loaded 43 flows from nist_contingency
✅ Loaded 72 flows from case_library
✅ Loaded 322 total flow documents

🔍 Initializing Vector Indexer...
✅ Using local embeddings: all-MiniLM-L6-v2 (dim=384)

💾 Indexing flows into Qdrant...
✅ Indexed 10/322 flows...
✅ Indexed 20/322 flows...
...
✅ Successfully indexed 322/322 flows

╔══════════════════════════════════════════════════════════╗
║  ✅ Business Flows Loading Complete!                     ║
╠══════════════════════════════════════════════════════════╣
║  Flows Loaded:      322                                  ║
║  Flows Indexed:     322                                  ║
║  Collection:       bcm_business_flows                    ║
║  Embedding:        local                                 ║
╚══════════════════════════════════════════════════════════╝

✅ Ready for production use!
```

---

## 🔍 Verify Loading

### Check Qdrant Collection:

```bash
# Check if collection exists
curl http://localhost:6333/collections/bcm_business_flows

# Expected output:
{
  "result": {
    "status": "green",
    "vectors_count": 322,
    "indexed_vectors_count": 322,
    ...
  }
}
```

---

### Test Search:

```python
# Test semantic search
from intelligent_core.ai_foundation.learning_knowledge.knowledge.indexer.vector_indexer import VectorIndexer

indexer = VectorIndexer(collection_name="bcm_business_flows")

# Search for healthcare BIA
results = await indexer.search("how to conduct BIA in healthcare organization", top_k=5)

# Should return:
# 1. WHO Healthcare BCM Flow 1: Health Service Continuity Planning
# 2. ISO Implementation Flow 12: BIA Template Completion (6 weeks)
# 3. Case Library: Healthcare BIA (14 days average)
# etc.
```

---

## 🚀 Use with RAG Pipeline

### Basic Query:

```python
from intelligent_core.ai_foundation.rag.pipeline import RAGPipeline

# Initialize RAG
rag = RAGPipeline(
    knowledge_sources=["bcm_business_flows"],
    top_k=5
)

# Query
results = rag.query("How to conduct BIA in healthcare?")

# Results include:
# - Top 5 most relevant flows
# - Context from WHO, ISO, Case Library
# - Metadata (source, ISO clause, complexity, etc.)
```

---

### With LLM:

```python
from intelligent_core.ai_foundation.llm.llm_router import LLMRouter
from intelligent_core.ai_foundation.rag.pipeline import RAGPipeline

# Initialize
rag = RAGPipeline()
llm = LLMRouter()

# Retrieve context
context = rag.query("How to conduct BIA in healthcare?", top_k=5)

# Generate response
response = await llm.route(
    messages=[
        {"role": "system", "content": f"Context:\n{context}"},
        {"role": "user", "content": "How should a hospital conduct BIA?"}
    ],
    provider="anthropic"
)

# Response will be grounded in WHO Healthcare BCM + ISO Implementation flows
```

---

## 📊 What Gets Indexed

### Flow Documents:

Each flow is indexed with:
- **flow_id**: Unique identifier (e.g., `who_healthcare_flow_1`)
- **flow_name**: Human-readable name
- **content**: Full flow description
- **source**: Source document (who_healthcare, iso_implementation, etc.)
- **priority**: Search priority (0.85-1.0)
- **domain**: Domain tag (healthcare, it_tech, general)
- **type**: Flow type (domain_specific, implementation_guide, etc.)
- **iso_clause**: ISO 22301 clause (if applicable)
- **complexity**: Low/Medium/High
- **tags**: List of tags (healthcare, bia, risk, testing, etc.)

### Example Document:

```json
{
  "flow_id": "who_healthcare_flow_1",
  "flow_name": "Health Service Continuity Planning Lifecycle",
  "content": "8-step process for healthcare BCM...",
  "source": "who_healthcare",
  "source_file": "WHO_HEALTHCARE_BCM_FLOWS.md",
  "priority": 0.95,
  "domain": "healthcare",
  "type": "domain_specific",
  "complexity": "high",
  "tags": ["healthcare", "planning"],
  "loaded_at": "2025-10-08T17:30:00Z"
}
```

---

## 🔄 Re-Loading / Updating

### To Update Flows:

If you add new flows or modify existing ones:

```bash
# Just re-run the loader
python scripts/load_business_flows.py

# It will:
# 1. Reload all flows
# 2. Re-index into Qdrant
# 3. Overwrite existing collection
```

### To Add New Source:

1. Add markdown file to `business_flows/` directory
2. Update `business_flows_loader.py`:

```python
self.sources = {
    # Existing sources...
    "new_source": {
        "file": "NEW_SOURCE_FLOWS.md",
        "priority": 0.9,
        "domain": "general",
        "type": "new_type"
    }
}
```

3. Re-run loader

---

## 🐛 Troubleshooting

### Error: "Connection refused to Qdrant"

**Problem:** Qdrant not running

**Solution:**
```bash
docker-compose up -d qdrant
# Wait 10 seconds for startup
curl http://localhost:6333/collections
```

---

### Error: "No source files found"

**Problem:** Business flows not in correct location

**Solution:**
```bash
# Check files exist:
ls -la /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge/knowledge/business_flows/

# Should see:
# WHO_HEALTHCARE_BCM_FLOWS.md
# ISO_IMPLEMENTATION_FLOWS.md
# NIST_CONTINGENCY_PLANNING_FLOWS.md
# CASE_LIBRARY_PRACTICAL_FLOWS.md
```

---

### Error: "Embedding provider failed"

**Problem:** OpenAI API key invalid or missing, local embeddings not installed

**Solution:**
```bash
# Install local embeddings (FREE):
pip install sentence-transformers

# Or use OpenAI (better quality, but costs $):
export OPENAI_API_KEY="sk-..."

# Or use TF-IDF fallback (lowest quality, but always works):
# No setup needed, will auto-fallback
```

---

### Warning: "TF-IDF fallback"

**Problem:** Neither OpenAI nor sentence-transformers available

**Impact:** Search quality lower (keyword-based vs semantic)

**Solution:**
```bash
# Install sentence-transformers for better search:
pip install sentence-transformers torch
```

---

## 📈 Performance

### Loading Time:

| Embedding Provider | Time | Quality |
|-------------------|------|---------|
| OpenAI (text-embedding-3-small) | 2-3 min | ⭐⭐⭐⭐⭐ Best |
| Local (all-MiniLM-L6-v2) | 3-5 min | ⭐⭐⭐⭐ Good |
| TF-IDF (fallback) | 1-2 min | ⭐⭐ Basic |

### Search Performance:

- **Query time:** <100ms (Qdrant)
- **Top-5 retrieval:** <50ms
- **With reranking:** <200ms

---

## ✅ Success Checklist

After loading, verify:

- [ ] Qdrant collection exists: `curl http://localhost:6333/collections/bcm_business_flows`
- [ ] 300+ vectors indexed (check `vectors_count`)
- [ ] Test search works: `python -c "from intelligent_core... import VectorIndexer; ..."`
- [ ] RAG query works: `rag.query("test query")`
- [ ] LLM integration works: Context retrieved and used

---

## 🎓 Next Steps

**Now that flows are loaded:**

1. **Use in Platform Services:**
   - BIA Service can retrieve BIA flows
   - Risk Service can retrieve risk assessment flows
   - Context-aware guidance for users

2. **Use in AI Orchestrator:**
   - Orchestrator queries flows for decision-making
   - "How should I orchestrate BIA → Risk flow?"
   - Retrieved context informs orchestration strategy

3. **Use in Collective Intelligence:**
   - Combine flows with case library patterns
   - "Show me healthcare organizations that solved X"
   - Flows + Cases = Complete guidance

4. **Use in Expertise Center:**
   - Domain specialists query relevant flows
   - BIA Specialist retrieves BIA-specific flows
   - Risk Analyst retrieves risk flows

---

## 📞 Questions?

**Collection info:**
- Name: `bcm_business_flows`
- Vectors: 320+
- Dimension: 384 (local) or 1536 (OpenAI)
- Distance: Cosine similarity

**Metadata fields:**
- `source`: Source document ID
- `domain`: healthcare / it_tech / general
- `type`: Flow type
- `iso_clause`: ISO clause (if applicable)
- `complexity`: low / medium / high
- `tags`: List of relevant tags

**Query examples:**
- "How to conduct BIA?"
- "Healthcare emergency preparedness"
- "IT disaster recovery procedures"
- "ISO certification audit preparation"

---

**Flows loaded and ready for RAG! 🚀**
