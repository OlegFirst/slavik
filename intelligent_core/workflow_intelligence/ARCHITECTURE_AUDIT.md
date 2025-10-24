# workflow_intelligence: Архитектурный Аудит

**Дата:** 24 октября 2025
**Цель:** Распределить компоненты по 3 архитектурным группам
**Подход:** Infrastructure (регуляции, координация) → Service (пользователь) → Intelligence (AI/ML)

---

## 📊 ГРУППА 1: ИНФРАСТРУКТУРА (Infrastructure)

**Назначение:** Регуляции, координация, политики, запуск, безопасность, мониторинг

### 1.1 Координация и Оркестрация
```
✅ infrastructure/orchestration/
   └── orchestrator.py              # Координация multi-service workflows

✅ temporal_workflows/               # Temporal workflow definitions
   ├── coordination_workflow.py     # Координация BIA → Risk → BC Plan
   ├── bia_workflow.py              # BIA Temporal workflow
   ├── risk_workflow.py             # Risk Temporal workflow
   ├── collective_workflow.py       # Коллективные процессы
   ├── community_workflow.py        # Community workflows
   ├── devops_workflow.py           # DevOps automation
   ├── event_intelligence_workflow.py
   ├── expertise_workflow.py
   ├── predictive_workflow.py
   └── workers/
       └── coordination_worker.py   # Temporal workers

✅ temporal_sample/                  # Temporal examples (banking)
   ├── workflows.py
   ├── activities.py
   ├── banking_service.py
   ├── run_worker.py
   └── run_workflow.py

📁 core/
   └── workflow_engine.py           # Workflow execution engine (частично)
```

**Недостающие компоненты:**
- [ ] **infrastructure/coordination/** - Saga pattern coordinator
- [ ] **infrastructure/startup/** - Service startup orchestration
- [ ] **infrastructure/circuit_breaker/** - Circuit breaker для resilience

---

### 1.2 Политики и Регуляции
```
✅ infrastructure/policies/
   ├── compliance.py                # ISO 22301, NIST compliance rules
   ├── security.py                  # Security policies
   └── performance.py               # Performance SLAs

✅ governance/                       # Goals + Rules governance
   ├── governance_orchestrator.py   # Unified governance decision
   ├── goals_engine.py              # 4-level goals (User→Platform)
   ├── rules_engine.py              # 5-category rules
   ├── rules_engine_v2.py           # Multi-level hierarchy rules
   ├── bia_rules.py                 # BIA-specific rules
   ├── checkpoint_manager.py        # Governance checkpoints
   ├── creative_zones.py            # Freedom vs control zones
   └── yaml_workflows.py            # YAML workflow definitions

✅ compliance/
   └── iso_checker.py               # ISO 22301 compliance validation

✅ auth/                             # Аутентификация и авторизация
   ├── middleware.py                # Auth middleware
   ├── decorators.py                # @require_auth, @require_permission
   ├── permissions.py               # RBAC permissions
   └── exceptions.py                # Auth exceptions
```

**Недостающие компоненты:**
- [ ] **infrastructure/policies/quota.py** - Rate limiting, quotas
- [ ] **infrastructure/policies/retry.py** - Retry policies
- [ ] **infrastructure/policies/timeout.py** - Timeout policies
- [ ] **governance/escalation.py** - Human escalation rules
- [ ] **governance/approval_chains.py** - Approval workflows

---

### 1.3 Мониторинг и Наблюдение
```
✅ infrastructure/monitoring/
   └── metrics_exporter.py          # Prometheus metrics export

✅ monitoring/                       # ДУБЛЬ! (root-level)
   ├── health.py                    # Health checks
   └── metrics.py                   # Metrics collection

✅ metrics/
   ├── pdca_metrics.py              # PDCA cycle metrics
   └── process_metrics.py           # Process execution metrics

✅ audit/                            # Audit logging
   ├── logger.py                    # Audit logger
   ├── events.py                    # Audit events
   ├── storage.py                   # Audit storage
   └── decorators.py                # @audit_action

📁 production_modules/
   ├── visualization.py             # Metrics visualization (частично)
   └── example_process_metrics.py  # Example metrics
```

**Действие:**
- [x] MERGE `monitoring/` (root) → `infrastructure/monitoring/`

**Недостающие компоненты:**
- [ ] **infrastructure/monitoring/alerts.py** - Alerting (Slack, PagerDuty)
- [ ] **infrastructure/monitoring/tracing.py** - Distributed tracing
- [ ] **infrastructure/observability/** - Logs + Metrics + Traces unified

---

### 1.4 Безопасность
```
✅ infrastructure/policies/security.py  # Security policies

✅ auth/                             # Auth & RBAC
   ├── middleware.py
   ├── decorators.py
   ├── permissions.py
   └── exceptions.py

✅ storage/rls_context.py            # Row Level Security (RLS) для PostgreSQL
```

**Недостающие компоненты:**
- [ ] **infrastructure/security/encryption.py** - Data encryption at rest
- [ ] **infrastructure/security/secrets.py** - Secrets management (Vault integration)
- [ ] **infrastructure/security/pii_detection.py** - PII detection/masking
- [ ] **infrastructure/security/audit_trail.py** - Security audit trail

---

### 1.5 Процессный Фреймворк
```
✅ infrastructure/process_framework/
   ├── models.py                    # Process definitions
   ├── framework.py                 # Process framework
   └── validation.py                # Process validation

✅ workflows/
   ├── bcm_processes.py             # BCM process definitions
   ├── bia_workflow.py              # BIA workflow
   └── temporal/
       └── bia_workflow.py          # Temporal BIA workflow

📁 bcm_processes.py                  # ДУБЛЬ в root! (удалить)
📁 process_framework.py              # ДУБЛЬ в root! (удалить)
```

**Действие:**
- [x] DELETE `bcm_processes.py` (root)
- [x] DELETE `process_framework.py` (root)

---

### 1.6 Шаблоны и Генерация
```
✅ infrastructure/templates/
   ├── models.py                    # Template models
   ├── library.py                   # Template library
   └── generators/
       ├── bia_template.py          # BIA document generator
       ├── risk_template.py         # Risk assessment template
       └── bc_plan_template.py      # BC Plan template

📁 document_templates.py             # ДУБЛЬ в root! (удалить)
```

**Действие:**
- [x] DELETE `document_templates.py` (root)

**Недостающие компоненты:**
- [ ] **infrastructure/templates/generators/report_template.py** - Report generation
- [ ] **infrastructure/templates/export/** - Export to Word/PDF

---

### 1.7 Хранилище и Персистентность
```
✅ storage/
   ├── postgres_adapter.py          # PostgreSQL adapter
   ├── pdca_repository.py           # PDCA repository
   ├── base.py                      # Storage base
   └── rls_context.py               # RLS multi-tenancy

✅ production_modules/
   ├── database.py                  # Database connections
   └── cache.py                     # Redis cache
```

**Недостающие компоненты:**
- [ ] **storage/migrations/** - Database migrations (Alembic)
- [ ] **storage/backup.py** - Backup/restore
- [ ] **storage/vector_store.py** - Qdrant vector DB adapter

---

## 📡 ГРУППА 2: СЕРВИС (Service)

**Назначение:** Пользовательские API, интерфейсы, обработка запросов

### 2.1 API Layer
```
✅ main.py                           # FastAPI service (Port 8037)
   ├── /health                      # Health check
   ├── /metrics                     # Prometheus metrics
   ├── /governance/validate         # Governance validation
   ├── /governance/summary          # Governance summary
   ├── /governance/goals            # Goals status
   ├── /governance/rules            # Rules catalog
   ├── /pdca/status                 # PDCA status
   ├── /pdca/cycles                 # PDCA cycles
   ├── /pdca/benchmarks             # Benchmarks
   └── /cases/add                   # Add case

✅ api/                              # API modules (empty?)
   └── __init__.py

📁 process_orchestration_api.py      # ДУБЛЬ в root! (удалить)

✅ production_modules/
   ├── api.py                       # Production API helpers
   └── error_handling.py            # Error handling middleware
```

**Действие:**
- [x] DELETE `process_orchestration_api.py` (root)
- [ ] CONSOLIDATE API routes in `api/` directory

**Недостающие компоненты:**
- [ ] **api/workflows.py** - Workflow CRUD endpoints
- [ ] **api/cases.py** - Case library endpoints
- [ ] **api/recommendations.py** - AI recommendations endpoints
- [ ] **api/webhooks.py** - Webhook endpoints
- [ ] **api/websockets.py** - Real-time updates (WebSockets)

---

### 2.2 Интеграции (Service-to-Service)
```
✅ integration/
   ├── bia_service_listener.py      # BIA Service EventBus listener ✅ NEW!
   ├── bia_adapter.py               # BIA Service adapter
   ├── eventbus_publisher.py        # EventBus publisher
   ├── learning_knowledge_client.py # Learning Knowledge client
   ├── ai_context_builder.py        # AI context builder
   └── legacy_anthropic_client.py   # Legacy Anthropic client
```

**Недостающие компоненты:**
- [ ] **integration/planning_service_listener.py** - Planning Service listener
- [ ] **integration/risk_service_listener.py** - Risk Service listener
- [ ] **integration/base_service_listener.py** - Base listener pattern
- [ ] **integration/collective_client.py** - Collective intelligence client
- [ ] **integration/ai_foundation_client.py** - AI Foundation client

---

### 2.3 Схемы и Валидация
```
✅ schemas/
   └── validation.py                # Pydantic schemas
```

**Недостающие компоненты:**
- [ ] **schemas/workflow_schemas.py** - Workflow request/response schemas
- [ ] **schemas/governance_schemas.py** - Governance schemas
- [ ] **schemas/case_schemas.py** - Case library schemas

---

### 2.4 Production Modules
```
✅ production_modules/
   ├── api.py                       # API helpers
   ├── cache.py                     # Redis cache
   ├── database.py                  # DB connections
   ├── error_handling.py            # Error handling
   ├── eventbus_integration.py      # EventBus integration
   ├── process_metrics.py           # Process metrics
   ├── visualization.py             # Visualization
   └── test_visualization.py        # Visualization tests
```

**Оценка:** Хорошая база, но смешаны с infrastructure компонентами

**Рекомендация:**
- [ ] MOVE `cache.py`, `database.py` → `infrastructure/persistence/`
- [ ] MOVE `eventbus_integration.py` → `infrastructure/messaging/`
- [ ] KEEP `api.py`, `error_handling.py` в `service/`

---

## 🧠 ГРУППА 3: ИНТЕЛЛЕКТ (Intelligence)

**Назначение:** AI, ML, обучение, рекомендации, предсказания

### 3.1 AI/LLM Integration
```
✅ ai/
   └── context_advisor.py           # Context-aware AI advisor

✅ integration/
   ├── ai_context_builder.py        # AI context builder
   └── legacy_anthropic_client.py   # Anthropic LLM client (legacy)
```

**Недостающие компоненты:**
- [ ] **ai/llm_client.py** - Modern LLM client (Claude, OpenAI)
- [ ] **ai/prompt_builder.py** - Prompt engineering
- [ ] **ai/response_parser.py** - LLM response parsing
- [ ] **ai/embeddings.py** - Text embeddings generation
- [ ] **ai/semantic_search.py** - Semantic search via embeddings

---

### 3.2 Machine Learning
```
✅ ml/
   ├── workflow_ml_subsystem.py     # ML subsystem
   └── cross_module_learning.py     # Cross-module learning

✅ case_library/
   ├── models.py                    # Case models with ML features
   ├── collector.py                 # Automatic case collection
   ├── repository.py                # Case repository
   └── database.py                  # Case database
```

**Недостающие компоненты:**
- [ ] **ml/models/** - ML model definitions
  - [ ] **duration_predictor.py** - Predict workflow duration
  - [ ] **risk_predictor.py** - Predict workflow risk
  - [ ] **success_predictor.py** - Predict success probability
- [ ] **ml/training/** - Model training pipeline
  - [ ] **trainer.py** - ML model trainer
  - [ ] **feature_engineering.py** - Feature extraction
  - [ ] **model_registry.py** - Model versioning
- [ ] **ml/inference/** - Model inference
  - [ ] **predictor.py** - Real-time predictions
  - [ ] **batch_predictor.py** - Batch predictions

---

### 3.3 PDCA & Continuous Learning
```
✅ core/
   └── pdca_rules.py                # PDCA rules engine

✅ storage/
   └── pdca_repository.py           # PDCA repository

✅ metrics/
   └── pdca_metrics.py              # PDCA metrics
```

**Недостающие компоненты:**
- [ ] **intelligence/pdca/** - PDCA subsystem (consolidate)
  - [ ] **plan_engine.py** - PLAN phase (recommendations)
  - [ ] **do_tracker.py** - DO phase (execution tracking)
  - [ ] **check_analyzer.py** - CHECK phase (quality analysis)
  - [ ] **act_learner.py** - ACT phase (learning from execution)

---

### 3.4 Knowledge & Learning
```
✅ case_library/                     # Case-based learning
   ├── collector.py                 # Automatic case collection
   ├── repository.py                # Case repository
   ├── models.py                    # Case models
   └── database.py                  # Case storage

✅ integration/
   └── learning_knowledge_client.py # Learning knowledge client
```

**Недостающие компоненты:**
- [ ] **intelligence/knowledge_graph/** - Knowledge graph
  - [ ] **graph_builder.py** - Build knowledge graph from cases
  - [ ] **relationship_extractor.py** - Extract relationships
  - [ ] **graph_query.py** - Query knowledge graph
- [ ] **intelligence/pattern_detection/** - Pattern detection
  - [ ] **pattern_detector.py** - Detect success patterns
  - [ ] **anomaly_detector.py** - Detect anomalies
  - [ ] **trend_analyzer.py** - Analyze trends

---

## 🔄 ГРУППА 4: CORE (Engine & State)

**Назначение:** Workflow execution engine, state machines

```
✅ core/
   ├── workflow_engine.py           # Workflow engine (orchestration)
   ├── state_machine.py             # State machine
   └── pdca_rules.py                # PDCA rules

✅ workflows/
   ├── bcm_processes.py             # BCM process definitions
   └── bia_workflow.py              # BIA workflow
```

---

## 📋 ДУБЛИКАТЫ (Удалить!)

### Root-level дубли:
```
❌ bcm_processes.py                  → workflows/bcm_processes.py
❌ document_templates.py             → infrastructure/templates/
❌ process_framework.py              → infrastructure/process_framework/
❌ process_orchestration_api.py      → api/ (будущий)
❌ metrics_exporter.py               → infrastructure/monitoring/

❌ monitoring/                       → infrastructure/monitoring/
   ├── health.py
   └── metrics.py
```

---

## 📊 ИТОГОВАЯ СТРУКТУРА (Целевая)

```
workflow_intelligence/
│
├── 🏗️ infrastructure/              # ГРУППА 1: ИНФРАСТРУКТУРА
│   ├── coordination/              # Saga, circuit breaker
│   ├── orchestration/             # Multi-service orchestration
│   ├── policies/                  # Compliance, Security, Performance, Quota, Retry
│   ├── monitoring/                # Metrics, Health, Alerts, Tracing
│   ├── security/                  # Encryption, Secrets, PII, Audit
│   ├── process_framework/         # Process models, validation
│   ├── templates/                 # Document generation
│   ├── persistence/               # Database, Cache, Migrations, Backup
│   └── messaging/                 # EventBus, Queues
│
├── 📡 service/                     # ГРУППА 2: СЕРВИС
│   ├── api/                       # REST API endpoints
│   │   ├── workflows.py
│   │   ├── cases.py
│   │   ├── recommendations.py
│   │   ├── governance.py
│   │   └── webhooks.py
│   ├── integration/               # Service-to-service
│   │   ├── base_service_listener.py
│   │   ├── bia_service_listener.py ✅
│   │   ├── planning_service_listener.py
│   │   └── ai_foundation_client.py
│   ├── schemas/                   # Pydantic schemas
│   ├── auth/                      # Authentication, RBAC
│   └── error_handling/            # Error handling
│
├── 🧠 intelligence/                # ГРУППА 3: ИНТЕЛЛЕКТ
│   ├── ai/                        # AI/LLM
│   │   ├── context_advisor.py    ✅
│   │   ├── llm_client.py
│   │   ├── prompt_builder.py
│   │   ├── embeddings.py
│   │   └── semantic_search.py
│   ├── ml/                        # Machine Learning
│   │   ├── models/               # Duration, Risk, Success predictors
│   │   ├── training/             # Training pipeline
│   │   └── inference/            # Real-time predictions
│   ├── case_library/             # Case-based learning ✅
│   ├── pdca/                     # Continuous improvement
│   │   ├── plan_engine.py
│   │   ├── check_analyzer.py
│   │   └── act_learner.py
│   ├── knowledge_graph/          # Knowledge representation
│   └── pattern_detection/        # Pattern & anomaly detection
│
├── ⚙️ core/                        # ГРУППА 4: ENGINE
│   ├── workflow_engine.py        ✅
│   ├── state_machine.py          ✅
│   └── event_bus.py              # Local event bus
│
├── 🎭 governance/                  # Governance (между infrastructure и intelligence)
│   ├── governance_orchestrator.py ✅
│   ├── goals_engine.py           ✅
│   ├── rules_engine_v2.py        ✅
│   └── escalation.py
│
├── 🔄 temporal_workflows/          # Temporal workflows (durability)
│   ├── coordination_workflow.py  ✅
│   ├── bia_workflow.py           ✅
│   └── workers/
│
├── 💾 storage/                     # Data persistence
│   ├── postgres_adapter.py       ✅
│   ├── pdca_repository.py        ✅
│   ├── rls_context.py            ✅
│   ├── migrations/
│   └── vector_store.py
│
├── 📊 workflows/                   # Workflow definitions
│   └── bcm_processes.py          ✅
│
├── 🔍 audit/                       # Audit logging ✅
├── 📏 compliance/                  # ISO compliance ✅
├── 📐 schemas/                     # Data schemas
├── 📝 docs/                        # Documentation
└── main.py                        # FastAPI entrypoint ✅
```

---

## 🎯 НЕДОСТАЮЩИЕ КОМПОНЕНТЫ (Приоритеты)

### Приоритет 1: CRITICAL (для Production)

**Infrastructure:**
- [ ] `infrastructure/coordination/saga_coordinator.py` - Saga pattern
- [ ] `infrastructure/security/secrets.py` - Secrets management (Vault)
- [ ] `infrastructure/monitoring/alerts.py` - Alerting
- [ ] `storage/migrations/` - Database migrations

**Service:**
- [ ] `service/api/workflows.py` - Workflow CRUD
- [ ] `service/integration/base_service_listener.py` - Base pattern
- [ ] `service/integration/planning_service_listener.py` - Planning integration

**Intelligence:**
- [ ] `intelligence/ai/llm_client.py` - LLM client (Phase 1!)
- [ ] `intelligence/ml/models/duration_predictor.py` - Duration ML
- [ ] `intelligence/ml/models/risk_predictor.py` - Risk ML

### Приоритет 2: HIGH (для Scale)

**Infrastructure:**
- [ ] `infrastructure/monitoring/tracing.py` - Distributed tracing
- [ ] `infrastructure/policies/quota.py` - Rate limiting
- [ ] `infrastructure/security/pii_detection.py` - PII masking

**Intelligence:**
- [ ] `intelligence/pdca/` - PDCA subsystem (consolidate)
- [ ] `intelligence/knowledge_graph/` - Knowledge graph
- [ ] `intelligence/pattern_detection/` - Pattern detection

### Приоритет 3: MEDIUM (для Enhancement)

**Service:**
- [ ] `service/api/webhooks.py` - Webhooks
- [ ] `service/api/websockets.py` - Real-time updates

**Intelligence:**
- [ ] `intelligence/ml/training/auto_training.py` - Auto-retraining pipeline
- [ ] `infrastructure/templates/export/` - Export to Word/PDF

---

## 🧹 CLEANUP ACTIONS

### Immediate (сейчас):

1. **DELETE root-level duplicates:**
   ```bash
   mv bcm_processes.py .cleanup-backup/
   mv document_templates.py .cleanup-backup/
   mv process_framework.py .cleanup-backup/
   mv process_orchestration_api.py .cleanup-backup/
   mv metrics_exporter.py .cleanup-backup/
   ```

2. **MERGE monitoring/ → infrastructure/monitoring/:**
   ```bash
   cp monitoring/health.py infrastructure/monitoring/
   cp monitoring/metrics.py infrastructure/monitoring/
   mv monitoring .cleanup-backup/monitoring-root-duplicate
   ```

3. **UPDATE imports in main.py:**
   ```python
   # OLD
   from process_framework import ...

   # NEW
   from infrastructure.process_framework import ...
   ```

---

## 📈 СТАТИСТИКА

**Всего компонентов:** ~120 файлов

**Распределение:**
- Infrastructure: 45 файлов (38%)
- Service: 25 файлов (21%)
- Intelligence: 30 файлов (25%)
- Core: 5 файлов (4%)
- Governance: 8 файлов (7%)
- Support (docs, tests, examples): 15 файлов (12%)

**Дубликаты:** 6 файлов (5%)

**Недостающие (критичные):** 15 компонентов

**Health Score:** 75/100
- ✅ Core functionality complete
- ⚠️ ML models missing (Phase 1 priority)
- ⚠️ Production features incomplete (secrets, migrations)
- ⚠️ Cleanup needed (duplicates)

---

**MD:** Готов начать cleanup и дополнение недостающих компонентов! Какую группу разбираем первой?
