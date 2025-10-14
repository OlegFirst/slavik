# AI Foundation - Module Analysis

## Назначение

AI Foundation - это базовый AI-слой всей платформы, предоставляющий:
- **RAG (Retrieval-Augmented Generation)** - контекстный поиск знаний
- **LLM Integration** - роутинг запросов к AI провайдерам
- **ML Models** - предиктивные модели и обнаружение аномалий
- **Learning Engine** - самообучающаяся система
- **Context Building** - построение контекста для AI

## Архитектурная Роль

```
┌─────────────────────────────────────────┐
│         AI FOUNDATION (Core)            │
│  ┌───────────┐  ┌──────────┐           │
│  │    RAG    │  │   LLM    │           │
│  │ Pipeline  │  │  Router  │           │
│  └─────┬─────┘  └────┬─────┘           │
│        │             │                  │
│  ┌─────┴─────────────┴─────┐           │
│  │   Context Builder       │           │
│  └────────────┬────────────┘           │
│               │                         │
│  ┌────────────┴────────────┐           │
│  │  ML & Learning Engines  │           │
│  └─────────────────────────┘           │
└─────────────────────────────────────────┘
         ▲         ▲         ▲
         │         │         │
    ┌────┴───┐ ┌───┴────┐ ┌─┴────────┐
    │workflow│ │expertise│ │community│
    │  _intl │ │ -center │ │  _intl   │
    └────────┘ └────────┘ └──────────┘
```

**Design Decision**: ai-foundation отделён от workflow_intelligence для:
- Независимого масштабирования
- Переиспользования AI компонентов
- Версионирования AI функционала

## Структура файлов

```
ai-foundation/
├── __init__.py                    # Main exports
├── requirements.txt               # Dependencies
│
├── rag/                          # RAG Pipeline
│   ├── __init__.py
│   ├── pipeline.py               # RAGPipeline, KnowledgeSourceManager
│   ├── embeddings.py             # EmbeddingService
│   ├── retrieval.py              # HybridRetriever
│   ├── reranking.py              # Reranker, DiversityReranker
│   ├── qdrant_client.py          # QdrantVectorStore
│   └── setup_collections.py      # Collection initialization
│
├── llm/                          # LLM Integration
│   ├── __init__.py
│   └── llm_router.py             # LLMRouter (Anthropic, OpenAI)
│
├── ml/                           # Machine Learning
│   ├── __init__.py
│   ├── predictive_models.py      # PredictiveModel
│   ├── training_pipeline.py      # MLTrainer
│   └── anomaly_detection.py      # AnomalyDetector
│
├── learning/                     # Self-Learning
│   ├── __init__.py
│   ├── self_learning_engine.py   # SelfLearningEngine
│   ├── pattern_extractor.py      # PatternExtractor
│   └── rule_generator.py         # RuleGenerator
│
├── context/                      # Context Building
│   ├── __init__.py
│   └── context_builder.py        # ContextBuilder
│
├── learning-knowledge/           # Learning & Knowledge System
│   ├── knowledge/                # ISO standards, case library loader
│   ├── learning/                 # Competency, gamification engines
│   ├── api/                      # REST API routers
│   └── training/                 # Training programs, AI coach
│
├── examples/
│   └── rag_llm_integration.py    # Integration example
│
└── tests/                        # Unit tests
```

## Основные компоненты

### 1. RAG Pipeline (rag/)

**RAGPipeline**
- Полный RAG workflow: ingestion → embedding → retrieval → reranking
- Поддерживает множественные источники знаний
- Hybrid search (vector + keyword)
- Diversity filtering для разнообразия результатов

**KnowledgeSourceManager**
- Загрузка ISO 22301 standards
- Загрузка case library
- Загрузка community annotations
- Загрузка BCI guidelines

**Компоненты:**
- `EmbeddingService` - генерация векторных представлений
- `HybridRetriever` - гибридный поиск
- `Reranker` - переранжирование по релевантности
- `QdrantVectorStore` - векторная база данных

### 2. LLM Router (llm/)

**LLMRouter**
- Автоматический выбор модели по типу задачи
- Поддержка провайдеров:
  - Anthropic Claude (Opus, Sonnet, Haiku)
  - OpenAI GPT (GPT-4, GPT-3.5)
  - Ollama (локальный fallback)

**Task Routing:**
- `strategic_analysis` → Claude Opus
- `content_generation` → Claude Sonnet
- `quick_tasks` → Claude Haiku / GPT-3.5

### 3. ML Models (ml/)

**PredictiveModel**
- Предсказание времени выполнения workflow
- Оценка рисков
- Рекомендации по оптимизации

**AnomalyDetector**
- Обнаружение аномалий в workflow
- Раннее предупреждение о проблемах

**MLTrainer**
- Обучение моделей на исторических данных
- Автоматическая переобучение

### 4. Learning Engine (learning/)

**SelfLearningEngine**
- Автоматическое извлечение паттернов
- Генерация правил из успешных кейсов
- Непрерывное улучшение

**PatternExtractor**
- Извлечение успешных паттернов из workflow
- Кластеризация похожих кейсов

**RuleGenerator**
- Генерация правил валидации
- Генерация best practices

### 5. Context Builder (context/)

**ContextBuilder**
- Агрегация контекста из всех источников
- Построение промптов для LLM
- Приоритизация релевантной информации

## Зависимости

### Внешние (pip пакеты)

```
# LLM Providers
anthropic>=0.25.0
openai>=1.30.0

# Vector DB
qdrant-client>=1.8.0

# Embeddings
sentence-transformers>=2.5.0
voyageai>=0.2.0

# ML & Learning
scikit-learn>=1.4.0
numpy>=1.26.0
pandas>=2.2.0

# Utilities
pydantic>=2.6.0
python-dotenv>=1.0.0
```

### Внутренние зависимости

**FROM ai-foundation:**
- None (это базовый слой)

**TO ai-foundation:**
- `workflow_intelligence` → использует RAG + LLM
- `expertise-center` → использует RAG + LLM + ML
- `community_intelligence` → использует RAG для поиска
- `orchestration/ai-orchestration` → использует LLM Router

## API контракты

### RAGPipeline

```python
# Инициализация
pipeline = RAGPipeline(
    embedding_provider="voyage",
    chunk_size=512,
    top_k=5
)

# Загрузка документов
doc_ids = await pipeline.ingest_documents(
    documents=[
        {"text": "...", "metadata": {...}}
    ],
    source_type="iso_standard"
)

# Поиск
results = await pipeline.retrieve(
    query="How to conduct BIA?",
    top_k=5,
    enable_reranking=True
)

# Построение контекста для LLM
context = await pipeline.build_context(
    query="...",
    max_context_length=2000
)
```

### LLMRouter

```python
# Инициализация
llm = LLMRouter()

# Запрос
response = await llm.query(
    system_prompt="You are BCM expert...",
    user_prompt="How to calculate RTO?",
    task_type="content_generation",
    temperature=0.7
)

# Генерация embeddings
embeddings = await llm.generate_embeddings(
    texts=["text1", "text2"]
)

# Информация о провайдерах
info = llm.get_provider_info()
```

### ML Models

```python
# Predictive Model
model = PredictiveModel()
await model.train(historical_data)
prediction = await model.predict(current_workflow)

# Anomaly Detection
detector = AnomalyDetector()
is_anomaly, score = await detector.detect(workflow_metrics)
```

## Точки интеграции

### 1. Workflow Intelligence Integration

```python
from ai_foundation import RAGPipeline, LLMRouter

# В workflow_intelligence используется для:
# - Контекстные подсказки
# - Автоматические рекомендации
# - Предсказание проблем
```

### 2. Expertise Center Integration

```python
from ai_foundation import RAGPipeline, LLMRouter

# В expertise-center используется для:
# - Knowledge retrieval для specialists
# - LLM-powered анализ
# - Обучение на кейсах
```

### 3. Community Intelligence Integration

```python
from ai_foundation import RAGPipeline

# В community_intelligence используется для:
# - Поиск похожих кейсов
# - Семантический поиск annotations
```

## Конфигурация

### Environment Variables

```bash
# LLM Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Vector DB
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=...

# Embeddings
VOYAGE_API_KEY=...  # Optional

# ML Models
MODEL_CACHE_DIR=./models
```

### Configuration Files

- `requirements.txt` - зависимости
- `.env` - API ключи (не в git)

## Проблемы/TODO

### Критичные (P0)
- [ ] **Vector DB Connection Management** - нужен connection pool для Qdrant
- [ ] **Error Handling** - добавить retry логику для LLM calls
- [ ] **Rate Limiting** - добавить rate limiting для API calls

### Важные (P1)
- [ ] **Caching** - кэширование embeddings и LLM responses
- [ ] **Monitoring** - метрики использования RAG и LLM
- [ ] **Fallback Strategy** - fallback на другие провайдеры при ошибках

### Улучшения (P2)
- [ ] **Multi-modal RAG** - поддержка изображений и таблиц
- [ ] **Adaptive Chunking** - динамический размер chunks
- [ ] **Query Expansion** - расширение запросов
- [ ] **Hybrid Embeddings** - комбинация разных embedding моделей

### Документация (P2)
- [ ] **API Documentation** - автогенерация OpenAPI specs
- [ ] **Usage Examples** - больше примеров интеграции
- [ ] **Performance Guide** - руководство по оптимизации

## Метрики и Мониторинг

### Текущие метрики
- Пока нет (TODO)

### Рекомендуемые метрики
- RAG retrieval latency
- LLM query latency
- Cache hit rate
- Vector DB query performance
- LLM token usage
- Error rates по провайдерам

## Тестирование

### Существующие тесты
- `tests/` - базовые unit tests

### Необходимые тесты
- [ ] Integration tests с реальными LLM
- [ ] RAG pipeline end-to-end tests
- [ ] Performance tests
- [ ] Error handling tests

## Deployment Notes

### Требования
- Python 3.11+
- Qdrant vector database
- API ключи для Anthropic/OpenAI
- ~2GB RAM для ML models

### Scaling Strategy
- RAG pipeline - horizontal scaling (stateless)
- Vector DB - vertical scaling (RAM для индексов)
- LLM calls - rate limiting + queueing

## Ключевые Решения

### Почему отдельный модуль?
- **Переиспользование**: один RAG для всей платформы
- **Версионирование**: AI компоненты могут меняться независимо
- **Тестирование**: легче тестировать AI изолированно
- **Масштабирование**: можно скалировать AI отдельно

### Почему Qdrant?
- Открытый исходный код
- Высокая производительность
- Поддержка hybrid search
- Простая интеграция

### Почему multi-provider LLM?
- Fallback при недоступности провайдера
- Выбор модели по типу задачи
- Оптимизация стоимости (Haiku для простых задач)

## Следующие Шаги

1. **Production Readiness** (P0)
   - Добавить connection pooling
   - Реализовать error handling
   - Добавить rate limiting

2. **Observability** (P1)
   - Метрики производительности
   - Logging
   - Tracing

3. **Optimization** (P2)
   - Caching strategy
   - Query optimization
   - Cost optimization

---

**Версия**: 1.0.0
**Последнее обновление**: 2025-10-07
**Статус**: ✅ Production-ready (с TODO списком)
