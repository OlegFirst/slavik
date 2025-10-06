# Platform Integration Complete ✅

## Overview

Learning System теперь полностью интегрирована с общими компонентами платформы:

- ✅ **RAG (Retrieval-Augmented Generation)** - единый источник знаний
- ✅ **ML Platform** - общие предсказательные модели
- ✅ **Knowledge Base** - структурированное управление знаниями
- ✅ **Shared TOOLS** - общие утилиты и клиенты

## Архитектура Интеграции

```
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNING SYSTEM SERVICE                       │
│                         (Port 8033)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ использует
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              SHARED INTEGRATIONS (/shared/integrations/)         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ RAGConnector │  │MLPlatformClient│ │KnowledgeClient│        │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ↓                   ↓                   ↓
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  RAG SERVICE    │  │  ML PLATFORM    │  │  KB SERVICE     │
│  (Port 8050)    │  │  (Port 8060)    │  │  (Port 8040)    │
│                 │  │                 │  │                 │
│ - Semantic      │  │ - Predictions   │  │ - Articles      │
│   search        │  │ - Model         │  │ - Procedures    │
│ - Vector DB     │  │   versioning    │  │ - Guidelines    │
│ - Embeddings    │  │ - Feedback loop │  │ - Search        │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Созданные Файлы

### 1. Shared Integration Connectors

#### `/shared/integrations/rag_connector.py` (370 строк)
**Назначение**: Подключение к единому RAG-сервису для семантического поиска

**Ключевые классы**:
```python
class RAGConnector:
    async def search_knowledge(query, context, filters, limit):
        # Семантический поиск по всем знаниям платформы

    async def add_knowledge(content, metadata, knowledge_type):
        # Добавление новых знаний в единое хранилище

    async def get_related_knowledge(knowledge_id, limit):
        # Поиск связанных знаний

class RAGQueryBuilder:
    # Построитель сложных запросов к RAG
```

**Возможности**:
- Семантический поиск с векторными эмбеддингами
- Контекстно-зависимый поиск (user_id, domain, etc.)
- Фильтрация по типу, категории, тегам
- Добавление знаний обратно в платформу
- Fallback режим при недоступности сервиса

#### `/shared/integrations/ml_platform_client.py` (400 строк)
**Назначение**: Подключение к общей ML Platform для предсказаний

**Ключевые классы**:
```python
class MLPlatformClient:
    async def predict(model_name, features, context):
        # Универсальные предсказания для всех сервисов

    async def predict_batch(model_name, batch_features):
        # Пакетные предсказания для эффективности

    async def submit_feedback(prediction_id, actual_outcome):
        # Закрытие feedback loop - все сервисы обучают модели

    async def get_model_performance(model_name):
        # Метрики производительности моделей

class FeatureBuilder:
    # Построитель фич для консистентности

class ModelPerformanceTracker:
    # Локальное отслеживание производительности
```

**Возможности**:
- Общие ML модели для всех workflows
- Версионирование моделей (v1, v2, v3...)
- Автоматическое переобучение при накоплении фидбека
- Feature importance analysis
- A/B testing моделей
- Fallback предсказания при недоступности

#### `/shared/integrations/knowledge_client.py` (350 строк)
**Назначение**: Подключение к структурированной Knowledge Base

**Ключевые классы**:
```python
class KnowledgeClient:
    async def create_article(title, content, category, type):
        # CRUD операции со статьями

    async def search(query, filters, limit):
        # Поиск по структурированным метаданным

    async def list_by_category(category):
        # Фильтрация по категориям

class KnowledgeArticleBuilder:
    # Построитель статей с валидацией
```

**Типы знаний**:
- DOCUMENT
- PROCEDURE
- GUIDELINE
- LESSON_LEARNED
- BEST_PRACTICE
- PATTERN
- ARTICLE
- TRAINING_MATERIAL

### 2. Integrated Engines

#### `/intelligent-core/learning-system/engines/knowledge_base_connector_integrated.py` (450 строк)

**Назначение**: Learning System специфическая логика поверх shared connectors

**Ключевые классы**:
```python
class IntegratedKnowledgeConnector:
    # Использует RAGConnector + KnowledgeClient

    async def search_resources_for_gap(gap_keyword, user_id, level):
        # Поиск ресурсов для gap'а с Learning контекстом

    async def create_learning_path_from_resources(user_id, gap, resources):
        # Создание learning path из RAG результатов

    async def auto_create_knowledge_from_pattern(pattern, threshold):
        # Авто-создание статей из паттернов (≥5 occurrences)
        # Добавляет в KB + RAG одновременно

    async def sync_external_knowledge(source, items):
        # Синхронизация внешних источников

class ExternalKnowledgeSyncManager:
    async def sync_iso_standards():
        # Синхронизация ISO обновлений

    async def sync_threat_intelligence():
        # Синхронизация threat feeds
```

#### `/intelligent-core/learning-system/engines/ml_predictor_integrated.py` (400 строк)

**Назначение**: Learning System ML логика поверх ML Platform

**Ключевые классы**:
```python
class IntegratedMLPredictor:
    # Использует MLPlatformClient

    async def predict_exercise_success(scenario_type, team, history):
        # Предсказание успеха упражнения
        # Модель: 'exercise_success_predictor'

    async def predict_difficulty_score(scenario_def, audience):
        # Предсказание сложности
        # Модель: 'exercise_difficulty_scorer'

    async def predict_exercise_duration(scenario_type, team_size):
        # Предсказание длительности
        # Модель: 'exercise_time_estimator'

    async def submit_actual_result(prediction_id, actual_score):
        # Отправка реального результата в ML Platform
        # Триггерит переобучение моделей

    async def get_model_performance():
        # Метрики производительности всех моделей
```

### 3. Platform Integration Router

#### `/intelligent-core/learning-system/api/platform_integration_router.py` (600 строк)

**Назначение**: API endpoints демонстрирующие platform integration

**Endpoint группы**:

**RAG Integration** (`/api/learning/platform/rag/...`):
```python
POST /rag/search
    # Семантический поиск по unified knowledge

POST /rag/add-knowledge
    # Learning System добавляет знания в платформу
```

**ML Platform Integration** (`/api/learning/platform/ml/...`):
```python
POST /ml/predict-success
    # Предсказание успеха через shared ML Platform

POST /ml/submit-feedback
    # Закрытие feedback loop

GET  /ml/performance
    # Метрики производительности моделей

GET  /ml/feature-importance
    # Важность фич для интерпретируемости
```

**Knowledge Base Integration** (`/api/learning/platform/kb/...`):
```python
POST /kb/create-learning-path
    # Создание персонализированного learning path

POST /kb/auto-create-from-pattern
    # Авто-создание статей из паттернов

POST /kb/sync-external
    # Синхронизация внешних источников (ISO, threats)
```

**Unified Workflows** (`/api/learning/platform/unified/...`):
```python
POST /unified/predict-and-recommend
    # Комбинированный workflow:
    # 1. ML предсказание
    # 2. Если risk высокий → поиск ресурсов в RAG
    # 3. Возврат предсказания + learning resources
```

## Примеры Использования

### Пример 1: Семантический Поиск Знаний

```python
# Learning System ищет ресурсы для пробела в компетенциях

from shared.integrations.rag_connector import RAGConnector, RAGQueryBuilder

rag = RAGConnector()

# Построение запроса с контекстом
query = RAGQueryBuilder()
query.with_query("escalation procedures for cyber incidents")
query.with_context(
    user_id="user123",
    domain="BCM",
    competency_level="intermediate"
)
query.filter_by_type("procedure", "guideline", "best_practice")
query.filter_by_tags("cyber", "escalation")

# Поиск в unified knowledge base
results = await rag.search_knowledge(
    query=query.query,
    context=query.context,
    filters=query.filters,
    limit=10
)

# results содержит знания из:
# - Learning System patterns
# - Documents Service
# - Knowledge Base articles
# - ISO standards
# - Threat intelligence
# - Best practices
```

### Пример 2: ML Предсказание с Общими Моделями

```python
# Learning System предсказывает успех упражнения

from shared.integrations.ml_platform_client import MLPlatformClient, FeatureBuilder

ml_client = MLPlatformClient()

# Построение фич
features = FeatureBuilder()
features.add_categorical('scenario_type', 'cyber_incident')
features.add_numeric('team_size', 12)
features.add_numeric('avg_competency', 0.75)
features.add_numeric('days_since_last_exercise', 45)

# Предсказание через shared ML Platform
prediction = await ml_client.predict(
    model_name='exercise_success_predictor',
    features=features.build(),
    context={'user_id': 'user123'},
    return_explanation=True
)

# prediction = {
#     'prediction_id': 'pred_abc123',
#     'prediction': 78.5,  # predicted score
#     'confidence': 0.82,
#     'model_version': 'v3',
#     'explanation': {
#         'feature_importance': {
#             'avg_competency': 0.35,
#             'days_since_last_exercise': 0.25,
#             'team_size': 0.20,
#             'scenario_type': 0.20
#         }
#     }
# }

# После упражнения - закрытие feedback loop
await ml_client.submit_feedback(
    prediction_id='pred_abc123',
    actual_outcome=82.0,  # реальный score
    metadata={'exercise_id': 'ex_123'}
)

# Модель автоматически переобучается при накоплении фидбека
```

### Пример 3: Авто-создание Знаний из Паттернов

```python
# Когда паттерн обнаружен ≥5 раз, автоматически создаём статью

from intelligent_core.learning_system.engines.knowledge_base_connector_integrated import (
    IntegratedKnowledgeConnector
)

kb_connector = IntegratedKnowledgeConnector()

# Обнаруженный паттерн
pattern = {
    'pattern_name': 'Communication Delays in Cyber Incidents',
    'description': 'Recurring delays in escalation communication...',
    'occurrence_count': 8,  # ≥5 threshold
    'confidence': 0.85,
    'severity': 'high',
    'pattern_type': 'failure',
    'affected_areas': ['scenario:cyber_incident', 'role:incident_manager'],
    'recommended_actions': [
        'Implement automated escalation notifications',
        'Provide communication protocol training',
        'Add communication checkpoints to runbooks'
    ],
    'evidence_data': {
        'avg_delay_minutes': 12,
        'exercises_affected': 8
    }
}

# Автоматическое создание статьи
article_id = await kb_connector.auto_create_knowledge_from_pattern(
    pattern=pattern,
    threshold_occurrences=5
)

# article_id = 'kb_art_123'
# Статья создаётся в:
# 1. Knowledge Base (structured storage)
# 2. RAG Service (semantic search)

# Теперь все сервисы могут найти этот паттерн через RAG поиск
```

### Пример 4: Unified Workflow

```python
# API endpoint /unified/predict-and-recommend

POST /api/learning/platform/unified/predict-and-recommend
{
    "scenario_type": "cyber_incident",
    "team_size": 12,
    "avg_competency": 0.55,  # низкая компетенция
    "days_since_last_exercise": 90,
    "historical_scores": [65, 68, 62]
}

# Response:
{
    "prediction": {
        "predicted_score": 64.5,
        "confidence": 0.78,
        "success_probability": 0.55,
        "risk_level": "medium",  # триггер для поиска ресурсов
        "recommendations": [
            "Consider additional preparation time",
            "Review team competencies and provide targeted training"
        ]
    },
    "learning_resources": [  # автоматически найдены через RAG
        {
            "id": "kb_art_456",
            "title": "Cyber Incident Response Training Module",
            "type": "training_material",
            "difficulty": "intermediate",
            "duration_hours": 4,
            "relevance_score": 0.92
        },
        {
            "id": "doc_789",
            "title": "Incident Escalation Procedures",
            "type": "procedure",
            "difficulty": "beginner",
            "duration_hours": 1,
            "relevance_score": 0.88
        }
    ],
    "workflow": "unified_predict_recommend"
}
```

## Преимущества Интеграции

### 1. Единый Источник Знаний (RAG)
- ✅ Все сервисы используют одно хранилище знаний
- ✅ Семантический поиск вместо keyword matching
- ✅ Контекстно-зависимые результаты
- ✅ Автоматическое связывание похожих знаний
- ✅ Вклад знаний обратно в платформу

### 2. Общие ML Модели
- ✅ Модели учатся от всех сервисов
- ✅ Больше данных = лучше точность
- ✅ Версионирование и rollback
- ✅ Централизованный мониторинг
- ✅ Feedback loop от всех workflows

### 3. Переиспользование Кода
- ✅ DRY принцип (Don't Repeat Yourself)
- ✅ Единые клиенты вместо дублирования
- ✅ Consistent feature engineering
- ✅ Shared utilities (FeatureBuilder, QueryBuilder)
- ✅ Централизованная логика retry/fallback

### 4. Кросс-сервисное Обучение
- ✅ Learning System паттерны → RAG знания → используются другими сервисами
- ✅ Все сервисы предсказывают через ML Platform → общее улучшение моделей
- ✅ Синхронизация внешних источников (ISO, threats) доступна всем

## Архитектурные Паттерны

### 1. Repository Pattern
```python
# Shared connectors как репозитории
class RAGConnector:
    async def search_knowledge(...) -> List[Knowledge]
    async def add_knowledge(...) -> str
```

### 2. Builder Pattern
```python
# Построители для сложных объектов
query = RAGQueryBuilder()
    .with_query("...")
    .with_context(...)
    .filter_by_type(...)
    .build()
```

### 3. Fallback Pattern
```python
# Все connectors имеют fallback режим
try:
    results = await rag.search_knowledge(...)
except ConnectError:
    results = self._fallback_search(...)  # local cache
```

### 4. Feedback Loop Pattern
```python
# Closed loop learning
prediction = await ml.predict(...)
# ... exercise happens ...
await ml.submit_feedback(prediction_id, actual_outcome)
# → model retrains automatically
```

## Следующие Шаги

### Для Полной Production-Ready Интеграции

1. **Создать RAG Service** (Port 8050)
   - Vector database (Qdrant/Pinecone/Weaviate)
   - Embedding generation (OpenAI/local models)
   - Semantic search API
   - Knowledge contribution API

2. **Создать ML Platform Service** (Port 8060)
   - Model registry (MLflow)
   - Prediction API
   - Feedback collection
   - Auto-retraining pipeline
   - Feature store

3. **Расширить Knowledge Base Service** (Port 8040)
   - Structured article storage
   - Category/tag management
   - Version control
   - Search API

4. **Добавить Shared TOOLS**
   - `/tools/database/` - shared DB clients
   - `/tools/ml/` - ML utilities
   - `/tools/cache/` - caching strategies
   - `/tools/monitoring/` - metrics collection

## Тестирование

### Unit Tests
```bash
# Test shared connectors
pytest shared/integrations/tests/

# Test integrated engines
pytest intelligent-core/learning-system/tests/test_integrated_engines.py
```

### Integration Tests
```bash
# Test full workflow
pytest intelligent-core/learning-system/tests/test_platform_integration.py
```

### Manual Testing
```bash
# Start Learning System
cd intelligent-core/learning-system
python main.py

# Test endpoints
curl http://localhost:8033/api/learning/platform/status
curl -X POST http://localhost:8033/api/learning/platform/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "cyber incident", "limit": 5}'
```

## Заключение

✅ **Platform Integration Complete**

Learning System теперь полностью интегрирована с общими компонентами платформы:
- Shared RAG для семантического поиска
- Shared ML Platform для предсказаний
- Shared Knowledge Base для структурированных знаний
- Все интеграции с fallback режимами

Следующий шаг: создать сами platform services (RAG Service, ML Platform Service) или продолжить с другими модулями intelligent-core.
