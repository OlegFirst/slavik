# AI Foundation

Core AI Infrastructure for BCM Platform

## Overview

`ai-foundation` provides core AI capabilities used across the platform:

- **RAG** - Retrieval Augmented Generation
- **ML** - Machine Learning (predictive models, anomaly detection)
- **Learning** - Self-learning and pattern extraction
- **Context** - Context building for AI
- **LLM** - Large Language Model routing

## Architecture

```
ai-foundation/
├── rag/              # RAG Pipeline
│   ├── pipeline.py
│   ├── embeddings.py
│   ├── retrieval.py
│   └── reranking.py
│
├── ml/               # Machine Learning
│   ├── predictive_models.py
│   ├── training_pipeline.py
│   └── anomaly_detection.py
│
├── learning/         # Self-Learning
│   ├── self_learning_engine.py
│   ├── pattern_extractor.py
│   └── rule_generator.py
│
├── context/          # Context Building
│   └── context_builder.py
│
└── llm/              # LLM Routing
    └── llm_router.py
```

## Usage

### From workflow_intelligence:

```python
from ai_foundation import RAGPipeline, MLPredictor, ContextBuilder

# Build context
context_builder = ContextBuilder()
context = await context_builder.build_context(
    workflow_id="wf-123",
    domain="bcm",
    tenant_id="tenant-1"
)

# Use RAG
rag = RAGPipeline()
results = await rag.search(query="ISO 22301 requirements", context=context)

# Use ML
ml_predictor = MLPredictor()
prediction = await ml_predictor.predict(data=workflow_data)
```

### From expertise-center:

```python
from ai_foundation import RAGPipeline, LLMRouter

# Use RAG for knowledge retrieval
rag = RAGPipeline()
knowledge = await rag.search(query="BIA best practices")

# Route to appropriate LLM
llm_router = LLMRouter()
response = await llm_router.route(
    task="strategic_analysis",
    prompt="Analyze BIA results..."
)
```

### From platform-services:

```python
from ai_foundation import AnomalyDetector

# Detect anomalies in business data
detector = AnomalyDetector()
anomalies = await detector.detect(data=risk_metrics)
```

## Why Separate from workflow_intelligence?

**Architecture Decision (V7 Improved):**

- **ai-foundation** = AI infrastructure (used by ALL)
- **workflow_intelligence** = Workflow logic only

Benefits:
1. ✅ Loose coupling - services can use AI without depending on workflow
2. ✅ Independent scaling - AI layer can scale separately
3. ✅ Reusability - same AI stack for all domains (BCM, HR, Finance)
4. ✅ Clear separation - workflow = orchestration, ai-foundation = computation

## Dependencies

```python
# External
- openai
- anthropic
- qdrant-client
- sentence-transformers
- scikit-learn

# Internal
- shared.database
- shared.cache
- infrastructure.vector-db
```

## Used By

1. **workflow_intelligence** - Workflow orchestration with AI
2. **expertise-center** - Domain specialists, colleagues, analyzers
3. **community_intelligence** - Community AI features
4. **platform-services** - Business services needing AI (BIA, Risk, etc.)

## Status

✅ **Production Ready** (V7 Architecture)

- RAG: Complete
- ML: Complete
- Learning: Complete
- Context: Basic (needs enrichment)
- LLM: Complete
