# AI Foundation - Практические примеры использования

**Version:** 1.0.0
**Last Updated:** 2025-10-07

Этот документ содержит практические примеры использования ai-foundation компонентов в разных сценариях.

---

## Table of Contents

1. [RAG Usage](#rag-usage)
2. [LLM Router Usage](#llm-router-usage)
3. [ML Models Usage](#ml-models-usage)
4. [Learning System Usage](#learning-system-usage)
5. [Context Builder Usage](#context-builder-usage)
6. [Integration Patterns](#integration-patterns)
7. [Production Best Practices](#production-best-practices)

---

## RAG Usage

### Example 1: Basic Knowledge Retrieval

```python
from ai_foundation import RAGPipeline

# Initialize RAG pipeline
rag = RAGPipeline(
    embedding_provider="voyage",  # or "openai"
    chunk_size=512,
    top_k=5
)

# Retrieve knowledge
query = "What is Business Impact Analysis?"
results = await rag.retrieve(
    query=query,
    enable_reranking=True,
    enable_diversity=False
)

# Process results
for i, result in enumerate(results, 1):
    print(f"{i}. Score: {result['score']:.3f}")
    print(f"   Source: {result['source']}")
    print(f"   Content: {result['content'][:200]}...")
    print()
```

**Output:**
```
1. Score: 0.892
   Source: iso_standard
   Content: Business Impact Analysis (BIA) is the process of identifying critical business functions and their dependencies...

2. Score: 0.845
   Source: case_study
   Content: Case Study: Financial Services Company implemented BIA using automated tools...
```

### Example 2: Ingesting Documents

```python
from ai_foundation import RAGPipeline, KnowledgeSourceManager

# Initialize
rag = RAGPipeline()
knowledge_manager = KnowledgeSourceManager(rag)

# Ingest ISO standards
iso_standards = [
    {
        "text": "Clause 8.2.2: Business Impact Analysis - Organizations shall conduct BIA...",
        "metadata": {
            "standard": "ISO 22301",
            "clause": "8.2.2",
            "section": "Business Impact Analysis"
        }
    },
    {
        "text": "Clause 8.2.1: Risk Assessment - Organizations shall identify and assess risks...",
        "metadata": {
            "standard": "ISO 22301",
            "clause": "8.2.1",
            "section": "Risk Assessment"
        }
    }
]

# Ingest with automatic chunking and embedding
doc_count = await knowledge_manager.load_iso_standards(iso_standards)
print(f"Ingested {doc_count} ISO standard documents")

# Ingest case studies
cases = [
    {
        "title": "Healthcare BCM Implementation",
        "industry": "healthcare",
        "org_size": "large",
        "summary": "Major hospital implemented BCM program during pandemic...",
        "key_challenge": "Coordinating across 50+ departments",
        "solution": "Centralized BCM platform with departmental champions",
        "outcome": "100% uptime during COVID-19 surge",
        "lessons_learned": ["Early engagement crucial", "Communication protocols vital"]
    }
]

case_count = await knowledge_manager.load_case_library(cases)
print(f"Ingested {case_count} case studies")
```

### Example 3: Filtered Search

```python
# Search with metadata filters
results = await rag.retrieve(
    query="risk assessment best practices",
    filters={
        "industry": "healthcare",
        "org_size": "large"
    },
    top_k=3,
    enable_reranking=True
)

# Results будут только healthcare large organizations
```

### Example 4: Context Building for LLM

```python
# Build optimized context for LLM prompt
query = "How to conduct BIA in financial services?"

context_str = await rag.build_context(
    query=query,
    max_context_length=2000  # Token budget
)

print(f"Context for LLM:\n{context_str}")
```

**Output:**
```
[1] Source: iso_standard
Business Impact Analysis (BIA) identifies critical functions...

[2] Source: case_study
Financial Services Company: Implemented BIA focusing on trading systems...

[3] Source: bci_guidelines
BCI Good Practice: Financial sector should prioritize payment systems...
```

### Example 5: RAG Statistics

```python
# Get RAG pipeline stats
stats = rag.get_stats()

print(f"Vector store: {stats['vector_store']['total_documents']} documents")
print(f"Embedding provider: {stats['embedding_provider']}")
print(f"Chunk size: {stats['chunk_size']}")
print(f"Default top_k: {stats['default_top_k']}")
```

---

## LLM Router Usage

### Example 1: Task-Specific Routing

```python
from ai_foundation import LLMRouter

llm = LLMRouter()

# Strategic analysis - uses Claude Opus
strategic_response = await llm.query(
    system_prompt="You are a senior BCM consultant with 20 years experience.",
    user_prompt="Analyze the strategic risks of not having a BCM program for a Fortune 500 financial institution.",
    task_type="strategic_analysis",
    temperature=0.7,
    max_tokens=2000
)

print("Strategic Analysis:")
print(strategic_response)

# Content generation - uses Claude Sonnet
content_response = await llm.query(
    system_prompt="You are a technical writer for BCM documentation.",
    user_prompt="Write a 3-paragraph introduction to Business Impact Analysis for executive audience.",
    task_type="content_generation",
    temperature=0.5,
    max_tokens=1000
)

print("\nGenerated Content:")
print(content_response)

# Quick task - uses Claude Haiku or GPT-3.5
quick_response = await llm.query(
    system_prompt="You are a helpful BCM assistant.",
    user_prompt="List 5 critical components of a BCM program.",
    task_type="quick_tasks",
    temperature=0.3,
    max_tokens=500
)

print("\nQuick Answer:")
print(quick_response)
```

### Example 2: RAG + LLM Integration

```python
from ai_foundation import RAGPipeline, LLMRouter

rag = RAGPipeline()
llm = LLMRouter()

# User question
question = "What are RTO and RPO in BCM context?"

# Step 1: Retrieve relevant knowledge
knowledge = await rag.retrieve(
    query=question,
    top_k=3,
    enable_reranking=True
)

# Step 2: Build context from knowledge
context_parts = []
for i, result in enumerate(knowledge, 1):
    context_parts.append(f"[Source {i}]: {result['content']}")

context_str = "\n\n".join(context_parts)

# Step 3: Query LLM with RAG context
system_prompt = """You are a BCM expert. Use the provided knowledge sources to answer questions accurately.
Always cite sources using [Source N] format when referencing information."""

user_prompt = f"""Knowledge base context:

{context_str}

Question: {question}

Please provide a comprehensive answer based on the sources above."""

answer = await llm.query(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    task_type="content_generation",
    temperature=0.3
)

print(f"Q: {question}")
print(f"\nA: {answer}")
```

**Output:**
```
Q: What are RTO and RPO in BCM context?

A: Based on the knowledge sources:

RTO (Recovery Time Objective) is the maximum acceptable time period within which a business process
must be restored after a disruption [Source 1]. For example, a trading system might have RTO of
2 hours, meaning it must be operational within 2 hours of an outage.

RPO (Recovery Point Objective) is the maximum acceptable amount of data loss measured in time
[Source 2]. An RPO of 15 minutes means you can afford to lose maximum 15 minutes of data.

In practice [Source 3], financial institutions typically set:
- Critical systems: RTO 1-4 hours, RPO 0-15 minutes
- Important systems: RTO 4-24 hours, RPO 1-4 hours
- Standard systems: RTO 24-72 hours, RPO 4-24 hours
```

### Example 3: Embeddings Generation

```python
# Generate embeddings for semantic search
texts = [
    "Business continuity planning is essential",
    "Risk assessment identifies threats",
    "Disaster recovery focuses on IT systems"
]

embeddings = await llm.generate_embeddings(texts)

print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding dimension: {len(embeddings[0])}")
```

### Example 4: Provider Information

```python
# Check available providers
info = llm.get_provider_info()

print("Available LLM Providers:")
for provider, details in info.items():
    print(f"\n{provider.upper()}:")
    print(f"  Available: {details['available']}")
    if details['available']:
        print(f"  Models: {', '.join(details['models'])}")
```

**Output:**
```
Available LLM Providers:

ANTHROPIC:
  Available: True
  Models: claude-opus-4-20250514, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022

OPENAI:
  Available: True
  Models: gpt-4-turbo-preview, gpt-3.5-turbo, text-embedding-3-large
```

---

## ML Models Usage

### Example 1: Workflow Duration Prediction

```python
from ai_foundation import WorkflowPredictor

# Initialize predictor
predictor = WorkflowPredictor()

# Organization context
org_context = {
    "size": "medium",
    "maturity": 3,
    "industry": "healthcare"
}

# Current workflow state
current_state = "bia_in_progress"

# Progress data
current_progress = {
    "current_stage_index": 2,
    "total_stages": 6,
    "complexity_score": 4,
    "ai_usage_count": 5,
    "challenges": [
        {"type": "stakeholder_engagement", "resolved": False},
        {"type": "data_collection", "resolved": True}
    ]
}

# Predict workflow journey
prediction = await predictor.predict_journey(
    org_context=org_context,
    current_state=current_state,
    current_progress=current_progress
)

print("Workflow Predictions:")
print(f"Current stage duration: {prediction['current_stage_prediction']['estimated_duration_hours']} hours")
print(f"Confidence: {prediction['current_stage_prediction']['confidence']}")
print(f"\nStuck probability: {prediction['stuck_probability']['probability']} ({prediction['stuck_probability']['risk_level']})")
print(f"Expert help needed: {prediction['expert_help_needed']}")
print(f"\nTotal completion estimate:")
print(f"  Hours: {prediction['total_completion_estimate']['estimated_hours']}")
print(f"  Days: {prediction['total_completion_estimate']['estimated_days']}")
print(f"\nRisk assessment: {prediction['risk_assessment']['level']} - {prediction['risk_assessment']['description']}")
print(f"\nRecommendations:")
for rec in prediction['recommendations']:
    print(f"  - {rec}")
```

**Output:**
```
Workflow Predictions:
Current stage duration: 19.2 hours
Confidence: 0.6

Stuck probability: 0.3 (low)
Expert help needed: False

Total completion estimate:
  Hours: 76.8
  Days: 9.6

Risk assessment: low - Low risk, progressing normally

Recommendations:
  - Progress is on track - continue with current approach
```

### Example 2: Anomaly Detection

```python
from ai_foundation import AnomalyDetector

detector = AnomalyDetector(sensitivity=0.8)

# Current workflow data
workflow_data = {
    "workflow_id": "wf-123",
    "org_size": "large",
    "org_maturity": 4,
    "current_stage": "risk_assessment",
    "duration_hours": 48,  # Unusually long
    "days_in_current_stage": 8,
    "days_since_last_activity": 2,
    "recent_activities": []  # Limited activity
}

# Historical data for baseline (optional)
historical_data = [
    {"stage": "risk_assessment", "duration_hours": 16},
    {"stage": "risk_assessment", "duration_hours": 20},
    {"stage": "risk_assessment", "duration_hours": 18},
]

# Detect anomalies
anomalies = await detector.detect_workflow_anomalies(
    workflow_data=workflow_data,
    historical_data=historical_data
)

print(f"Anomalies detected: {anomalies['anomalies_detected']}")
print(f"Risk level: {anomalies['risk_level']}")

for anomaly in anomalies['anomalies']:
    print(f"\n{anomaly['type'].upper()} ({anomaly['severity']})")
    print(f"  {anomaly['description']}")
    print(f"  Recommendation: {anomaly['recommendation']}")
```

**Output:**
```
Anomalies detected: 1
Risk level: medium

DURATION (high)
  Stage duration (48h) is 2.5 std devs from baseline (18.0h)
  Recommendation: Investigate cause of unusual duration
```

### Example 3: Training ML Models

```python
from ai_foundation import TrainingPipeline

# Initialize training pipeline
trainer = TrainingPipeline(model_dir=Path("./models"))

# Run training
result = await trainer.run_training(
    model_type='workflow_predictor',
    min_samples=50,
    force_retrain=False
)

if result['status'] == 'success':
    print("Training successful!")
    print(f"Samples trained: {result['samples_train']}")
    print(f"Samples tested: {result['samples_test']}")
    print(f"\nMetrics:")
    print(f"  Duration R²: {result['metrics']['duration_r2']}")
    print(f"  Duration MAE: {result['metrics']['duration_mae_hours']} hours")
    print(f"  Stuck accuracy: {result['metrics']['stuck_accuracy']}")
    print(f"  Help accuracy: {result['metrics']['help_accuracy']}")
    print(f"\nModel saved to: {result['model_path']}")
else:
    print(f"Training failed: {result.get('message', result.get('error'))}")
```

### Example 4: Data Quality Check

```python
# Check data quality before processing
data = {
    "org_size": "medium",
    "industry": "healthcare",
    "current_stage": "bia",
    "stage_index": 2,
    "total_stages": 6
}

quality = await detector.detect_data_quality_issues(data)

print(f"Data quality score: {quality['quality_score']}/100")
print(f"Status: {quality['status']}")

if quality['issues_detected'] > 0:
    print(f"\nIssues found: {quality['issues_detected']}")
    for issue in quality['issues']:
        print(f"  - {issue['type']}: {issue['description']}")
```

---

## Learning System Usage

### Example 1: Learning from Completed Workflow

```python
from ai_foundation import SelfLearningEngine

# Initialize learning engine
learning = SelfLearningEngine(
    min_pattern_frequency=10,
    min_success_rate=0.8
)

# Completed workflow case (anonymized)
workflow_case = {
    "id": "case-456",
    "industry": "finance",
    "org_size": "large",
    "maturity": 4,
    "module": "bia",
    "duration_hours": 24,
    "success": True,
    "challenges": [
        {
            "type": "data_collection",
            "description": "Difficulty gathering process data from legacy systems",
            "resolution": "Implemented automated data extraction tools"
        }
    ],
    "strategies_used": [
        "automated_data_collection",
        "stakeholder_workshops",
        "ai_assisted_analysis"
    ],
    "outcomes": {
        "completion_rate": 1.0,
        "stakeholder_satisfaction": 4.5
    }
}

# Learn from completion
result = await learning.learn_from_workflow_completion(workflow_case)

print(f"Learning Results:")
print(f"Patterns extracted: {result['patterns_extracted']}")
print(f"Benchmarks updated: {result['benchmarks_updated']}")

if result['suggested_rules']:
    print(f"\nSuggested rules: {len(result['suggested_rules'])}")
    for rule in result['suggested_rules']:
        print(f"\nRule: {rule['rule_text']}")
        print(f"Type: {rule['type']}")
        print(f"Evidence: {rule['evidence']['frequency']} occurrences, {rule['evidence']['success_rate']:.1%} success")
        print(f"Status: {rule['status']}")
```

### Example 2: Approving Learned Rules

```python
# Get pending rules
pending_rules = learning.get_pending_rules()

print(f"Pending rules for approval: {len(pending_rules)}")

for rule in pending_rules:
    print(f"\nRule ID: {rule['id']}")
    print(f"Type: {rule['type']}")
    print(f"Text: {rule['rule_text']}")
    print(f"Frequency: {rule['frequency']}")
    print(f"Success rate: {rule['success_rate']:.1%}")

    # Human review decision
    user_decision = input("Approve this rule? (y/n): ")

    if user_decision.lower() == 'y':
        approval_result = await learning.approve_rule(rule['id'])
        print(f"✓ Rule approved: {approval_result['status']}")
    else:
        reason = input("Rejection reason: ")
        rejection_result = await learning.reject_rule(rule['id'], reason)
        print(f"✗ Rule rejected: {rejection_result['status']}")
```

### Example 3: Learning Statistics

```python
# Get learning stats
stats = learning.get_learning_stats()

print("Learning System Statistics:")
print(f"Total patterns learned: {stats['total_patterns_learned']}")
print(f"Pending rules (awaiting approval): {stats['pending_rules']}")
print(f"Approved rules (active): {stats['approved_rules']}")
print(f"Learning active: {stats['learning_active']}")
```

---

## Context Builder Usage

### Example 1: Basic Context Building

```python
from ai_foundation import ContextBuilder

context_builder = ContextBuilder()

# Build context for workflow
context = await context_builder.build_context(
    workflow_id="wf-123",
    domain="bcm",
    tenant_id="tenant-456",
    user_id="user-789",
    additional_context={
        "current_stage": "bia",
        "industry": "healthcare",
        "org_size": "large"
    }
)

print("Built Context:")
print(f"Timestamp: {context['timestamp']}")
print(f"Workflow: {context['workflow_id']}")
print(f"Domain: {context['domain']}")
print(f"Tenant: {context['tenant_id']}")
print(f"Stage: {context['current_stage']}")
print(f"Industry: {context['industry']}")
```

### Example 2: Context Enrichment (when implemented)

```python
# Build base context
base_context = await context_builder.build_context(
    workflow_id="wf-123",
    domain="bcm"
)

# Enrich with additional sources
enriched_context = await context_builder.enrich_context(
    base_context=base_context,
    enrichment_sources=[
        'rag_knowledge',
        'historical_data',
        'similar_workflows'
    ]
)

# Enriched context would include:
# - RAG knowledge relevant to current stage
# - Historical workflow data for predictions
# - Similar workflows for benchmarking
```

---

## Integration Patterns

### Pattern 1: Expertise-Center Integration

```python
# In expertise-center specialist class
from ai_foundation import RAGPipeline, LLMRouter, ContextBuilder

class BCMAdvisor:
    def __init__(self):
        self.rag = RAGPipeline()
        self.llm = LLMRouter()
        self.context_builder = ContextBuilder()

    async def provide_advice(self, query: str, org_context: dict):
        # 1. Build context
        context = await self.context_builder.build_context(
            domain="bcm",
            tenant_id=org_context['tenant_id'],
            additional_context=org_context
        )

        # 2. Retrieve knowledge via RAG
        knowledge = await self.rag.retrieve(
            query=query,
            context=context,
            top_k=5,
            enable_reranking=True
        )

        # 3. Build RAG context for LLM
        rag_context = await self.rag.build_context(query, max_context_length=1500)

        # 4. Generate advice with LLM
        system_prompt = """You are a senior BCM advisor with 20 years experience.
        Provide strategic advice based on ISO 22301 and industry best practices."""

        user_prompt = f"""Organization context:
Industry: {org_context['industry']}
Size: {org_context['size']}
Maturity: {org_context['maturity']}

Knowledge base:
{rag_context}

Question: {query}

Provide strategic recommendations with justification."""

        advice = await self.llm.query(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task_type="strategic_analysis",
            temperature=0.7
        )

        return {
            'advice': advice,
            'sources': knowledge,
            'context': context
        }
```

### Pattern 2: Workflow Intelligence Integration

```python
# In workflow_intelligence service
from ai_foundation import WorkflowPredictor, AnomalyDetector, ContextBuilder

class WorkflowIntelligenceService:
    def __init__(self):
        self.predictor = WorkflowPredictor()
        self.anomaly_detector = AnomalyDetector()
        self.context_builder = ContextBuilder()

    async def analyze_workflow_health(self, workflow_id: str):
        # Get workflow data
        workflow = await self.db.get_workflow(workflow_id)

        # Build context
        context = await self.context_builder.build_context(
            workflow_id=workflow_id,
            domain=workflow['domain']
        )

        # Predict journey
        prediction = await self.predictor.predict_journey(
            org_context=workflow['org_context'],
            current_state=workflow['current_state'],
            current_progress=workflow['progress']
        )

        # Detect anomalies
        anomalies = await self.anomaly_detector.detect_workflow_anomalies(
            workflow_data=workflow['data'],
            historical_data=await self.db.get_historical_data(workflow['org_id'])
        )

        return {
            'workflow_id': workflow_id,
            'prediction': prediction,
            'anomalies': anomalies,
            'health_score': self._calculate_health_score(prediction, anomalies)
        }

    def _calculate_health_score(self, prediction, anomalies):
        score = 100
        score -= prediction['stuck_probability']['probability'] * 30
        score -= anomalies['anomalies_detected'] * 15
        return max(0, min(100, score))
```

### Pattern 3: Community Intelligence Integration

```python
# In community_intelligence service
from ai_foundation import RAGPipeline

class CommunitySearchService:
    def __init__(self):
        self.rag = RAGPipeline()

    async def search_community_knowledge(
        self,
        query: str,
        filters: dict = None
    ):
        # Search with optional filters
        results = await self.rag.retrieve(
            query=query,
            filters=filters or {},
            top_k=10,
            enable_reranking=True,
            enable_diversity=True  # Diverse results
        )

        # Format for community display
        formatted_results = []
        for result in results:
            formatted_results.append({
                'content': result['content'],
                'source': result['source'],
                'score': result['score'],
                'metadata': result['metadata']
            })

        return {
            'query': query,
            'results': formatted_results,
            'total_found': len(formatted_results)
        }
```

---

## Production Best Practices

### Best Practice 1: Connection Management

```python
# ❌ BAD: Creating new connections per request
async def handle_request(query):
    rag = RAGPipeline()  # New Qdrant connection!
    results = await rag.retrieve(query)
    return results

# ✅ GOOD: Singleton pattern
class RAGService:
    _instance = None
    _rag = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._rag = RAGPipeline()
        return cls._rag

async def handle_request(query):
    rag = RAGService.get_instance()
    results = await rag.retrieve(query)
    return results
```

### Best Practice 2: Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def robust_llm_query(llm, system_prompt, user_prompt):
    try:
        response = await llm.query(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task_type="content_generation"
        )
        return response
    except Exception as e:
        logger.error(f"LLM query failed: {e}")
        raise  # Will retry

# Usage
try:
    answer = await robust_llm_query(llm, system, user)
except Exception as e:
    # After 3 retries failed
    return "Unable to generate response at this time. Please try again later."
```

### Best Practice 3: Caching

```python
from functools import lru_cache
import hashlib

class CachedRAG:
    def __init__(self):
        self.rag = RAGPipeline()
        self.cache = {}

    def _cache_key(self, query: str, filters: dict) -> str:
        key_data = f"{query}:{json.dumps(filters, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def retrieve_cached(self, query: str, filters: dict = None):
        cache_key = self._cache_key(query, filters or {})

        # Check cache
        if cache_key in self.cache:
            logger.info(f"Cache hit for query: {query[:50]}...")
            return self.cache[cache_key]

        # Retrieve and cache
        results = await self.rag.retrieve(query, filters=filters)
        self.cache[cache_key] = results

        return results
```

### Best Practice 4: Rate Limiting

```python
from aiolimiter import AsyncLimiter

class RateLimitedLLM:
    def __init__(self):
        self.llm = LLMRouter()
        # 50 requests per minute
        self.rate_limiter = AsyncLimiter(max_rate=50, time_period=60)

    async def query(self, system_prompt, user_prompt, task_type="general"):
        async with self.rate_limiter:
            return await self.llm.query(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                task_type=task_type
            )
```

### Best Practice 5: Monitoring

```python
import time
import structlog

logger = structlog.get_logger()

async def monitored_rag_query(rag, query, user_id, tenant_id):
    start_time = time.time()

    try:
        results = await rag.retrieve(query)

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "rag_query_success",
            query=query[:100],
            results_count=len(results),
            duration_ms=duration_ms,
            user_id=user_id,
            tenant_id=tenant_id
        )

        return results

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000

        logger.error(
            "rag_query_failed",
            query=query[:100],
            error=str(e),
            duration_ms=duration_ms,
            user_id=user_id,
            tenant_id=tenant_id
        )

        raise
```

### Best Practice 6: Configuration Management

```python
from pydantic import BaseSettings

class AIFoundationConfig(BaseSettings):
    # LLM
    anthropic_api_key: str
    openai_api_key: str

    # Vector DB
    qdrant_url: str
    qdrant_api_key: str

    # Embeddings
    embedding_provider: str = "voyage"
    voyage_api_key: str | None = None

    # RAG
    rag_chunk_size: int = 512
    rag_top_k: int = 5
    rag_enable_reranking: bool = True

    # LLM
    llm_rate_limit: int = 50  # per minute
    llm_timeout: int = 30  # seconds

    # ML
    ml_model_dir: str = "./models"
    ml_min_samples: int = 50

    class Config:
        env_file = ".env"

# Usage
config = AIFoundationConfig()

rag = RAGPipeline(
    embedding_provider=config.embedding_provider,
    chunk_size=config.rag_chunk_size,
    top_k=config.rag_top_k
)
```

---

## Complete End-to-End Example

```python
"""
Complete example: BCM Q&A System with AI Foundation
"""

import asyncio
from ai_foundation import (
    RAGPipeline,
    LLMRouter,
    ContextBuilder,
    WorkflowPredictor,
    AnomalyDetector
)

class BCMIntelligenceSystem:
    def __init__(self):
        self.rag = RAGPipeline(embedding_provider="voyage", top_k=5)
        self.llm = LLMRouter()
        self.context_builder = ContextBuilder()
        self.predictor = WorkflowPredictor()
        self.anomaly_detector = AnomalyDetector()

    async def initialize(self):
        """Initialize system with knowledge"""
        # Ingest ISO standards
        iso_docs = [
            {
                "text": "ISO 22301 Clause 8.2.2: Business Impact Analysis...",
                "metadata": {"source_type": "iso_standard", "clause": "8.2.2"}
            }
        ]
        await self.rag.ingest_documents(iso_docs, source_type="iso_standard")
        print("✓ Knowledge base initialized")

    async def answer_question(
        self,
        question: str,
        user_context: dict
    ) -> dict:
        """Answer BCM question with RAG + LLM"""

        # 1. Build context
        context = await self.context_builder.build_context(
            domain="bcm",
            tenant_id=user_context['tenant_id'],
            user_id=user_context['user_id'],
            additional_context=user_context
        )

        # 2. Retrieve knowledge
        knowledge = await self.rag.retrieve(
            query=question,
            context=context,
            top_k=3,
            enable_reranking=True
        )

        # 3. Build RAG context
        rag_context = await self.rag.build_context(question, max_context_length=1500)

        # 4. Generate answer
        system_prompt = """You are a BCM expert assistant. Use the knowledge base to answer questions accurately.
        Always cite sources and provide actionable recommendations."""

        user_prompt = f"""Context: {rag_context}

Question: {question}

Provide a detailed answer with recommendations."""

        answer = await self.llm.query(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task_type="content_generation",
            temperature=0.5
        )

        return {
            'question': question,
            'answer': answer,
            'sources': knowledge,
            'context': context
        }

    async def analyze_workflow_health(self, workflow_data: dict) -> dict:
        """Analyze workflow health using ML"""

        # Predict journey
        prediction = await self.predictor.predict_journey(
            org_context=workflow_data['org_context'],
            current_state=workflow_data['current_state'],
            current_progress=workflow_data['progress']
        )

        # Detect anomalies
        anomalies = await self.anomaly_detector.detect_workflow_anomalies(
            workflow_data=workflow_data['metrics']
        )

        # Combine insights
        return {
            'health_score': self._calculate_health_score(prediction, anomalies),
            'prediction': prediction,
            'anomalies': anomalies,
            'recommendations': self._combine_recommendations(prediction, anomalies)
        }

    def _calculate_health_score(self, prediction, anomalies):
        score = 100
        score -= prediction['stuck_probability']['probability'] * 30
        score -= anomalies['anomalies_detected'] * 15
        return max(0, min(100, score))

    def _combine_recommendations(self, prediction, anomalies):
        recs = prediction['recommendations'].copy()
        recs.extend(anomalies['recommendations'])
        return list(set(recs))  # Deduplicate

async def main():
    # Initialize system
    system = BCMIntelligenceSystem()
    await system.initialize()

    # Example 1: Answer question
    user_context = {
        'tenant_id': 'tenant-123',
        'user_id': 'user-456',
        'industry': 'healthcare',
        'org_size': 'large'
    }

    result = await system.answer_question(
        question="How should we prioritize critical business functions in BIA?",
        user_context=user_context
    )

    print("\n=== Q&A Result ===")
    print(f"Q: {result['question']}")
    print(f"\nA: {result['answer']}")
    print(f"\nSources used: {len(result['sources'])}")

    # Example 2: Analyze workflow
    workflow_data = {
        'org_context': {'size': 'large', 'maturity': 4, 'industry': 'healthcare'},
        'current_state': 'bia',
        'progress': {'current_stage_index': 2, 'total_stages': 6},
        'metrics': {'duration_hours': 20}
    }

    health = await system.analyze_workflow_health(workflow_data)

    print("\n=== Workflow Health ===")
    print(f"Health Score: {health['health_score']}/100")
    print(f"Stuck Probability: {health['prediction']['stuck_probability']['probability']:.2%}")
    print(f"Anomalies: {health['anomalies']['anomalies_detected']}")
    print(f"\nRecommendations:")
    for rec in health['recommendations'][:3]:
        print(f"  - {rec}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Next Steps

1. **Read DEEP_TECHNICAL_ANALYSIS.md** - понять критические проблемы
2. **Review examples** - выбрать patterns для вашего use case
3. **Start with simple** - начать с basic RAG + LLM
4. **Add complexity** - добавить ML predictions, learning
5. **Monitor production** - добавить logging, metrics, alerting

**Questions?** Check README.md или MODULE_ANALYSIS.md

**End of Usage Patterns Guide**
