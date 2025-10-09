# RAG + LLM Integration Plan

**Для**: Следующая сессия
**Время**: ~1 час
**Статус**: Qdrant подключен ✅, осталось интегрировать

---

## ✅ Что Уже Готово

1. **QdrantVectorStore** создан (`ai-foundation/rag/qdrant_client.py`)
2. **Экспортирован** в `ai-foundation/rag/__init__.py`
3. **Credentials** есть в `.env.example`:
   ```
   QDRANT_URL=https://...
   QDRANT_API_KEY=...
   ```

---

## 📋 Что Осталось (30-40 минут)

### Task 1: Обновить RAGPipeline (15-20 мин)

**Файл**: `ai-foundation/rag/pipeline.py`

**Что делать**:
```python
# Добавить в __init__
from .qdrant_client import QdrantVectorStore

class RAGPipeline:
    def __init__(self):
        self.vector_store = QdrantVectorStore(
            collection_name="bcm_knowledge"
        )
        self.embeddings = EmbeddingGenerator()  # уже есть

    async def search(self, query: str, limit: int = 5):
        # 1. Generate embedding
        query_embedding = await self.embeddings.generate(query)

        # 2. Search in Qdrant
        results = await self.vector_store.search(
            query_vector=query_embedding,
            limit=limit
        )

        return results
```

### Task 2: Создать Collections в Qdrant (10 мин)

**Файл**: `ai-foundation/rag/setup_collections.py` (новый)

```python
"""
Setup Qdrant collections for RAG
"""
from .qdrant_client import QdrantVectorStore

async def setup_collections():
    """Create Qdrant collections."""

    # 1. BCM Knowledge (ISO 22301, BCI guidelines)
    bcm_knowledge = QdrantVectorStore(collection_name="bcm_knowledge")
    await bcm_knowledge.create_collection(
        collection_name="bcm_knowledge",
        vector_size=1536  # OpenAI ada-002
    )

    # 2. Workflow Cases (successful workflows)
    workflow_cases = QdrantVectorStore(collection_name="workflow_cases")
    await workflow_cases.create_collection(
        collection_name="workflow_cases",
        vector_size=1536
    )

    # 3. Documents (organization docs)
    documents = QdrantVectorStore(collection_name="documents")
    await documents.create_collection(
        collection_name="documents",
        vector_size=1536
    )
```

### Task 3: Настроить Embeddings (5-10 мин)

**Файл**: `ai-foundation/rag/embeddings.py`

**Проверить что использует**:
- OpenAI `text-embedding-ada-002` (1536 dim)
- Или Voyage AI (if available)

**Добавить в .env** (если нет):
```bash
# В .env добавить реальный ключ вместо YOUR_OPENAI_KEY_HERE
OPENAI_API_KEY=sk-...
```

---

## 📋 LLM Routing (20-30 минут)

### Task 1: Обновить LLMRouter (20 мин)

**Файл**: `ai-foundation/llm/llm_router.py`

**Что делать**:
```python
"""
LLM Router - routes requests to Claude or OpenAI
"""
import os
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

class LLMRouter:
    def __init__(self):
        self.claude = AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.openai = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    async def route(self, task_type: str, prompt: str, **kwargs):
        """
        Route to appropriate LLM based on task type.

        Task types:
        - strategic_analysis → Claude Opus (best reasoning)
        - code_generation → Claude Sonnet (fast + good)
        - embedding → OpenAI ada-002 (cheap)
        - simple_qa → Claude Haiku (fast)
        """

        if task_type == "strategic_analysis":
            return await self._claude_opus(prompt, **kwargs)
        elif task_type in ["tactical_analysis", "code_generation"]:
            return await self._claude_sonnet(prompt, **kwargs)
        elif task_type == "simple_qa":
            return await self._claude_haiku(prompt, **kwargs)
        else:
            # Default: Claude Sonnet
            return await self._claude_sonnet(prompt, **kwargs)

    async def _claude_opus(self, prompt, **kwargs):
        message = await self.claude.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=kwargs.get("max_tokens", 4096),
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    async def _claude_sonnet(self, prompt, **kwargs):
        message = await self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=kwargs.get("max_tokens", 4096),
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    async def _claude_haiku(self, prompt, **kwargs):
        message = await self.claude.messages.create(
            model="claude-haiku-4-20250312",
            max_tokens=kwargs.get("max_tokens", 2048),
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
```

### Task 2: Добавить в .env реальные ключи (5 мин)

**Файл**: `.env`

```bash
# Заменить заглушки на реальные API keys
OPENAI_API_KEY=sk-...   # твой реальный ключ
ANTHROPIC_API_KEY=sk-ant-...  # твой реальный ключ
```

### Task 3: Обновить exports (5 мин)

**Файл**: `ai-foundation/llm/__init__.py`

```python
from .llm_router import LLMRouter

__all__ = ['LLMRouter']
```

---

## 🧪 Testing (10-15 минут)

### Test RAG:

```python
# test_rag.py
from ai_foundation import RAGPipeline

async def test_rag():
    rag = RAGPipeline()

    # Search
    results = await rag.search("ISO 22301 requirements")
    print(f"Found {len(results)} results")

    for result in results:
        print(f"Score: {result['score']}")
        print(f"Content: {result['payload']}")
```

### Test LLM:

```python
# test_llm.py
from ai_foundation import LLMRouter

async def test_llm():
    llm = LLMRouter()

    # Strategic analysis (Opus)
    response = await llm.route(
        task_type="strategic_analysis",
        prompt="Analyze BIA results for critical processes"
    )
    print(response)

    # Simple QA (Haiku)
    response = await llm.route(
        task_type="simple_qa",
        prompt="What is RTO?"
    )
    print(response)
```

---

## 📊 Success Criteria

- [ ] RAGPipeline использует QdrantVectorStore
- [ ] 3 collections созданы в Qdrant (bcm_knowledge, workflow_cases, documents)
- [ ] Embeddings работают (OpenAI или Voyage)
- [ ] LLMRouter маршрутизирует по типу задачи
- [ ] Claude Opus/Sonnet/Haiku доступны
- [ ] Тесты проходят

---

## 🎯 Integration Points (для других модулей)

### workflow_intelligence:
```python
from ai_foundation import RAGPipeline, LLMRouter

class ContextAdvisor:
    def __init__(self):
        self.rag = RAGPipeline()
        self.llm = LLMRouter()

    async def get_advice(self, workflow_context):
        # 1. Search knowledge
        knowledge = await self.rag.search(
            f"best practices for {workflow_context.domain}"
        )

        # 2. Generate advice
        advice = await self.llm.route(
            task_type="tactical_analysis",
            prompt=f"Context: {knowledge}\nWorkflow: {workflow_context}\nAdvice:"
        )

        return advice
```

### expertise-center:
```python
from ai_foundation import RAGPipeline, LLMRouter

class BaseSpecialist:
    def __init__(self):
        self.rag = RAGPipeline()
        self.llm = LLMRouter()

    async def analyze(self, domain_context):
        # Use RAG + LLM for analysis
        pass
```

---

## ✅ Готово!

Этот план содержит всё для быстрой интеграции RAG + LLM в следующей сессии.

**Время**: 1 час максимум
**Статус**: ПЛАН ГОТОВ
