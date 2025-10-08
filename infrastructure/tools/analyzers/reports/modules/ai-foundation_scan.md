# Module Scan Report: ai-foundation

**Дата сканирования:** 2025-10-06 21:10
**Путь:** `intelligent-core/ai-foundation`

---

## 📊 Метрики

| Метрика | Значение |
|---------|----------|
| **LOC** | 19908 |
| **Python файлов** | 75 |
| **Классов** | 110 |
| **Функций** | 23 |
| **API Endpoints** | 109 |
| **Зависимостей** | 133 |

---

## 🔗 Зависимости (133)


### ai_foundation
- `ai_foundation`
- `ai_foundation/workflow_intelligence_adapter`

### ai_services
- `ai_services/ml`
- `ai_services/predictive_models`

### aiohttp
- `aiohttp`

### analytics
- `analytics`

### anomaly_detection
- `anomaly_detection`

### api.main
- `api.main`

### article
- `article`

### asyncio
- `asyncio`

### bs4
- `bs4`

### case_loader
- `case_loader`

### collections
- `collections`

### context.context_builder
- `context.context_builder`

### context_builder
- `context_builder`

### creators.article_creator
- `creators.article_creator`

### creators.lesson_creator
- `creators.lesson_creator`

### database
- `database`
- `database/postgresql`
- `database/vector-db`

### database.base
- `database.base`

### dataclasses
- `dataclasses`

### datetime
- `datetime`

### embeddings
- `embeddings`

### engines.competency_tracker
- `engines.competency_tracker`

### engines.gamification_engine
- `engines.gamification_engine`

### engines.knowledge_base_connector
- `engines.knowledge_base_connector`

### engines.knowledge_integrator
- `engines.knowledge_integrator`

### engines.learning_needs_collector
- `engines.learning_needs_collector`

### engines.ml_predictor
- `engines.ml_predictor`

### engines.pattern_detector
- `engines.pattern_detector`

### engines.process_gap_analyzer
- `engines.process_gap_analyzer`

### engines.self_learning_engine
- `engines.self_learning_engine`

### enum
- `enum`

### external
- `external/anthropic`

### fastapi
- `fastapi`

### fastapi.middleware.cors
- `fastapi.middleware.cors`

### fastapi.responses
- `fastapi.responses`

### feedparser
- `feedparser`

### functools
- `functools`

### hashlib
- `hashlib`

### httpx
- `httpx`

### indexer
- `indexer`

### indexer.vector_indexer
- `indexer.vector_indexer`

### integrations
- `integrations`

### integrations.knowledge_client
- `integrations.knowledge_client`

### integrations.ml_platform_client
- `integrations.ml_platform_client`

### integrations.rag_connector
- `integrations.rag_connector`

### json
- `json`

### knowledge.indexer
- `knowledge.indexer`

### knowledge.loader
- `knowledge.loader`

### knowledge.updater
- `knowledge.updater`

### knowledge_base_connector_integrated
- `knowledge_base_connector_integrated`

### knowledge_system.loader.case_loader
- `knowledge_system.loader.case_loader`

### knowledge_system.loader.standards_loader
- `knowledge_system.loader.standards_loader`

### learning.analytics_router
- `learning.analytics_router`

### learning.competency_router
- `learning.competency_router`

### learning.engines
- `learning.engines`

### learning.gamification_router
- `learning.gamification_router`

### learning.knowledge_router
- `learning.knowledge_router`

### learning.learning_router
- `learning.learning_router`

### learning.ml_router
- `learning.ml_router`

### learning.pattern_extractor
- `learning.pattern_extractor`

### learning.pattern_router
- `learning.pattern_router`

### learning.platform_integration_router
- `learning.platform_integration_router`

### learning.process_gap_router
- `learning.process_gap_router`

### learning.recommendation_router
- `learning.recommendation_router`

### learning.rule_generator
- `learning.rule_generator`

### learning.self_learning_engine
- `learning.self_learning_engine`

### learning.self_learning_router
- `learning.self_learning_router`

### learning_models
- `learning_models`

### llm.llm_router
- `llm.llm_router`

### loader
- `loader`

### loader.case_loader
- `loader.case_loader`

### loader.standards_loader
- `loader.standards_loader`

### logging
- `logging`

### main
- `main`

### managers.cache_manager
- `managers.cache_manager`

### managers.db_manager
- `managers.db_manager`

### metrics
- `metrics`

### ml.anomaly_detection
- `ml.anomaly_detection`

### ml.training_pipeline
- `ml.training_pipeline`

### ml_predictor_integrated
- `ml_predictor_integrated`

### models.database
- `models.database`

### models.domain
- `models.domain`

### numpy
- `numpy`

### openai
- `openai`

### os
- `os`

### pathlib
- `pathlib`

### pattern_detector
- `pattern_detector`

### pattern_extractor
- `pattern_extractor`

### pickle
- `pickle`

### pipeline
- `pipeline`

### prometheus_client
- `prometheus_client`

### pydantic
- `pydantic`

### pytest
- `pytest`

### rag.embeddings
- `rag.embeddings`

### rag.pipeline
- `rag.pipeline`

### rag.reranking
- `rag.reranking`

### rag.retrieval
- `rag.retrieval`

### rag.setup_collections
- `rag.setup_collections`

### random
- `random`

### re
- `re`

### repositories.gamification_repository
- `repositories.gamification_repository`

### repositories.training_repository
- `repositories.training_repository`

### reranking
- `reranking`

### retrieval
- `retrieval`

### rule_generator
- `rule_generator`

### runtime
- `runtime/eventbus`

### self_learning_engine
- `self_learning_engine`

### sentence_transformers
- `sentence_transformers`

### sklearn.ensemble
- `sklearn.ensemble`

### sklearn.feature_extraction.text
- `sklearn.feature_extraction.text`

### sklearn.metrics
- `sklearn.metrics`

### sklearn.model_selection
- `sklearn.model_selection`

### standards_loader
- `standards_loader`

### standards_monitor
- `standards_monitor`

### statistics
- `statistics`

### structlog
- `structlog`

### synthesis.virtuous_cycle
- `synthesis.virtuous_cycle`

### sys
- `sys`

### time
- `time`

### training_pipeline
- `training_pipeline`

### typing
- `typing`

### updater
- `updater`

### updater.standards_monitor
- `updater.standards_monitor`

### uuid
- `uuid`

### uvicorn
- `uvicorn`

### vector_indexer
- `vector_indexer`

### voyageai
- `voyageai`

### workflows.gamification_workflow
- `workflows.gamification_workflow`

### workflows.training_workflow
- `workflows.training_workflow`

### yaml
- `yaml`

---

## 🌐 API Endpoints (109)

- **GET** `/...` (файл: `database.py`)
- **GET** `/health` (файл: `main.py`)
- **GET** `/` (файл: `main.py`)
- **GET** `/standards` (файл: `main.py`)
- **GET** `/standards/{standard_id:path}` (файл: `main.py`)
- **GET** `/standards/{standard_id:path}/metadata` (файл: `main.py`)
- **GET** `/cases` (файл: `main.py`)
- **GET** `/cases/{case_id}` (файл: `main.py`)
- **POST** `/cases/search` (файл: `main.py`)
- **POST** `/api/cross-learning/virtuous-cycle/workflow` (файл: `main.py`)

---

## 💻 Классы (110)

- **LearningNeedsCollector** (23 методов) - `learning_needs_collector.py`
- **SelfLearningEngine** (13 методов) - `self_learning_engine.py`
- **GamificationEngine** (10 методов) - `gamification_engine.py`
- **IntegratedMLPredictor** (9 методов) - `ml_predictor_integrated.py`
- **AILearningCoach** (9 методов) - `ai_coach.py`
- **WorkflowPredictor** (9 методов) - `predictive_models.py`
- **ProcessGapAnalyzer** (8 методов) - `process_gap_analyzer.py`
- **PatternDetector** (8 методов) - `pattern_detector.py`
- **SelfLearningEngine** (7 методов) - `self_learning_engine.py`
- **ExerciseSuccessPredictor** (7 методов) - `ml_predictor.py`

---

## 📄 README

**Файл:** `README.md`
**Размер:** 3103 символов (138 строк)

**Превью:**
```
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
from ai_
```

---

## ⚙️ Конфигурация

- `requirements.txt` → `intelligent-core/ai-foundation/requirements.txt`

---

## 📂 Структура

**Всего файлов:** 88
**Директорий:** 26
